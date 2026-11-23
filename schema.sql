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

-- TODO: write the log_entries table yourself, following the pattern above.
-- It needs these columns:
--   id            (same as users.id)
--   user_id       INTEGER NOT NULL, the user this entry belongs to
--   tmdb_id       INTEGER
--   title         TEXT NOT NULL
--   year          INTEGER
--   rating        INTEGER, the user's 1-10 rating
--   date_watched  TEXT, e.g. '2026-11-22'
--   notes         TEXT
--   runtime       INTEGER
--   genres        TEXT, a JSON list, e.g. '["Action", "Sci-Fi"]'
--   cast_members  TEXT, a JSON list ("cast" is a reserved word in SQL!)
--   director      TEXT
--   keywords      TEXT, a JSON list
--   poster_path   TEXT
--
-- At the end, add:  FOREIGN KEY (user_id) REFERENCES users(id)
-- (This tells the database each entry must belong to a real user.)
--
-- Watch out: the column is cast_members but your dictionaries use "cast",
-- so translate between them in db.py.
