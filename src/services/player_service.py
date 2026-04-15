# src/players_service.py
import logging
import re
from datetime import datetime
from database.db import execute_query


class PlayersService:
    
    # Валидни позиции
    VALID_POSITIONS = ['GK', 'DF', 'MF', 'FW']
    VALID_STATUSES = ['active', 'injured', 'suspended']
    
    @staticmethod
    def validate_date(date_str):
        """Валидира дата във формат YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_number(number, club_id=None, player_id=None):
        """Валидира номер (1-99) и уникалност в клуба"""
        try:
            number = int(number)
            if number < 1 or number > 99:
                return False, "Номерът трябва да е между 1 и 99"
            
            # Проверка за уникалност в клуба
            if club_id:
                query = "SELECT id FROM players WHERE club_id = ? AND number = ?"
                params = [club_id, number]
                
                # При ъпдейт, изключваме текущия играч
                if player_id:
                    query += " AND id != ?"
                    params.append(player_id)
                
                existing = execute_query(query, params, fetch_one=True)
                if existing:
                    return False, f"Номер {number} вече е зает в този клуб"
            
            return True, number
        except ValueError:
            return False, "Номерът трябва да е число"
    
    @staticmethod
    def validate_position(position):
        """Валидира позиция"""
        position = position.upper()
        if position not in PlayersService.VALID_POSITIONS:
            return False, f"Позицията трябва да е една от: {', '.join(PlayersService.VALID_POSITIONS)}"
        return True, position
    
    @staticmethod
    def add_player(club_name, full_name, birth_date, nationality, position, number, status="active"):
        """Добавя нов играч с всички параметри (за инициализация)"""
        try:
            # Намиране на клуб
            club = execute_query(
                "SELECT id FROM clubs WHERE name = ?", 
                (club_name,), 
                fetch_one=True
            )
            
            if not club:
                return f"❌ Клуб '{club_name}' не съществува"
            
            # Валидации
            valid_number, number_msg = PlayersService.validate_number(number, club['id'])
            if not valid_number:
                return f"❌ {number_msg}"
            
            valid_pos, pos_msg = PlayersService.validate_position(position)
            if not valid_pos:
                return f"❌ {pos_msg}"
            
            # Добавяне на играч
            execute_query(
                """INSERT INTO players 
                   (club_id, full_name, birth_date, nationality, position, number, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (club['id'], full_name.strip(), birth_date, nationality.strip(), pos_msg, number_msg, status)
            )
            
            return f"✅ Добавен играч: {full_name} в {club_name}"
            
        except Exception as e:
            logging.error(f"Грешка при добавяне на играч: {e}")
            return f"❌ Грешка: {str(e)}"

    @staticmethod
    def find_player_by_name(player_name):
        """Намира играч по име (без значение на малки/главни букви)"""
        if not player_name:
            return None

        # Взимаме всички играчи и търсим ръчно
        all_players = execute_query("SELECT * FROM players", fetch_all=True)
        search_name = player_name.strip().lower()

        for player in all_players:
            if player['full_name'].lower() == search_name:
                return player

        for player in all_players:
            if search_name in player['full_name'].lower():
                return player

        return None
    @staticmethod
    def find_club_by_name(club_name):
        """Намира клуб по име (за трансфери)"""
        if not club_name or club_name.lower() in ['няма', 'свободен', 'без клуб']:
            return None
        return execute_query(
            "SELECT * FROM clubs WHERE name LIKE ?",
            (f"%{club_name}%",),
            fetch_one=True
        )

    @staticmethod
    def get_players_by_club(club_name):
        """Връща всички играчи в даден клуб"""
        try:
            # Използваме ClubsService за търсене на клуб (с малки/главни букви)
            from club_service import ClubsService
            club = ClubsService.find_club_by_name(club_name)

            if not club:
                return None, f"❌ Клуб '{club_name}' не съществува"

            # Вземане на играчите
            players = execute_query(
                """SELECT * FROM players 
                   WHERE club_id = ? 
                   ORDER BY 
                       CASE position 
                           WHEN 'GK' THEN 1
                           WHEN 'DF' THEN 2
                           WHEN 'MF' THEN 3
                           WHEN 'FW' THEN 4
                       END,
                       number""",
                (club['id'],),
                fetch_all=True
            )

            return players, club['name']

        except Exception as e:
            logging.error(f"Грешка при вземане на играчи: {e}")
            return [], None
    
    @staticmethod
    def get_all_players():
        """Връща всички играчи с имена на клубове"""
        try:
            players = execute_query(
                """SELECT p.*, c.name as club_name 
                   FROM players p
                   JOIN clubs c ON p.club_id = c.id
                   ORDER BY c.name, p.position, p.number""",
                fetch_all=True
            )
            return players
        except Exception as e:
            logging.error(f"Грешка при вземане на всички играчи: {e}")
            return []
    
    @staticmethod
    def update_player_number(player_name, new_number, club_name=None):
        """Сменя номера на играч"""
        try:
            # Валидация на номер
            valid_number, number_msg = PlayersService.validate_number(new_number)
            if not valid_number:
                return f"❌ {number_msg}"
            
            # Намиране на играча
            if club_name:
                # Търсене по име на играч и клуб
                club = execute_query(
                    "SELECT id FROM clubs WHERE name = ?", 
                    (club_name,), 
                    fetch_one=True
                )
                if not club:
                    return f"❌ Клуб '{club_name}' не съществува"
                
                player = execute_query(
                    "SELECT * FROM players WHERE full_name LIKE ? AND club_id = ?",
                    (f"%{player_name}%", club['id']),
                    fetch_one=True
                )
            else:
                # Търсене само по име (връща първия)
                player = execute_query(
                    "SELECT * FROM players WHERE full_name LIKE ?",
                    (f"%{player_name}%",),
                    fetch_one=True
                )
            
            if not player:
                return f"❌ Играч '{player_name}' не е намерен"
            
            # Проверка дали номерът е свободен в клуба
            valid, msg = PlayersService.validate_number(new_number, player['club_id'], player['id'])
            if not valid:
                return f"❌ {msg}"
            
            # Обновяване на номера
            execute_query(
                "UPDATE players SET number = ? WHERE id = ?",
                (number_msg, player['id'])
            )
            
            return f"✅ Номерът на {player['full_name']} е сменен на {number_msg}"
            
        except Exception as e:
            logging.error(f"Грешка при смяна на номер: {e}")
            return f"❌ Грешка: {str(e)}"
    
    @staticmethod
    def update_player_status(player_name, new_status, club_name=None):
        """Променя статуса на играч"""
        try:
            new_status = new_status.lower()
            if new_status not in PlayersService.VALID_STATUSES:
                return f"❌ Статусът трябва да е: {', '.join(PlayersService.VALID_STATUSES)}"
            
            # Намиране на играча
            if club_name:
                club = execute_query(
                    "SELECT id FROM clubs WHERE name = ?", 
                    (club_name,), 
                    fetch_one=True
                )
                if not club:
                    return f"❌ Клуб '{club_name}' не съществува"
                
                player = execute_query(
                    "SELECT * FROM players WHERE full_name LIKE ? AND club_id = ?",
                    (f"%{player_name}%", club['id']),
                    fetch_one=True
                )
            else:
                player = execute_query(
                    "SELECT * FROM players WHERE full_name LIKE ?",
                    (f"%{player_name}%",),
                    fetch_one=True
                )
            
            if not player:
                return f"❌ Играч '{player_name}' не е намерен"
            
            # Обновяване на статуса
            execute_query(
                "UPDATE players SET status = ? WHERE id = ?",
                (new_status, player['id'])
            )
            
            status_emoji = {
                'active': '✅',
                'injured': '🤕',
                'suspended': '⛔'
            }
            
            return f"{status_emoji[new_status]} Статусът на {player['full_name']} е променен на {new_status}"
            
        except Exception as e:
            logging.error(f"Грешка при промяна на статус: {e}")
            return f"❌ Грешка: {str(e)}"
    
    @staticmethod
    def delete_player(player_name, club_name=None):
        """Изтрива играч"""
        try:
            # Намиране на играча
            if club_name:
                club = execute_query(
                    "SELECT id FROM clubs WHERE name = ?", 
                    (club_name,), 
                    fetch_one=True
                )
                if not club:
                    return f"❌ Клуб '{club_name}' не съществува"
                
                player = execute_query(
                    "SELECT * FROM players WHERE full_name LIKE ? AND club_id = ?",
                    (f"%{player_name}%", club['id']),
                    fetch_one=True
                )
            else:
                player = execute_query(
                    "SELECT * FROM players WHERE full_name LIKE ?",
                    (f"%{player_name}%",),
                    fetch_one=True
                )
            
            if not player:
                return f"❌ Играч '{player_name}' не е намерен"
            
            # Изтриване
            execute_query("DELETE FROM players WHERE id = ?", (player['id'],))
            
            return f"✅ Играч {player['full_name']} е изтрит"
            
        except Exception as e:
            logging.error(f"Грешка при изтриване на играч: {e}")
            return f"❌ Грешка: {str(e)}"
            
