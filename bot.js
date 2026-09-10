import os
import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

from database import init_db, get_user, create_user, update_user, get_top_users
from game import (
    CANH_GIOI, MON_PHAI, DAN_DUOC,
    get_canh_gioi_info, tinh_dot_pha_thanh_cong,
    tinh_sat_thuong, chon_quai_vat, format_number
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Thời gian hồi chiêu (giây)
CD_TU_LUYEN = 30
CD_DAO_KHOANG = 60
CD_PK = 120

# ============ HELPER ============
def check_cd(last_time_str, cd_seconds: int):
    """Kiểm tra cooldown, trả về (còn_lại, ok)"""
    if not last_time_str:
        return 0, True
    last = datetime.fromisoformat(last_time_str)
    elapsed = (datetime.now() - last).total_seconds()
    if elapsed >= cd_seconds:
        return 0, True
    return int(cd_seconds - elapsed), False

async def ensure_user(update: Update):
    """Đảm bảo user tồn tại"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    user = await get_user(user_id)
    if not user:
        user = await create_user(user_id, username)
    return user

def tinh_chi_so(user: dict):
    """Tính chỉ số tổng hợp"""
    cg = get_canh_gioi_info(user["canh_gioi"])
    mp = MON_PHAI.get(user["mon_phai"], MON_PHAI["Tán Tu"])
    hp_max = cg["hp"] + mp["hp"] + user["canh_gioi"] * 50
    atk = cg["atk"] + mp["atk"] + user["cong_kich"]
    def_ = cg["def"] + mp["def"] + user["phong_thu"]
    return hp_max, max(atk, 1), max(def_, 0)

# ============ COMMANDS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    text = (
        "🧘‍♂️ *Chào mừng đến với Tu Tiên Bot!* 🧘‍♂️\n\n"
        f"Đạo hữu *{update.effective_user.first_name}*, "
        "hành trình tu tiên ngàn năm bắt đầu từ đây.\n\n"
        "📜 *Lệnh cơ bản:*\n"
        "• /thongtin - Xem thông tin bản thân\n"
        "• /tuluyen - Tu luyện tăng tu vi\n"
        "• /dotpha - Đột phá cảnh giới\n"
        "• /daokhoang - Khai thác linh thạch\n"
        "• /bangxephang - Bảng xếp hạng\n\n"
        "⚔️ *Chiến đấu:*\n"
        "• /sanquai - Săn quái luyện cấp\n"
        "• /pk @username - Khiêu chiến người khác\n\n"
        "🏯 *Tông môn:*\n"
        "• /monphai - Danh sách môn phái\n"
        "• /giamon <tên> - Gia nhập môn phái\n\n"
        "💊 *Đan dược:*\n"
        "• /cuahang - Cửa hàng đan dược\n"
        "• /muadan <tên> - Mua đan dược\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def thongtin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    cg = get_canh_gioi_info(user["canh_gioi"])
    hp_max, atk, def_ = tinh_chi_so(user)
    next_cg = get_canh_gioi_info(user["canh_gioi"] + 1) if user["canh_gioi"] + 1 < len(CANH_GIOI) else None
    
    text = (
        f"📜 *Hồ sơ tu tiên*\n\n"
        f"👤 Đạo hiệu: *{user['username']}*\n"
        f"🏯 Môn phái: *{user['mon_phai']}*\n"
        f"⭐ Cảnh giới: *{cg['ten']}* (cấp {user['canh_gioi'] + 1})\n"
        f"✨ Tu vi: *{format_number(user['tu_vi'])}*\n"
        f"💎 Linh thạch: *{format_number(user['linh_thach'])}*\n"
        f"🌊 Linh khí: *{user['linh_khi']}*\n\n"
        f"❤️ HP: *{hp_max}*\n"
        f"⚔️ Công kích: *{atk}*\n"
        f"🛡️ Phòng thủ: *{def_}*\n"
    )
    
    if next_cg:
        can_thiet = next_cg["tu_vi_can"]
        text += (
            f"\n🎯 Cần *{format_number(can_thiet - user['tu_vi'])}* tu vi "
            f"để đột phá *{next_cg['ten']}*"
        )
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def tuluyen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    cd_con, ok = check_cd(user.get("last_tu_luyen"), CD_TU_LUYEN)
    if not ok:
        await update.message.reply_text(f"⏳ Đang bế quan, chờ *{cd_con}s* nữa.", parse_mode="Markdown")
        return
    
    if user["linh_khi"] < 10:
        await update.message.reply_text("❌ Linh khí cạn kiệt! Dùng /daokhoang để hồi phục.")
        return
    
    # Random tu vi nhận được
    cg = get_canh_gioi_info(user["canh_gioi"])
    tu_vi_nhan = int((cg["tu_vi_can"] * 0.05 + 10) * random.uniform(0.8, 1.5))
    
    new_tu_vi = user["tu_vi"] + tu_vi_nhan
    new_linh_khi = user["linh_khi"] - 10
    now = datetime.now().isoformat()
    
    await update_user(
        user["user_id"],
        tu_vi=new_tu_vi,
        linh_khi=new_linh_khi,
        last_tu_luyen=now
    )
    
    cg_moi = get_canh_gioi_info(user["canh_gioi"])
    text = (
        f"🧘‍♂️ *Bế quan tu luyện...*\n\n"
        f"✨ Nhận được: *+{format_number(tu_vi_nhan)}* tu vi\n"
        f"💫 Tu vi hiện tại: *{format_number(new_tu_vi)}*\n"
        f"🌊 Linh khí còn: *{new_linh_khi}*\n\n"
    )
    
    if new_tu_vi >= cg_moi["tu_vi_can"] and user["canh_gioi"] + 1 < len(CANH_GIOI):
        text += "🔥 *Đã đủ tu vi! Dùng /dotpha để đột phá!*"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def dotpha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    
    if user["canh_gioi"] + 1 >= len(CANH_GIOI):
        await update.message.reply_text("🌟 Đạo hữu đã đạt đỉnh cao Tiên Nhân! Không thể đột phá thêm.")
        return
    
    cg_hien_tai = get_canh_gioi_info(user["canh_gioi"])
    if user["tu_vi"] < cg_hien_tai["tu_vi_can"] * 1.5:
        await update.message.reply_text(
            f"❌ Tu vi chưa đủ! Cần *{format_number(int(cg_hien_tai['tu_vi_can'] * 1.5))}* "
            f"tu vi để đột phá (hiện có *{format_number(user['tu_vi'])}*).",
            parse_mode="Markdown"
        )
        return
    
    if tinh_dot_pha_thanh_cong(user):
        new_cap = user["canh_gioi"] + 1
        cg_moi = get_canh_gioi_info(new_cap)
        await update_user(
            user["user_id"],
            canh_gioi=new_cap,
            tu_vi=0,
            so_lan_dot_pha=0,
            hp=cg_moi["hp"],
            linh_khi=200
        )
        text = (
            f"⚡ *ĐỘT PHÁ THÀNH CÔNG!* ⚡\n\n"
            f"🎉 Chúc mừng đạo hữu đã đột phá *{cg_moi['ten']}*!\n"
            f"❤️ HP tối đa tăng lên *{cg_moi['hp']}*\n"
            f"⚔️ Công kích cơ bản: *{cg_moi['atk']}*"
        )
    else:
        # Thất bại - mất tu vi, tăng cơ hội lần sau
        mat_tu_vi = int(user["tu_vi"] * 0.2)
        await update_user(
            user["user_id"],
            tu_vi=user["tu_vi"] - mat_tu_vi,
            so_lan_dot_pha=user["so_lan_dot_pha"] + 1
        )
        text = (
            f"💥 *ĐỘT PHÁ THẤT BẠI!*\n\n"
            f"😵 Tẩu hỏa nhập ma, mất *{format_number(mat_tu_vi)}* tu vi.\n"
            f"📈 Cơ hội lần sau tăng thêm 10%!"
        )
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def daokhoang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    cd_con, ok = check_cd(user.get("last_dao_khoang"), CD_DAO_KHOANG)
    if not ok:
        await update.message.reply_text(f"⏳ Mỏ linh thạch đang hồi phục, chờ *{cd_con}s*.", parse_mode="Markdown")
        return
    
    linh_thach = random.randint(20, 80) + user["canh_gioi"] * 30
    linh_khi = 50
    
    await update_user(
        user["user_id"],
        linh_thach=user["linh_thach"] + linh_thach,
        linh_khi=min(user["linh_khi"] + linh_khi, 9999),
        last_dao_khoang=datetime.now().isoformat()
    )
    
    text = (
        f"⛏️ *Khai thác linh mạch...*\n\n"
        f"💎 Nhận được: *+{format_number(linh_thach)}* linh thạch\n"
        f"🌊 Linh khí hồi phục: *+{linh_khi}*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def sanquai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    cd_con, ok = check_cd(user.get("last_dao_khoang"), 30)
    if not ok:
        await update.message.reply_text(f"⏳ Mệt mỏi, chờ *{cd_con}s*.", parse_mode="Markdown")
        return
    
    quai = chon_quai_vat(user["canh_gioi"])
    hp_max, atk, def_ = tinh_chi_so(user)
    
    # Mô phỏng trận đấu
    hp_ta = hp_max
    hp_quai = quai["hp"]
    log = [f"⚔️ *Gặp {quai['ten']}!* (HP: {hp_quai})"]
    turn = 1
    
    while hp_ta > 0 and hp_quai > 0 and turn <= 20:
        # Ta đánh
        st, chi_mang = tinh_sat_thuong(atk, 0)
        hp_quai -= st
        log.append(f"Turn {turn}: Ta gây *{st}* dmg" + (" 💥CHÍ MẠNG" if chi_mang else ""))
        if hp_quai <= 0:
            break
        # Quái đánh
        st_q, _ = tinh_sat_thuong(quai["atk"], def_)
        hp_ta -= st_q
        log.append(f"          Quái gây *{st_q}* dmg")
        turn += 1
    
    if hp_quai <= 0:
        reward = quai["reward"]
        tu_vi = int(reward * 0.5)
        await update_user(
            user["user_id"],
            linh_thach=user["linh_thach"] + reward,
            tu_vi=user["tu_vi"] + tu_vi,
            last_dao_khoang=datetime.now().isoformat()
        )
        text = (
            "\n".join(log[:8]) + "\n...\n\n"
            f"🏆 *CHIẾN THẮNG!*\n"
            f"💎 +{format_number(reward)} linh thạch\n"
            f"✨ +{format_number(tu_vi)} tu vi"
        )
    else:
        mat = int(user["linh_thach"] * 0.1)
        await update_user(
            user["user_id"],
            linh_thach=max(0, user["linh_thach"] - mat),
            last_dao_khoang=datetime.now().isoformat()
        )
        text = (
            "\n".join(log[:8]) + "\n...\n\n"
            f"💀 *THẤT BẠI!*\n"
            f"Mất *{format_number(mat)}* linh thạch để chữa thương."
        )
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def monphai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🏯 *Danh sách môn phái:*\n\n"
    for ten, info in MON_PHAI.items():
        text += (
            f"• *{ten}*\n"
            f"  ⚔️ ATK: +{info['atk']} | 🛡️ DEF: +{info['def']} | ❤️ HP: +{info['hp']}\n"
        )
    text += "\nDùng `/giamon <tên>` để gia nhập. Ví dụ: `/giamon Thanh Vân Tông`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def giamon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    if not context.args:
        await update.message.reply_text("❌ Dùng: `/giamon <tên môn phái>`", parse_mode="Markdown")
        return
    
    ten = " ".join(context.args)
    if ten not in MON_PHAI:
        await update.message.reply_text("❌ Môn phái không tồn tại! Dùng /monphai để xem danh sách.")
        return
    
    await update_user(user["user_id"], mon_phai=ten)
    await update.message.reply_text(f"🎉 Đã gia nhập *{ten}*!", parse_mode="Markdown")

async def cuahang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💊 *Cửa hàng đan dược:*\n\n"
    for ten, info in DAN_DUOC.items():
        text += f"• *{ten}* - {format_number(info['gia'])} 💎\n"
        text += f"   └ Tăng {info['gia_tri']} {info['cong_dung']}\n"
    text += "\nDùng `/muadan <tên>` để mua."
    await update.message.reply_text(text, parse_mode="Markdown")

async def muadan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    if not context.args:
        await update.message.reply_text("❌ Dùng: `/muadan <tên đan>`", parse_mode="Markdown")
        return
    
    ten = " ".join(context.args)
    if ten not in DAN_DUOC:
        await update.message.reply_text("❌ Đan dược không tồn tại!")
        return
    
    info = DAN_DUOC[ten]
    if user["linh_thach"] < info["gia"]:
        await update.message.reply_text(f"❌ Không đủ linh thạch! Cần {format_number(info['gia'])}.")
        return
    
    update_data = {"linh_thach": user["linh_thach"] - info["gia"]}
    if info["cong_dung"] == "tu_vi":
        update_data["tu_vi"] = user["tu_vi"] + info["gia_tri"]
    elif info["cong_dung"] == "linh_khi":
        update_data["linh_khi"] = user["linh_khi"] + info["gia_tri"]
    
    await update_user(user["user_id"], **update_data)
    await update.message.reply_text(
        f"✅ Đã dùng *{ten}*\n+{info['gia_tri']} {info['cong_dung']}",
        parse_mode="Markdown"
    )

async def bangxephang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = await get_top_users(10)
    if not top:
        await update.message.reply_text("Chưa có ai tu tiên!")
        return
    
    text = "🏆 *Bảng Xếp Hạng Tu Tiên* 🏆\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(top):
        cg = get_canh_gioi_info(u["canh_gioi"])
        rank = medals[i] if i < 3 else f"#{i+1}"
        text += (
            f"{rank} *{u['username']}*\n"
            f"   └ {cg['ten']} • {format_number(u['tu_vi'])} tu vi\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")

async def pk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    
    # Lấy đối thủ từ reply
    target_id = None
    target_name = None
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_name = update.message.reply_to_message.from_user.first_name
    else:
        await update.message.reply_text("❌ Reply tin nhắn đối thủ và gõ /pk")
        return
    
    if target_id == user["user_id"]:
        await update.message.reply_text("❌ Không thể tự đánh mình!")
        return
    
    target = await get_user(target_id)
    if not target:
        await update.message.reply_text("❌ Đối thủ chưa tu tiên! Bảo họ gõ /start")
        return
    
    hp1, atk1, def1 = tinh_chi_so(user)
    hp2, atk2, def2 = tinh_chi_so(target)
    
    # Mô phỏng
    h1, h2 = hp1, hp2
    turn = 1
    while h1 > 0 and h2 > 0 and turn <= 30:
        st1, _ = tinh_sat_thuong(atk1, def2)
        h2 -= st1
        if h2 <= 0:
            break
        st2, _ = tinh_sat_thuong(atk2, def1)
        h1 -= st2
        turn += 1
    
    if h2 <= 0:
        reward = int(target["linh_thach"] * 0.1)
        await update_user(user["user_id"], linh_thach=user["linh_thach"] + reward)
        await update_user(target_id, linh_thach=max(0, target["linh_thach"] - reward))
        text = (
            f"⚔️ *PK: {user['username']} vs {target['username']}*\n\n"
            f"🏆 *{user['username']} THẮNG!*\n"
            f"💎 Cướp được *{format_number(reward)}* linh thạch"
        )
    else:
        reward = int(user["linh_thach"] * 0.1)
        await update_user(user["user_id"], linh_thach=max(0, user["linh_thach"] - reward))
        await update_user(target_id, linh_thach=target["linh_thach"] + reward)
        text = (
            f"⚔️ *PK: {user['username']} vs {target['username']}*\n\n"
            f"💀 *{target['username']} THẮNG!*\n"
            f"💎 {user['username']} mất *{format_number(reward)}* linh thạch"
        )
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Hướng dẫn Tu Tiên*\n\n"
        "*Cơ bản:*\n"
        "/thongtin - Xem hồ sơ\n"
        "/tuluyen - Tu luyện (CD 30s)\n"
        "/dotpha - Đột phá cảnh giới\n"
        "/daokhoang - Đào linh thạch (CD 60s)\n"
        "/bangxephang - Top 10\n\n"
        "*Chiến đấu:*\n"
        "/sanquai - Săn quái\n"
        "/pk (reply) - Khiêu chiến\n\n"
        "*Tông môn:*\n"
        "/monphai - Xem môn phái\n"
        "/giamon <tên> - Gia nhập\n\n"
        "*Đan dược:*\n"
        "/cuahang - Xem shop\n"
        "/muadan <tên> - Mua\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ MAIN ============
async def post_init(app):
    await init_db()
    print("✅ Database đã khởi tạo")

def main():
    if not BOT_TOKEN:
        raise ValueError("Thiếu BOT_TOKEN!")
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("thongtin", thongtin))
    app.add_handler(CommandHandler("tuluyen", tuluyen))
    app.add_handler(CommandHandler("dotpha", dotpha))
    app.add_handler(CommandHandler("daokhoang", daokhoang))
    app.add_handler(CommandHandler("sanquai", sanquai))
    app.add_handler(CommandHandler("monphai", monphai))
    app.add_handler(CommandHandler("giamon", giamon))
    app.add_handler(CommandHandler("cuahang", cuahang))
    app.add_handler(CommandHandler("muadan", muadan))
    app.add_handler(CommandHandler("bangxephang", bangxephang))
    app.add_handler(CommandHandler("pk", pk))
    
    print("🚀 Bot tu tiên đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
