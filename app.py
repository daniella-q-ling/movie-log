"""
app.py: the Flask website.

Each "route" is a function that runs when someone visits a URL.
It usually gets some data, then returns render_template("page.html", ...)
to show an HTML page from the templates/ folder.

Run locally with:  flask --app app run --debug
(Codespaces will offer to open the page in your browser.)
"""

import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import db
from tmdb import (search_movie, get_details, get_cast, get_reviews, get_keywords,
                  get_genre, find_person, find_keyword, discover, POSTER_URL)
from movie_log import build_profile, score_movie  

app = Flask(__name__)
# Signs the login cookie. Store FLASK_SECRET_KEY as a Codespaces secret (any long random string).
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


@app.context_processor
def add_globals():
    """Makes POSTER_URL available in every template. (Already done for you.)"""
    return {"POSTER_URL": POSTER_URL}


def login_required(view):
    """
    Put @login_required above a route to make it logged-in only.
    If nobody is logged in, it sends them to the login page.
    (Already done for you. Decorators are an advanced Python feature.)
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# =============================================================================
# PART 12-13: Home and search
# =============================================================================

@app.route("/")
def index():
    """
    The homepage: shows a search box (templates/index.html).
    Part 12: start by returning just the text "Hello, Movie Log!" to check Flask works.
    Then switch to render_template("index.html").
    """
    return render_template("index.html")


@app.route("/search")
def search():
    """
    Search results page. The search box sends the title as ?q=Inception in the URL.

    Steps:
      1. Read it with request.args.get("q", "").
      2. If it's empty, redirect back to the homepage.
      3. Call search_movie(q).
      4. Return render_template("search.html", query=q, results=results)
    """
    q = request.args.get("q", "")
    if not q:
        return redirect(url_for("index"))
    results = search_movie(q)
    return render_template("search.html", query=q, results=results)


# =============================================================================
# PART 14: Movie details page
# =============================================================================

@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    """
    Full info page for one movie: /movie/27205

    Steps:
      1. Call get_details, get_cast, get_reviews, and get_keywords.
      2. If someone is logged in, also check whether this movie is already in
         their log (db.get_log_entry) so the page can say "Already logged".
      3. render_template("movie.html", ...) passing everything the page needs.
    """
    details = get_details(movie_id)
    print("DETAILS:", details)
    cast = get_cast(movie_id)
    reviews = get_reviews(movie_id)
    keywords = get_keywords(movie_id)
    entry = None
    if session.get("user_id"):
        entry = db.get_log_entry(session["user_id"], movie_id)

    return render_template("movie.html", details=details, cast=cast,
                       reviews=reviews, keywords=keywords, entry=entry)

# =============================================================================
# PART 17: Accounts
# =============================================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    GET: show the sign-up form (templates/signup.html).
    POST: the form was submitted:
      1. Read username and password from request.form.
      2. Check that neither is empty and that the username isn't taken
         (db.get_user_by_username). If there's a problem, flash() a message
         and show the form again.
      3. Save the user with db.create_user(username, generate_password_hash(password)).
         Never store the plain password!
      4. Log them in: session["user_id"] = the new user's id.
      5. Redirect to the homepage.
    """
    if request.method == "POST":
        # Step 1: read the form
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Step 2: neither can be empty
        if not username or not password:
            flash("Please fill in both fields.")
            return render_template("signup.html")

        # Step 3: username must not be taken
        if db.get_user_by_username(username):
            flash("That username is taken.")
            return render_template("signup.html")


        # Step 4: create user with hashed password
        user_id = db.create_user(username, generate_password_hash(password))

        # Step 5: log them in
        session["user_id"] = user_id
        session["username"] = username
        # Step 6: welcome and go home
        flash("Welcome to Mochiroll!")
        return redirect(url_for("index"))
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: show the login form.
    POST:
      1. Look up the user by username.
      2. If there's no user, or check_password_hash(user["password_hash"], password)
         is False, flash "Wrong username or password" and show the form again.
         (Use the same message for both, so people can't guess which usernames exist.)
      3. Otherwise set session["user_id"] and session["username"], then redirect home.
    """
    if request.method == "POST":
        # Step 1: read form
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Step 2: look up user
        user = db.get_user_by_username(username)

        # Step 3: check password
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Wrong username or password.")
            return render_template("login.html")

        # Step 4: log in and redirect
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Welcome back!")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear the session (session.clear()) and redirect to the homepage."""
    session.clear()
    flash("Logged out.")
    return redirect(url_for("index"))


# =============================================================================
# PART 18: The user's log
# =============================================================================

@app.route("/log")
@login_required
def my_log():
    """
    Show the logged-in user's movies (templates/log.html).

    Bonus: let the user sort with ?sort=rating or ?sort=date
    (read it from request.args, like in search).
    """
    movies = db.get_log(session["user_id"])
    return render_template("log.html", movies=movies)


@app.route("/log/add/<int:movie_id>", methods=["POST"])
@login_required
def add_to_log(movie_id):
    """
    Runs when the "Log it" form on a movie page is submitted.

    Steps:
      1. Read rating, date_watched, and notes from request.form.
      2. Fetch the movie's details, cast, and keywords from TMDB.
      3. Save it with db.add_log_entry(session["user_id"], movie_dict).
         Build movie_dict exactly like your terminal version did in Part 6,
         so your recommender code still works.
      4. flash("Added to your log!") and redirect to the movie page.
    """
    bucket = request.form.get("bucket")
    if bucket not in db.BUCKET_ORDER:
        flash("Pick Loved, Fine, or Didn't like.")
        return redirect(url_for("movie", movie_id=movie_id))
    
    details = get_details(movie_id)
    cast = get_cast(movie_id)
    keywords = get_keywords(movie_id)

    pending = {
        "tmdb_id": movie_id,
        "title": details["title"],
        "year": details["year"],
        "bucket": bucket,
        "my_rating": round(float(request.form.get("my_rating", 0)), 2), 
        "date_watched": request.form.get("date_watched", ""),
        "notes": request.form.get("notes", ""),
        "runtime": details["runtime"],
        "genres": details["genres"],
        "cast": cast["cast"],
        "director": cast["director"],
        "keywords": keywords,
        "poster_path": details["poster_path"],
    }

    others = db.get_bucket(session["user_id"], bucket)

    if not others:
        pending["position"] = 0
        db.add_log_entry(session["user_id"], pending)
        flash("Added to your log :)")
        return redirect(url_for("movie", movie_id=movie_id))

    session["pending"] = pending
    session["lo"] = 0
    session["hi"] = len(others)
    return redirect(url_for("rank"))

@app.route("/rank", methods=["GET", "POST"])
@login_required
def rank():
    pending = session.get("pending")
    if not pending:
        return redirect(url_for("index"))

    others = db.get_bucket(session["user_id"], pending["bucket"])
    lo = session["lo"]
    hi = session["hi"]
    mid = (lo + hi) // 2

    if request.method == "POST":
        # 1. Narrow the range based on the answer
        choice = request.form.get("choice")
        if choice == "new":
            hi = mid
        elif choice == "old":
            lo = mid + 1
        else:
            lo = mid
            hi = mid

        # 2. Down to one spot? Save it.
        if lo == hi:
            pending["position"] = lo
            db.add_log_entry(session["user_id"], pending)
            session.pop("pending")
            session.pop("lo")
            session.pop("hi")
            flash(f"Ranked #{lo + 1} in {pending['bucket']}!")
            return redirect(url_for("movie", movie_id=pending["tmdb_id"]))

        # 3. Otherwise, save the new range and ask again
        session["lo"] = lo
        session["hi"] = hi
        return redirect(url_for("rank"))

    return render_template("rank.html", pending=pending, other=others[mid])

@app.route("/log/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete_from_log(entry_id):
    """
    Delete one entry, but ONLY if it belongs to the logged-in user.
    (Otherwise anyone could delete anyone's movies by guessing numbers!)
    Then redirect back to the log page.
    """
    db.delete_log_entry(session["user_id"], entry_id)
    flash("Removed from your log.")
    return redirect(url_for("my_log"))


# =============================================================================
# PART 19: Stats, discover, recommendations
# =============================================================================

@app.route("/stats")
@login_required
def stats():
    """
    Calculate the same stats as your terminal version (total, average rating,
    top rated), plus anything else you like (favorite genre? total hours watched?),
    and show them in templates/stats.html.

    Tip: write a helper that RETURNS the numbers instead of printing them,
    so the template can display them.
    """
    # TODO
    pass


@app.route("/discover")
def discover_page():
    """
    A filter form (genre dropdown, max runtime, min year, actor, theme)
    and its results, all on one page (templates/discover.html).

    The form uses GET, so the filters arrive in request.args.
    If no filters were submitted yet, just show the empty form.
    Turn names into IDs with get_genre_list, find_person, and find_keyword,
    then call discover(...).
    """
    # TODO
    pass


@app.route("/recommend")
@login_required
def recommend_page():
    """
    Personalized recommendations for the logged-in user.

    Steps:
      1. movies = db.get_log(session["user_id"]). These are the same kind of
         dictionaries as your terminal version, so build_profile works unchanged.
      2. Gather candidates and score them the way your Part 9 code does.
      3. render_template("recommend.html", recs=...) where each rec includes
         its title, poster, score, and reasons.

    Note: your terminal recommend() PRINTS. Refactor the logic into a function
    that RETURNS the list, and use it both here and in the terminal version.
    If the user has fewer than ~5 movies logged, show a friendly
    "Log a few more movies first" message instead.
    """
    # TODO
    pass


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
