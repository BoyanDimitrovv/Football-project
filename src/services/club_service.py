"""
CLUBS SERVICE - ЕТАП 2 (актуализиран за Етап 4)
"""

import logging
import sqlite3
from pathlib import Path

# Път до базата данни
DB_PATH = Path(__file__).parent.parent.parent / "clubs.db"


def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Изпълнява заявка към базата"""
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
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

    except Exception as e:
        logging.error(f"Грешка: {e}")
        raise
    finally:
        if conn:
            conn.close()


class ClubsService:

    @staticmethod
    def add_club(name):
        """Добавя нов клуб"""
        if not name or not name.strip():
            return "❌ Името на клуба не може да бъде празно"

        try:
            name = name.strip()

            existing = execute_query(
                "SELECT id FROM clubs WHERE name = ?",
                (name,),
                fetch_one=True
            )

            if existing:
                return f"❌ Клуб '{name}' вече съществува"

            execute_query("INSERT INTO clubs (name) VALUES (?)", (name,))
            return f"✅ Успешно добавен клуб: {name}"

        except Exception as e:
            logging.error(f"Грешка при добавяне на клуб: {e}")
            return f"❌ Грешка: {str(e)}"

    @staticmethod
    def get_all_clubs():
        """Връща всички клубове"""
        try:
            return execute_query(
                "SELECT * FROM clubs ORDER BY name",
                fetch_all=True
            )
        except Exception as e:
            logging.error(f"Грешка при вземане на клубове: {e}")
            return []

    @staticmethod
    def find_club_by_name(club_name):
        """Намира клуб по име (за трансфери)"""
        if not club_name or club_name.lower() in ['няма', 'свободен', 'без клуб']:
            return None

        club = execute_query(
            "SELECT * FROM clubs WHERE name LIKE ?",
            (f"%{club_name}%",),
            fetch_one=True
        )
        return club
