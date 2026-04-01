"""
SEED DATA - ЕТАП 4 (ПРАВИЛЕН РЕД)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "clubs.db"


def execute_query(query, params=()):
    """Изпълнява заявка"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def execute_fetch(query, params=()):
    """Изпълнява заявка и връща резултат"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result


def init_database():
    """Инициализира базата"""
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        print("✅ Базата е инициализирана")
    except Exception as e:
        print(f"❌ Грешка: {e}")


def seed_data():
    print("📦 Добавяне на тестови данни...")

    # Изчистване
    execute_query("DELETE FROM transfers")
    execute_query("DELETE FROM players")
    execute_query("DELETE FROM clubs")

    # ----- 1. КЛУБОВЕ -----
    clubs = ["Левски София", "ЦСКА София", "Лудогорец Разград", "Ботев Пловдив"]
    for club in clubs:
        execute_query("INSERT INTO clubs (name) VALUES (?)", (club,))
        print(f"  ✅ Добавен клуб: {club}")

    # Взимане на ID на клубове
    club_ids = {}
    for club in clubs:
        row = execute_fetch("SELECT id FROM clubs WHERE name = ?", (club,))
        if row:
            club_ids[club] = row['id']

    # ----- 2. ТРАНСФЕРИ (първо, защото са от свободен агент) -----
    transfers = [
        ("Пламен Андреев", "няма", "Левски София", "2023-07-01", None),
        ("Келиан ван дер Каап", "няма", "Левски София", "2024-01-15", None),
        ("Густаво Бусато", "няма", "ЦСКА София", "2023-06-01", None),
        ("Юрген Матей", "няма", "ЦСКА София", "2023-07-15", None),
        ("Серджио Падт", "няма", "Лудогорец Разград", "2023-07-01", None),
        ("Антон Недялков", "няма", "Лудогорец Разград", "2023-07-01", None),
        ("Антон Илиев", "няма", "Ботев Пловдив", "2024-02-01", None),
    ]

    # Първо добавяме играчите (като свободни агенти, без club_id)
    players_temp = [
        ("Пламен Андреев", "2004-12-15", "България", "GK", 1),
        ("Келиан ван дер Каап", "1998-08-15", "Нидерландия", "DF", 5),
        ("Густаво Бусато", "1990-10-23", "Бразилия", "GK", 1),
        ("Юрген Матей", "1993-04-15", "Нидерландия", "DF", 4),
        ("Серджио Падт", "1990-06-16", "Нидерландия", "GK", 1),
        ("Антон Недялков", "1993-04-30", "България", "DF", 3),
        ("Антон Илиев", "1999-03-05", "България", "DF", 4),
    ]

    for player in players_temp:
        execute_query(
            """INSERT INTO players (full_name, birth_date, nationality, position, number, status, club_id) 
               VALUES (?, ?, ?, ?, ?, 'active', NULL)""",
            (player[0], player[1], player[2], player[3], player[4])
        )

    # Сега изпълняваме трансферите
    player_ids = {}
    for player in players_temp:
        row = execute_fetch("SELECT id FROM players WHERE full_name = ?", (player[0],))
        if row:
            player_ids[player[0]] = row['id']

    for transfer in transfers:
        player_id = player_ids.get(transfer[0])
        to_club_id = club_ids.get(transfer[2])

        if player_id and to_club_id:
            execute_query(
                """INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee) 
                   VALUES (?, NULL, ?, ?, ?)""",
                (player_id, to_club_id, transfer[3], transfer[4])
            )
            # Обновяване на текущия клуб на играча
            execute_query(
                "UPDATE players SET club_id = ? WHERE id = ?",
                (to_club_id, player_id)
            )
            print(f"  ✅ Трансфер: {transfer[0]} → {transfer[2]}")

    print("\n✅ Тестовите данни са заредени успешно!")


if __name__ == "__main__":
    init_database()
    seed_data()
