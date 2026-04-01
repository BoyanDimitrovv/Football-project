"""
MAIN - ЕТАП 4
"""

import sys
from pathlib import Path

# Добавяне на src към пътя - ТОВА Е КЛЮЧОВО!
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from database.db import init_database
from chatbot.nlu import NLU
from chatbot.router import Router


def main():
    print("=" * 60)
    print("🏆 ЧАТБОТ ЗА УПРАВЛЕНИЕ НА ТРАНСФЕРИ 🏆")
    print("=" * 60)
    print("Въведете 'помощ' за списък с команди")
    print("Въведете 'изход' за край на програмата")
    print("-" * 60)

    try:
        init_database()

        nlu = NLU()
        router = Router()

        while True:
            try:
                user_input = input("\n👤 Вие: ").strip()

                if not user_input:
                    continue

                parse_result = nlu.parse(user_input)
                response = router.route(
                    parse_result['intent'],
                    parse_result['params'],
                    user_input
                )

                print(f"🤖 Бот: {response}")

                if parse_result['intent'] == 'exit':
                    break

            except KeyboardInterrupt:
                print("\n🤖 Бот: Довиждане! 👋")
                break
            except Exception as e:
                print(f"🤖 Бот: ❗ Грешка: {e}")

    except Exception as e:
        print(f"❌ Грешка: {e}")


if __name__ == "__main__":
    main()
