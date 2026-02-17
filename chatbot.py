import json
import re
from club import add_club, get_all_clubs, delete_club


with open("src/intents.json", encoding="utf-8") as f:
    intents = json.load(f)


def parse_input(user_input):
    user_input = user_input.lower()

    for intent, data in intents.items():
        for pattern in data["patterns"]:
            match = re.match(pattern, user_input)
            if match:
                return intent, match.groups()

    return None, None


def handle_intent(intent, params):
    if intent == "help":
        return """
Команди:
- Добави клуб Име
- Покажи всички клубове
- Изтрий клуб Име
- помощ
- изход
"""

    if intent == "add_club":
        return add_club(params[0])

    if intent == "list_clubs":
        return get_all_clubs()

    if intent == "delete_club":
        return delete_club(params[0])

    if intent == "exit":
        return "exit"

    return "Не разбирам командата."
