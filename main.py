import logging
import datetime
from pathlib import Path
from db import init_database
from chatbot import ChatBot

# Конфигурация на logging
LOG_FILE = Path(__file__).parent.parent / "commands.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    """Основна функция за стартиране на чатбота"""
    
    print("=" * 50)
    print("🏆 Чатбот за управление на клубове 🏆")
    print("=" * 50)
    print("Въведете 'помощ' за списък с команди")
    print("Въведете 'изход' за край на програмата")
    print("-" * 50)
    
    try:
        # Инициализиране на базата данни
        init_database()
        logging.info("Базата данни е инициализирана")
        
        # Създаване на чатбот
        chatbot = ChatBot()
        
        # Главен цикъл
        while True:
            try:
                # Вход от потребителя
                user_input = input("\n👤 Вие: ").strip()
                
                if not user_input:
                    continue
                
                # Обработка на командата
                response = chatbot.process_command(user_input)
                
                # Логване на командата
                logging.info(f"COMMAND: '{user_input}' -> RESPONSE: '{response[:50]}...'")
                
                # Показване на отговора
                print(f"🤖 Бот: {response}")
                
                # Проверка за изход
                if user_input.lower() in ['изход', 'exit', 'quit', 'край']:
                    break
                    
            except KeyboardInterrupt:
                print("\n🤖 Бот: Довиждане! 👋")
                break
            except Exception as e:
                logging.error(f"Грешка при обработка: {e}")
                print(f"🤖 Бот: ❗ Възникна грешка: {e}")
    
    except Exception as e:
        logging.error(f"Грешка при стартиране: {e}")
        print(f"❌ Грешка при стартиране: {e}")

if __name__ == "__main__":
    main()
