"""
TRANSFERS SERVICE - ЕТАП 4
Бизнес логика за трансфери с атомични транзакции
"""

from src.database.db import execute_query, execute_transaction
from src.utils.logger import log_error
from src.services.players_service import PlayersService
from src.services.clubs_service import ClubsService
from datetime import datetime

class TransfersService:
    
    @staticmethod
    def validate_date(date_str):
        """Проверка за валидна дата YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, date_str
        except ValueError:
            return False, "Невалидна дата. Използвайте формат YYYY-MM-DD (пример: 2026-03-10)"
    
    @staticmethod
    def validate_fee(fee_str):
        """Проверка за валидна сума"""
        if not fee_str:
            return True, None
        try:
            fee = float(fee_str)
            if fee < 0:
                return False, "Сумата не може да е отрицателна"
            return True, fee
        except ValueError:
            return False, "Сумата трябва да е число"
    
    @staticmethod
    def transfer_player(player_name, from_club_name, to_club_name, date_str, fee_str=None):
        """
        ИЗВЪРШВА ТРАНСФЕР НА ИГРАЧ (АТОМИЧНА ОПЕРАЦИЯ)
        
        Бизнес логика стъпка по стъпка:
        1. Намира играча по име
        2. Намира клубовете from и to
        3. Проверява дали играчът е в from_club
        4. Проверява from != to
        5. Валидира дата и сума
        6. Създава запис в transfers
        7. Обновява players.club_id = to_club_id
        8. Всичко в една транзакция (атомично)
        """
        try:
            # ----- 1. НАМИРАНЕ НА ИГРАЧ -----
            player = PlayersService.find_player_by_name(player_name)
            if not player:
                return f"❌ Играч '{player_name}' не е намерен"
            
            # ----- 2. НАМИРАНЕ НА КЛУБОВЕ -----
            from_club = ClubsService.find_club_by_name(from_club_name)
            to_club = ClubsService.find_club_by_name(to_club_name)
            
            # Проверка за from_club (може да е 'няма'/'свободен')
            if from_club_name and from_club_name.lower() not in ['няма', 'свободен', 'без клуб']:
                if not from_club:
                    return f"❌ Клуб '{from_club_name}' не е намерен"
            
            if not to_club:
                return f"❌ Клуб '{to_club_name}' не е намерен"
            
            # ----- 3. ПРОВЕРКА ЗА ЕДНАКВИ КЛУБОВЕ -----
            if from_club and to_club and from_club['id'] == to_club['id']:
                return f"❌ Не може да трансферирате в същия клуб"
            
            # ----- 4. ПРОВЕРКА НА ТЕКУЩИЯ КЛУБ НА ИГРАЧА -----
            current_club_id = player['club_id']
            expected_from_id = from_club['id'] if from_club else None
            
            if current_club_id != expected_from_id:
                current_club_name = player['club_name'] if player['club_name'] else 'свободен агент'
                expected_from_name = from_club['name'] if from_club else 'свободен агент'
                
                if current_club_id is None:
                    return f"❌ Играчът е свободен агент, а не в {expected_from_name}"
                else:
                    return f"❌ Играчът е в {current_club_name}, а не в {expected_from_name}"
            
            # ----- 5. ВАЛИДАЦИЯ НА ДАТА -----
            valid_date, date_msg = TransfersService.validate_date(date_str)
            if not valid_date:
                return f"❌ {date_msg}"
            
            # ----- 6. ВАЛИДАЦИЯ НА СУМА -----
            valid_fee, fee_msg = TransfersService.validate_fee(fee_str)
            if not valid_fee:
                return f"❌ {fee_msg}"
            
            # ----- 7. АТОМИЧНА ТРАНЗАКЦИЯ -----
            queries = [
                # Добавяне на запис в transfers
                (
                    """INSERT INTO transfers 
                       (player_id, from_club_id, to_club_id, transfer_date, fee) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (player['id'], 
                     from_club['id'] if from_club else None, 
                     to_club['id'], 
                     date_str, 
                     fee_msg)
                ),
                # Обновяване на текущия клуб на играча
                (
                    "UPDATE players SET club_id = ? WHERE id = ?",
                    (to_club['id'], player['id'])
                )
            ]
            
            # Изпълнение на транзакцията - или всичко, или нищо
            execute_transaction(queries)
            
            # ----- 8. ПОДГОТОВКА НА ОТГОВОР -----
            from_text = from_club['name'] if from_club else "свободен агент"
            fee_text = f" за {fee_msg} евро" if fee_msg else ""
            
            return (f"✅ Трансфер: {player['full_name']} от {from_text} "
                    f"в {to_club['name']} на {date_str}{fee_text}")
            
        except Exception as e:
            log_error(str(e), f"transfer {player_name}")
            return f"❌ Грешка при трансфер: {str(e)}"
    
    @staticmethod
    def list_transfers_by_player(player_name):
        """Показва история на трансферите на играч"""
        try:
            player = PlayersService.find_player_by_name(player_name)
            if not player:
                return f"❌ Играч '{player_name}' не е намерен"
            
            transfers = execute_query(
                """SELECT t.*, 
                          fc.name as from_club_name,
                          tc.name as to_club_name
                   FROM transfers t
                   LEFT JOIN clubs fc ON t.from_club_id = fc.id
                   JOIN clubs tc ON t.to_club_id = tc.id
                   WHERE t.player_id = ?
                   ORDER BY t.transfer_date DESC""",
                (player['id'],),
                fetch_all=True
            )
            
            if not transfers:
                return f"📋 Няма трансфери за {player['full_name']}"
            
            response = f"📋 История на трансферите на {player['full_name']}:\n"
            for t in transfers:
                from_text = t['from_club_name'] if t['from_club_name'] else "свободен агент"
                fee_text = f", {t['fee']} евро" if t['fee'] else ""
                response += f"  • {t['transfer_date']}: {from_text} → {t['to_club_name']}{fee_text}\n"
            
            return response
            
        except Exception as e:
            log_error(str(e), f"list transfers {player_name}")
            return f"❌ Грешка: {str(e)}"
    
    @staticmethod
    def list_transfers_by_club(club_name):
        """Показва всички входящи трансфери в клуб"""
        try:
            club = ClubsService.find_club_by_name(club_name)
            if not club:
                return f"❌ Клуб '{club_name}' не е намерен"
            
            transfers = execute_query(
                """SELECT t.*, p.full_name as player_name,
                          fc.name as from_club_name
                   FROM transfers t
                   JOIN players p ON t.player_id = p.id
                   LEFT JOIN clubs fc ON t.from_club_id = fc.id
                   WHERE t.to_club_id = ?
                   ORDER BY t.transfer_date DESC""",
                (club['id'],),
                fetch_all=True
            )
            
            if not transfers:
                return f"📋 Няма входящи трансфери в {club['name']}"
            
            response = f"📋 Входящи трансфери в {club['name']}:\n"
            for t in transfers:
                from_text = t['from_club_name'] if t['from_club_name'] else "свободен агент"
                fee_text = f", {t['fee']} евро" if t['fee'] else ""
                response += f"  • {t['transfer_date']}: {t['player_name']} от {from_text}{fee_text}\n"
            
            return response
            
        except Exception as e:
            log_error(str(e), f"list transfers club {club_name}")
            return f"❌ Грешка: {str(e)}"
