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

BUCKET_RANGES = {"loved": (7.0, 10.0), "fine": (4.0, 7.0), "disliked": (0.0, 4.0)}
BUCKET_ORDER = ["loved", "fine", "disliked"]

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

def score_for(bucket, position, count):
    """
    Return the score out of 10 for a movie at 'position' in a bucket of 'count'movies.
    Posiiton 0 (best) gets bucket's highest score, and each lower position
    gets little less. Round to 1 decimal. 
    """
    low, high = BUCKET_RANGES[bucket]

    score = high - (high - low) * position / count

    return round(score, 1)


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
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return new_id


def get_user_by_username(username):
    """
    Return the user row (acts like a dict with id, username, password_hash)
    or None if no user has that username.
    """
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


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
    conn = get_connection()
    conn.execute(
        "UPDATE log_entries SET position = position + 1 " 
        "WHERE user_id = ? AND bucket = ? AND position >= ?",
        (user_id, movie["bucket"], movie["position"])
    )

    conn.execute(
    "INSERT INTO log_entries (user_id, tmdb_id, title, year, bucket, position, my_rating, "
    "date_watched, notes, runtime, genres, cast_members, director, keywords, poster_path) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (
        user_id,
        movie["tmdb_id"],
        movie["title"],
        movie["year"],
        movie["bucket"],
        movie["position"],
        movie.get("my_rating"),
        movie["date_watched"],
        movie["notes"],
        movie["runtime"],
        json.dumps(movie["genres"]),
        json.dumps(movie["cast"]),
        movie["director"],
        json.dumps(movie["keywords"]),
        movie["poster_path"],
    )
)
    conn.commit()
    conn.close()


def row_to_movie(row):
    """
    Turn one database row back into a normal movie dictionary:
    dict(row), then json.loads() the genres, cast, and keywords fields.

    Lets recommender code work unchanged!
    """
    movie = dict(row)
    movie["genres"] = json.loads(movie["genres"])
    movie["keywords"] = json.loads(movie["keywords"])
    movie["cast"] = json.loads(movie.pop("cast_members"))
    return movie

def get_bucket(user_id, bucket):
    """
    Return user's movies in one bucket ("loved", "fine", "disliked")
    as movie dictionaries, best first.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM log_entries WHERE user_id = ? AND bucket = ? ORDER BY position",
        (user_id, bucket)
    ).fetchall()

    conn.close()

    movies = []
    for r in rows:
        movies.append(row_to_movie(r))
    return movies

def get_log(user_id):
    """
    Return a list of movie dictionaries for this user (use row_to_movie on each row),
    newest first (ORDER BY date_watched DESC).
    """
    log = []
    for bucket in BUCKET_ORDER:
        movies = get_bucket(user_id, bucket)
        for movie in movies:
            movie["rating"] = score_for(bucket, movie["position"], len(movies))
        log += movies
    return log


def get_log_entry(user_id, tmdb_id):
    """
    Return this user's entry for a given TMDB movie as a dictionary,
    or None if they haven't logged it. (Used to show "Already logged".)
    """
    for movie in get_log(user_id):
        if movie["tmdb_id"] == tmdb_id:
            return movie
    return None


def delete_log_entry(user_id, entry_id):
    """
    Delete the entry with this id, but only if it belongs to user_id.

    DELETE FROM log_entries WHERE id = ? AND user_id = ?
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT bucket, position FROM log_entries WHERE id = ? AND user_id = ?",
        (entry_id, user_id)
    ).fetchone()

    if row is None:
        conn.close()
        return

    conn.execute(
    "DELETE FROM log_entries WHERE id = ? AND user_id = ?",
    (entry_id, user_id)
)
    conn.execute(
    "UPDATE log_entries SET position = position - 1 "
    "WHERE user_id = ? AND bucket = ? AND position > ?",
    (user_id, row["bucket"], row["position"])
)
    conn.commit()
    conn.close()

def add_to_watchlist(user_id, movie):
    """Save a movie to the user's watchlist. Does nothing if it's already there."""
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO watchlist (user_id, tmdb_id, title, year, poster_path) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, movie["id"], movie["title"], movie["year"], movie["poster_path"])
    )
    conn.commit()
    conn.close()

def remove_from_watchlist(user_id, tmdb_id):
    """Remove a movie from the user's watchlist (if it's there)."""
    conn = get_connection()
    conn.execute(
        "DELETE FROM watchlist WHERE user_id = ? AND tmdb_id = ?",
        (user_id, tmdb_id)
    )

    conn.commit()
    conn.close()

def get_watchlist(user_id):
    """Return the user's watchlist as a list of dictionaries, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_on DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def is_on_watchlist(user_id, tmdb_id):
    """Return True if this movie is on the user's watchlist, otherwise False."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM watchlist WHERE user_id = ? AND tmdb_id = ?",
        (user_id, tmdb_id)
    ).fetchone()

    conn.close()

    return row is not None
