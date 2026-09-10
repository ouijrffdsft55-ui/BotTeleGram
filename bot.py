import os
import logging
import threading
import time

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

from database import init_db, get_player, update_player, get_top
from game import (
    get_realm, exp_needed, cultivate, breakthrough,
    meditate, check_daily
)
from web_server import run_web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_player(user.id, user.username or user.first_name)

    text = (
        f"🧘 **Chào mừng {user.first_name} đến Tu Tiên Giới!**\n\n"
        "📜 **Danh sách lệnh:**\n"
        "• /thongtin - Xem thông tin tu sĩ\n"
        "• /tuluyen - Tu luyện nhận EXP\n"
        "• /dotpha - Đột phá cảnh giới\n"
        "• /beguan - Bế quan hồi máu\n"
        "• /bangxephang - Bảng xếp hạng\n"
        "• /daily - Điểm danh nhận thưởng"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def thong_tin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = get_player(user.id, user.username or user.first_name)

    needed = exp_needed(p[2])
    realm = get_realm(p[2])
    ratio = min(p[3] / needed, 1.0)
    filled = int(ratio * 10)
    bar = "█" * filled + "░" * (10 - filled)

    text = (
        f"🧙 **Thông tin tu sĩ: {user.first_name}**\n\n"
        f"⚔️ Cảnh giới: **{realm}** (Cấp {p[2]})\n"
        f"💫 Tu vi: `{bar}` {p[3]}/{needed}\n"
        f"❤️ HP: {p[6]}/{p[7]}\n"
        f"🗡️ ATK: {p[8]} | 🛡️ DEF: {p[9]}\n"
        f"🌿 Linh khí: {p[5]}\n"
        f"💎 Linh thạch: {p[10]}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def tu_luyen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = get_player(user.id)

    ok, *res = cultivate(p)
    if not ok:
        await update.message.reply_text(res[0], parse_mode="Markdown")
        return

    exp_gain, lk_gain = res
    update_player(
        user.id,
        exp=p[3] + exp_gain,
        linh_khi=p[5] + lk_gain,
        last_cultivate=int(time.time())
    )

    await update.message.reply_text(
        f"🧘 **Tu luyện thành công!**\n"
        f"✨ Nhận **{exp_gain}** EXP\n"
        f"🌿 Nhận **{lk_gain}** linh khí",
        parse_mode="Markdown"
    )


async def dot_pha(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = get_player(user.id)

    ok, *res = breakthrough(p)
    if not ok:
        await update.message.reply_text(res[0], parse_mode="Markdown")
        return

    new_level, new_exp, new_max_hp, new_atk, new_defense = res
    update_player(
        user.id,
        level=new_level, exp=new_exp,
        max_hp=new_max_hp, hp=new_max_hp,
        atk=new_atk, defense=new_defense
    )

    await update.message.reply_text(
        f"⚡ **ĐỘT PHÁ THÀNH CÔNG!**\n\n"
        f"🎉 Cảnh giới mới: **{get_realm(new_level)}**\n"
        f"❤️ Max HP: +20\n"
        f"🗡️ ATK: +5\n"
        f"🛡️ DEF: +3",
        parse_mode="Markdown"
    )


async def be_guan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = get_player(user.id)

    ok, *res = meditate(p)
    if not ok:
        await update.message.reply_text(res[0], parse_mode="Markdown")
        return

    hp_gain, lt_gain = res
    new_hp = min(p[6] + hp_gain, p[7])
    update_player(
        user.id,
        hp=new_hp,
        linh_thach=p[10] + lt_gain,
        last_meditate=int(time.time())
    )

    await update.message.reply_text(
        f"🧘 **Bế quan hoàn tất!**\n"
        f"❤️ Hồi **{hp_gain}** HP\n"
        f"💎 Nhận **{lt_gain}** linh thạch",
        parse_mode="Markdown"
    )


async def bang_xep_hang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    top = get_top(10)
    if not top:
        await update.message.reply_text("📭 Chưa có ai tu luyện!")
        return

    text = "🏆 **BẢNG XẾP HẠNG TU SĨ**\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, level, exp) in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} **{name or 'Ẩn danh'}** - {get_realm(level)}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def daily(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = get_player(user.id)

    ok, msg = check_daily(p)
    if not ok:
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    bonus = 50
    update_player(
        user.id,
        linh_thach=p[10] + bonus,
        last_daily=int(time.time())
    )

    await update.message.reply_text(
        f"🎁 **Điểm danh thành công!**\n💎 Nhận **{bonus}** linh thạch",
        parse_mode="Markdown"
    )


async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {ctx.error}", exc_info=ctx.error)


def main():
    if not TOKEN:
        raise ValueError("❌ Thiếu biến môi trường BOT_TOKEN!")

    init_db()
    logger.info("✅ Database đã sẵn sàng")

    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    logger.info("✅ Web server đã khởi động")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("thongtin", thong_tin))
    app.add_handler(CommandHandler("tuluyen", tu_luyen))
    app.add_handler(CommandHandler("dotpha", dot_pha))
    app.add_handler(CommandHandler("beguan", be_guan))
    app.add_handler(CommandHandler("bangxephang", bang_xep_hang))
    app.add_handler(CommandHandler("daily", daily))

    app.add_error_handler(error_handler)

    logger.info("🤖 Bot đang chạy...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
