"""
AI MODULE - ЕТАП 8
Извличане на характеристики за отбори
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import execute_query


class TeamFeatures:
    """Клас за извличане на статистически характеристики на отбор"""

    @staticmethod
    def get_team_id_by_name(team_name):
        """Намира ID на отбор по име (без значение на малки/главни)"""
        # Първо търсене с точно съвпадение (без значение на малки/главни)
        result = execute_query(
            "SELECT id FROM clubs WHERE LOWER(name) = LOWER(?)",
            (team_name.strip(),),
            fetch_one=True
        )

        # Второ търсене с LIKE
        if not result:
            result = execute_query(
                "SELECT id FROM clubs WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{team_name.strip()}%",),
                fetch_one=True
            )

        # Трето - вземаме всички клубове и търсим ръчно
        if not result:
            all_clubs = execute_query("SELECT id, name FROM clubs", fetch_all=True)
            for club in all_clubs:
                if team_name.lower() in club['name'].lower():
                    result = {'id': club['id']}
                    break

        return result

    @staticmethod
    def get_last_n_matches(team_id, n=5):
        """Връща последните N мача на отбор"""
        matches = execute_query(
            """SELECT m.*, 
                      h.name as home_name, a.name as away_name,
                      CASE 
                          WHEN m.home_club_id = ? THEN 'home'
                          ELSE 'away'
                      END as venue
               FROM matches m
               JOIN clubs h ON m.home_club_id = h.id
               JOIN clubs a ON m.away_club_id = a.id
               WHERE (m.home_club_id = ? OR m.away_club_id = ?) 
                 AND m.status = 'played'
               ORDER BY m.created_at DESC
               LIMIT ?""",
            (team_id, team_id, team_id, n),
            fetch_all=True
        )
        return matches

    @staticmethod
    def get_team_form(team_id, n=5):
        """Изчислява формата на отбора от последните N мача"""
        matches = TeamFeatures.get_last_n_matches(team_id, n)

        if len(matches) < 1:
            return None, f"Недостатъчно мачове за анализ (нужни са минимум 5, налични {len(matches)})"

        points = 0
        total_goals_scored = 0
        total_goals_conceded = 0

        for match in matches:
            if match['venue'] == 'home':
                scored = match['home_goals'] or 0
                conceded = match['away_goals'] or 0
            else:
                scored = match['away_goals'] or 0
                conceded = match['home_goals'] or 0

            if scored > conceded:
                points += 3
            elif scored == conceded:
                points += 1

            total_goals_scored += scored
            total_goals_conceded += conceded

        max_points = n * 3
        form_score = points / max_points

        avg_goals_scored = total_goals_scored / n
        avg_goals_conceded = total_goals_conceded / n

        return {
            'form_score': form_score,
            'avg_scored': avg_goals_scored,
            'avg_conceded': avg_goals_conceded,
            'points': points,
            'matches_played': len(matches)
        }, None

    @staticmethod
    def get_team_standing(team_id, league_id):
        """Намира позицията на отбора в класирането"""
        teams = execute_query(
            """SELECT c.id, c.name,
                      COALESCE(SUM(CASE 
                          WHEN m.home_club_id = c.id AND m.home_goals > m.away_goals THEN 3
                          WHEN m.away_club_id = c.id AND m.away_goals > m.home_goals THEN 3
                          WHEN m.home_goals = m.away_goals THEN 1
                          ELSE 0
                      END), 0) as points
               FROM clubs c
               JOIN league_teams lt ON c.id = lt.club_id
               LEFT JOIN matches m ON (m.home_club_id = c.id OR m.away_club_id = c.id) 
                  AND m.league_id = ? AND m.status = 'played'
               WHERE lt.league_id = ?
               GROUP BY c.id
               ORDER BY points DESC""",
            (league_id, league_id),
            fetch_all=True
        )

        for idx, team in enumerate(teams, 1):
            if team['id'] == team_id:
                position = idx
                total_teams = len(teams)
                normalized_position = 1 - (position - 1) / (total_teams - 1) if total_teams > 1 else 0.5
                return {
                    'position': position,
                    'total_teams': total_teams,
                    'normalized': normalized_position,
                    'points': team['points']
                }

        return None

    @staticmethod
    def get_league_for_teams(team1_id, team2_id):
        """Намира обща лига за два отбора"""
        return execute_query(
            """SELECT l.id, l.name, l.season
               FROM leagues l
               JOIN league_teams lt1 ON l.id = lt1.league_id
               JOIN league_teams lt2 ON l.id = lt2.league_id
               WHERE lt1.club_id = ? AND lt2.club_id = ?""",
            (team1_id, team2_id),
            fetch_one=True
        )
