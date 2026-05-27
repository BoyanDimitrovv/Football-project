import sqlite3
import os

# Път до базата
db_path = os.path.join(os.path.dirname(__file__), 'clubs.db')

print(f"Свързване с база: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Проверка дали таблицата matches съществува
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
if not cursor.fetchone():
    print("❌ Таблицата matches не съществува!")
    print("Първо създайте лига и генерирайте програма в чатбота.")
    conn.close()
    exit()

# Добавяне на колона status
try:
    cursor.execute('ALTER TABLE matches ADD COLUMN status TEXT DEFAULT "scheduled"')
    print("✅ Колона status е добавена успешно!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Колона status вече съществува")
    else:
        print(f"❌ Грешка: {e}")

# Обновяване на статуса за мачове с резултати
cursor.execute('UPDATE matches SET status = "played" WHERE home_goals IS NOT NULL AND home_goals > 0')
print(f"✅ Обновени мачове с резултати")

# Проверка
cursor.execute("PRAGMA table_info(matches)")
columns = [row[1] for row in cursor.fetchall()]
print(f"Колони в matches: {columns}")

conn.commit()
conn.close()

print("\n✅ Готово! Грешката 'no such column: status' НЯМА да се появи повече.")
print("👉 Сега рестартирайте чатбота: python src/main.py")
