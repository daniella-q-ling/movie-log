# Movie Log Website: Phase 4 Step-by-Step Guide

This is everything you need to turn your terminal movie log into a real website with accounts, and put it online. It continues in your existing `movie-log` repo.

**How to use this guide**
- Do the steps **in order**. Each step says which file to work in, what to write, and how to check it.
- Check off boxes as you go (`[ ]` → `[x]`).
- **Write every line yourself.** The cheat sheets show general syntax, not your answers.
- Run the site after every step. Commit and **push** after every part.
- Stuck for 15+ minutes? Send Claude your code and the error message.

**Contents**
1. How a website works (read first)
2. Cheat sheets: Flask · Jinja · HTML · SQL
3. Setup (W1–W6)
4. Part 12: Hello Flask
5. Part 13: Homepage and search
6. Part 14: Movie page
7. Part 15: Styling
8. Part 16: Database
9. Part 17: Accounts
10. Part 18: The log on the web
11. Part 19: Stats, Discover, For You
12. Part 20: Polish
13. Part 21: Deploy to PythonAnywhere
14. Finish
15. Common errors and fixes

---

## 1. How a website works (read first)

When someone visits your site, this happens every time:

```
Browser  ──asks for a URL──▶  Flask (app.py)
                                  │  finds the "route" function for that URL
                                  │  gets data from tmdb.py and/or db.py
                                  │  fills in an HTML template with the data
Browser  ◀──sends back HTML──     ┘
   │
   └─ applies style.css → the user sees the page
```

**Key words**
| Word | Meaning |
|---|---|
| **Route** | A Python function in `app.py` connected to a URL, like `/search`. |
| **Template** | An HTML file in `templates/` with blanks (`{{ }}`) that Flask fills in. |
| **GET request** | The browser *asking* for a page. Clicking a link, or a search form. |
| **POST request** | The browser *sending* data that changes something: logging a movie, signing up, deleting. |
| **Query string** | The `?q=Inception` part of a URL. Read it with `request.args`. |
| **Form data** | What a POST form sends. Read it with `request.form`. |
| **Session** | A signed cookie that remembers who's logged in between pages. |
| **Database** | A file (`movielog.db`) that stores users and logs permanently, replacing `movies.json`. |

**Which file does what**
| File | Job | Language |
|---|---|---|
| `app.py` | What happens at each URL | Python |
| `db.py` | Saving and loading users and logs | Python |
| `schema.sql` | The shape of the database tables | SQL |
| `tmdb.py` | Getting movie data (yours, already done) | Python |
| `movie_log.py` | Recommender and stats logic (yours, already done) | Python |
| `templates/*.html` | What each page shows | HTML + Jinja |
| `static/style.css` | How everything looks | CSS |

---

## 2. Cheat sheets

### Flask (in `app.py`)
```python
@app.route("/hello")                       # runs when someone visits /hello
def hello():
    return "plain text"                    # simplest response

return render_template("page.html", name=value)   # show a template, passing data in

@app.route("/thing/<int:thing_id>")        # a number in the URL becomes a parameter
def thing(thing_id): ...

@app.route("/form", methods=["GET", "POST"])     # a route that accepts form submissions
if request.method == "POST": ...

request.args.get("q", "")                  # read ?q=... from the URL (GET)
request.form.get("rating")                 # read a submitted form field (POST)

redirect(url_for("index"))                 # send the user to another route
flash("Saved!")                            # a one-time message shown on the next page
session["user_id"] = 5                     # remember something for this user
session.get("user_id")                     # read it (None if not set)
session.clear()                            # forget everything (log out)
```

### Jinja (in templates)
```html
{{ movie.title }}                         <!-- print a value -->
{{ movie.genres | join(", ") }}           <!-- list → "Action, Sci-Fi" -->
{{ movies | length }}                     <!-- count -->

{% if movies %} ... {% else %} ... {% endif %}

{% for movie in movies %}
  ... {{ movie.title }} ...
{% endfor %}

{{ url_for('movie', movie_id=movie.id) }} <!-- URL for a route, with a parameter -->

{% extends "base.html" %}                 <!-- first line of every page -->
{% block content %} ... {% endblock %}    <!-- your page goes inside this -->
```

