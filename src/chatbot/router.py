"""
ROUTER - ЕТАП 1-8
Маршрутизира командите към съответните services
"""

import sys
from pathlib import Path

# Добавяне на src към пътя
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from services.clubs_service import ClubsService
from services.players_service import PlayersService
from services.transfers_service import TransfersService
from services.leagues_service import LeaguesService
from services.matches_service import MatchesService
from services.standings_service import StandingsService
from ai.ai_service import AIService
from utils.logger import log_command
from database.db import execute_query


class Router:

    def __init__(self):
        self.clubs_service = ClubsService()
        self.players_service = PlayersService()
        self.transfers_service = TransfersService()
        self.leagues_service = LeaguesService()
        self.matches_service = MatchesService()
        self.standings_service = StandingsService()
        self.ai_service = AIService()
        self.selected_club = None
        self.selected_league_name = None
        self.selected_league_season = None

    def route(self, intent, params, raw_input):
        result = None
        status = "OK"

        try:
            # ПОМОЩ
            if intent == 'help':
                result = self._get_help()

            # ИЗХОД
            elif intent == 'exit':
                result = "Довиждане! 👋"

            # КЛУБОВЕ
            elif intent == 'add_club':
                result = self.clubs_service.add_club(params.get('club', ''))

            elif intent == 'list_clubs':
                clubs = self.clubs_service.get_all_clubs()
                if not clubs:
                    result = "📋 Няма добавени клубове."
                else:
                    response = "🏆 Списък с клубове:\n"
                    for club in clubs:
                        response += f"  🏆 {club['id']}. {club['name']}\n"
                    result = response

            # ИГРАЧИ
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

            # ДОБАВИ ИГРАЧ
            elif intent == 'add_player':
                result = self.players_service.add_player(
                    club_name=params.get('club_name', ''),
                    full_name=params.get('player_name', ''),
                    birth_date="2000-01-01",
                    nationality="България",
                    position=params.get('position', ''),
                    number=params.get('number', 0)
                )

            # ТРАНСФЕРИ
            elif intent == 'transfer_player':
                from datetime import date
                date_str = params.get('date', '') or date.today().isoformat()
                result = self.transfers_service.transfer_player(
                    player_name=params.get('player', ''),
                    from_club_name=params.get('from_club', ''),
                    to_club_name=params.get('to_club', ''),
                    date_str=date_str,
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

            # ЛИГИ
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

            # МАЧОВЕ
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

            # КЛАСИРАНЕ
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

            # ИЗБЕРИ КЛУБ (контекст)
            elif intent == 'select_club':
                from services.clubs_service import ClubsService
                club = ClubsService.find_club_by_name(params.get('club', ''))
                if not club:
                    result = f"❌ Клуб '{params.get('club', '')}' не съществува"
                else:
                    self.selected_club = club
                    result = f"✅ Избран клуб: {club['name']}"

            elif intent == 'unselect_club':
                if self.selected_club:
                    club_name = self.selected_club['name']
                    self.selected_club = None
                    result = f"✅ Излязохте от клуб {club_name}"
                else:
                    result = "ℹ️ Няма избран клуб"

            elif intent == 'list_players_selected':
                if not self.selected_club:
                    result = "ℹ️ Няма избран клуб. Използвайте 'избери клуб <ИМЕ>'"
                else:
                    club_name = self.selected_club['name']
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

            # ИЗБЕРИ ЛИГА (контекст)
            elif intent == 'select_league':
                league_name = params.get('league_name', '')
                season = params.get('season', '')
                from services.leagues_service import LeaguesService
                valid, league_or_msg = LeaguesService.validate_league_exists(league_name, season)
                if valid:
                    self.selected_league_name = league_name
                    self.selected_league_season = season
                    result = f"✅ Избрана лига: {league_name} ({season})"
                else:
                    result = league_or_msg

            elif intent == 'generate_fixture_selected':
                if not self.selected_league_name:
                    result = "ℹ️ Няма избрана лига. Използвайте 'избери лига <ИМЕ> <СЕЗОН>'"
                else:
                    result = self.leagues_service.generate_fixture(
                        league_name=self.selected_league_name,
                        season=self.selected_league_season
                    )

            elif intent == 'show_round_selected':
                if not self.selected_league_name:
                    result = "ℹ️ Няма избрана лига. Използвайте 'избери лига <ИМЕ> <СЕЗОН>'"
                else:
                    result = self.matches_service.show_round(
                        round_no=int(params.get('round_no', 0)),
                        league_name=self.selected_league_name,
                        season=self.selected_league_season
                    )

            elif intent == 'show_standings_selected':
                if not self.selected_league_name:
                    result = "ℹ️ Няма избрана лига. Използвайте 'избери лига <ИМЕ> <СЕЗОН>'"
                else:
                    success, message, standings = self.standings_service.calculate_standings(
                        league_name=self.selected_league_name,
                        season=self.selected_league_season
                    )
                    if success:
                        result = self.standings_service.format_standings_table(
                            standings,
                            self.selected_league_name,
                            self.selected_league_season
                        )
                    else:
                        result = message

            # AI ПРОГНОЗА
            elif intent == 'predict_match':
                prediction, error = self.ai_service.predict_match(
                    team1_name=params.get('team1', ''),
                    team2_name=params.get('team2', '')
                )
                if error:
                    result = error
                else:
                    result = (f"🔮 **ПРОГНОЗА: {prediction['home_team']} vs {prediction['away_team']}**\n\n"
                              f"🏠 **{prediction['home_team']}**: {prediction['home_win']}%\n"
                              f"🤝 **Равен**: {prediction['draw']}%\n"
                              f"🛫 **{prediction['away_team']}**: {prediction['away_win']}%\n\n"
                              f"📊 **Анализ:**\n"
                              f"   • Форма: {prediction['home_team']} {prediction['home_form']}% vs {prediction['away_team']} {prediction['away_form']}%")

            # НЕПОЗНАТА КОМАНДА - с директна обработка на картони
            else:
                # Проверка за картон
                if raw_input.lower().startswith('картон'):
                    parts = raw_input.lower().split()
                    card_type = None
                    minute = None
                    player_name = ''
                    for i, part in enumerate(parts):
                        if part in ['y', 'r']:
                            card_type = part.upper()
                            if i + 1 < len(parts):
                                minute = parts[i + 1]
                            break
                        elif i > 0 or (i == 0 and part == 'картон'):
                            if part != 'картон':
                                player_name += part + ' '
                    player_name = player_name.strip()

                    if card_type and minute:
                        current_match = self.matches_service.get_current_match()
                        if current_match:
                            all_players = execute_query("SELECT * FROM players", fetch_all=True)
                            found = False
                            for p in all_players:
                                if player_name.lower() in p['full_name'].lower():
                                    club_id = p['club_id']
                                    if club_id == current_match['home_club_id']:
                                        club_name = current_match['home_club_name']
                                    elif club_id == current_match['away_club_id']:
                                        club_name = current_match['away_club_name']
                                    else:
                                        continue

                                    result = self.matches_service.add_card(
                                        player_name=player_name,
                                        club_name=club_name,
                                        card_type=card_type,
                                        minute=minute
                                    )
                                    found = True
                                    break
                            if not found:
                                result = f"❌ Играч '{player_name}' не е намерен или не участва в мача"
                        else:
                            result = "❌ Няма избран мач. Използвай 'избери мач <ID>'"
                    else:
                        result = "❌ Невалиден формат. Използвайте: картон [ИГРАЧ] [Y/R] [МИНУТА]"
                else:
                    result = "❓ Не разбирам командата. Напишете 'помощ' за списък с команди."

        except Exception as e:
            status = "ERROR"
            result = f"❌ Грешка: {str(e)}"

        log_command(raw_input, intent, params, result, status)
        return result

    def _get_help(self):
        return """
🏆 НАЛИЧНИ КОМАНДИ:

🏁 КЛУБОВЕ:
• добави клуб [име]
• покажи клубове

⚽ ИГРАЧИ:
• покажи играчи на [КЛУБ]
• добави играч [ИМЕ] в [КЛУБ] позиция [GK/DF/MF/FW] номер [1-99]

🔄 ТРАНСФЕРИ:
• трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА]
• трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА] сума [ЧИСЛО]
• покажи трансфери на [ИГРАЧ]
• покажи трансфери на клуб [КЛУБ]

🏆 ЛИГИ:
• създай лига [ИМЕ] [СЕЗОН]
• добави отбор [КЛУБ] в лига [ЛИГА] [СЕЗОН]
• премахни отбор [КЛУБ] от лига [ЛИГА] [СЕЗОН]
• покажи отбори в лига [ЛИГА] [СЕЗОН]
• генерирай програма [ЛИГА] [СЕЗОН]
• покажи програма [ЛИГА] [СЕЗОН]

⚽ МАЧОВЕ:
• покажи кръг [N] [ЛИГА] [СЕЗОН]
• избери мач [ID]
• резултат [ДОМАКИН]-[ГОСТ] [X]:[Y] запиши
• гол [ИГРАЧ] за [КЛУБ] в [МИНУТА] минута
• картон [ИГРАЧ] [Y/R] [МИНУТА]
• покажи събития [ID]

📊 КЛАСИРАНЕ:
• покажи класиране [ЛИГА] [СЕЗОН]

🔮 AI ПРОГНОЗА:
• прогноза [ОТБОР1] срещу [ОТБОР2]

❓ ДРУГИ:
• помощ
• изход
"""
