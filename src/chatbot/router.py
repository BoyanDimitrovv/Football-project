import sys
from pathlib import Path

# Добавяне на services папката към пътя
services_path = Path(__file__).parent.parent / "services"
sys.path.insert(0, str(services_path))

# Добавяне на utils папката към пътя
utils_path = Path(__file__).parent.parent / "utils"
sys.path.insert(0, str(utils_path))

from clubs_service import ClubsService
from player_service import PlayersService
from transfers_service import TransfersService
from leagues_service import LeaguesService
from matches_service import MatchesService
from utils.logger import log_command
from standings_service import StandingsService

class Router:
    """Клас, който насочва командите към правилния service"""

    def __init__(self):
        """Инициализира всички services"""
        self.clubs_service = ClubsService()
        self.players_service = PlayersService()
        self.transfers_service = TransfersService()
        self.leagues_service = LeaguesService()
        self.matches_service = MatchesService()
        self.standings_service = StandingsService()

    def route(self, intent, params, raw_input):
        """
        Насочва заявката към съответния service

        Args:
            intent (str): Разпознатото намерение
            params (dict): Параметри извлечени от командата
            raw_input (str): Оригиналното съобщение от потребителя

        Returns:
            str: Отговор от съответния service
        """

        result = None
        status = "OK"

        try:
            # ============================================================
            # ПОМОЩ И ИЗХОД
            # ============================================================

            if intent == 'help':
                result = self._get_help()

            elif intent == 'exit':
                result = "Довиждане! 👋"

            # ============================================================
            # ЕТАП 2 - КЛУБОВЕ
            # ============================================================

            elif intent == 'add_club':
                club_name = params.get('club', '')
                result = self.clubs_service.add_club(club_name)

            elif intent == 'list_clubs':
                clubs = self.clubs_service.get_all_clubs()
                if not clubs:
                    result = "📋 Няма добавени клубове."
                else:
                    response = "🏆 Списък с клубове:\n"
                    for club in clubs:
                        response += f"  🏆 {club['id']}. {club['name']}\n"
                    result = response

            # ============================================================
            # ЕТАП 3 - ИГРАЧИ
            # ============================================================

            elif intent == 'list_players':
                club_name = params.get('club', '')
                players, club = self.players_service.get_players_by_club(club_name)

                if players is None:
                    result = club
                elif not players:
                    result = f"📋 Няма играчи в {club}"
                else:
                    response = f"📋 Играчи на {club}:\n"
                    emoji = {'GK': '🧤', 'DF': '🛡️', 'MF': '⚙️', 'FW': '⚽'}

                    for player in players:
                        response += (f"  {emoji[player['position']]} {player['number']}. "
                                     f"{player['full_name']} ({player['nationality']})\n")
                    result = response

            # ============================================================
            # ЕТАП 4 - ТРАНСФЕРИ
            # ============================================================

            elif intent == 'transfer_player':
                result = self.transfers_service.transfer_player(
                    player_name=params.get('player', ''),
                    from_club_name=params.get('from_club', ''),
                    to_club_name=params.get('to_club', ''),
                    date_str=params.get('date', ''),
                    fee_str=params.get('fee', None)
                )

            elif intent == 'show_transfers_player':
                result = self.transfers_service.list_transfers_by_player(
                    player_name=params.get('player', '')
                )

            elif intent == 'show_transfers_club':
                result = self.transfers_service.list_transfers_by_club(
                    club_name=params.get('club', '')
                )

            # ============================================================
            # ЕТАП 5 - ЛИГИ
            # ============================================================

            elif intent == 'create_league':
                result = self.leagues_service.create_league(
                    name=params.get('name', ''),
                    season=params.get('season', '')
                )

            elif intent == 'add_team_to_league':
                result = self.leagues_service.add_team_to_league(
                    club_name=params.get('club', ''),
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )

            elif intent == 'remove_team_from_league':
                result = self.leagues_service.remove_team_from_league(
                    club_name=params.get('club', ''),
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )

            elif intent == 'show_teams_in_league':
                result = self.leagues_service.show_teams_in_league(
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )

            elif intent == 'generate_fixture':
                result = self.leagues_service.generate_fixture(
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )

            elif intent == 'show_fixture':
                result = self.leagues_service.show_fixture(
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )
            # ============================================================
            # ЕТАП 6 - МАЧОВЕ
            # ============================================================

            elif intent == 'show_round':
                result = self.matches_service.show_round(
                    round_no=int(params.get('round_no', 0)),
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )

            elif intent == 'select_match':
                valid, msg = self.matches_service.set_current_match(
                    match_id=int(params.get('match_id', 0))
                )
                result = msg

            elif intent == 'set_result':
                result = self.matches_service.set_result(
                    home_team=params.get('home_team', ''),
                    away_team=params.get('away_team', ''),
                    home_goals=params.get('home_goals', 0),
                    away_goals=params.get('away_goals', 0)
                )

            elif intent == 'add_goal':
                result = self.matches_service.add_goal(
                    player_name=params.get('player', ''),
                    club_name=params.get('club', ''),
                    minute=params.get('minute', 0)
                )

            elif intent == 'add_card':
                result = self.matches_service.add_card(
                    player_name=params.get('player', ''),
                    club_name=params.get('club', ''),
                    card_type=params.get('card_type', ''),
                    minute=params.get('minute', 0)
                )
            elif intent == 'add_card_simple':
                result = self.matches_service.add_card_simple(
                    player_name=params.get('player', ''),
                    card_type=params.get('card_type', ''),
                    minute=params.get('minute', 0)
                )

            elif intent == 'show_events':
                match_id = params.get('match_id', None)
                if match_id:
                    result = self.matches_service.show_events(match_id=int(match_id))
                else:
                    result = self.matches_service.show_events()
            # ============================================================
            # ЕТАП 7 - КЛАСИРАНЕ
            # ============================================================

            elif intent == 'show_standings':
                success, message, standings = self.standings_service.calculate_standings(
                    league_name=params.get('league_name', ''),
                    season=params.get('season', '')
                )
                if success:
                    result = self.standings_service.format_standings_table(
                        standings,
                        params.get('league_name', ''),
                        params.get('season', '')
                    )
                else:
                    result = message

            elif intent == 'refresh_standings':
                # Може да се използва за контекстна лига
                result = "🔄 За да обновите класирането, използвайте 'покажи класиране [лига] [сезон]'"
            # ============================================================
            # НЕПОЗНАТА КОМАНДА
            # ============================================================

            else:
                result = "❓ Не разбирам командата. Напишете 'помощ' за списък с команди."

        except Exception as e:
            status = "ERROR"
            result = f"❌ Грешка: {str(e)}"

        # Логване на командата
        log_command(raw_input, intent, params, result, status)

        return result

    def _get_help(self):
        """Връща помощно съобщение с всички команди"""
        return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         🏆 НАЛИЧНИ КОМАНДИ 🏆                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🏁 КЛУБОВЕ (ЕТАП 2)                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ • добави клуб [име]                    - добавя нов клуб                     │
