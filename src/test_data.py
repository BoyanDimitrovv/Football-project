# src/test_data.py
from clubs_service import ClubsService
from players_service import PlayersService

def add_test_data():
    """Добавя тестови клубове и играчи"""
    
    # Добавяне на клубове
    clubs = ["Левски София", "ЦСКА София", "Лудогорец"]
    for club in clubs:
        print(ClubsService.add_club(club))
    
    # Тестови играчи за Левски
    levski_players = [
        ("Пламен Андреев", "2004-12-15", "България", "GK", 1),
        ("Келиан ван дер Каап", "1998-08-15", "Нидерландия", "DF", 5),
        ("Асими Фадига", "2001-06-10", "Франция", "MF", 10),
        ("Мустафа Сангаре", "1998-12-24", "Франция", "FW", 9)
    ]
    
    for player in levski_players:
        print(PlayersService.add_player("Левски София", *player))
    
    # Тестови играчи за ЦСКА
    cska_players = [
        ("Густаво Бусато", "1990-10-23", "Бразилия", "GK", 1),
        ("Юрген Матей", "1993-04-15", "Нидерландия", "DF", 4),
        ("Джонатан Линдсет", "1996-03-25", "Норвегия", "MF", 10),
        ("Годуин Коялипу", "2000-07-15", "Либерия", "FW", 9)
    ]
    
    for player in cska_players:
        print(PlayersService.add_player("ЦСКА София", *player))
    
    # Тестови играчи за Лудогорец
    ludogorets_players = [
        ("Серджио Падт", "1990-06-16", "Нидерландия", "GK", 1),
        ("Антон Недялков", "1993-04-30", "България", "DF", 3),
        ("Педро Нареси", "1998-01-10", "Бразилия", "MF", 8),
        ("Руан Крус", "1996-03-20", "Бразилия", "FW", 9)
    ]
    
    for player in ludogorets_players:
        print(PlayersService.add_player("Лудогорец", *player))

if __name__ == "__main__":
    add_test_data()
