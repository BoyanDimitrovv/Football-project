from chatbot import parse_input, handle_intent
from datetime import datetime

LOG_FILE = "commands.log"
def log_command(user_input, response):

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {user_input} | {response}\n")

def main():
    print("⚽ Football Chatbot стартиран!")
    print("Напиши 'помощ' за списък с команди.")

    while True:
        user_input = input(">> ")

        intent, params = parse_input(user_input)

        response = handle_intent(intent, params)

        print(response)

        log_command(user_input, response)

        if response == "exit":
            print("Довиждане!")
            break

if __name__ == "__main__":
    main()
