import sqlite3
import logging
from pathlib import Path

# Конфигурация
DB_PATH = Path(__file__).parent.parent / "clubs.db"

def get_connection():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row  # Достъп по име на колона
        return conn
    except sqlite3.Error as e:
        logging.error(f"Грешка при свързване с базата: {e}")
        raise

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
            return cursor.lastrowid
        
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        
        return cursor.fetchall()
    
    except sqlite3.Error as e:
        logging.error(f"Грешка при изпълнение на заявка: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_database()
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        logging.info("Базата данни е инициализирана успешно")
    except Exception as e:
        logging.error(f"Грешка при инициализация на базата: {e}")
        raise
