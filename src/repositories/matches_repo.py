"""
MATCHES REPOSITORY - ЕТАП 6
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import execute_query, execute_transaction


class MatchesRepo:

    # ============================================================
    # MATCHES
    # ============================================================

    @staticmethod
    def get_matches_by_league_round(league_id, round_no):
        """Връща всички мачове за даден кръг и лига"""
        print(f"DEBUG: Търсене на мачове - league_id={league_id}, round_no={round_no}")
        result = execute_query(
            """SELECT m.*, 
                      h.name as home_club_name, 
                      a.name as away_club_name
               FROM matches m
               JOIN clubs h ON m.home_club_id = h.id
               JOIN clubs a ON m.away_club_id = a.id
               WHERE m.league_id = ? AND m.round_no = ?
               ORDER BY m.id""",
            (league_id, round_no),
            fetch_all=True
        )
        print(f"DEBUG: Намерени {len(result) if result else 0} мача")
        return result

    @staticmethod
    def get_match_by_teams(home_club_id, away_club_id, league_id=None):
        """Намира мач по отбори (опционално по лига)"""
        query = "SELECT * FROM matches WHERE home_club_id = ? AND away_club_id = ?"
        params = [home_club_id, away_club_id]

        if league_id:
            query += " AND league_id = ?"
            params.append(league_id)

        return execute_query(query, params, fetch_one=True)

    @staticmethod
    def get_match_by_id(match_id):
        """Връща мач по ID"""
        return execute_query(
            """SELECT m.*, 
                      h.name as home_club_name, 
                      a.name as away_club_name,
                      l.name as league_name,
                      l.season
               FROM matches m
               JOIN clubs h ON m.home_club_id = h.id
               JOIN clubs a ON m.away_club_id = a.id
               JOIN leagues l ON m.league_id = l.id
               WHERE m.id = ?""",
            (match_id,),
            fetch_one=True
        )

    @staticmethod
    def update_match_result(match_id, home_goals, away_goals):
        """Обновява резултат на мач (без status)"""
        return execute_query(
            "UPDATE matches SET home_goals = ?, away_goals = ? WHERE id = ?",
            (home_goals, away_goals, match_id)
        )

    @staticmethod
    def get_current_round(league_id):
        """Връща текущия кръг (най-малкия неизигран)"""
        result = execute_query(
            "SELECT MIN(round_no) as round FROM matches WHERE league_id = ? AND status = 'scheduled'",
            (league_id,),
            fetch_one=True
        )
        return result['round'] if result and result['round'] else 1

    # ============================================================
    # GOALS
    # ============================================================

    @staticmethod
    def add_goal(match_id, player_id, club_id, minute, is_own_goal=0):
        """Добавя гол"""
        return execute_query(
            "INSERT INTO goals (match_id, player_id, club_id, minute, is_own_goal) VALUES (?, ?, ?, ?, ?)",
            (match_id, player_id, club_id, minute, is_own_goal)
        )

    @staticmethod
    def get_goals_by_match(match_id):
        """Връща всички голове за мач"""
        return execute_query(
            """SELECT g.*, p.full_name as player_name, c.name as club_name
               FROM goals g
               JOIN players p ON g.player_id = p.id
               JOIN clubs c ON g.club_id = c.id
               WHERE g.match_id = ?
               ORDER BY g.minute""",
            (match_id,),
            fetch_all=True
        )

    # ============================================================
    # CARDS
    # ============================================================

    @staticmethod
    def add_card(match_id, player_id, club_id, minute, card_type):
        """Добавя картон"""
        return execute_query(
            "INSERT INTO cards (match_id, player_id, club_id, minute, card_type) VALUES (?, ?, ?, ?, ?)",
            (match_id, player_id, club_id, minute, card_type)
        )

    @staticmethod
    def get_cards_by_match(match_id):
        """Връща всички картони за мач"""
        return execute_query(
            """SELECT c.*, p.full_name as player_name, cl.name as club_name
               FROM cards c
               JOIN players p ON c.player_id = p.id
               JOIN clubs cl ON c.club_id = cl.id
               WHERE c.match_id = ?
               ORDER BY c.minute""",
            (match_id,),
            fetch_all=True
        )

    @staticmethod
    def get_player_cards_in_match(match_id, player_id):
        """Връща всички картони на играч в мач"""
        return execute_query(
            "SELECT * FROM cards WHERE match_id = ? AND player_id = ? ORDER BY minute",
            (match_id, player_id),
            fetch_all=True
        )
