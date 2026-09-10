import sqlite3

DB_PATH = "tu_tien.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            linh_khi INTEGER DEFAULT 100,
            hp INTEGER DEFAULT 100,
            max_hp INTEGER DEFAULT 100,
            atk INTEGER DEFAULT 10,
            def INTEGER DEFAULT 5,
            linh_thach INTEGER DEFAULT 0,
            last_cultivate INTEGER DEFAULT 0,
            last_meditate INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_player(user_id, username=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        c.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return row

def update_player(user_id, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE players SET {key} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

def get_top(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, level, exp FROM players ORDER BY level DESC, exp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
