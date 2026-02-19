PRAGMA foreign_keys = ON;

CREATE TABLE clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    city TEXT,
    founded_year INTEGER
);


CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth_date TEXT,
    nationality TEXT,
    position TEXT CHECK(position IN ('GK','DF','MF','FW')),
    number INTEGER,
    club_id INTEGER,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);


CREATE TABLE transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    from_club_id INTEGER,
    to_club_id INTEGER,
    transfer_date TEXT,
    fee REAL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (from_club_id) REFERENCES clubs(id),
    FOREIGN KEY (to_club_id) REFERENCES clubs(id)
);


CREATE TABLE leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    season TEXT NOT NULL
);


CREATE TABLE league_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER,
    club_id INTEGER,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);


CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    match_date TEXT,
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    FOREIGN KEY (home_team_id) REFERENCES clubs(id),
    FOREIGN KEY (away_team_id) REFERENCES clubs(id)
);


CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    player_id INTEGER,
    minute INTEGER,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);


CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    player_id INTEGER,
    card_type TEXT CHECK(card_type IN ('yellow','red')),
    minute INTEGER,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

INSERT INTO clubs (name, city, founded_year) VALUES
('Левски', 'София', 1914),
('Ботев', 'Пловдив', 1912),
('Лудогорец', 'Разград', 2001),
('ЦСКА', 'София', 1948),
('Берое', 'Стара Загора', 1924);


INSERT INTO players (name, birth_date, nationality, position, number, club_id) VALUES
('Иван Петров', '2000-05-12', 'България', 'FW', 9, 1),
('Георги Иванов', '1998-03-20', 'България', 'MF', 8, 1),
('Марин Димитров', '1999-07-10', 'България', 'DF', 5, 2),
('Петър Стоянов', '2001-01-15', 'България', 'GK', 3, 3),
('Александър Георгиев', '1997-11-05', 'България', 'MF', 10, 4),
('Димитър Тодоров', '2000-08-20', 'България', 'FW', 11, 5),
('Николай Костов', '2001-02-14', 'България', 'DF', 4, 5),
('Стефан Илиев', '1999-12-12', 'България', 'FW', 7, 2),
('Христо Димитров', '2002-06-30', 'България', 'GK', 1, 4),
('Пламен Петров', '2000-04-17', 'България', 'MF', 6, 3);


INSERT INTO leagues (name, season) VALUES
('Първа лига', '2025/2026'),
('Втора лига', '2025/2026');

INSERT INTO league_teams (league_id, club_id) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5);

INSERT INTO matches (league_id, home_team_id, away_team_id, match_date, home_goals, away_goals) VALUES
(1, 1, 2, '2025-09-01', 3, 1),
(1, 3, 5, '2025-09-02', 2, 2),
(1, 4, 1, '2025-09-03', 1, 0);

INSERT INTO goals (match_id, player_id, minute) VALUES
(1, 1, 23),
(1, 1, 55),
(1, 2, 78),
(1, 3, 60),
(2, 6, 12),
(2, 7, 35),
(2, 3, 50),
(2, 5, 75),
(3, 5, 20);


INSERT INTO cards (match_id, player_id, card_type, minute) VALUES
(1, 3, 'yellow', 30),
(1, 2, 'yellow', 70),
(2, 6, 'red', 80),
(2, 7, 'yellow', 40),
(3, 1, 'yellow', 55);


INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee) VALUES
(1, 1, 3, '2026-01-10', 500000),
(6, 5, 2, '2026-02-01', 200000),
(8, 2, 4, '2026-03-15', 150000);



