"""
STANDINGS SERVICE - ЕТАП 7
Бизнес логика за изчисляване на класиране
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from repositories.standings_repo import StandingsRepo
from database.db import execute_query


class StandingsService:
    """Клас за изчисляване и управление на класиране"""

    @staticmethod
    def calculate_standings(league_name, season, use_head_to_head=True):
        """
        Изчислява класиране за дадена лига

        Args:
            league_name: Име на лигата
            season: Сезон (формат YYYY/YYYY)
            use_head_to_head: Използва ли директни срещи при равенство

        Returns:
            tuple: (success, message, standings_list)
        """
        # 1. Намиране на лигата
        league = StandingsRepo.get_league_by_name_season(league_name, season)
        if not league:
            return False, f"❌ Лига '{league_name}' за сезон {season} не съществува", None

        # 2. Проверка за отбори
        if not StandingsRepo.check_league_has_teams(league['id']):
            return False, f"📋 Лига '{league_name}' ({season}) няма добавени отбори", None

        # 3. Вземане на отборите в лигата
        teams = StandingsRepo.get_teams_in_league(league['id'])

        # 4. Инициализиране на статистиките
        stats = {}
        for team in teams:
            stats[team['id']] = {
                'name': team['name'],
                'id': team['id'],
                'mp': 0,  # Мачове
                'w': 0,  # Победи
                'd': 0,  # Равни
                'l': 0,  # Загуби
                'gf': 0,  # Вкарани голове
                'ga': 0,  # Допуснати голове
                'gd': 0,  # Голова разлика
                'pts': 0  # Точки
            }

        # 5. Вземане на изиграните мачове
        matches = StandingsRepo.get_played_matches_for_league(league['id'])

        # 6. Обработка на всеки мач
        for match in matches:
            home_id = match['home_club_id']
            away_id = match['away_club_id']
            home_goals = match['home_goals'] or 0
            away_goals = match['away_goals'] or 0

            # Обновяване на головете
            if home_id in stats:
                stats[home_id]['gf'] += home_goals
                stats[home_id]['ga'] += away_goals
                stats[home_id]['mp'] += 1

            if away_id in stats:
                stats[away_id]['gf'] += away_goals
                stats[away_id]['ga'] += home_goals
                stats[away_id]['mp'] += 1

            # Определяне на резултата
            if home_goals > away_goals:
                # Домакин печели
                if home_id in stats:
                    stats[home_id]['w'] += 1
                    stats[home_id]['pts'] += 3
                if away_id in stats:
                    stats[away_id]['l'] += 1
            elif away_goals > home_goals:
                # Гост печели
                if home_id in stats:
                    stats[home_id]['l'] += 1
                if away_id in stats:
                    stats[away_id]['w'] += 1
                    stats[away_id]['pts'] += 3
            else:
                # Равен
                if home_id in stats:
                    stats[home_id]['d'] += 1
                    stats[home_id]['pts'] += 1
                if away_id in stats:
                    stats[away_id]['d'] += 1
                    stats[away_id]['pts'] += 1

        # 7. Изчисляване на голова разлика
        for team_id in stats:
            stats[team_id]['gd'] = stats[team_id]['gf'] - stats[team_id]['ga']

        # 8. Преобразуване в списък за сортиране
        standings_list = list(stats.values())

        # 9. Сортиране
        if use_head_to_head:
            standings_list = StandingsService._sort_with_head_to_head(standings_list, matches, league['id'])
        else:
            standings_list.sort(key=lambda x: (-x['pts'], -x['gd'], -x['gf'], x['name']))

        # 10. Добавяне на позиции
        for idx, team in enumerate(standings_list, 1):
            team['position'] = idx

        has_matches = len(matches) > 0
        return True, "Класирането е изчислено успешно", standings_list

    @staticmethod
    def _sort_with_head_to_head(standings_list, matches, league_id):
        """
        Сортиране с отчитане на директни срещи (за отличен)
        """
        # Първоначално сортиране по основни критерии
        standings_list.sort(key=lambda x: (-x['pts'], -x['gd'], -x['gf'], x['name']))

        # Групиране на отбори с равни точки
        i = 0
        while i < len(standings_list):
            j = i
            while j < len(standings_list) and standings_list[j]['pts'] == standings_list[i]['pts']:
                j += 1

            if j - i > 1:  # Има равни точки
                tied_teams = standings_list[i:j]

                # Вземане на ID-тата на отборите
                tied_ids = [t['id'] for t in tied_teams]

                # Намиране на директните срещи между тях
                head_to_head = StandingsRepo.get_head_to_head_matches(league_id, tied_ids)

                # Изчисляване на статистики само от директните срещи
                h2h_stats = {}
                for team in tied_teams:
                    h2h_stats[team['id']] = {
                        'pts': 0,
                        'gd': 0,
                        'gf': 0
                    }

                for match in head_to_head:
                    home_id = match['home_club_id']
                    away_id = match['away_club_id']

                    if home_id not in h2h_stats or away_id not in h2h_stats:
                        continue

                    home_goals = match['home_goals'] or 0
                    away_goals = match['away_goals'] or 0

                    # Обновяване на голове
                    h2h_stats[home_id]['gf'] += home_goals
                    h2h_stats[home_id]['gd'] += (home_goals - away_goals)
                    h2h_stats[away_id]['gf'] += away_goals
                    h2h_stats[away_id]['gd'] += (away_goals - home_goals)

                    # Обновяване на точки
                    if home_goals > away_goals:
                        h2h_stats[home_id]['pts'] += 3
                    elif away_goals > home_goals:
                        h2h_stats[away_id]['pts'] += 3
                    else:
                        h2h_stats[home_id]['pts'] += 1
                        h2h_stats[away_id]['pts'] += 1

                # Сортиране на равните отбори по директни срещи
                tied_teams.sort(key=lambda x: (-h2h_stats[x['id']]['pts'],
                                               -h2h_stats[x['id']]['gd'],
                                               -h2h_stats[x['id']]['gf'],
                                               x['name']))

                standings_list[i:j] = tied_teams

            i = j

        return standings_list

    @staticmethod
    def format_standings_table(standings_list, league_name, season):
        """
        Форматира класирането в таблица за показване
        """
        if not standings_list:
            return f"📋 Няма данни за класиране в {league_name} ({season})"

        # Проверка дали има изиграни мачове
        has_played_matches = any(t['mp'] > 0 for t in standings_list)

        # Заглавие
        result = f"📊 КЛАСИРАНЕ - {league_name} ({season})\n"
        result += "=" * 60 + "\n"
        result += f"{'#':<3} {'Отбор':<25} {'М':<3} {'П':<3} {'Р':<3} {'З':<3} {'Голове':<12} {'ГР':<4} {'Т':<3}\n"
        result += "-" * 60 + "\n"

        for team in standings_list:
            result += (f"{team['position']:<3} "
                       f"{team['name'][:24]:<25} "
                       f"{team['mp']:<3} "
                       f"{team['w']:<3} "
                       f"{team['d']:<3} "
                       f"{team['l']:<3} "
                       f"{team['gf']}:{team['ga']:<9} "
                       f"{team['gd']:<4} "
                       f"{team['pts']:<3}\n")

        result += "=" * 60 + "\n"

        if not has_played_matches:
            result += "\n📋 Няма изиграни мачове в тази лига.\n"

        return result


def update_standings_after_result(match_id):
    """
    Обновява класирането след въвеждане на резултат
    (задава статуса на мача като 'played')
    """
    execute_query(
        "UPDATE matches SET status = 'played' WHERE id = ?",
        (match_id,)
    )
