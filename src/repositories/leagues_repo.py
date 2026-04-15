import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import execute_query, execute_transaction

class LeaguesRepo:

    # ============================================================
    # LEAGUES
    # ============================================================

    @staticmethod
    def create_league(name, season):
        """Създава нова лига"""
        return execute_query(
            "INSERT INTO leagues (name, season) VALUES (?, ?)",
            (name, season)
        )

    @staticmethod
    def get_league_by_name_season(name, season):
        """Намира лига по име и сезон"""
        return execute_query(
            "SELECT * FROM leagues WHERE name = ? AND season = ?",
            (name, season),
            fetch_one=True
        )

    @staticmethod
    def get_all_leagues():
        """Връща всички лиги"""
        return execute_query(
            "SELECT * FROM leagues ORDER BY season DESC, name",
            fetch_all=True
        )

    # ============================================================
    # LEAGUE TEAMS
    # ============================================================

    @staticmethod
    def add_team_to_league(league_id, club_id):
        """Добавя отбор към лига"""
        return execute_query(
            "INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)",
            (league_id, club_id)
        )

    @staticmethod
    def remove_team_from_league(league_id, club_id):
        """Премахва отбор от лига"""
        return execute_query(
            "DELETE FROM league_teams WHERE league_id = ? AND club_id = ?",
            (league_id, club_id)
        )

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
    def is_team_in_league(league_id, club_id):
        """Проверява дали отбор е в лига"""
        result = execute_query(
            "SELECT 1 FROM league_teams WHERE league_id = ? AND club_id = ?",
            (league_id, club_id),
            fetch_one=True
        )
        return result is not None

    @staticmethod
    def get_team_count(league_id):
        """Брой отбори в лига"""
        result = execute_query(
            "SELECT COUNT(*) as count FROM league_teams WHERE league_id = ?",
            (league_id,),
            fetch_one=True
        )
        return result['count'] if result else 0

    # ============================================================
    # MATCHES
    # ============================================================

    @staticmethod
    def clear_matches(league_id):
        """Изтрива всички мачове за дадена лига"""
        execute_query("DELETE FROM matches WHERE league_id = ?", (league_id,))

    @staticmethod
    def create_match(league_id, round_no, home_club_id, away_club_id):
        """Създава мач"""
        return execute_query(
            "INSERT INTO matches (league_id, round_no, home_club_id, away_club_id) VALUES (?, ?, ?, ?)",
            (league_id, round_no, home_club_id, away_club_id)
        )

    @staticmethod
    def get_matches_by_league(league_id):
        """Връща всички мачове за лига"""
        return execute_query(
            """SELECT m.*, 
                      h.name as home_club_name, 
                      a.name as away_club_name
               FROM matches m
               JOIN clubs h ON m.home_club_id = h.id
               JOIN clubs a ON m.away_club_id = a.id
               WHERE m.league_id = ?
               ORDER BY m.round_no""",
            (league_id,),
            fetch_all=True
        )

    @staticmethod
    def get_matches_summary(league_id):
        """Статистика за мачовете"""
        result = execute_query(
            "SELECT COUNT(*) as total, COUNT(DISTINCT round_no) as rounds FROM matches WHERE league_id = ?",
            (league_id,),
            fetch_one=True
        )
        return result
