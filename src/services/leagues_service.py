"""
LEAGUES SERVICE - ЕТАП 5
Бизнес логика за лиги, отбори и генериране на програма
"""

import re
from repositories.leagues_repo import LeaguesRepo
from services.club_service import ClubsService


class LeaguesService:

    # ============================================================
    # ВАЛИДАЦИИ
    # ============================================================

    @staticmethod
    def validate_season(season):
        """Проверка за валиден сезон (YYYY/YYYY)"""
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
        """Проверява дали лига съществува"""
        league = LeaguesRepo.get_league_by_name_season(name, season)
        if not league:
            return False, f"❌ Лига '{name}' за сезон {season} не съществува"
        return True, league

    # ============================================================
    # ОСНОВНИ ФУНКЦИИ
    # ============================================================

    @staticmethod
    def create_league(name, season):
        """Създава нова лига"""
        # Валидация на сезон
        valid, result = LeaguesService.validate_season(season)
        if not valid:
            return result

        # Проверка дали лигата вече съществува
        existing = LeaguesRepo.get_league_by_name_season(name, season)
        if existing:
            return f"❌ Лига '{name}' за сезон {season} вече съществува"

        # Създаване
        league_id = LeaguesRepo.create_league(name, season)
        return f"✅ Създадена лига: {name} ({season}) с ID: {league_id}"

    @staticmethod
    def add_team_to_league(club_name, league_name, season):
        """Добавя отбор към лига"""
        # Проверка дали клубът съществува
        club = ClubsService.find_club_by_name(club_name)
        if not club:
            return f"❌ Клуб '{club_name}' не съществува. Използвай: покажи клубове"

        # Проверка дали лигата съществува
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        # Проверка дали отборът вече е в лигата
        if LeaguesRepo.is_team_in_league(league['id'], club['id']):
            return f"❌ Клуб '{club_name}' вече е в лига '{league_name}' ({season})"

        # Добавяне
        LeaguesRepo.add_team_to_league(league['id'], club['id'])
        return f"✅ Добавен отбор: {club_name} в лига {league_name} ({season})"

    @staticmethod
    def remove_team_from_league(club_name, league_name, season):
        """Премахва отбор от лига"""
        # Проверка за клуб
        club = ClubsService.find_club_by_name(club_name)
        if not club:
            return f"❌ Клуб '{club_name}' не съществува"

        # Проверка за лига
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        # Проверка дали отборът е в лигата
        if not LeaguesRepo.is_team_in_league(league['id'], club['id']):
            return f"❌ Клуб '{club_name}' не е в лига '{league_name}' ({season})"

        # Премахване
        LeaguesRepo.remove_team_from_league(league['id'], club['id'])
        return f"✅ Премахнат отбор: {club_name} от лига {league_name} ({season})"

    @staticmethod
    def show_teams_in_league(league_name, season):
        """Показва всички отбори в лига"""
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

    # ============================================================
    # ГЕНЕРИРАНЕ НА ПРОГРАМА (Round-Robin)
    # ============================================================

    @staticmethod
    def generate_fixture(league_name, season):
        """
        Генерира програма за лига (Round-Robin)
        Алгоритъм: "Circle method" за една среща (single round-robin)
        """
        # Проверка за лига
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        # Взимаме отборите
        teams = LeaguesRepo.get_teams_in_league(league['id'])
        team_count = len(teams)

        # Проверка за минимален брой отбори (минимум 4)
        if team_count < 4:
            return f"❌ Недостатъчно отбори за програма (минимум 4). В момента има {team_count} отбора."

        # Изтриваме старата програма
        LeaguesRepo.clear_matches(league['id'])

        # Подготовка на отборите
        team_ids = [team['id'] for team in teams]

        # Ако е нечетен брой, добавяме BYE (None)
        has_bye = team_count % 2 == 1
        if has_bye:
            team_ids.append(None)
            n = team_count + 1
        else:
            n = team_count

        rounds = n - 1
        matches_per_round = n // 2
        total_matches = (team_count * (team_count - 1)) // 2

        # Circle method алгоритъм
        fixture = []
        fixed = team_ids[0]
        rotating = team_ids[1:]

        for round_num in range(rounds):
            round_matches = []

            # Създаваме двойките за този кръг
            for i in range(matches_per_round):
                home = fixed if i == 0 else rotating[i - 1]
                away = rotating[-i - 1] if i < len(rotating) else None

                if home is not None and away is not None:
                    round_matches.append((home, away))

            fixture.append(round_matches)

            # Ротация на отборите
            if rotating:
                rotating = [rotating[-1]] + rotating[:-1]

        # Записване на мачовете в базата
        matches_added = 0
        for round_idx, round_matches in enumerate(fixture, 1):
            for home_id, away_id in round_matches:
                if home_id and away_id:  # Пропускаме BYE мачове
                    LeaguesRepo.create_match(league['id'], round_idx, home_id, away_id)
                    matches_added += 1

        # Показване на първия кръг за пример
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
        """Показва програмата на лига"""
        valid, result = LeaguesService.validate_league_exists(league_name, season)
        if not valid:
            return result
        league = result

        teams = {t['id']: t['name'] for t in LeaguesRepo.get_teams_in_league(league['id'])}
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
