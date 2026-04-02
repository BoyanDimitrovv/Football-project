
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "clubs.db"

def execute_query(query, params=()):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def execute_fetch(query, params=()):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result

def init_database():
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
    print("=" * 60)
    print("📦 ДОБАВЯНЕ НА ТЕСТОВИ ДАННИ")
    print("=" * 60)

    # Изчистване
    execute_query("DELETE FROM transfers")
    execute_query("DELETE FROM players")
    execute_query("DELETE FROM clubs")

    # ============================================================
    # 1. КЛУБОВЕ (10)
    # ============================================================
    clubs = [
        "Левски София",
        "ЦСКА София",
        "Лудогорец Разград",
        "Ботев Пловдив",
        "Черно море Варна",
        "Славия София",
        "Локомотив Пловдив",
        "Арда Кърджали",
        "Берое Стара Загора",
        "Спартак Варна"
    ]

    for club in clubs:
        execute_query("INSERT INTO clubs (name) VALUES (?)", (club,))
        print(f"  ✅ Добавен клуб: {club}")

    # Взимане на ID на клубове
    club_ids = {}
    for club in clubs:
        row = execute_fetch("SELECT id FROM clubs WHERE name = ?", (club,))
        if row:
            club_ids[club] = row['id']

    # ============================================================
    # 2. ИГРАЧИ (по 11 уникални играча във всеки клуб)
    # ============================================================

    # Позиции и номера за 11-те играчи
    positions_with_numbers = [
        ('GK', 1),
        ('DF', 2), ('DF', 3), ('DF', 4), ('DF', 5),
        ('MF', 6), ('MF', 7), ('MF', 8),
        ('FW', 9), ('FW', 10), ('FW', 11)
    ]

    # Имена за генериране на уникални играчи
    first_names = [
        "Иван", "Георги", "Димитър", "Николай", "Петър", "Христо", "Александър", "Ангел",
        "Валентин", "Владимир", "Кирил", "Пламен", "Мартин", "Стоян", "Тодор", "Борис",
        "Росен", "Емил", "Живко", "Калоян", "Любомир", "Мирослав", "Венцислав", "Антонио",
        "Кристиан", "Даниел", "Стефан", "Радослав", "Илия", "Васил", "Атанас", "Божидар"
    ]

    last_names = [
        "Иванов", "Георгиев", "Димитров", "Николов", "Петров", "Христов", "Александров", "Ангелов",
        "Валентинов", "Владимиров", "Кирилов", "Пламенов", "Мартинов", "Стоянов", "Тодоров", "Борисов",
        "Росенов", "Емилов", "Живков", "Калоянов", "Любомиров", "Мирославов", "Венциславов", "Антониев",
        "Кристианов", "Даниелов", "Стефанов", "Радославов", "Илиев", "Василев", "Атанасов", "Божидаров"
    ]

    nationalities = ["България", "Бразилия", "Нидерландия", "Франция", "Испания", "Португалия", "Аржентина", "Англия", "Германия", "Италия"]

    total_players = 0
    player_counter = 0

    for club_idx, club in enumerate(clubs):
        club_id = club_ids[club]

        for pos_idx, (position, number) in enumerate(positions_with_numbers):
            # Генерираме уникално име
            first_idx = (player_counter + club_idx * 11 + pos_idx) % len(first_names)
            last_idx = (player_counter + club_idx * 7 + pos_idx * 3) % len(last_names)

            first_name = first_names[first_idx]
            last_name = last_names[last_idx]
            full_name = f"{first_name} {last_name}"

            # Националност (80% българи, 20% чужденци)
            if (player_counter + club_idx) % 5 == 0:
                nationality = nationalities[(player_counter + club_idx) % len(nationalities)]
            else:
                nationality = "България"

            # Дата на раждане
            year = 1985 + (player_counter + club_idx) % 20
            month = 1 + (player_counter + club_idx) % 12
            day = 1 + (player_counter + club_idx) % 28
            birth_date = f"{year}-{month:02d}-{day:02d}"

            # Добавяне на играча
            try:
                execute_query(
                    """INSERT INTO players 
                       (club_id, full_name, birth_date, nationality, position, number, status) 
                       VALUES (?, ?, ?, ?, ?, ?, 'active')""",
                    (club_id, full_name, birth_date, nationality, position, number)
                )
                total_players += 1
            except sqlite3.IntegrityError:
                # Ако има дублиране, добавяме число към името
                full_name = f"{first_name} {last_name} {player_counter + club_idx}"
                execute_query(
                    """INSERT INTO players 
                       (club_id, full_name, birth_date, nationality, position, number, status) 
                       VALUES (?, ?, ?, ?, ?, ?, 'active')""",
                    (club_id, full_name, birth_date, nationality, position, number)
                )
                total_players += 1

            player_counter += 1

        print(f"  ✅ {club}: Добавени 11 играчи")

    # ============================================================
    # 3. ТРАНСФЕРИ (начални трансфери от свободен агент)
    # ============================================================

    # Взимаме всички играчи
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM players")
    all_players = cursor.fetchall()
    conn.close()

    # Добавяме трансфери за първите 30 играча
    transfers_added = 0
    for i, player in enumerate(all_players[:30]):
        # Намираме клуба на играча
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT club_id FROM players WHERE id = ?", (player['id'],))
        player_data = cursor.fetchone()
        conn.close()

        if player_data and player_data['club_id']:
            year = 2020 + (i % 4)
            month = 6 + (i % 3)
            day = 1 + (i % 28)
            transfer_date = f"{year}-{month:02d}-{day:02d}"

            execute_query(
                """INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee) 
                   VALUES (?, NULL, ?, ?, NULL)""",
                (player['id'], player_data['club_id'], transfer_date)
            )
            transfers_added += 1

    print(f"  ✅ Добавени {transfers_added} начални трансфера")

    # ============================================================
    # СТАТИСТИКА
    # ============================================================
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА НА БАЗАТА ДАННИ")
    print("=" * 60)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM clubs")
    clubs_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM players")
    players_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM transfers")
    transfers_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT c.name, COUNT(p.id) as player_count 
        FROM clubs c 
        LEFT JOIN players p ON p.club_id = c.id 
        GROUP BY c.id 
        ORDER BY c.name
    """)
    club_stats = cursor.fetchall()

    conn.close()

    print(f"🏆 Клубове: {clubs_count}")
    print(f"⚽ Играчи: {players_count}")
    print(f"🔄 Трансфери: {transfers_count}")
    print("\n📋 ИГРАЧИ ПО КЛУБОВЕ:")
    for stat in club_stats:
        print(f"   • {stat['name']}: {stat['player_count']} играчи")

    print("\n" + "=" * 60)
    print("✅ ТЕСТОВИТЕ ДАННИ СА ЗАРЕДЕНИ УСПЕШНО!")
    print("=" * 60)

if __name__ == "__main__":
    init_database()
    seed_data()
