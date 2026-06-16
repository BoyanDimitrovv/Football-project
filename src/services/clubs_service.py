import logging
from database.db import execute_query


class ClubsService:

    @staticmethod
    def add_club(name):
        if not name or not name.strip():
            return "❌ Името на клуба не може да бъде празно"

        try:
            name = name.strip()
            existing = execute_query(
                "SELECT id FROM clubs WHERE LOWER(name) = LOWER(?)",
                (name,),
                fetch_one=True
            )
            if existing:
                return f"❌ Клуб '{name}' вече съществува"
            execute_query("INSERT INTO clubs (name) VALUES (?)", (name,))
            return f"✅ Успешно добавен клуб: {name}"
        except Exception as e:
            return f"❌ Грешка: {str(e)}"

    @staticmethod
    def get_all_clubs():
        try:
            return execute_query("SELECT * FROM clubs ORDER BY name", fetch_all=True)
        except Exception as e:
            return []

    @staticmethod
    def find_club_by_name(club_name):
        """Намира клуб по име (без значение на малки/главни букви)"""
        if not club_name:
            return None

        # Взимаме всички клубове и търсим ръчно
        all_clubs = execute_query("SELECT * FROM clubs", fetch_all=True)
        for club in all_clubs:
            if club_name.lower() in club['name'].lower():
                return club

        return None

