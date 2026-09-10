import random
import time

REALMS = [
    "Luyện Khí", "Trúc Cơ", "Kim Đan", "Nguyên Anh",
    "Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa", "Độ Kiếp", "Tiên Nhân"
]

CULTIVATE_CD = 30
MEDITATE_CD = 60
DAILY_CD = 86400


def get_realm(level):
    idx = min((level - 1) // 10, len(REALMS) - 1)
    stage = ((level - 1) % 10) + 1
    return f"{REALMS[idx]} - Tầng {stage}"


def exp_needed(level):
    return 100 * level * level


def cultivate(player):
    now = int(time.time())
    last = player[10]
    if now - last < CULTIVATE_CD:
        remain = CULTIVATE_CD - (now - last)
        return False, f"⏳ Cần nghỉ **{remain}s** trước khi tu luyện tiếp!"

    exp_gain = random.randint(15, 30)
    lk_gain = random.randint(5, 15)
    return True, exp_gain, lk_gain


def breakthrough(player):
    level = player[2]
    exp = player[3]
    needed = exp_needed(level)

    if exp < needed:
        return False, f"❌ Chưa đủ tu vi! Cần thêm **{needed - exp}** EXP."

    new_level = level + 1
    new_exp = exp - needed
    new_max_hp = player[7] + 20
    new_atk = player[8] + 5
    new_def = player[9] + 3

    return True, new_level, new_exp, new_max_hp, new_atk, new_def


def meditate(player):
    now = int(time.time())
    last = player[11]
    if now - last < MEDITATE_CD:
        remain = MEDITATE_CD - (now - last)
        return False, f"⏳ Bế quan cần thêm **{remain}s**!"

    hp_gain = random.randint(20, 50)
    lt_gain = random.randint(1, 5)
    return True, hp_gain, lt_gain


def check_daily(player):
    now = int(time.time())
    last = player[12]
    if now - last < DAILY_CD:
        remain = DAILY_CD - (now - last)
        hours = remain // 3600
        mins = (remain % 3600) // 60
        return False, f"⏳ Điểm danh lại sau **{hours}h {mins}p**!"
    return True, "OK"
