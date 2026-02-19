import logging
from db import execute_query

class ClubsService:
    
    @staticmethod
    def validate_name(name):
        """Валидира име на клуб"""
        if not name or not name.strip():
            raise ValueError("Името на клуба не може да бъде празно")
        return name.strip()
    
    @staticmethod
    def add_club(name):
        """Добавя нов клуб"""
        try:
            name = ClubsService.validate_name(name)
            
            # Проверка за дублиране
            existing = execute_query(
                "SELECT id FROM clubs WHERE name = ?", 
                (name,), 
                fetch_one=True
            )
            
            if existing:
                return f"❌ Клуб '{name}' вече съществува"
            
            # Добавяне на клуб
            execute_query(
                "INSERT INTO clubs (name) VALUES (?)", 
                (name,)
            )
            
            logging.info(f"Добавен клуб: {name}")
            return f"✅ Успешно добавен клуб: {name}"
            
        except Exception as e:
            logging.error(f"Грешка при добавяне на клуб: {e}")
            return f"❌ Грешка: {str(e)}"
    
    @staticmethod
    def get_all_clubs():
        """Връща всички клубове"""
        try:
            clubs = execute_query(
                "SELECT * FROM clubs ORDER BY name", 
                fetch_all=True
            )
            return clubs
        except Exception as e:
            logging.error(f"Грешка при вземане на клубове: {e}")
            return []
    
    @staticmethod
    def delete_club(identifier):
        """Изтрива клуб по име или ID"""
        try:
            # Проверка дали е ID или име
            if str(identifier).isdigit():
                # Търсене по ID
                club = execute_query(
                    "SELECT * FROM clubs WHERE id = ?", 
                    (identifier,), 
                    fetch_one=True
                )
                if club:
                    execute_query("DELETE FROM clubs WHERE id = ?", (identifier,))
                    return f"✅ Изтрит клуб с ID {identifier}: {club['name']}"
            else:
                # Търсене по име
                name = identifier.strip()
                club = execute_query(
                    "SELECT * FROM clubs WHERE name = ?", 
                    (name,), 
                    fetch_one=True
                )
                if club:
                    execute_query("DELETE FROM clubs WHERE name = ?", (name,))
                    return f"✅ Изтрит клуб: {name}"
            
            return f"❌ Клуб '{identifier}' не е намерен"
            
        except Exception as e:
            logging.error(f"Грешка при изтриване на клуб: {e}")
            return f"❌ Грешка: {str(e)}"
    
    @staticmethod
    def update_club(old_name, new_name):
        """Обновява име на клуб (по желание)"""
        try:
            new_name = ClubsService.validate_name(new_name)
            
            # Проверка дали клубът съществува
            club = execute_query(
                "SELECT * FROM clubs WHERE name = ?", 
                (old_name,), 
                fetch_one=True
            )
            
            if not club:
                return f"❌ Клуб '{old_name}' не е намерен"
            
            # Проверка за дублиране на новото име
            existing = execute_query(
                "SELECT id FROM clubs WHERE name = ?", 
                (new_name,), 
                fetch_one=True
            )
            
            if existing:
                return f"❌ Клуб '{new_name}' вече съществува"
            
            # Обновяване
            execute_query(
                "UPDATE clubs SET name = ? WHERE name = ?", 
                (new_name, old_name)
            )
            
            return f"✅ Клубът '{old_name}' е преименуван на '{new_name}'"
            
        except Exception as e:
            logging.error(f"Грешка при обновяване на клуб: {e}")
            return f"❌ Грешка: {str(e)}"
