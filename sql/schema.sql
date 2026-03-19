CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    CHECK (to_club_id != from_club_id OR from_club_id IS NULL),
    CHECK (transfer_date LIKE '____-__-__')
);

CREATE INDEX idx_players_name ON players(full_name);
CREATE INDEX idx_players_club ON players(club_id);
CREATE INDEX idx_transfers_player ON transfers(player_id);
CREATE INDEX idx_transfers_from_club ON transfers(from_club_id);
CREATE INDEX idx_transfers_to_club ON transfers(to_club_id);
CREATE INDEX idx_transfers_date ON transfers(transfer_date);
