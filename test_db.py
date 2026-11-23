"""
test_db.py: checks every Part 16 function in db.py.

Run with:  python test_db.py

It uses a separate test database (test_movielog.db), so your real
movielog.db is never touched. Each test prints PASS or FAIL with a hint.
Run it after each step: tests for functions you haven't written yet will fail,
and that's expected.
"""

import os
import db

db.DB_FILE = "test_movielog.db"          # use a throwaway database
if os.path.exists(db.DB_FILE):
    os.remove(db.DB_FILE)
db.init_db()

passed = 0
failed = 0


def check(name, condition, hint=""):
    global passed, failed
    if condition:
        print(f"  PASS  {name}")
        passed += 1
    else:
        print(f"  FAIL  {name}" + (f"\n        hint: {hint}" if hint else ""))
        failed += 1


def run(name, test):
    """Runs one group of tests; if the code crashes, shows the error instead of stopping."""
    print(f"\n{name}")
    try:
        test()
    except Exception as e:
        global failed
        failed += 1
        print(f"  FAIL  crashed: {type(e).__name__}: {e}")


def make_movie(title, tmdb_id, bucket, position):
    return {
        "tmdb_id": tmdb_id, "title": title, "year": 2010,
        "bucket": bucket, "position": position,
        "date_watched": "2026-11-23", "notes": "",
        "runtime": 120, "genres": ["Drama"], "cast": ["Someone"],
        "director": "A Director", "keywords": ["test"], "poster_path": "",
    }


# ---------------------------------------------------------------------------
def test_score():
    check("#1 of 1 loved = 10.0", db.score_for("loved", 0, 1) == 10.0,
          "top movie in a bucket should get the bucket's highest score")
    check("#1 of 3 loved = 10.0", db.score_for("loved", 0, 3) == 10.0)
    check("#2 of 3 loved = 9.0", db.score_for("loved", 1, 3) == 9.0,
          "high - (high - low) * position / count, rounded to 1 decimal")
    check("#3 of 3 loved = 8.0", db.score_for("loved", 2, 3) == 8.0)
    check("#1 of 2 fine = 7.0", db.score_for("fine", 0, 2) == 7.0)
    check("#2 of 2 disliked = 2.0", db.score_for("disliked", 1, 2) == 2.0)

run("16.2  score_for", test_score)


# ---------------------------------------------------------------------------
user_ids = {}

def test_users():
    a = db.create_user("alice", "hash-a")
    b = db.create_user("bob", "hash-b")
    user_ids["alice"], user_ids["bob"] = a, b
    check("create_user returns an id number", isinstance(a, int),
          "return cur.lastrowid")
    check("second user gets a different id", a != b)
    u = db.get_user_by_username("alice")
    check("get_user_by_username finds alice", u is not None and u["id"] == a,
          "SELECT * FROM users WHERE username = ?  then .fetchone()")
    check("unknown username returns None", db.get_user_by_username("nobody") is None)

run("16.3-16.4  users", test_users)


# ---------------------------------------------------------------------------
def test_add_and_read():
    a = user_ids["alice"]
    db.add_log_entry(a, make_movie("Inception", 1, "loved", 0))
    db.add_log_entry(a, make_movie("Interstellar", 2, "loved", 0))   # goes ABOVE Inception
    db.add_log_entry(a, make_movie("Tenet", 3, "loved", 2))          # goes at the bottom
    loved = db.get_bucket(a, "loved")
    titles = [m["title"] for m in loved]
    check("get_bucket returns 3 loved movies", len(loved) == 3)
    check("order is Interstellar, Inception, Tenet",
          titles == ["Interstellar", "Inception", "Tenet"],
          f"got {titles}. add_log_entry must shift positions >= new position down by 1 BEFORE inserting")
    check("positions are 0, 1, 2", [m["position"] for m in loved] == [0, 1, 2])
    check("genres comes back as a list", loved[0]["genres"] == ["Drama"],
          "use json.loads in row_to_movie")
    check("'cast' key exists (not cast_members)", "cast" in loved[0] and "cast_members" not in loved[0],
          "movie['cast'] = json.loads(movie.pop('cast_members'))")

run("16.5-16.7  add_log_entry / get_bucket / row_to_movie", test_add_and_read)


# ---------------------------------------------------------------------------
def test_get_log():
    a = user_ids["alice"]
    db.add_log_entry(a, make_movie("Cats", 4, "disliked", 0))
    db.add_log_entry(a, make_movie("Okay Movie", 5, "fine", 0))
    log = db.get_log(a)
    titles = [m["title"] for m in log]
    check("get_log returns all 5", len(log) == 5)
    check("ordered loved -> fine -> disliked",
          titles == ["Interstellar", "Inception", "Tenet", "Okay Movie", "Cats"],
          f"got {titles}")
    scores = [m.get("rating") for m in log]
    check("each movie has a 'rating' score", scores == [10.0, 9.0, 8.0, 7.0, 4.0],
          f"got {scores}. set movie['rating'] = score_for(bucket, position, count)")
    check("get_log_entry finds Tenet by tmdb_id",
          (db.get_log_entry(a, 3) or {}).get("title") == "Tenet")
    check("get_log_entry returns None if not logged", db.get_log_entry(a, 999) is None)

run("16.8-16.9  get_log / get_log_entry", test_get_log)


# ---------------------------------------------------------------------------
def test_delete_and_privacy():
    a, b = user_ids["alice"], user_ids["bob"]
    inception = db.get_log_entry(a, 1)
    db.delete_log_entry(b, inception["id"])            # bob tries to delete alice's movie
    check("other users can't delete your movies", db.get_log_entry(a, 1) is not None,
          "DELETE ... WHERE id = ? AND user_id = ?")
    db.delete_log_entry(a, inception["id"])
    loved = db.get_bucket(a, "loved")
    check("Inception deleted", [m["title"] for m in loved] == ["Interstellar", "Tenet"])
    check("positions close the gap (0, 1)", [m["position"] for m in loved] == [0, 1],
          "after deleting, shift positions > deleted position UP by 1")
    check("bob's log is empty", db.get_log(b) == [])

run("16.10  delete_log_entry", test_delete_and_privacy)


# ---------------------------------------------------------------------------
print(f"\n{passed} passed, {failed} failed")
if failed == 0:
    print("All of Part 16 works!")
os.remove(db.DB_FILE)
