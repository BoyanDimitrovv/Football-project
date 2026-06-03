import sqlite3

conn = sqlite3.connect('clubs.db')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM matches WHERE status = 'played'")
count = c.fetchone()[0]
print(f"Изиграни мачове: {count}")

# Покажи кои са изиграните мачове
c.execute("SELECT m.id, h.name, a.name, m.home_goals, m.away_goals FROM matches m JOIN clubs h ON m.home_club_id = h.id JOIN clubs a ON m.away_club_id = a.id WHERE m.status = 'played'")
matches = c.fetchall()
for m in matches:
    print(f"  Мач {m[0]}: {m[1]} {m[3]}:{m[4]} {m[2]}")

conn.close()
