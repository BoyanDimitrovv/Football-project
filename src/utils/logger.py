import logging
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent.parent.parent / "commands.log"

# Конфигурация на логване
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        #logging.StreamHandler()
    ]
)

def log_command(user_input, intent, params, result, status="OK"):
    """
    Записва команда в лог файла с всички детайли
    изискване: timestamp, raw input, intent, params, резултат
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params_str = json.dumps(params, ensure_ascii=False)[:100]  # съкратено
    result_preview = result[:100] if result else ""
    
    message = (f"TIMESTAMP: {timestamp} | "
               f"INPUT: '{user_input}' | "
               f"INTENT: {intent} | "
               f"PARAMS: {params_str} | "
               f"STATUS: {status} | "
               f"RESULT: {result_preview}")
    
    if status == "OK":
        logging.info(message)
    else:
        logging.error(message)

def log_error(error_msg, command=None):
    """Записва грешка в лог файла"""
    if command:
        logging.error(f"ERROR: {error_msg} | COMMAND: {command}")
    else:
        logging.error(f"ERROR: {error_msg}")
