import re
import json
import logging
from pathlib import Path
from clubs_service import ClubsService

class ChatBot:
    
    def __init__(self):
        self.intents = self.load_intents()
        self.clubs_service = ClubsService()
        
    def load_intents(self):
        """Зарежда intents от JSON файл"""
        intents_path = Path(__file__).parent / "intents.json"
        
        try:
            with open(intents_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['intents']
        except Exception as e:
            logging.error(f"Грешка при зареждане на intents: {e}")
            return []
    
    def match_intent(self, text):
        """Разпознава intent от текста чрез regex"""
        text = text.lower().strip()
        
        for intent in self.intents:
            for pattern in intent['patterns']:
                # Конвертиране на pattern към regex
                regex_pattern = pattern.replace('(.+)', '(.*)')
                regex_pattern = '^' + regex_pattern + '$'
                
                match = re.match(regex_pattern, text)
                if match:
                    groups = match.groups()
                    return intent['tag'], groups
        
        return "unknown", ()
    
    def process_command(self, user_input):
        """Обработва команда и връща отговор"""
        intent, params = self.match_intent(user_input)
        
        # Намиране на intent от JSON
        intent_data = next((i for i in self.intents if i['tag'] == intent), None)
        base_response = intent_data['responses'][0] if intent_data else "Не разбирам командата."
        
        # Обработка според типа intent
        if intent == "help":
            return base_response
        
        elif intent == "exit":
            return base_response
        
        elif intent == "add_club" and params:
            club_name = params[0].strip()
            return self.clubs_service.add_club(club_name)
        
        elif intent == "list_clubs":
            clubs = self.clubs_service.get_all_clubs()
            if not clubs:
                return "📋 Няма добавени клубове."
            
            response = base_response + "\n"
            for club in clubs:
                response += f"  🏆 {club['id']}. {club['name']}\n"
            return response
        
        elif intent == "delete_club" and params:
            club_identifier = params[0].strip()
            return self.clubs_service.delete_club(club_identifier)
        
        elif intent == "update_club" and len(params) >= 2:
            old_name = params[0].strip()
            new_name = params[1].strip()
            return self.clubs_service.update_club(old_name, new_name)
        
        elif intent == "unknown":
            return "❓ Не разбирам командата. Напишете 'помощ' за списък с команди."
        
        # Новите команди за играчи
        elif intent == "add_player" and len(params) >= 4:
            # Парсване на параметрите
            text = user_input.lower()
            # Пример: "добави играч Меси в Барселона позиция FW номер 10"
            match = re.search(r'добави играч (.+?) в (.+?) позиция (.+?) номер (\d+)', user_input.lower())
            if match:
                player_name = match.group(1).strip()
                club_name = match.group(2).strip()
                position = match.group(3).strip().upper()
                number = match.group(4).strip()
                
                # За демо, слагаме тестови данни
                from players_service import PlayersService
                return PlayersService.add_player(
                    club_name, 
                    player_name, 
                    "1995-03-15",  # Примерна дата
                    "България",     # Примерна националност
                    position, 
                    number
                )
            return "❌ Неправилен формат. Използвайте: добави играч [ИМЕ] в [КЛУБ] позиция [GK/DF/MF/FW] номер [1-99]"
        
        elif intent == "list_players" and params:
            club_name = params[0].strip()
            from players_service import PlayersService
            players, club = PlayersService.get_players_by_club(club_name)
            
            if players is None:
                return club  # това е съобщението за грешка
            
            if not players:
                return f"📋 Няма играчи в {club}"
            
            response = f"📋 Играчи на {club}:\n"
            position_emoji = {'GK': '🧤', 'DF': '🛡️', 'MF': '⚙️', 'FW': '⚽'}
            status_emoji = {'active': '✅', 'injured': '🤕', 'suspended': '⛔'}
            
            for p in players:
                response += f"  {position_emoji[p['position']]} {p['number']}. {p['full_name']} "
                response += f"({p['nationality']}) {status_emoji[p['status']]}\n"
            return response
        
        elif intent == "change_number" and len(params) >= 2:
            # Пример: "смени номер на Меси на 10" или "смени номер на Меси в Барселона на 10"
            text = user_input.lower()
            match = re.search(r'смени номер на (.+?)(?: в (.+?))? на (\d+)', user_input.lower())
            if match:
                player_name = match.group(1).strip()
                club_name = match.group(2).strip() if match.group(2) else None
                new_number = match.group(3).strip()
                
                from players_service import PlayersService
                return PlayersService.update_player_number(player_name, new_number, club_name)
            
        elif intent == "change_status" and len(params) >= 2:
            # Пример: "смени статус на Меси на injured"
            match = re.search(r'смени статус на (.+?)(?: в (.+?))? на (.+)', user_input.lower())
            if match:
                player_name = match.group(1).strip()
                club_name = match.group(2).strip() if match.group(2) else None
                new_status = match.group(3).strip().lower()
                
                from players_service import PlayersService
                return PlayersService.update_player_status(player_name, new_status, club_name)
        
        elif intent == "delete_player" and params:
            # Пример: "изтрий играч Меси" или "изтрий играч Меси от Барселона"
            text = user_input.lower()
            match = re.search(r'изтрий играч (.+?)(?: от (.+))?$', user_input.lower())
            if match:
                player_name = match.group(1).strip()
                club_name = match.group(2).strip() if match.group(2) else None
                
                from players_service import PlayersService
                return PlayersService.delete_player(player_name, club_name)
        return base_response
