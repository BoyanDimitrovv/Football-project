import re

class NLU:
    """Клас за разпознаване на команди и извличане на параметри"""
    
    def parse(self, text):
        """
        Разпознава intent и параметри от текста
        
        Args:
            text (str): Входният текст от потребителя
            
        Returns:
            dict: {'intent': 'име_на_intent', 'params': {...}}
        """
        text_lower = text.lower().strip()
        
        # ----- ПОМОЩ -----
        if any(word in text_lower for word in ['помощ', 'help', 'команди']):
            return {'intent': 'help', 'params': {}}
        
        # ----- ИЗХОД -----
        if any(word in text_lower for word in ['изход', 'exit', 'край', 'quit']):
            return {'intent': 'exit', 'params': {}}
        
        # ----- 🔄 ТРАНСФЕР (с опционална сума) -----
        # Формат 1: трансфер ИМЕ от КЛУБ в КЛУБ ДАТА
        # Формат 2: трансфер ИМЕ от КЛУБ в КЛУБ ДАТА сума ЧИСЛО
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
                # Ако има сума (група 5)
                if len(groups) > 4 and groups[4]:
                    params['fee'] = groups[4].strip()
                
                return {'intent': 'transfer_player', 'params': params}
        
        # ----- 🔄 ПОКАЖИ ТРАНСФЕРИ НА ИГРАЧ -----
        # Формат: покажи трансфери на ИМЕ
        player_match = re.search(r'покажи трансфери на (.+)', text_lower)
        if player_match and 'клуб' not in text_lower:
            return {
                'intent': 'show_transfers_player',
                'params': {'player': player_match.group(1).strip()}
            }
        
        # ----- 🔄 ПОКАЖИ ТРАНСФЕРИ НА КЛУБ -----
        # Формат: покажи трансфери на клуб ИМЕ
        club_match = re.search(r'покажи трансфери на клуб (.+)', text_lower)
        if club_match:
            return {
                'intent': 'show_transfers_club',
                'params': {'club': club_match.group(1).strip()}
            }
        
        # ----- ⚽ ПОКАЖИ ИГРАЧИ НА КЛУБ (от Етап 3) -----
        # Формат: покажи играчи на КЛУБ
        players_match = re.search(r'покажи играчи на (.+)', text_lower)
        if players_match:
            return {
                'intent': 'list_players',
                'params': {'club': players_match.group(1).strip()}
            }
        
        # ----- 🏆 ПОКАЖИ КЛУБОВЕ (от Етап 2) -----
        if any(phrase in text_lower for phrase in ['покажи клубове', 'клубове', 'всички клубове']):
            return {'intent': 'list_clubs', 'params': {}}
        
        # ----- 🏆 ДОБАВИ КЛУБ (от Етап 2) -----
        # Формат: добави клуб ИМЕ
        add_club_match = re.search(r'добави клуб (.+)', text_lower)
        if add_club_match:
            return {
                'intent': 'add_club',
                'params': {'club': add_club_match.group(1).strip()}
            }
        
        # ----- ❓ НЕПОЗНАТА КОМАНДА -----
        return {'intent': 'unknown', 'params': {}}
    
    def _extract_transfer_params(self, text):
        """Помощен метод за извличане на параметри за трансфер"""
        # Може да добавите допълнителна логика тук
        pass
