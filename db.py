"""
db.py: every function that touches the database lives here.

We use SQLite: the whole database is one file (movielog.db), and Python
has the sqlite3 module built in, so there's nothing to install.

Key idea: the rest of the app never writes SQL. It just calls these functions.

Lists (genres, cast, keywords) can't go in a SQLite column directly,
so store them as JSON text with json.dumps() and turn them back with json.loads().
"""

import json
import sqlite3

DB_FILE = "movielog.db"


def get_connection():
    """
    Open the database and return the connection. (Already done for you.)
    row_factory makes each row act like a dictionary: row["title"]
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the tables by running schema.sql. Safe to run more than once.
    (Already done for you. Run it once with:  python -c "import db; db.init_db()")
    """
    with open("schema.sql") as f:
        conn = get_connection()
        conn.executescript(f.read())
        conn.commit()
        conn.close()


# =============================================================================
# PART 16: Users
# =============================================================================

def create_user(username, password_hash):
    """
    Insert a new user and return their new id.

    Hints:
      - Use ? placeholders, NEVER f-strings, to put values into SQL:
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                         (username, password_hash))
        (Placeholders protect against "SQL injection" attacks. Worth looking up!)
      - cursor.lastrowid gives the new id.
      - Remember conn.commit() after any change, then conn.close().
    """
    # TODO
    pass


def get_user_by_username(username):
    """
    Return the user row (acts like a dict with id, username, password_hash)
    or None if no user has that username.

    Hint: conn.execute(...).fetchone()
    """
    # TODO
    pass


# =============================================================================
# PART 16: Log entries
# =============================================================================

def add_log_entry(user_id, movie):
    """
    Insert one movie into the user's log.
    `movie` is the same dictionary your terminal version builds:
        title, year, rating, date_watched, notes,
        tmdb_id, genres, runtime, cast, director, keywords, poster_path

    Convert the list fields with json.dumps() before inserting.
    """
    # TODO
    pass


def row_to_movie(row):
    """
    Turn one database row back into a normal movie dictionary:
    dict(row), then json.loads() the genres, cast, and keywords fields.

    This is what lets your recommender code work unchanged!
    """
    # TODO
    pass


def get_log(user_id):
    """
    Return a list of movie dictionaries for this user (use row_to_movie on each row),
    newest first (ORDER BY date_watched DESC).
    """
    # TODO
    pass


def get_log_entry(user_id, tmdb_id):
    """
    Return this user's entry for a given TMDB movie as a dictionary,
    or None if they haven't logged it. (Used to show "Already logged".)
    """
    # TODO
    pass


def delete_log_entry(user_id, entry_id):
    """
    Delete the entry with this id, but only if it belongs to user_id.

    Hint: DELETE FROM log_entries WHERE id = ? AND user_id = ?
    """
    # TODO
    pass