### HTML you'll need
```html
<h1>Big heading</h1>  <h2>Smaller</h2>  <p>Paragraph</p>
<a href="URL">Link text</a>
<img src="URL" alt="description">
<div class="name">a box you can style</div>
<strong>bold</strong>

<!-- Forms -->
<form action="URL" method="get">   <!-- or method="post" -->
  <input type="text" name="q" placeholder="Search movies" required>
  <input type="number" name="rating" min="1" max="10">
  <input type="date" name="date_watched">
  <input type="password" name="password">
  <textarea name="notes"></textarea>
  <select name="genre">
    <option value="">Any</option>
    <option value="Action">Action</option>
  </select>
  <button type="submit">Go</button>
</form>
<!-- The input's `name` is the key you read in Python. -->

<!-- Tables -->
<table>
  <thead><tr><th>Title</th><th>Rating</th></tr></thead>
  <tbody><tr><td>Inception</td><td>9</td></tr></tbody>
</table>
```

### SQL you'll need (in `schema.sql` and `db.py`)
```sql
CREATE TABLE IF NOT EXISTS things (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
INSERT INTO things (name) VALUES (?);
SELECT * FROM things WHERE id = ?;
SELECT * FROM things WHERE owner = ? ORDER BY created DESC;
DELETE FROM things WHERE id = ? AND owner = ?;
```
```python
conn = get_connection()
cur = conn.execute("INSERT INTO things (name) VALUES (?)", (name,))   # note the comma!
conn.commit()                 # required after INSERT, UPDATE, DELETE
new_id = cur.lastrowid
row  = conn.execute("SELECT ...", (x,)).fetchone()    # one row or None
rows = conn.execute("SELECT ...", (x,)).fetchall()    # list of rows
conn.close()
```
⚠️ **Always use `?` placeholders. Never build SQL with f-strings.** Otherwise someone could type SQL into your forms and run it (a "SQL injection" attack).

---

## 3. Setup

- [ ] **W1. Add the starter files.** Drag `website-starter.zip` into your `movie-log` Codespace, then run:
  ```
  unzip website-starter.zip
  rm website-starter.zip
  ```
  ✅ You now have `app.py`, `db.py`, `schema.sql`, `templates/`, and `static/`.

- [ ] **W2. Install Flask:** `pip install flask`

- [ ] **W3. Update `requirements.txt`** so it has two lines: `requests` and `flask`.

- [ ] **W4. Keep the database off GitHub.** Add this line to `.gitignore`: `movielog.db`

- [ ] **W5. Add a secret key.** github.com → Settings → Codespaces → New secret
  - Name: `FLASK_SECRET_KEY`
  - Value: any long random string (mash the keyboard for 40+ characters)
  - Repository access: `movie-log`
  - Then **stop and restart** your Codespace.
  - Why: Flask uses it to sign the login cookie so nobody can fake being logged in.

- [ ] **W6. Check your imports.** Open `app.py`. The `from tmdb import ...` and `from movie_log import ...` lines must match your actual function names. Rename them if yours differ.

- [ ] Commit and push: "Add website starter files"

---

## 4. Part 12: Hello Flask (~20 min)

**Goal:** see your first page in the browser.

- [ ] **12.1** In `app.py`, in `index()`, replace `pass` with a line that returns the text `"Hello, Movie Log!"`.
- [ ] **12.2** In the terminal, run:
  ```
  flask --app app run --debug
  ```
- [ ] **12.3** Codespaces shows a pop-up: **Open in Browser**. Click it. (If you miss it: the **Ports** tab next to Terminal → port 5000 → globe icon.)
- [ ] **12.4** Change the text, save, and refresh the browser.

💡 `--debug` restarts the site whenever you save, and shows detailed error pages. Leave the terminal running while you work. Press **Ctrl+C** to stop the server.

✅ **Test:** your message shows up, and editing it updates after a refresh.

---

## 5. Part 13: Homepage and search (~1.5 hr)

**Goal:** type a movie on the homepage → see results with posters.

