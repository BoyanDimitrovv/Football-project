"""
MATCHES SERVICE - ЕТАП 6
"""

import sys
from pathlib import Path

# Добавяне на src към пътя
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from repositories.matches_repo import MatchesRepo
from repositories.leagues_repo import LeaguesRepo
from clubs_service import ClubsService
from player_service import PlayersService
from database.db import execute_transaction

class MatchesService:

    _current_match_id = None
    _current_league_id = None
    _current_league_name = None
    _current_season = None

    @staticmethod
    def set_current_match(match_id):
        match = MatchesRepo.get_match_by_id(match_id)
        if not match:
            return False, f"❌ Мач с ID {match_id} не съществува"

        MatchesService._current_match_id = match['id']
        MatchesService._current_league_id = match['league_id']
        MatchesService._current_league_name = match['league_name']
        MatchesService._current_season = match['season']
        return True, f"✅ Избран мач: {match['home_club_name']} - {match['away_club_name']} (ID: {match_id})"

    @staticmethod
    def get_current_match():
        if not MatchesService._current_match_id:
            return None
        return MatchesRepo.get_match_by_id(MatchesService._current_match_id)

    @staticmethod
    def clear_context():
        MatchesService._current_match_id = None
        MatchesService._current_league_id = None
        MatchesService._current_league_name = None
        MatchesService._current_season = None

    @staticmethod
    def show_round(round_no, league_name, season):
        league = LeaguesRepo.get_league_by_name_season(league_name, season)
        if not league:
            return f"❌ Лига '{league_name}' за сезон {season} не съществува"

        matches = MatchesRepo.get_matches_by_league_round(league['id'], round_no)

        if not matches:
            return f"📋 Няма мачове в {league_name} ({season}), кръг {round_no}"

        response = f"📋 КРЪГ {round_no} - {league_name} ({season}):\n"
        for m in matches:
            home_name = m['home_club_name']
            away_name = m['away_club_name']
            match_id = m['id']

            # Проверка дали мачът има резултат
            if m['home_goals'] is not None and m['home_goals'] != 0:
                result = f"{m['home_goals']}:{m['away_goals']}"
            else:
                result = "неизигран"

            response += f"   🏆 {home_name} - {away_name} ({result}) [ID:{match_id}]\n"

        return response

    @staticmethod

    def set_result(home_team, away_team, home_goals, away_goals, league_name=None, season=None, round_no=None):
        try:
            home_goals = int(home_goals)
            away_goals = int(away_goals)
            if home_goals < 0 or away_goals < 0:
                return "❌ Головете не могат да бъдат отрицателни числа"
        except ValueError:
            return "❌ Невалиден формат на резултата. Използвайте X:Y (пример: 3:0)"

        home_club = ClubsService.find_club_by_name(home_team)
        away_club = ClubsService.find_club_by_name(away_team)

        if not home_club:
            return f"❌ Клуб '{home_team}' не съществува"
        if not away_club:
            return f"❌ Клуб '{away_team}' не съществува"

        match = MatchesRepo.get_match_by_teams(home_club['id'], away_club['id'])

        if not match:
            return f"❌ Не е намерен мач между {home_team} и {away_team}"

        MatchesRepo.update_match_result(match['id'], home_goals, away_goals)
        from standings_service import update_standings_after_result
        update_standings_after_result(match['id'])
        return f"✅ Записано: {home_team} - {away_team} {home_goals}:{away_goals} (мач #{match['id']})"

    @staticmethod
    def add_goal(player_name, club_name, minute, match_id=None):
        match = None
        if match_id:
            match = MatchesRepo.get_match_by_id(match_id)
        elif MatchesService._current_match_id:
            match = MatchesRepo.get_match_by_id(MatchesService._current_match_id)

        if not match:
            return "❌ Няма избран мач. Използвай 'избери мач <ID>'"

        player = PlayersService.find_player_by_name(player_name)
        if not player:
            return f"❌ Играч '{player_name}' не е намерен"

        club = ClubsService.find_club_by_name(club_name)
        if not club:
            return f"❌ Клуб '{club_name}' не съществува"

        if club['id'] not in [match['home_club_id'], match['away_club_id']]:
            return f"❌ Клуб '{club_name}' не участва в този мач"

        if player['club_id'] != club['id']:
            return f"❌ Играч '{player_name}' не играе за {club_name}"

        try:
            minute = int(minute)
            if minute < 1 or minute > 120:
                return "❌ Минутата трябва да е между 1 и 120"
        except ValueError:
            return "❌ Невалидна минута"

        MatchesRepo.add_goal(match['id'], player['id'], club['id'], minute)

        return f"✅ Гол! {player_name} ({club_name}) в {minute} минута"

    @staticmethod
    def add_card(player_name, club_name, card_type, minute, match_id=None):
        match = None
        if match_id:
            match = MatchesRepo.get_match_by_id(match_id)
        elif MatchesService._current_match_id:
            match = MatchesRepo.get_match_by_id(MatchesService._current_match_id)

        if not match:
            return "❌ Няма избран мач. Използвай 'избери мач <ID>'"

        card_type = card_type.upper()
        if card_type not in ['Y', 'R']:
            return "❌ Невалиден тип картон. Използвай 'Y' за жълт или 'R' за червен"

        player = PlayersService.find_player_by_name(player_name)
        if not player:
            return f"❌ Играч '{player_name}' не е намерен"

        club = ClubsService.find_club_by_name(club_name)
        if not club:
            return f"❌ Клуб '{club_name}' не съществува"

        if club['id'] not in [match['home_club_id'], match['away_club_id']]:
            return f"❌ Клуб '{club_name}' не участва в този мач"

        if player['club_id'] != club['id']:
            return f"❌ Играч '{player_name}' не играе за {club_name}"

        try:
            minute = int(minute)
            if minute < 1 or minute > 120:
                return "❌ Минутата трябва да е между 1 и 120"
        except ValueError:
            return "❌ Невалидна минута"

        MatchesRepo.add_card(match['id'], player['id'], club['id'], minute, card_type)

        card_name = "жълт картон" if card_type == 'Y' else "червен картон"
        return f"✅ {card_name} за {player_name} ({club_name}) в {minute} минута"

    @staticmethod
    def add_card_simple(player_name, card_type, minute):
        """Добавя картон за текущия мач (отборът се определя от контекста)"""
        match = MatchesService.get_current_match()
        if not match:
            return "❌ Няма избран мач. Използвай 'избери мач <ID>'"

        card_type = card_type.upper()
        if card_type not in ['Y', 'R']:
            return "❌ Невалиден тип картон. Използвай 'Y' за жълт или 'R' за червен"

        player = PlayersService.find_player_by_name(player_name)
        if not player:
            return f"❌ Играч '{player_name}' не е намерен"

        # Определяме отбора на играча
        club_id = player['club_id']
        if club_id not in [match['home_club_id'], match['away_club_id']]:
            return f"❌ Играч '{player_name}' не участва в този мач"

        club_name = match['home_club_name'] if club_id == match['home_club_id'] else match['away_club_name']

        try:
            minute = int(minute)
            if minute < 1 or minute > 120:
                return "❌ Минутата трябва да е между 1 и 120"
        except ValueError:
            return "❌ Невалидна минута"

        MatchesRepo.add_card(match['id'], player['id'], club_id, minute, card_type)

        card_name = "жълт картон" if card_type == 'Y' else "червен картон"
        return f"✅ {card_name} за {player_name} ({club_name}) в {minute} минута"
    @staticmethod
    def show_events(match_id=None):
        match = None
        if match_id:
            match = MatchesRepo.get_match_by_id(match_id)
        elif MatchesService._current_match_id:
            match = MatchesRepo.get_match_by_id(MatchesService._current_match_id)

        if not match:
            return "❌ Няма избран мач. Използвай 'избери мач <ID>' или 'покажи събития <ID>'"

        goals = MatchesRepo.get_goals_by_match(match['id'])
        cards = MatchesRepo.get_cards_by_match(match['id'])

        events = []
        for g in goals:
            events.append((g['minute'], '⚽', f"ГОЛ: {g['player_name']} ({g['club_name']})"))
        for c in cards:
            card_symbol = '🟨' if c['card_type'] == 'Y' else '🟥'
            card_name = "ЖЪЛТ" if c['card_type'] == 'Y' else "ЧЕРВЕН"
            events.append((c['minute'], card_symbol, f"{card_name} КАРТОН: {c['player_name']} ({c['club_name']})"))

        events.sort(key=lambda x: x[0])

        if not events:
            return f"📋 Няма събития за мача {match['home_club_name']} - {match['away_club_name']}"

        response = f"📋 СЪБИТИЯ: {match['home_club_name']} - {match['away_club_name']}\n"
        for minute, symbol, text in events:
            response += f"   {minute}' {symbol} {text}\n"

        return response
