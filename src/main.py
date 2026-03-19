import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.database.db import init_database
from src.chatbot.nlu import NLU
from src.chatbot.router import Router

def main():
    print("=" * 60)
    print("🏆 ЧАТБОТ ЗА УПРАВЛЕНИЕ НА ТРАНСФЕРИ 🏆")
    print("=" * 60)
    print("Въведете 'помощ' за списък с команди")
    print("Въведете 'изход' за край на програмата")
    print("-" * 60)
    
    try:
        # Инициализиране на базата
        init_database()
        
        # Създаване на компоненти
        nlu = NLU()
        router = Router()
        
        # Главен цикъл
        while True:
            try:
                user_input = input("\n👤 Вие: ").strip()
                
                if not user_input:
                    continue
                
                # Разпознаване на intent
                parse_result = nlu.parse(user_input)
                
                # Изпълнение на командата
                response = router.route(
                    parse_result['intent'], 
                    parse_result['params'], 
                    user_input
                )
                
                # Показване на отговора
                print(f"🤖 Бот: {response}")
                
                if parse_result['intent'] == 'exit':
                    break
                    
            except KeyboardInterrupt:
                print("\n🤖 Бот: Довиждане! 👋")
                break
            except Exception as e:
                print(f"🤖 Бот: ❗ Възникна грешка: {e}")
    
    except Exception as e:
        print(f"❌ Грешка при стартиране: {e}")

if __name__ == "__main__":
    main()