- [ ] **13.1 `app.py` → `index()`:** return `render_template("index.html")` instead of the text.
- [ ] **13.2 `templates/index.html`:** below the comment, write:
  - an `<h1>` with the app name and a `<p>` tagline
  - a `<form>` with `action="{{ url_for('search') }}"` and `method="get"`
  - inside it, a text `<input>` with `name="q"` and a submit `<button>`

  ✅ Refresh: you see the heading and search box. Searching gives an error for now, which is expected.
- [ ] **13.3 `tmdb.py` → `search_movie`:** make sure each result also includes `poster_path` (TMDB includes it in search results; you may have left it out).
- [ ] **13.4 `app.py` → `search()`:**
  1. `q = request.args.get("q", "")`
  2. if `q` is empty → `return redirect(url_for("index"))`
  3. call `search_movie(q)`
  4. `return render_template("search.html", query=q, results=results)`
- [ ] **13.5 `templates/search.html`:**
  1. an `<h2>` reading `Results for "{{ query }}"`
  2. `{% if results %}` … `{% else %}` "No movies found." `{% endif %}`
  3. inside the `if`: `<div class="grid-cards">`, then a `{% for movie in results %}` loop
  4. for each movie: an `<a>` linking to `{{ url_for('movie', movie_id=movie.id) }}`, containing:
     - `<img src="{{ POSTER_URL }}{{ movie.poster_path }}">` (only if `movie.poster_path` exists)
     - the title and year

✅ **Test:** search "Inception" → a list of results with posters, and the URL ends in `?q=Inception`. Search for gibberish → "No movies found." Clicking a movie gives an error for now; that's next.

---

## 6. Part 14: Movie page (~1.5 hr)

**Goal:** a full info page for any movie.

- [ ] **14.1 `app.py` → `movie(movie_id)`:**
  1. call `get_details`, `get_cast`, `get_reviews`, and `get_keywords` with `movie_id`
  2. set `entry = None` for now (Part 18 fills this in)
  3. `return render_template("movie.html", details=details, cast=cast, reviews=reviews, keywords=keywords, entry=entry)`
- [ ] **14.2 `templates/movie.html`**, the info section:
  1. `<div class="movie-layout">` containing two parts:
     - left: the poster `<img>`
     - right: `<h1>{{ details.title }} ({{ details.year }})</h1>`, then runtime, TMDB rating, genres (`| join(", ")`), director, cast, themes, and plot
- [ ] **14.3** A reviews section:
  - `<h2>Reviews</h2>`, then `{% for review in reviews %}` → author in `<strong>`, text in `<p>`
  - `{% else %}` inside the for loop works too: `{% for ... %} ... {% else %} No reviews yet. {% endfor %}`
- [ ] **14.4** Leave the "Log it" section as a comment until Part 18.

✅ **Test:** click 3 different search results, including an old or obscure movie. Every page loads, and missing reviews show "No reviews yet."

---

## 7. Part 15: Make it look good (~1–2 hr)

**Goal:** a site you'd actually send to a friend.

