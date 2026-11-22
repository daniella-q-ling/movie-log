"""
Movie Log: main program (menu, log, stats, recommendations)

Each movie in the log is a dictionary.
{"title": "Inception", "year": 2010, "rating": 9,
 "date_watched": 2026-11-22", "notes": "loved the ending"}

After Part 6, will include:
"tmdb_id", "genres", "runtime", "cast", "director", "keywords"

Run with: python movie_log.py
"""
import json
from tmdb import search_movie, get_details, get_cast, get_keywords

LOG_FILE = "movie_log.json"

# PHASE 1, PART 1: Menu and data

def add_movie(movies):
    """
    Ask user for movie's title, year, rating (1-10), date watched, and notes.
    Build dictionary and append to 'movies'.
    """
    movie = []
    title = input("Enter movie title: ")
    year = input("Enter movie year: ")
    rating = input("Enter movie rating (1-10): ")
    
    if rating not in range(1,11):
        print("Rating must be between 1 and 10.")
        return
    
    date_watched = input("Enter date watched (yyyy-mm-dd): ")
    notes = input("Enter any notes about the movie: ")

    # Build dictionary and append to 'movies' per each movie
    movie = {
        "Title": title,
        "Year": year,
        "Rating": rating,
        "Date Watched": date_watched,
        "Notes": notes
    }
    movies.append(movie)

def list_movies(movies):
    """
    Print every movie on its own line, numbered from 1, like:
        1. Inception (2010), 9/10

    If 'movies' is empty, print "No movies. yet." instead.
    """
    if len(movies) == 0:
        print("No movies yet.")
    else:
        for i, movie in enumerate(movies, start=1):
            print(f"{i}. {movie['Title']} ({movie['Year']}), {movie['Rating']}/10")

def delete_movie(movies):
    """
    Show the list, ask movie number to delete, remove that movie.
    *User numbers start at 1, list position starts at 0.
    *If number is out of range or not a number, print message.
    """
    list_movies(movies)
    if len(movies) == 0:
        return
    try:
        movie_num = int(input("Enter the number of the movie to delete: "))
        if 1 <= movie_num <= len(movies):
            deleted_movie = movies.pop(movie_num - 1)
            print(f"Deleted movie: {deleted_movie['Title']} ({deleted_movie['Year']})")
        else:
            print("Invalid movie number.")
    except ValueError:
        print("Please enter a valid number.")

# PHASE 1, PART 2: Save and load

def save_log(movies):
    """
    Write the 'movies' list to LOG_FILE as JSON
    """
    with open(LOG_FILE, 'w') as f:
        json.dump(movies, f, indent=4)
        print(f"Saved {len(movies)} movies to {LOG_FILE}.")

def load_log():
    """
    Read LOG_FILE and return the list of movies
    If the file doesn't exist yet (first run), return an empty list.
    """
    try:
        with open(LOG_FILE, 'r') as f:
            movies = json.load(f)
            print(f"Loaded {len(movies)} movies from {LOG_FILE}. ")
            return movies
    except FileNotFoundError:
        print(f"No log file found. Starting with an empty movie list. ")

# PHASE 1, PART 3: Filter, sort, stats

def filter_by_rating(movies, min_rating):
    """
    Return a new list with only the movies rated min_rating or higher.
    Does not change original list.
    """
    filtered_movies = []
    for movie in movies:
        if movie['Rating'] >= min_rating:
            filtered_movies.append(movie)
    return filtered_movies

def sort_movies(movies, by):
    """
    Return a new list of movies sorted by 'by', which is eithe "rating" (highest first)
    or "date watched" (most recent first). 
    Does not change original list.
    """
    if by == "rating":
        return sorted(movies, key=lambda x: x['Rating'], reverse = True)
    elif by == "date watched":
        return sorted(movies, key=lambda x: x['Date Watched'], reverse = True)

def show_stats(movies):
    """
    Print:
    - total number of movies watched
    - average rating (rounded 1 decimal place)
    - highest-rated movie(s) -> if multiple, print all
    """
    total_movies = len(movies)
    if total_movies == 0:
        print("No movies to show stats for.")
        return

    average_rating = sum(movie['Rating'] for movie in movies) / total_movies
    highest_rating = max(movie['Rating'] for movie in movies)
    highest_rated_movies = [movie for movie in movies if movie['Rating'] == highest_rating]

    print(f"Total movies watched: {total_movies}")
    print(f"Average rating: {average_rating:.1f}")
    print(f"Highest-rated movie(s) ({highest_rating}/10):")
    
    for movie in highest_rated_movies:
        print(f"- {movie['Title']} ({movie['Year']})")

# PHASE 2, PART 6: Connect lookup to the log

def add_movie_from_search(movies):
    """
    Uses TMDB:
    1. Ask for title and call search_tmdb(title)
    2. Display search results, numbered, and let user pick one
    3. Use get_details, get_cast, and get_keywords with movie's ID
    4. Ask ONLY for user's rating, date watched, notes
    5. Build full dictionary (including tmdb_id, genres, runtie, cast, director, keywords) and append
    
    Menu's 'ADD' option should call this function instead of add_movie().
    """
    title = input("Enter movie title to search: ")
    search_results = search_movie(title)

    if not search_results:
        print("No results found.")
        return

    for i, movie in enumerate(search_results, start=1):
        year = movie.get("release_date", "")[:4]
        print(f"{i}. {movie["title"]} ({year})")

    try:
        movie_num = int(input("Enter the number of the movie you want to add: "))

        if movie_num < 1 or movie_num > len(search_results):
            print("Invalid movie number.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    # Get selected movie's TMDB ID
    selected_movie = search_results[movie_num - 1]
    tmdb_id = selected_movie["id"]

    # Get additional movie information
    details = get_details(tmdb_id)
    cast_info = get_cast(tmdb_id)
    keywords = get_keywords(tmdb_id)

    # Ask user for information
    rating = input("Enter your rating (1-10: ")

    try:
        rating = int(rating)
        if rating < 1 or rating > 10:
            print("Rating must be 1 and 10.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    date_watched = input("Enter date watched (yyyy-mm-dd): ")
    notes = input("Enter any notes about the movie: ")

    # Build movie dictionary
    movie = {
        "Title": details["Title"],
        "Year": details["Year"],
        "Rating": rating,
        "Date Watched": date_watched,
        "Notes": notes,
        "tmdb_id": tmdb_id,
        "Genres": details["Genres"],
        "Runtime": details["Runtime"],
        "Cast": cast_info["Cast"],
        "Director": cast_info["Director"],
        "Keywords": keywords
    }

    movies.append(movie)
    print(f"Added {movie["Titlr"]} ({movie["Year"]}) to your movie log.")






