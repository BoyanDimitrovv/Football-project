import re
from repositories.leagues_repo import LeaguesRepo
from database.db import execute_query

class LeaguesService:

    @staticmethod
    def validate_season(season):
        pattern = r'^\d{4}/\d{4}$'
        if not re.match(pattern, season):
            return False, "Невалиден формат на сезон. Използвайте YYYY/YYYY (пример: 2025/2026)"
        start_year = int(season[:4])
        end_year = int(season[5:])
        if end_year != start_year + 1:
            return False, "Годините трябва да са последователни (напр. 2025/2026)"
        return True, season

    @staticmethod
    def validate_league_exists(name, season):
        league = LeaguesRepo.get_league_by_name_season(name, season)
        if not league:
            return False, f"❌ Лига '{name}' за сезон {season} не съществува"
        return True, league

    @staticmethod
    def create_league(name, season):
        valid, result = LeaguesService.validate_season(season)
        if not valid:
            return result
        existing = LeaguesRepo.get_league_by_name_season(name, season)
        if existing:
            return f"❌ Лига '{name}' за сезон {season} вече съществува"
        league_id = LeaguesRepo.create_league(name, season)
        return f"✅ Създадена лига: {name} ({season}) с ID: {league_id}"

    @staticmethod
    def add_team_to_league(club_name, league_name, season):
        # Взимаме всички клубове и търсим ръчно (най-сигурния начин)
        all_clubs = execute_query("SELECT * FROM clubs", fetch_all=True)

        club = None
        search_name = club_name.strip().lower()

        for c in all_clubs:
            if c['name'].lower() == search_name:
                club = c
                break

        if not club:
            for c in all_clubs:
                if search_name in c['name'].lower():
                    club = c
                    break

        if not club:
            return f"❌ Клуб '{club_name}' не съществува. Използвай: покажи клубове"

        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        if LeaguesRepo.is_team_in_league(league['id'], club['id']):
            return f"❌ Клуб '{club['name']}' вече е в лига '{league_name}' ({season})"

        LeaguesRepo.add_team_to_league(league['id'], club['id'])
        return f"✅ Добавен отбор: {club['name']} в лига {league_name} ({season})"

    @staticmethod
    def remove_team_from_league(club_name, league_name, season):
        # Взимаме всички клубове и търсим ръчно
        all_clubs = execute_query("SELECT * FROM clubs", fetch_all=True)

        club = None
        search_name = club_name.strip().lower()

        for c in all_clubs:
            if c['name'].lower() == search_name:
                club = c
                break

        if not club:
            for c in all_clubs:
                if search_name in c['name'].lower():
                    club = c
                    break

        if not club:
            return f"❌ Клуб '{club_name}' не съществува"

        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        if not LeaguesRepo.is_team_in_league(league['id'], club['id']):
            return f"❌ Клуб '{club['name']}' не е в лига '{league_name}' ({season})"

        LeaguesRepo.remove_team_from_league(league['id'], club['id'])
        return f"✅ Премахнат отбор: {club['name']} от лига {league_name} ({season})"

    @staticmethod
    def show_teams_in_league(league_name, season):
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        teams = LeaguesRepo.get_teams_in_league(league['id'])

        if not teams:
            return f"📋 Няма отбори в лига {league_name} ({season})"

        response = f"📋 Отбори в {league_name} ({season}):\n"
        for team in teams:
            response += f"  🏆 {team['id']}. {team['name']}\n"
        return response

    @staticmethod
    def generate_fixture(league_name, season):
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        teams = LeaguesRepo.get_teams_in_league(league['id'])
        team_count = len(teams)

        if team_count < 4:
            return f"❌ Недостатъчно отбори за програма (минимум 4). В момента има {team_count} отбора."

        LeaguesRepo.clear_matches(league['id'])

        team_ids = [team['id'] for team in teams]
        has_bye = team_count % 2 == 1
        if has_bye:
            team_ids.append(None)
            n = team_count + 1
        else:
            n = team_count

        rounds = n - 1
        matches_per_round = n // 2

        fixture = []
        fixed = team_ids[0]
        rotating = team_ids[1:]

        for round_num in range(rounds):
            round_matches = []
            for i in range(matches_per_round):
                home = fixed if i == 0 else rotating[i - 1]
                away = rotating[-i - 1] if i < len(rotating) else None
                if home is not None and away is not None:
                    round_matches.append((home, away))
            fixture.append(round_matches)
            if rotating:
                rotating = [rotating[-1]] + rotating[:-1]

        matches_added = 0
        for round_idx, round_matches in enumerate(fixture, 1):
            for home_id, away_id in round_matches:
                if home_id and away_id:
                    LeaguesRepo.create_match(league['id'], round_idx, home_id, away_id)
                    matches_added += 1

        first_round = fixture[0] if fixture else []
        first_round_preview = []
        for home_id, away_id in first_round:
            if home_id and away_id:
                home_name = next((t['name'] for t in teams if t['id'] == home_id), "?")
                away_name = next((t['name'] for t in teams if t['id'] == away_id), "?")
                first_round_preview.append(f"{home_name} - {away_name}")

        return (f"✅ Генерирана програма за {league_name} ({season})\n"
                f"   📊 Отбори: {team_count}\n"
                f"   📅 Кръгове: {rounds}\n"
                f"   ⚽ Мачове: {matches_added}\n"
                f"   🔍 Примерен 1-ви кръг:\n"
                f"      {', '.join(first_round_preview)}")

    @staticmethod
    def show_fixture(league_name, season):
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        matches = LeaguesRepo.get_matches_by_league(league['id'])

        if not matches:
            return f"📋 Няма генерирана програма за {league_name} ({season}). Използвай 'генерирай програма'"

        current_round = None
        response = f"📋 Програма за {league_name} ({season}):\n"

        for match in matches:
            if match['round_no'] != current_round:
                current_round = match['round_no']
                response += f"\n  🔄 КРЪГ {current_round}:\n"
            response += f"     🏆 {match['home_club_name']} - {match['away_club_name']}\n"

        return response
