"""
NLU (Natural Language Understanding) - ЕТАП 6
"""

import re

class NLU:

    def parse(self, text):
        text_lower = text.lower().strip()

        # ПОМОЩ
        if any(word in text_lower for word in ['помощ', 'help', 'команди']):
            return {'intent': 'help', 'params': {}}

        # ИЗХОД
        if any(word in text_lower for word in ['изход', 'exit', 'край', 'quit']):
            return {'intent': 'exit', 'params': {}}

        # ДОБАВИ КЛУБ
        add_club_match = re.search(r'добави клуб (.+)', text_lower)
        if add_club_match:
            return {'intent': 'add_club', 'params': {'club': add_club_match.group(1).strip()}}

        # ПОКАЖИ КЛУБОВЕ
        if any(phrase in text_lower for phrase in ['покажи клубове', 'клубове', 'всички клубове']):
            return {'intent': 'list_clubs', 'params': {}}

        # ПОКАЖИ ИГРАЧИ
        players_match = re.search(r'покажи играчи на (.+)', text_lower)
        if players_match:
            return {'intent': 'list_players', 'params': {'club': players_match.group(1).strip()}}

        # ТРАНСФЕРИ
        transfer_patterns = [
            r'трансфер (.+?) от (.+?) в (.+?) (\d{4}-\d{2}-\d{2}) сума (\d+(?:\.\d+)?)',
            r'трансфер (.+?) от (.+?) в (.+?) (\d{4}-\d{2}-\d{2})'
        ]

        for pattern in transfer_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                params = {
                    'player': groups[0].strip(),
                    'from_club': groups[1].strip(),
                    'to_club': groups[2].strip(),
                    'date': groups[3].strip()
                }
                if len(groups) > 4 and groups[4]:
                    params['fee'] = groups[4].strip()
                return {'intent': 'transfer_player', 'params': params}

        # ПОКАЖИ ТРАНСФЕРИ
        player_match = re.search(r'покажи трансфери на (.+)', text_lower)
        if player_match and 'клуб' not in text_lower:
            return {'intent': 'show_transfers_player', 'params': {'player': player_match.group(1).strip()}}

        club_match = re.search(r'покажи трансфери на клуб (.+)', text_lower)
        if club_match:
            return {'intent': 'show_transfers_club', 'params': {'club': club_match.group(1).strip()}}

        # ЛИГИ
        create_league_match = re.search(r'създай лига (.+?) (\d{4}/\d{4})', text_lower)
        if create_league_match:
            return {
                'intent': 'create_league',
                'params': {
                    'name': create_league_match.group(1).strip(),
                    'season': create_league_match.group(2).strip()
                }
            }

        add_team_match = re.search(r'добави отбор (.+?) в лига (.+?) (\d{4}/\d{4})', text_lower)
        if add_team_match:
            return {
                'intent': 'add_team_to_league',
                'params': {
                    'club': add_team_match.group(1).strip(),
                    'league_name': add_team_match.group(2).strip(),
                    'season': add_team_match.group(3).strip()
                }
            }

        show_teams_match = re.search(r'покажи отбори в лига (.+?) (\d{4}/\d{4})', text_lower)
        if show_teams_match:
            return {
                'intent': 'show_teams_in_league',
                'params': {
                    'league_name': show_teams_match.group(1).strip(),
                    'season': show_teams_match.group(2).strip()
                }
            }

        generate_fixture_match = re.search(r'генерирай програма (.+?) (\d{4}/\d{4})', text_lower)
        if generate_fixture_match:
            return {
                'intent': 'generate_fixture',
                'params': {
                    'league_name': generate_fixture_match.group(1).strip(),
                    'season': generate_fixture_match.group(2).strip()
                }
            }

        show_fixture_match = re.search(r'покажи програма (.+?) (\d{4}/\d{4})', text_lower)
        if show_fixture_match:
            return {
                'intent': 'show_fixture',
                'params': {
                    'league_name': show_fixture_match.group(1).strip(),
                    'season': show_fixture_match.group(2).strip()
                }
            }

        # МАЧОВЕ
        show_round_match = re.search(r'покажи кръг (\d+) (.+?) (\d{4}/\d{4})', text_lower)
        if show_round_match:
            return {
                'intent': 'show_round',
                'params': {
                    'round_no': show_round_match.group(1).strip(),
                    'league_name': show_round_match.group(2).strip(),
                    'season': show_round_match.group(3).strip()
                }
            }

        select_match = re.search(r'избери мач (\d+)', text_lower)
        if select_match:
            return {
                'intent': 'select_match',
                'params': {'match_id': select_match.group(1).strip()}
            }

        result_match = re.search(r'резултат (.+?)-(.+?) (\d+):(\d+) запиши', text_lower)
        if result_match:
            return {
                'intent': 'set_result',
                'params': {
                    'home_team': result_match.group(1).strip(),
                    'away_team': result_match.group(2).strip(),
                    'home_goals': result_match.group(3).strip(),
                    'away_goals': result_match.group(4).strip()
                }
            }

        # ГОЛ - формат: гол [ИГРАЧ] за [КЛУБ] в [МИНУТА] минута
        goal_match = re.search(r'гол (.+?) за (.+?) в (\d+) минута', text_lower)
        if goal_match:
            return {
                'intent': 'add_goal',
                'params': {
                    'player': goal_match.group(1).strip(),
                    'club': goal_match.group(2).strip(),
                    'minute': goal_match.group(3).strip()
                }
            }

        # КАРТОН - формат: картон [ИГРАЧ] [КЛУБ] [Y/R] [МИНУТА]
        card_match = re.search(r'картон (.+?) (.+?) ([YR]) (\d+)', text_lower)
        if card_match:
            return {
                'intent': 'add_card',
                'params': {
                    'player': card_match.group(1).strip(),
                    'club': card_match.group(2).strip(),
                    'card_type': card_match.group(3).strip(),
                    'minute': card_match.group(4).strip()
                }
            }

        # КАРТОН - опростен формат: картон [ИГРАЧ] [Y/R] [МИНУТА]
        card_match_simple = re.search(r'картон (.+?) ([YR]) (\d+)', text_lower, re.IGNORECASE)
        if card_match_simple:
            return {
                'intent': 'add_card_simple',
                'params': {
                    'player': card_match_simple.group(1).strip(),
                    'card_type': card_match_simple.group(2).strip().upper(),
                    'minute': card_match_simple.group(3).strip()
                }
            }
        # КАРТОН - формат: картон [ИГРАЧ] за [КЛУБ] [Y/R] в [МИНУТА]
        card_match_with_prepositions = re.search(r'картон (.+?) за (.+?) ([YR]) в (\d+)', text_lower, re.IGNORECASE)
        if card_match_with_prepositions:
            return {
                'intent': 'add_card',
                'params': {
                    'player': card_match_with_prepositions.group(1).strip(),
                    'club': card_match_with_prepositions.group(2).strip(),
                    'card_type': card_match_with_prepositions.group(3).strip().upper(),
                    'minute': card_match_with_prepositions.group(4).strip()
                }
            }
        # ============================================================
        # ЕТАП 7 - КЛАСИРАНЕ
        # ============================================================

        # Покажи класиране
        standings_match = re.search(r'покажи класиране (.+?) (\d{4}/\d{4})', text_lower)
        if standings_match:
            return {
                'intent': 'show_standings',
                'params': {
                    'league_name': standings_match.group(1).strip(),
                    'season': standings_match.group(2).strip()
                }
            }

        # Обнови класиране (препоръчително)
        if text_lower == 'обнови класиране':
            return {'intent': 'refresh_standings', 'params': {}}

        # ПОКАЖИ СЪБИТИЯ
        if 'покажи събития' in text_lower:
            show_events_match = re.search(r'покажи събития (\d+)', text_lower)
            if show_events_match:
                return {
                    'intent': 'show_events',
                    'params': {'match_id': show_events_match.group(1).strip()}
                }
            return {'intent': 'show_events', 'params': {}}

        return {'intent': 'unknown', 'params': {}}
