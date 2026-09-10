import os
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")
USE_PG = DATABASE_URL is not None

if USE_PG:
    import psycopg2

DB_PATH = "tu_tien.db"


def get_conn():
    if USE_PG:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_PATH)


def ph():
    return "%s" if USE_PG else "?"


def init_db():
    conn = get_conn()
    c = conn.cursor()

    if USE_PG:
        c.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                linh_khi INTEGER DEFAULT 100,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                atk INTEGER DEFAULT 10,
                def INTEGER DEFAULT 5,
                linh_thach INTEGER DEFAULT 0,
                last_cultivate BIGINT DEFAULT 0,
                last_meditate BIGINT DEFAULT 0,
                last_daily BIGINT DEFAULT 0
            )
        """)
    else:
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
                last_meditate INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0
            )
        """)

    conn.commit()
    conn.close()


def get_player(user_id, username=""):
    conn = get_conn()
    c = conn.cursor()
    p = ph()
    c.execute(f"SELECT * FROM players WHERE user_id = {p}", (user_id,))
    row = c.fetchone()

    if not row:
        c.execute(
            f"INSERT INTO players (user_id, username) VALUES ({p}, {p})",
            (user_id, username)
        )
        conn.commit()
        c.execute(f"SELECT * FROM players WHERE user_id = {p}", (user_id,))
        row = c.fetchone()

    conn.close()
    return row


def update_player(user_id, **kwargs):
    if not kwargs:
        return
    conn = get_conn()
    c = conn.cursor()
    p = ph()
    fields = ", ".join([f"{k} = {p}" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE players SET {fields} WHERE user_id = {p}", values)
    conn.commit()
    conn.close()


def get_top(limit=10):
    conn = get_conn()
    c = conn.cursor()
    p = ph()
    c.execute(
        f"SELECT username, level, exp FROM players ORDER BY level DESC, exp DESC LIMIT {p}",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return rows
