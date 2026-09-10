import random
import time

# Cảnh giới tu tiên
REALMS = [
    "Luyện Khí", "Trúc Cơ", "Kim Đan", "Nguyên Anh",
    "Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa", "Độ Kiếp", "Tiên Nhân"
]

def get_realm(level):
    idx = min((level - 1) // 10, len(REALMS) - 1)
    stage = ((level - 1) % 10) + 1
    return f"{REALMS[idx]} - Tầng {stage}"

def exp_needed(level):
    return 100 * level * level

def cultivate(user_id, player):
    """Tu luyện - nhận EXP và linh khí"""
    now = int(time.time())
    last = player[10]  # last_cultivate
    cooldown = 30  # 30 giây
    
    if now - last < cooldown:
        remain = cooldown - (now - last)
        return False, f"⏳ Cần nghỉ ngơi **{remain}s** trước khi tu luyện tiếp!"
    
    exp_gain = random.randint(15, 30)
    lk_gain = random.randint(5, 15)
    return True, exp_gain, lk_gain

def breakthrough(player):
    """Đột phá cảnh giới"""
    level = player[2]
    exp = player[3]
    needed = exp_needed(level)
    
    if exp < needed:
        return False, f"❌ Chưa đủ tu vi! Cần **{needed - exp}** EXP nữa."
    
    new_level = level + 1
    new_exp = exp - needed
    new_max_hp = player[7] + 20
    new_atk = player[8] + 5
    new_def = player[9] + 3
    
    return True, new_level, new_exp, new_max_hp, new_atk, new_def

def meditate(player):
    """Bế quan - hồi máu và nhận linh thạch"""
    now = int(time.time())
    last = player[11]  # last_meditate
    cooldown = 60
    
    if now - last < cooldown:
        remain = cooldown - (now - last)
        return False, f"⏳ Bế quan cần thêm **{remain}s**!"
    
    hp_gain = random.randint(20, 50)
    lt_gain = random.randint(1, 5)
    return True, hp_gain, lt_gain
