"""
AI MODULE - ЕТАП 8
Rule-based модел за прогнозиране на мачове
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.features import TeamFeatures


class AIService:
    """Клас за прогнозиране на резултати от мачове"""

    # Тежести за различните фактори
    WEIGHTS = {
        'home_advantage': 1.15,
        'form': 0.35,
        'attack': 0.25,
        'defense': 0.20,
        'standing': 0.20
    }

    @staticmethod
    def calculate_home_advantage():
        """Изчислява общо домакинско предимство"""
        from database.db import execute_query

        stats = execute_query(
            """SELECT 
                  COUNT(CASE WHEN home_goals > away_goals THEN 1 END) as home_wins,
                  COUNT(CASE WHEN away_goals > home_goals THEN 1 END) as away_wins,
                  COUNT(*) as total
               FROM matches WHERE status = 'played'""",
            fetch_one=True
        )

        if stats and stats['total'] > 0:
            home_win_rate = stats['home_wins'] / stats['total']
            away_win_rate = stats['away_wins'] / stats['total']
            advantage = home_win_rate / (away_win_rate + 0.01)
            return min(advantage, 1.5)
        return 1.15

    @staticmethod
    def predict_match(team1_name, team2_name):
        """
        Прогнозира резултат между два отбора

        Returns:
            tuple: (prediction_dict, error_message)
        """
        # 1. Намиране на ID на отборите
        team1 = TeamFeatures.get_team_id_by_name(team1_name)
        team2 = TeamFeatures.get_team_id_by_name(team2_name)

        if not team1:
            return None, f"❌ Отбор '{team1_name}' не съществува"
        if not team2:
            return None, f"❌ Отбор '{team2_name}' не съществува"

        if team1['id'] == team2['id']:
            return None, "❌ Не може да прогнозирате мач на отбор със себе си"

        # 2. Намиране на обща лига
        league = TeamFeatures.get_league_for_teams(team1['id'], team2['id'])
        if not league:
            return None, f"❌ Отборите '{team1_name}' и '{team2_name}' не играят в една лига"

        # 3. Извличане на характеристики
        team1_form, err1 = TeamFeatures.get_team_form(team1['id'])
        team2_form, err2 = TeamFeatures.get_team_form(team2['id'])

        if err1:
            return None, err1
        if err2:
            return None, err2

        team1_standing = TeamFeatures.get_team_standing(team1['id'], league['id'])
        team2_standing = TeamFeatures.get_team_standing(team2['id'], league['id'])

        # 4. Изчисляване на индекси
        home_advantage = AIService.calculate_home_advantage()

        home_index = (
                AIService.WEIGHTS['home_advantage'] * home_advantage *
                (team1_form['form_score'] * 0.4 + team2_form['form_score'] * 0.6)
        )

        away_index = team2_form['form_score']

        # Атакуваща сила
        if team1_form['avg_scored'] > team2_form['avg_conceded']:
            home_index *= 1.1
        if team2_form['avg_scored'] > team1_form['avg_conceded']:
            away_index *= 1.1

        # Позиция в класирането
        if team1_standing:
            home_index *= (1 + team1_standing['normalized'] * 0.2)
        if team2_standing:
            away_index *= (1 + team2_standing['normalized'] * 0.2)

        # Индекс за равен
        draw_index = 1 - abs(home_index - away_index) * 0.5

        # Нормализиране до 100%
        total = home_index + draw_index + away_index
        home_prob = round((home_index / total) * 100)
        draw_prob = round((draw_index / total) * 100)
        away_prob = round((away_index / total) * 100)

        # Корекция за закръгляне
        total_prob = home_prob + draw_prob + away_prob
        if total_prob != 100:
            diff = 100 - total_prob
            home_prob += diff

        return {
            'home_win': home_prob,
            'draw': draw_prob,
            'away_win': away_prob,
            'home_team': team1_name,
            'away_team': team2_name,
            'home_form': round(team1_form['form_score'] * 100),
            'away_form': round(team2_form['form_score'] * 100),
            'home_standing': team1_standing['position'] if team1_standing else '?',
            'away_standing': team2_standing['position'] if team2_standing else '?'
        }, None
