-- schema.sql: the shape of your database (PART 16)
--
-- A table is like a spreadsheet: each column has a name and a type.
-- SQLite types you need: INTEGER, TEXT, REAL (decimals)
--
-- "IF NOT EXISTS" means running this again won't wipe your data.

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS log_entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    tmdb_id      INTEGER,
    title        TEXT    NOT NULL,
    year         INTEGER,
    rating       INTEGER,
    date_watched TEXT,
    notes        TEXT,
    runtime      INTEGER,
    genres       TEXT,
    cast         TEXT,
    director     TEXT,
    keywords     TEXT,
    poster_path  TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

