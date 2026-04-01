"""
TRANSFERS SERVICE - ЕТАП 4
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / "clubs.db"


def execute_query(query, params=(), fetch_one=False, fetch_all=False):
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
    finally:
        if conn:
            conn.close()


def execute_transaction(queries):
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        for query, params in queries:
            cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


class TransfersService:

    @staticmethod
    def find_club(club_name):
        """Намира клуб по име (без значение на малки/главни букви)"""
        if not club_name or club_name.lower() in ['няма', 'свободен', 'без клуб']:
            return None

        # Премахваме празни места от началото и края
        club_name = club_name.strip()

        # Опитваме с LIKE за частично съвпадение
        result = execute_query(
            "SELECT * FROM clubs WHERE name LIKE ?",
            (f"%{club_name}%",),
            fetch_one=True
        )

        # Ако не намери, опитваме с LOWER за малки букви
        if not result:
            result = execute_query(
                "SELECT * FROM clubs WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{club_name}%",),
                fetch_one=True
            )

        # Ако пак не намери, опитваме да премахнем интервали
        if not result:
            # Взимаме всички клубове и търсим ръчно
            all_clubs = execute_query("SELECT * FROM clubs", fetch_all=True)
            for club in all_clubs:
                if club_name.lower() in club['name'].lower():
                    result = club
                    break
        return result

    @staticmethod
    def find_player(player_name):
        """Намира играч по име (без значение на малки/главни букви)"""
        if not player_name:
            return None

        player_name = player_name.strip().lower()

        # Първо вземаме всички играчи и търсим ръчно (най-сигурно)
        all_players = execute_query(
            "SELECT p.*, c.name as club_name FROM players p LEFT JOIN clubs c ON p.club_id = c.id",
            fetch_all=True
        )

        for player in all_players:
            if player_name in player['full_name'].lower():
                return player

        # Ако не намери, опитваме с LIKE
        result = execute_query(
            "SELECT p.*, c.name as club_name FROM players p LEFT JOIN clubs c ON p.club_id = c.id WHERE LOWER(p.full_name) LIKE LOWER(?)",
            (f"%{player_name}%",),
            fetch_one=True
        )

        return result

    @staticmethod
    def list_transfers_by_club(club_name):
        """Показва входящи трансфери в клуб"""
        print(f"DEBUG: list_transfers_by_club called with: '{club_name}'")
        club = TransfersService.find_club(club_name)
        if not club:
            return f"❌ Клуб '{club_name}' не е намерен"

        transfers = execute_query(
            """SELECT t.*, p.full_name as player_name, fc.name as from_name
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
            from_text = t['from_name'] if t['from_name'] else "свободен агент"
            fee_text = f", {t['fee']} евро" if t['fee'] else ""
            response += f"  • {t['transfer_date']}: {t['player_name']} от {from_text}{fee_text}\n"
        return response

    @staticmethod
    def list_transfers_by_player(player_name):
        """Показва история на трансферите на играч"""
        player = TransfersService.find_player(player_name)
        if not player:
            return f"❌ Играч '{player_name}' не е намерен"

        transfers = execute_query(
            """SELECT t.*, fc.name as from_name, tc.name as to_name
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
            from_text = t['from_name'] if t['from_name'] else "свободен агент"
            fee_text = f", {t['fee']} евро" if t['fee'] else ""
            response += f"  • {t['transfer_date']}: {from_text} → {t['to_name']}{fee_text}\n"
        return response

    @staticmethod
    def transfer_player(player_name, from_club_name, to_club_name, date_str, fee_str=None):
        """Извършва трансфер (опростена версия за тест)"""
        player = TransfersService.find_player(player_name)
        if not player:
            return f"❌ Играч '{player_name}' не е намерен"

        to_club = TransfersService.find_club(to_club_name)
        if not to_club:
            return f"❌ Клуб '{to_club_name}' не е намерен"

        from_club = TransfersService.find_club(from_club_name) if from_club_name else None

        # Проверка на текущия клуб
        current_club = player['club_name'] if player['club_name'] else "свободен агент"
        expected_from = from_club['name'] if from_club else "свободен агент"

        if current_club != expected_from:
            return f"❌ Играчът е в {current_club}, а не в {expected_from}"

        # Транзакция
        queries = [
            (
                "INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee) VALUES (?, ?, ?, ?, ?)",
                (player['id'], from_club['id'] if from_club else None, to_club['id'], date_str,
                 float(fee_str) if fee_str else None)
            ),
            (
                "UPDATE players SET club_id = ? WHERE id = ?",
                (to_club['id'], player['id'])
            )
        ]

        execute_transaction(queries)

        from_text = from_club['name'] if from_club else "свободен агент"
        fee_text = f" за {fee_str} евро" if fee_str else ""

        return f"✅ Трансфер: {player['full_name']} от {from_text} в {to_club['name']} на {date_str}{fee_text}"
