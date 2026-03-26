# src/init_data.py
from services.club_service import ClubsService  
from services.player_service import PlayersService
import logging

def init_sample_data():
    """Добавя примерни клубове и играчи в базата данни"""   
    
    print("📦 Добавяне на примерни данни...")
    
    # КЛУБОВЕ
    clubs = [
        "Левски София",
        "ЦСКА София", 
        "Лудогорец Разград",
        "Ботев Пловдив",
        "Черно море Варна"
    ]
    
    for club in clubs:
        result = ClubsService.add_club(club)
        print(f"  {result}")
    
    # ИГРАЧИ ЗА ЛЕВСКИ
    levski_players = [
        ("Пламен Андреев", "2004-12-15", "България", "GK", 1, "active"),
        ("Келиан ван дер Каап", "1998-08-15", "Нидерландия", "DF", 5, "active"),
        ("Асими Фадига", "2001-06-10", "Франция", "MF", 10, "active"),
        ("Мустафа Сангаре", "1998-12-24", "Франция", "FW", 9, "active"),
        ("Цунами", "1998-08-06", "Испания", "DF", 4, "injured"),
    ]
    
    for player in levski_players:
        result = PlayersService.add_player_full(
            "Левски София", 
            player[0], player[1], player[2], player[3], player[4], player[5]
        )
        print(f"  {result}")
    
    # ИГРАЧИ ЗА ЦСКА
    cska_players = [
        ("Густаво Бусато", "1990-10-23", "Бразилия", "GK", 1, "active"),
        ("Юрген Матей", "1993-04-15", "Нидерландия", "DF", 4, "active"),
        ("Джонатан Линдсет", "1996-03-25", "Норвегия", "MF", 10, "active"),
        ("Годуин Коялипу", "2000-07-15", "Либерия", "FW", 9, "active"),
        ("Иван Турицов", "1999-07-18", "България", "DF", 19, "active"),
    ]
    
    for player in cska_players:
        result = PlayersService.add_player_full(
            "ЦСКА София", 
            player[0], player[1], player[2], player[3], player[4], player[5]
        )
        print(f"  {result}")
    
    # ИГРАЧИ ЗА ЛУДОГОРЕЦ
    ludogorets_players = [
        ("Серджио Падт", "1990-06-16", "Нидерландия", "GK", 1, "active"),
        ("Антон Недялков", "1993-04-30", "България", "DF", 3, "active"),
        ("Педро Нареси", "1998-01-10", "Бразилия", "MF", 8, "active"),
        ("Руан Крус", "1996-03-20", "Бразилия", "FW", 9, "active"),
        ("Якуб Пьотровски", "1997-10-04", "Полша", "MF", 6, "suspended"),
    ]
    
    for player in ludogorets_players:
        result = PlayersService.add_player_full(
            "Лудогорец Разград", 
            player[0], player[1], player[2], player[3], player[4], player[5]
        )
        print(f"  {result}")
    
    # ИГРАЧИ ЗА БОТЕВ
    botev_players = [
        ("Хидайет Ханкич", "1994-06-29", "Босна", "GK", 1, "active"),
        ("Антон Илиев", "1999-03-05", "България", "DF", 4, "active"),
        ("Дилан Мертенс", "1995-07-09", "Белгия", "MF", 8, "active"),
        ("Мартин Тошев", "2000-08-10", "България", "FW", 9, "active"),
    ]
    
    for player in botev_players:
        result = PlayersService.add_player_full(
            "Ботев Пловдив", 
            player[0], player[1], player[2], player[3], player[4], player[5]
        )
        print(f"  {result}")
    
    # ИГРАЧИ ЗА ЧЕРНО МОРЕ
    cherno_players = [
        ("Иван Дюлгеров", "1999-07-15", "България", "GK", 1, "active"),
        ("Виктор Попов", "2000-03-05", "България", "DF", 3, "active"),
        ("Васил Панайотов", "1990-07-16", "България", "MF", 8, "injured"),
        ("Исмаил Иса", "1999-06-26", "Нигерия", "FW", 9, "active"),
    ]
    
    for player in cherno_players:
        result = PlayersService.add_player_full(
            "Черно море Варна", 
            player[0], player[1], player[2], player[3], player[4], player[5]
        )
        print(f"  {result}")
    
    print("\n✅ Примерните данни са заредени успешно!")
    print("🔍 Можете да тествате с команди като:")
    print("   • покажи клубове")
    print("   • покажи играчи на Левски София")
    print("   • покажи играчи на ЦСКА София")

if __name__ == "__main__":
    init_sample_data()
