import sqlite3
import logging
from pathlib import Path

# Път до базата данни (в главната папка на проекта)
DB_PATH = Path(__file__).parent.parent.parent / "clubs.db"

def get_connection():
    """
    Създава и връща връзка към базата данни
    
    Returns:
        sqlite3.Connection: Връзка към базата данни
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row  # Достъп по име на колона
        return conn
    except sqlite3.Error as e:
        logging.error(f"Грешка при свързване с базата: {e}")
        raise

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """
    Изпълнява единична SQL заявка
    
    Args:
        query (str): SQL заявка
        params (tuple): Параметри за заявката
        fetch_one (bool): Връща един резултат
        fetch_all (bool): Връща всички резултати
    
    Returns:
        int | dict | list | None: Резултат от заявката
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # За INSERT, UPDATE, DELETE
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
            return cursor.lastrowid
        
        # За SELECT
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

def execute_transaction(queries):
    """
    Изпълнява няколко заявки в една транзакция (атомично)
    Използва се за трансфери - или всичко минава, или нищо
    
    Args:
        queries (list): Списък от (query, params) tuples
    
    Returns:
        bool: True ако всичко е успешно
    
    Raises:
        Exception: При грешка се прави rollback
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Изпълнява всички заявки
        for query, params in queries:
            cursor.execute(query, params)
        
        # Ако всички заявки са успешни - commit
        conn.commit()
        return True
        
    except Exception as e:
        logging.error(f"Грешка при транзакция: {e}")
        # При грешка - rollback (връщане към предишното състояние)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_database():
    """
    Инициализира базата данни от schema.sql файла
    Създава всички таблици и индекси
    """
    # Път до schema.sql файла
    schema_path = Path(__file__).parent.parent.parent / "sql" / "schema.sql"
    
    try:
        # Четене на SQL скрипта
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Изпълнение на скрипта
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        logging.info("Базата данни е инициализирана успешно")
        
    except FileNotFoundError:
        logging.error(f"Файлът schema.sql не е намерен на: {schema_path}")
        raise
    except Exception as e:
        logging.error(f"Грешка при инициализация на базата: {e}")
        raise

def get_table_info(table_name):
    """
    Връща информация за структурата на таблица
    
    Args:
        table_name (str): Име на таблицата
    
    Returns:
        list: Списък с колоните на таблицата
    """
    try:
        return execute_query(f"PRAGMA table_info({table_name})", fetch_all=True)
    except Exception as e:
        logging.error(f"Грешка при вземане на информация за таблица {table_name}: {e}")
        return []

def table_exists(table_name):
    """
    Проверява дали дадена таблица съществува
    
    Args:
        table_name (str): Име на таблицата
    
    Returns:
        bool: True ако таблицата съществува
    """
    try:
        result = execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
            fetch_one=True
        )
        return result is not None
    except Exception as e:
        logging.error(f"Грешка при проверка за таблица {table_name}: {e}")
        return False

# Тест на модула (ако се изпълни директно)
if __name__ == "__main__":
    print("🔍 Тестване на database модула...")
    
    # Тест 1: Инициализация
    print("1. Инициализиране на базата...")
    init_database()
    print("   ✅ Базата е инициализирана")
    
    # Тест 2: Проверка на таблиците
    print("2. Проверка на таблиците...")
    tables = ['clubs', 'players', 'transfers']
    for table in tables:
        exists = table_exists(table)
        print(f"   📋 Таблица '{table}': {'✅ съществува' if exists else '❌ липсва'}")
    
    # Тест 3: Информация за таблиците
    print("3. Информация за таблица 'clubs':")
    info = get_table_info('clubs')
    for col in info:
        print(f"   📊 {col['name']} ({col['type']})")
    
    print("\n✅ Тестът приключи успешно!")
