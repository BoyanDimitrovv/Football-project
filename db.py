import sqlite3
DB_PATH = "football.db"

def get_connection():
    """
    Създава и връща връзка към базата данни.
    Включва PRAGMA foreign_keys = ON за работа с външни ключове.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print("Database connection error:", e)
        raise

def execute_query(sql, params=()):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor
    except sqlite3.IntegrityError as e:
        print("Integrity error:", e)
        raise
    except sqlite3.Error as e:
        print("Database error:", e)
        raise

def fetch_all(sql, params=()):

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print("Database fetch_all error:", e)
        raise

def fetch_one(sql, params=()):

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
    except sqlite3.Error as e:
        print("Database fetch_one error:", e)
        raise
