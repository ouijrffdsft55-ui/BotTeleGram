import aiosqlite

DB_NAME = "tutien.db"

async def init_db():
    """Khởi tạo database"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                tu_vi INTEGER DEFAULT 0,
                canh_gioi INTEGER DEFAULT 0,
                linh_khi INTEGER DEFAULT 100,
                linh_thach INTEGER DEFAULT 100,
                hp INTEGER DEFAULT 100,
                cong_kich INTEGER DEFAULT 10,
                phong_thu INTEGER DEFAULT 5,
                mon_phai TEXT DEFAULT 'Tán Tu',
                last_tu_luyen TEXT,
                last_dao_khoang TEXT,
                so_lan_dot_pha INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_user(user_id: int):
    """Lấy thông tin user"""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_user(user_id: int, username: str):
    """Tạo user mới"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()
    return await get_user(user_id)

async def update_user(user_id: int, **kwargs):
    """Cập nhật thông tin user"""
    if not kwargs:
        return
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
        await db.commit()

async def get_top_users(limit: int = 10):
    """Lấy bảng xếp hạng"""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users ORDER BY canh_gioi DESC, tu_vi DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
