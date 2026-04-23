"""
STANDINGS REPOSITORY - ЕТАП 7
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import execute_query


class StandingsRepo:

    @staticmethod
    def get_teams_in_league(league_id):
        """Връща всички отбори в лига"""
        return execute_query(
            """SELECT c.id, c.name 
               FROM league_teams lt
               JOIN clubs c ON lt.club_id = c.id
               WHERE lt.league_id = ?
               ORDER BY c.name""",
            (league_id,),
            fetch_all=True
        )

    @staticmethod
    def get_played_matches_for_league(league_id):
        """Връща всички изиграни мачове за лига"""
        return execute_query(
            """SELECT m.*, 
                      h.name as home_club_name, 
                      a.name as away_club_name
               FROM matches m
               JOIN clubs h ON m.home_club_id = h.id
               JOIN clubs a ON m.away_club_id = a.id
               WHERE m.league_id = ? AND m.status = 'played'
               ORDER BY m.round_no""",
            (league_id,),
            fetch_all=True
        )

    @staticmethod
    def get_league_by_name_season(name, season):
        """Намира лига по име и сезон"""
        return execute_query(
            "SELECT * FROM leagues WHERE LOWER(name) = LOWER(?) AND season = ?",
            (name, season),
            fetch_one=True
        )

    @staticmethod
    def check_league_has_teams(league_id):
        """Проверява дали лигата има отбори"""
        result = execute_query(
            "SELECT COUNT(*) as count FROM league_teams WHERE league_id = ?",
            (league_id,),
            fetch_one=True
        )
        return result['count'] > 0 if result else False

    @staticmethod
    def check_league_has_played_matches(league_id):
        """Проверява дали лигата има изиграни мачове"""
        result = execute_query(
            "SELECT COUNT(*) as count FROM matches WHERE league_id = ? AND status = 'played'",
            (league_id,),
            fetch_one=True
        )
        return result['count'] > 0 if result else False

    @staticmethod
    def get_head_to_head_matches(league_id, team_ids):
        """Връща директните срещи между дадени отбори"""
        if not team_ids or len(team_ids) < 2:
            return []

        placeholders = ','.join(['?' for _ in team_ids])
        query = f"""
            SELECT m.*, 
                   h.name as home_name, a.name as away_name
            FROM matches m
            JOIN clubs h ON m.home_club_id = h.id
            JOIN clubs a ON m.away_club_id = a.id
            WHERE m.league_id = ? 
              AND m.status = 'played'
              AND m.home_club_id IN ({placeholders})
              AND m.away_club_id IN ({placeholders})
        """
        params = [league_id] + team_ids + team_ids
        return execute_query(query, params, fetch_all=True)
