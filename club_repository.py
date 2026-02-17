from db import execute, fetch_all, fetch_one
import sqlite3

def add_club(name, city=None):
    if not name or not name.strip():
        raise ValueError("Club name cannot be empty.")

    sql = "INSERT INTO clubs (name, city) VALUES (?, ?)"

    try:
        execute(sql, (name.strip(), city))
        row = fetch_one("SELECT last_insert_rowid()")
        return row[0]
    except sqlite3.IntegrityError:
        raise ValueError("Club with this name already exists.")

def list_clubs():
    sql = "SELECT club_id, name, city FROM clubs"
    return fetch_all(sql)

def get_club_by_id(club_id):
    sql = "SELECT club_id, name, city FROM clubs WHERE club_id = ?"
    return fetch_one(sql, (club_id,))

def update_club(club_id, name, city=None):
    if not name or not name.strip():
        raise ValueError("Club name cannot be empty.")

    sql = """
        UPDATE clubs
        SET name = ?, city = ?
        WHERE club_id = ?
    """

    try:
        affected = execute(sql, (name.strip(), city, club_id))
        if affected == 0:
            raise ValueError("Invalid club ID.")
        return affected
    except sqlite3.IntegrityError:
        raise ValueError("Club with this name already exists.")

def delete_club(club_id):
    sql = "DELETE FROM clubs WHERE club_id = ?"
    affected = execute(sql, (club_id,))
    if affected == 0:
        raise ValueError("Invalid club ID.")
    return affected
