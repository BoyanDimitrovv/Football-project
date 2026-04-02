-- ============================================================
-- ФУТБОЛЕН ЧАТБОТ - ПЪЛНА БАЗА ДАННИ
-- ЕТАП 1-5: Клубове, Играчи, Трансфери, Лиги, Мачове
-- ============================================================

-- ============================================================
-- ЕТАП 1-2: КЛУБОВЕ
-- ============================================================
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ЕТАП 3: ИГРАЧИ
-- ============================================================
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER,
    full_name TEXT NOT NULL UNIQUE,
    birth_date TEXT NOT NULL,
    nationality TEXT NOT NULL,
    position TEXT NOT NULL CHECK(position IN ('GK', 'DF', 'MF', 'FW')),
    number INTEGER CHECK(number BETWEEN 1 AND 99),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'injured', 'suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs (id) ON DELETE SET NULL
);

-- ============================================================
-- ЕТАП 4: ТРАНСФЕРИ
-- ============================================================
CREATE TABLE IF NOT EXISTS transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    from_club_id INTEGER,
    to_club_id INTEGER NOT NULL,
    transfer_date TEXT NOT NULL,
    fee REAL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE,
    FOREIGN KEY (from_club_id) REFERENCES clubs (id) ON DELETE SET NULL,
    FOREIGN KEY (to_club_id) REFERENCES clubs (id) ON DELETE CASCADE,
    CHECK (to_club_id != from_club_id OR from_club_id IS NULL)
);

-- ============================================================
-- ЕТАП 5: ЛИГИ, ОТБОРИ В ЛИГИ, МАЧОВЕ
-- ============================================================

-- Таблица за лиги
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    season TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, season)
);

-- Таблица за отбори в лиги
CREATE TABLE IF NOT EXISTS league_teams (
    league_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (league_id, club_id),
    FOREIGN KEY (league_id) REFERENCES leagues (id) ON DELETE CASCADE,
    FOREIGN KEY (club_id) REFERENCES clubs (id) ON DELETE CASCADE
);

-- Таблица за мачове
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    round_no INTEGER NOT NULL,
    home_club_id INTEGER NOT NULL,
    away_club_id INTEGER NOT NULL,
    match_date TEXT,
    home_goals INTEGER,
    away_goals INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (league_id) REFERENCES leagues (id) ON DELETE CASCADE,
    FOREIGN KEY (home_club_id) REFERENCES clubs (id) ON DELETE CASCADE,
    FOREIGN KEY (away_club_id) REFERENCES clubs (id) ON DELETE CASCADE,
    CHECK (home_club_id != away_club_id)
);

-- ============================================================
-- ИНДЕКСИ ЗА БЪРЗО ТЪРСЕНЕ
-- ============================================================

-- Индекси за клубове и играчи
CREATE INDEX IF NOT EXISTS idx_players_name ON players(full_name);
CREATE INDEX IF NOT EXISTS idx_players_club ON players(club_id);

-- Индекси за трансфери
CREATE INDEX IF NOT EXISTS idx_transfers_player ON transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_from_club ON transfers(from_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to_club ON transfers(to_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(transfer_date);

-- Индекси за лиги и мачове
CREATE INDEX IF NOT EXISTS idx_league_teams_league ON league_teams(league_id);
CREATE INDEX IF NOT EXISTS idx_league_teams_club ON league_teams(club_id);
CREATE INDEX IF NOT EXISTS idx_matches_league ON matches(league_id);
CREATE INDEX IF NOT EXISTS idx_matches_round ON matches(round_no);