│   Пример: добави клуб Левски София                                          │
│                                                                              │
│ • покажи клубове                        - списък на всички клубове           │
│   Пример: покажи клубове                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚽ ИГРАЧИ (ЕТАП 3)                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ • покажи играчи на [КЛУБ]               - списък на играчите в клуб          │
│   Пример: покажи играчи на Левски София                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔄 ТРАНСФЕРИ (ЕТАП 4)                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ • трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА]                                   │
│   Пример: трансфер Пламен Андреев от Левски София в ЦСКА София 2026-03-10    │
│                                                                              │
│ • трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА] сума [ЧИСЛО]                       │
│   Пример: трансфер Пламен Андреев от ЦСКА София в Лудогорец 2026-03-15 сума 500000 │
│                                                                              │
│ • покажи трансфери на [ИГРАЧ]           - история на трансферите на играч    │
│   Пример: покажи трансфери на Пламен Андреев                                 │
│                                                                              │
│ • покажи трансфери на клуб [КЛУБ]       - входящи трансфери в клуб           │
│   Пример: покажи трансфери на клуб Лудогорец                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🏆 ЛИГИ (ЕТАП 5 )                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ • създай лига [ИМЕ] [СЕЗОН]              - създава нова лига                  │
│   Пример: създай лига Първа лига 2025/2026                                   │
│                                                                              │
│ • добави отбор [КЛУБ] в лига [ЛИГА] [СЕЗОН] - добавя отбор към лига          │
│   Пример: добави отбор Левски София в лига Първа лига 2025/2026              │
│                                                                              │
│ • премахни отбор [КЛУБ] от лига [ЛИГА] [СЕЗОН] - премахва отбор от лига      │
│   Пример: премахни отбор Левски София от лига Първа лига 2025/2026           │
│                                                                              │
│ • покажи отбори в лига [ЛИГА] [СЕЗОН]   - списък на отборите в лига           │
│   Пример: покажи отбори в лига Първа лига 2025/2026                          │
│                                                                              │
│ • генерирай програма [ЛИГА] [СЕЗОН]     - създава програма (round-robin)      │
│   Пример: генерирай програма Първа лига 2025/2026                            │
│                                                                              │
│ • покажи програма [ЛИГА] [СЕЗОН]        - показва програмата                 │
│   Пример: покажи програма Първа лига 2025/2026                               │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚽ МАЧОВЕ (ЕТАП 6 )                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ • покажи кръг [N] [ЛИГА] [СЕЗОН] - показва мачовете за кръг                 │
│   Пример: покажи кръг 3 Първа лига 2025/2026                                │
│                                                                              │
│ • избери мач [ID] - избира мач за последващи операции                       │
│   Пример: избери мач 12                                                     │
│                                                                              │
│ • резултат [ДОМАКИН]-[ГОСТ] [X]:[Y] запиши - записва резултат               │
│   Пример: резултат Левски-ЦСКА 3:0 запиши                                   │
│                                                                              │
│ • гол [ИГРАЧ] [КЛУБ] [МИНУТА] минута - добавя гол                           │
│   Пример: гол Иван Петров Левски 23 минута                                  │
│                                                                              │
│ • картон [ИГРАЧ] [КЛУБ] [Y/R] [МИНУТА] - добавя картон                      │
│   Пример: картон Иван Петров Левски Y 55                                    │
│                                                                              │
│ • покажи събития [ID] - показва голове и картони за мач                     │
│   Пример: покажи събития 12                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 КЛАСИРАНЕ (ЕТАП 7 - НОВО)                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ • покажи класиране [ЛИГА] [СЕЗОН] - показва таблица с класиране            │
│   Пример: покажи класиране Първа лига 2025/2026                            │
│                                                                              │
│ • обнови класиране - преизчислява класирането (за избрана лига)             │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────┐
│ ❓ ДРУГИ                                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ • помощ                                 - показва това меню                 │
│ • изход                                 - излиза от програмата              │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║  📌 ЗА ДА РАБОТЯТ КОМАНДИТЕ, ПЪРВО ПУСНЕТЕ:                                 ║
║     python src/seed_data.py                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
