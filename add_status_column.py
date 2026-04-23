import sqlite3

conn = sqlite3.connect('clubs.db')
cursor = conn.cursor()

# Добавяне на колона status
cursor.execute('ALTER TABLE matches ADD COLUMN status TEXT DEFAULT "scheduled"')
print("✅ Колона status е добавена")

# Обновяване на съществуващите мачове с резултати
cursor.execute('UPDATE matches SET status = "played" WHERE home_goals IS NOT NULL AND home_goals > 0')
print(f"✅ Обновени мачове")

conn.commit()
conn.close()

print("\nГотово! Сега стартирайте main.py")
