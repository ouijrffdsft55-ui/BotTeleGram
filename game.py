import random

# Danh sách cảnh giới tu tiên
CANH_GIOI = [
    {"ten": "Luyện Khí", "tu_vi_can": 100, "hp": 100, "atk": 10, "def": 5},
    {"ten": "Trúc Cơ", "tu_vi_can": 500, "hp": 300, "atk": 30, "def": 15},
    {"ten": "Kim Đan", "tu_vi_can": 2000, "hp": 800, "atk": 80, "def": 40},
    {"ten": "Nguyên Anh", "tu_vi_can": 8000, "hp": 2000, "atk": 200, "def": 100},
    {"ten": "Hóa Thần", "tu_vi_can": 30000, "hp": 5000, "atk": 500, "def": 250},
    {"ten": "Luyện Hư", "tu_vi_can": 100000, "hp": 12000, "atk": 1200, "def": 600},
    {"ten": "Hợp Thể", "tu_vi_can": 350000, "hp": 30000, "atk": 3000, "def": 1500},
    {"ten": "Đại Thừa", "tu_vi_can": 1000000, "hp": 70000, "atk": 7000, "def": 3500},
    {"ten": "Độ Kiếp", "tu_vi_can": 3000000, "hp": 150000, "atk": 15000, "def": 7500},
    {"ten": "Tiên Nhân", "tu_vi_can": 10000000, "hp": 500000, "atk": 50000, "def": 25000},
]

# Môn phái
MON_PHAI = {
    "Tán Tu": {"atk": 0, "def": 0, "hp": 0},
    "Thanh Vân Tông": {"atk": 20, "def": 10, "hp": 50},
    "Ma Đạo": {"atk": 40, "def": -10, "hp": 0},
    "Phật Môn": {"atk": 0, "def": 30, "hp": 100},
    "Yêu Tộc": {"atk": 30, "def": 0, "hp": 80},
}

# Quái vật theo cảnh giới
QUAI_VAT = [
    {"ten": "Linh Thỏ", "hp": 50, "atk": 5, "reward": 20},
    {"ten": "Hắc Lang", "hp": 150, "atk": 15, "reward": 50},
    {"ten": "Yêu Xà", "hp": 400, "atk": 40, "reward": 150},
    {"ten": "Huyết Ma", "hp": 1000, "atk": 100, "reward": 400},
    {"ten": "Cổ Thú", "hp": 3000, "atk": 300, "reward": 1200},
    {"ten": "Ma Vương", "hp": 8000, "atk": 800, "reward": 3000},
    {"ten": "Yêu Long", "hp": 20000, "atk": 2000, "reward": 8000},
]

# Đan dược
DAN_DUOC = {
    "Tụ Linh Đan": {"gia": 500, "cong_dung": "tu_vi", "gia_tri": 100},
    "Hồi Khí Đan": {"gia": 300, "cong_dung": "linh_khi", "gia_tri": 200},
    "Trúc Cơ Đan": {"gia": 2000, "cong_dung": "tu_vi", "gia_tri": 500},
    "Kim Đan": {"gia": 10000, "cong_dung": "tu_vi", "gia_tri": 2000},
}

def get_canh_gioi_info(cap: int):
    """Lấy thông tin cảnh giới theo cấp"""
    if cap < 0 or cap >= len(CANH_GIOI):
        return CANH_GIOI[-1]
    return CANH_GIOI[cap]

def tinh_dot_pha_thanh_cong(user: dict) -> bool:
    """Tính tỉ lệ đột phá thành công"""
    so_lan = user.get("so_lan_dot_pha", 0)
    # Mỗi lần đột phá thất bại tăng 10% cơ hội
    ti_le = min(50 + so_lan * 10, 95)
    return random.randint(1, 100) <= ti_le

def tinh_sat_thuong(atk: int, def_: int) -> int:
    """Tính sát thương với random"""
    co_ban = max(atk - def_, 1)
    random_phan_tram = random.uniform(0.8, 1.2)
    chi_mang = random.randint(1, 100) <= 10  # 10% chí mạng
    sat_thuong = int(co_ban * random_phan_tram)
    if chi_mang:
        sat_thuong *= 2
    return sat_thuong, chi_mang

def chon_quai_vat(canh_gioi: int) -> dict:
    """Chọn quái vật phù hợp cảnh giới"""
    idx = min(canh_gioi, len(QUAI_VAT) - 1)
    # Có thể gặp quái yếu hơn hoặc mạnh hơn
    idx = max(0, idx + random.randint(-1, 1))
    quai = QUAI_VAT[idx].copy()
    # Random HP quái
    quai["hp"] = int(quai["hp"] * random.uniform(0.8, 1.3))
    quai["max_hp"] = quai["hp"]
    return quai

def format_number(n: int) -> str:
    """Format số có dấu phẩy"""
    return f"{n:,}".replace(",", ".")
