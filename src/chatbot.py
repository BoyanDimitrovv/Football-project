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
        
        return base_response