- [ ] **15.1 `static/style.css`, the card grid:**
  ```css
  .grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }
  ```
  (This one line of CSS is the hardest to figure out, so it's given. Write the rest yourself.)
- [ ] **15.2 Posters:** make `.grid-cards img` 100% wide with rounded corners (`border-radius`).
- [ ] **15.3 Movie page layout:** make `.movie-layout` a two-column grid: poster on the left (about 300px), info on the right. Look up `grid-template-columns`.
- [ ] **15.4 Hover effect:** when hovering over a card link, scale it up slightly. Look up `transform: scale()` and `transition`.
- [ ] **15.5 Footer:** in `base.html`, add the TMDB credit: *"This product uses the TMDB API but is not endorsed or certified by TMDB."* Optionally add a link to your GitHub.
- [ ] **15.6 Your own style:** pick an accent color (search "Pico CSS customize colors") and a font, and give it personality.
- [ ] **15.7 Phone check:** right-click → Inspect → the phone/tablet icon. Does it still look OK when narrow?

💡 **Experiment in the browser first:** right-click anything → Inspect → edit the CSS on the right side. You'll see changes instantly. When you like something, copy it into `style.css`.

✅ **Test:** search and movie pages look clean on both desktop and phone sizes.

- [ ] 🎉 **Commit and push:** "Website: search and movie pages"

---

## 8. Part 16: Database (~2 hr)

**Goal:** a database that stores users and each user's log.

- [ ] **16.1 `schema.sql`:** write the `log_entries` table, following the `users` table above it and the column list in the comment. End it with `FOREIGN KEY (user_id) REFERENCES users(id)`.
- [ ] **16.2 Create the database:**
  ```
  python -c "import db; db.init_db()"
  ```
  ✅ A file called `movielog.db` appears. If you see an error, it's a typo in `schema.sql`; the message says roughly where.

  💡 Changed the schema after creating the database? Delete `movielog.db` and run the command again, since `IF NOT EXISTS` won't update an existing table.
- [ ] **16.3 `db.py` → `create_user`:** INSERT with `?` placeholders → commit → return `cur.lastrowid` → close.
- [ ] **16.4 `db.py` → `get_user_by_username`:** SELECT → `.fetchone()` → close → return the row (or None).
- [ ] **16.5 `db.py` → `add_log_entry(user_id, movie)`:** INSERT every column. For `genres`, `cast_members`, and `keywords`, insert `json.dumps(movie["genres"])` and so on. Note: your dictionary key is `"cast"`, but the column is `cast_members`.
- [ ] **16.6 `db.py` → `row_to_movie(row)`:**
  1. `movie = dict(row)`
  2. `json.loads` the three list fields
  3. rename `cast_members` back to `cast`: `movie["cast"] = json.loads(movie.pop("cast_members"))`
  4. return `movie`
- [ ] **16.7 `db.py` → `get_log(user_id)`:** SELECT this user's entries, `ORDER BY date_watched DESC`, and return `[row_to_movie(r) for r in rows]`.
- [ ] **16.8 `db.py` → `get_log_entry(user_id, tmdb_id)`:** SELECT one → `row_to_movie` if found, else `None`.
- [ ] **16.9 `db.py` → `delete_log_entry(user_id, entry_id)`:** DELETE with **both** `id = ?` and `user_id = ?` → commit.

✅ **Test** without the website. Type `python` in the terminal, then type each line:
```python
import db
uid = db.create_user("test", "fakehash")
print(db.get_user_by_username("test")["id"])        # same as uid?
db.add_log_entry(uid, {"tmdb_id": 27205, "title": "Inception", "year": 2010, "rating": 9,
    "date_watched": "2026-11-22", "notes": "", "runtime": 148, "genres": ["Sci-Fi"],
    "cast": ["Leonardo DiCaprio"], "director": "Christopher Nolan",
    "keywords": ["dream"], "poster_path": ""})
log = db.get_log(uid)
print(log[0]["genres"], type(log[0]["genres"]))     # ['Sci-Fi'] <class 'list'>  ← must be a list!
db.delete_log_entry(uid, log[0]["id"])
print(db.get_log(uid))                              # []
exit()
```
Then delete `movielog.db` and run `init_db` again for a fresh start.

---

## 9. Part 17: Accounts (~1.5 hr)

**Goal:** sign up, log in, and log out.

- [ ] **17.1 `templates/signup.html`:** an `<h1>`, then a `<form method="post">` with a `username` text input, a `password` password input (both `required`), and a submit button. Add a link to log in underneath.
- [ ] **17.2 `app.py` → `signup()`:**
  1. `if request.method == "POST":`
  2. read `username` and `password` from `request.form` (use `.strip()` on the username)
  3. if either is empty → `flash(...)` and `return render_template("signup.html")`
  4. if `db.get_user_by_username(username)` finds someone → flash "Username taken" and show the form again
  5. `user_id = db.create_user(username, generate_password_hash(password))`
  6. `session["user_id"] = user_id` and `session["username"] = username`
  7. `flash("Welcome!")` → `return redirect(url_for("index"))`
  8. outside the `if` (a GET request): `return render_template("signup.html")`
- [ ] **17.3 `templates/login.html`:** copy `signup.html` and change the wording.
- [ ] **17.4 `app.py` → `login()`:** same shape as signup, except:
  - look up the user → `if user is None or not check_password_hash(user["password_hash"], password):` → flash "Wrong username or password" and show the form again
  - otherwise set `session["user_id"] = user["id"]` and `session["username"]`, then redirect home
- [ ] **17.5 `app.py` → `logout()`:** `session.clear()` → flash "Logged out" → redirect home.
- [ ] **17.6 Optional:** show "Hi, {{ session.username }}" in the nav bar in `base.html`.

✅ **Test:**
1. Sign up → the nav bar switches to My Log / For You / Stats / Log out.
2. Log out → it switches back.
3. Log in with the wrong password → error. Right password → logged in.
4. Sign up again with the same username → "Username taken."
5. Check that passwords aren't stored readably:
   ```
   python -c "import db; c=db.get_connection(); print([dict(r) for r in c.execute('SELECT * FROM users')])"
   ```
   The `password_hash` should be a long scrambled string, never your actual password.

---

## 10. Part 18: The log on the web (~2 hr)

**Goal:** log movies from their pages, view your log, and delete entries, with each user seeing only their own.

- [ ] **18.1 `app.py` → `movie()`:** replace `entry = None` with: if `session.get("user_id")`, then `entry = db.get_log_entry(session["user_id"], movie_id)`.
- [ ] **18.2 `templates/movie.html`, the "Log it" section:**
  ```
  {% if not session.get('user_id') %}  → a link: "Log in to log this movie"
  {% elif entry %}                      → "You rated this {{ entry.rating }}/10 on {{ entry.date_watched }}"
  {% else %}                            → the form
  {% endif %}
  ```
  The form: `method="post"`, `action="{{ url_for('add_to_log', movie_id=details.id) }}"`, with inputs named `rating` (number, 1–10, required), `date_watched` (date), `notes` (textarea), and a submit button.
- [ ] **18.3 `app.py` → `add_to_log(movie_id)`:**
  1. read `rating` (convert with `int()`), `date_watched`, and `notes` from `request.form`
  2. fetch details, cast, and keywords from TMDB
  3. build the movie dictionary with every field `add_log_entry` expects (same as Part 6, plus `poster_path`)
  4. `db.add_log_entry(session["user_id"], movie)`
  5. flash "Added to your log!" → `redirect(url_for("movie", movie_id=movie_id))`
- [ ] **18.4 `app.py` → `my_log()`:** `movies = db.get_log(session["user_id"])` → `render_template("log.html", movies=movies)`.
- [ ] **18.5 `templates/log.html`:** heading with the count, then an empty message or a `<table>`. Each row has: a small poster, the title linking to its movie page, rating, date, notes, and a delete form (see the comment in the file; it must be a POST form, not a link).
- [ ] **18.6 `app.py` → `delete_from_log(entry_id)`:** `db.delete_log_entry(session["user_id"], entry_id)` → flash → redirect to `my_log`.
- [ ] **18.7 Bonus, sorting:** in `my_log()`, read `request.args.get("sort")`, and if it's `"rating"`, sort with your `sort_movies` function. Add the two sort links to `log.html`.

✅ **Test (important!):**
1. Log 3 movies → they appear in My Log. The movie page now says "You rated this…"
2. Delete one → it's gone.
3. **Make a second account.** Log different movies. Each account sees **only its own** log.
4. Visit `/log` while logged out → you're sent to the login page.

- [ ] 🎉 **Commit and push:** "Website: accounts and per-user logs"

---

## 11. Part 19: Stats, Discover, For You (~2–3 hr)

**Goal:** bring your Phase 1–3 features to the website.

- [ ] **19.1 Refactor first** (in `movie_log.py`). Your terminal functions *print*. Websites need functions that *return* data. For example:
  - `get_stats(movies)` returns a dictionary: `{"total": ..., "average": ..., "top": ..., ...}`
  - `show_stats(movies)` calls `get_stats` and prints the results, so your terminal version still works
  - do the same for recommendations: `get_recommendations_for(movies, top_n)` returns a list of `{"id", "title", "poster_path", "score", "reasons"}`
  - ✅ Run `python movie_log.py`. The terminal version should still work exactly as before.
- [ ] **19.2 Stats:**
  - `app.py` → `stats()`: get the log → `get_stats(movies)` → render `stats.html`
  - `stats.html`: a `<div class="grid">` of stat cards (`<article>` tags look like cards in Pico) for total, average, hours watched (sum of runtimes ÷ 60), and favorite genre, plus a top-5 list
  - handle an empty log: "Log some movies to see stats"
- [ ] **19.3 Discover:**
  - `app.py` → `discover_page()`:
    1. `genres = get_genre_list()` (for the dropdown)
    2. if `request.args` is empty → render the page with just the form
    3. otherwise read each filter, turning the genre name into an ID, actor → `find_person`, theme → `find_keyword`; convert numbers with `int()`, and skip blank ones
    4. `results = discover(...)` → render `discover.html` with `genres` and `results`
  - `discover.html`: a form with `method="get"` and the 5 fields (loop over `genres` to build the `<option>`s), then results cards (copy the loop from `search.html`)
- [ ] **19.4 For You:**
  - `app.py` → `recommend_page()`: get the log → if fewer than 5 movies, render with a message → otherwise `recs = get_recommendations_for(movies, 12)` → render
  - `recommend.html`: cards with poster, title, and a "Why:" line (`{{ rec.reasons | join(" · ") }}`)
  - 💡 This page makes lots of TMDB calls and can take several seconds. That's OK for now.

✅ **Test:** on a test account, log 10+ movies with obvious tastes (lots of high-rated sci-fi, low-rated rom-coms). The For You page should show sci-fi with sensible reasons. Discover results should match the filters.

---

## 12. Part 20: Polish (~1–2 hr)

- [ ] **20.1 Error handling around TMDB:** wrap API calls in `try`/`except requests.RequestException`. On failure, flash "Couldn't reach the movie database, please try again" instead of crashing.
- [ ] **20.2 Movie not found:** if TMDB returns an error for `/movie/99999999`, show a friendly page instead of crashing. Look up `abort(404)`.
- [ ] **20.3 Custom 404 page:** create `templates/404.html` and add:
  ```python
  @app.errorhandler(404)
  def not_found(e): ...    # return render_template("404.html"), 404
  ```
- [ ] **20.4 Empty states everywhere:** no results, no reviews, empty log, no stats, and not enough movies for recommendations. Every page should say something helpful.
- [ ] **20.5 Rating validation:** if someone submits a rating outside 1–10, flash an error instead of saving it.
- [ ] **20.6 Final click-through:** use every page on desktop and phone sizes, both logged in and logged out.

- [ ] 🎉 **Commit and push:** "Website: stats, discover, recommendations, polish"

---

## 13. Part 21: Deploy to PythonAnywhere (~1–1.5 hr)

**Why PythonAnywhere:** its free plan keeps your files between restarts, so your SQLite database (users and logs) survives. On some other free hosts, the filesystem is wiped on every restart. Free accounts can only reach approved websites, and TMDB's API (`api.themoviedb.org`) has been added to that list. If you hit a "403 Forbidden" when the site calls TMDB, see the troubleshooting note at the end of this part.

**Your site will be at:** `https://YOURUSERNAME.pythonanywhere.com`

- [ ] **21.1 Sign up** at pythonanywhere.com → the free "Beginner" account. Your username becomes part of the URL, so pick a good one.
- [ ] **21.2 Get your code there.** Dashboard → **Consoles** → **Bash**, then:
  ```
  git clone https://github.com/daniella-q-ling/movie-log.git
  cd movie-log
  pip install --user -r requirements.txt
  python -c "import db; db.init_db()"
  ```
  ✅ `ls` shows your files plus a new `movielog.db`.
- [ ] **21.3 Create the web app.** Dashboard → **Web** tab → **Add a new web app** → Next → choose **Manual configuration** (not "Flask") → choose the newest Python version available.
- [ ] **21.4 Point it at your code.** On the Web tab, set:
  - **Source code:** `/home/YOURUSERNAME/movie-log`
  - **Working directory:** `/home/YOURUSERNAME/movie-log` (so `schema.sql` and `movielog.db` are found)
- [ ] **21.5 Edit the WSGI file** (a link on the Web tab: "WSGI configuration file"). Delete everything in it and write:
  ```python
  import os, sys
  path = "/home/YOURUSERNAME/movie-log"
  if path not in sys.path:
      sys.path.insert(0, path)
  os.chdir(path)

  os.environ["TMDB_API_KEY"] = "your TMDB key"
  os.environ["FLASK_SECRET_KEY"] = "a long random string"

  from app import app as application
  ```
  ⚠️ This file lives only on PythonAnywhere, never in your repo, so putting your keys here is OK. **Never** commit them to GitHub.
- [ ] **21.6 Make sure debug is off.** The `app.run(debug=True)` line at the bottom of `app.py` doesn't run on PythonAnywhere (it uses the WSGI file instead), so you're fine.
- [ ] **21.7 Reload.** Click the big green **Reload** button on the Web tab, then visit your URL.
- [ ] **21.8 Test everything live:** sign up, search, log a movie, check recommendations. Then try it on your phone.

**Updating the live site later** (after you push changes to GitHub):
```
cd ~/movie-log
git pull
```
then click **Reload** on the Web tab.

**Keeping it running:** free web apps need you to log in and click a "Run until 3 months from today" button on the Web tab every few months, or the site turns off. PythonAnywhere emails you a reminder.

**Troubleshooting**
- **Something broke?** Web tab → **Error log** (the newest errors are at the bottom). It shows the Python error, just like your terminal did.
- **"Something went wrong" page:** almost always a typo in the WSGI file or a wrong path. Check the error log.
- **403 Forbidden or a proxy error when calling TMDB:** the free-account allowlist is blocking it. Request an addition through PythonAnywhere's allowlist request form (search "PythonAnywhere requesting allowlist additions"), including TMDB's API documentation link. Or ask Claude about other hosting options.
- **Posters missing:** posters load in the visitor's browser straight from `image.tmdb.org`, so the allowlist doesn't affect them. Check the `POSTER_URL` + `poster_path` code instead.

---

## 14. Finish

- [ ] **README update:** add a **Live demo** link at the top, 2–3 screenshots (homepage, movie page, For You page), a "Tech stack" line (*Python · Flask · SQLite · TMDB API · Pico CSS · PythonAnywhere*), and a short "How the website works" section.
- [ ] **Repo About box:** add the live URL in the "Website" field.
- [ ] **Resume line**, for example:
  > **Movie Log** (Python, Flask, SQLite) · live link · GitHub
  > Built a full-stack movie journal with user accounts, TMDB API integration, and a custom taste-profile recommendation algorithm that explains each suggestion; deployed on PythonAnywhere.
- [ ] Send the link to friends and get real users 🎉

---

## 15. Common errors and fixes

| Error / symptom | Usual cause | Fix |
|---|---|---|
| `TypeError: The view function did not return a valid response` | A route still has `pass`, or a code path doesn't `return` | Make sure every route returns something on every path |
| `jinja2.exceptions.TemplateNotFound` | Wrong file name, or the template isn't in `templates/` | Check the spelling and folder |
| `jinja2.exceptions.UndefinedError` / blank spot on the page | The template uses a variable you didn't pass in | Add it to `render_template(..., name=value)` |
| `werkzeug.routing.BuildError` | `url_for('name')` doesn't match any route function name | Use the **function** name, not the URL |
| `405 Method Not Allowed` | A form POSTs to a route without `methods=["POST"]` | Add `methods=[...]` to `@app.route` |
| `400 Bad Request` / `KeyError` on a form field | Input `name=` doesn't match `request.form["..."]` | Make the names match; use `.get()` |
| `sqlite3.OperationalError: no such table` | The database wasn't created, or the schema changed | Delete `movielog.db` and run `init_db` again |
| `sqlite3.OperationalError: near "...": syntax error` | A typo in SQL | Check commas, quotes, and parentheses |
| `sqlite3.ProgrammingError: Incorrect number of bindings` | The count of `?` doesn't match the values, or you're missing a comma in `(x,)` | Count them; one value needs `(x,)` |
| Changes don't save in the database | Forgot `conn.commit()` | Commit after INSERT and DELETE |
| `KeyError: 'TMDB_API_KEY'` | Secret not set, or the Codespace wasn't restarted | Recheck the secret and restart |
| Logged out on every page | `secret_key` changes between restarts | Make sure `FLASK_SECRET_KEY` is set |
| Page looks unstyled | CSS link broken | Check `static/style.css` exists; hard-refresh with Cmd+Shift+R |
| Site won't start: `Address already in use` | An old server is still running | Ctrl+C in that terminal, or close it |
