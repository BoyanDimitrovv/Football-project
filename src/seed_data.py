
from src.database.db import init_database, execute_query
from src.services.clubs_service import ClubsService
from src.services.players_service import PlayersService
from src.services.transfers_service import TransfersService

def seed_data():

    print("📦 Добавяне на тестови данни за Етап 4...")
    
    # Изчистване на старата база
    execute_query("DELETE FROM transfers")
    execute_query("DELETE FROM players")
    execute_query("DELETE FROM clubs")
    
    # ----- 1. КЛУБОВЕ (4) -----
    clubs = [
        "Левски София",
        "ЦСКА София",
        "Лудогорец Разград",
        "Ботев Пловдив"
    ]
    
    for club in clubs:
        ClubsService.add_club(club)
    print(f"  ✓ Добавени {len(clubs)} клуба")
    
    # ----- 2. ИГРАЧИ (7) -----
    players = [
        # Левски (2)
        ("Пламен Андреев", "2004-12-15", "България", "GK", 1, "Левски София"),
        ("Келиан ван дер Каап", "1998-08-15", "Нидерландия", "DF", 5, "Левски София"),
        
        # ЦСКА (2)
        ("Густаво Бусато", "1990-10-23", "Бразилия", "GK", 1, "ЦСКА София"),
        ("Юрген Матей", "1993-04-15", "Нидерландия", "DF", 4, "ЦСКА София"),
        
        # Лудогорец (2)
        ("Серджио Падт", "1990-06-16", "Нидерландия", "GK", 1, "Лудогорец Разград"),
        ("Антон Недялков", "1993-04-30", "България", "DF", 3, "Лудогорец Разград"),
        
        # Ботев (1)
        ("Антон Илиев", "1999-03-05", "България", "DF", 4, "Ботев Пловдив"),
    ]
    
    for player in players:
        PlayersService.add_player(player[5], player[0], player[1], player[2], player[3], player[4])
    print(f"  ✓ Добавени {len(players)} играчи")
    
    # ----- 3. ТРАНСФЕРИ (7) -----
    transfers = [
        # Първи трансфери (от свободен агент)
        ("Пламен Андреев", "няма", "Левски София", "2023-07-01", None),
        ("Келиан ван дер Каап", "няма", "Левски София", "2024-01-15", None),
        ("Густаво Бусато", "няма", "ЦСКА София", "2023-06-01", None),
        ("Юрген Матей", "няма", "ЦСКА София", "2023-07-15", None),
        ("Серджио Падт", "няма", "Лудогорец Разград", "2023-07-01", None),
        ("Антон Недялков", "няма", "Лудогорец Разград", "2023-07-01", None),
        ("Антон Илиев", "няма", "Ботев Пловдив", "2024-02-01", None),
    ]
    
    transfer_count = 0
    for transfer in transfers:
        try:
            TransfersService.transfer_player(
                transfer[0], transfer[1], transfer[2], transfer[3], transfer[4]
            )
            transfer_count += 1
        except Exception as e:
            print(f"  ⚠️ Грешка при трансфер {transfer[0]}: {e}")
    
    print(f"  ✓ Добавени {transfer_count} трансфера")
    print("\n✅ Тестовите данни са заредени успешно!")

if __name__ == "__main__":
    init_database()
    seed_data()
