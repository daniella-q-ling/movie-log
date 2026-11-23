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
from tmdb import search_movie, get_details, get_cast, get_keywords, show_movie_page, get_recommended

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
    print(f"Added {movie["Title"]} ({movie["Year"]}) to your movie log.")

def look_up_movie():
    """
    Ask for a title, let user pick from search results.
    Then call show_movie_page(movie_id). This doesn't add anything to the log.
    """
    title = input("Enter movie title to search: ")
    search_results = search_movie(title)

    if not search_results:
        print("No results found.")
        return
    
    for i, movie in enumerate(search_results, start=1):
        year = movie.get("release_date", "")[:4]
        print(f"{i}. {movie["title"]} ({year})")

    # Let user select a movie
    try:
        movie_num = int(input("enter the number of the movie to look up: "))

        if movie_num < 1 or movie_num > len(search_results):
            print(f"Invalid movie number.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    # Get selected movie's TMDB_ID
    selected_movie = search_results[movie_num -1]
    tmdb_id = selected_movie["id"]

    # Display full movie information
    show_movie_page(tmdb_id)

# PHASE 3, PART 8: Because you liked...

def because_you_liked(movies, min_rating=8, top_n = 10):
    """
    For every movie in log rated min_rating or higher, 
    get TMDB recommendations (get_recommendations in tmdb.py)

    Combine them all, skip anything already in the log, 
    and count how many times each movie appears.

    Return top_n movies, most frequent first.
    """
    recommendations = {}

    for movie in movies:
        if movie["Rating"] >= min_rating:
            recommended_movies = get_recommended(movie["tmdb_id"])

            for recommended in recommended_movies:
                movie_id = recommended["id"]
                already_logged = False

                for logged_movie in movies:
                    if logged_movie["tmdb_id"] == movie_id:
                        already_logged = True

                if not already_logged:
                    if movie_id in recommendations:
                        recommendations[movie_id]["Count"] += 1
                    else:
                        recommendations[movie_id] = {
                            "Title": recommended["title"],
                            "Year": recommended.get("release_date", "")[:4],
                            "Rating": recommended.get("vote_average"),
                            "tmdb_id": movie_id,
                            "Count": 1
                        }

    sorted_recommendations = sorted(
        recommendations.values(),
        key=lambda movie: movie["Count"], 
        reverse=True
    )

    return sorted_recommendations[:top_n]

# PHASE 3, PART 9: Own taste profile

def build_profile(movies):
    """
    Go through log and score every genre, actor, director, keyword.
    Each time one appears in a movie, add (that movie's rating -5) to its score.
    Movies you loved push score up, movies disliked pull it down.

    Return dictionary:
    {"genres": {"Science Fiction": 8, "Romance": -3, ...}, 
     "cast": {"Leonardo DiCaprio": 4, ...},
     "director": {"Christopher Nolan": 8, ...},
     "keywords": {"time traavel": 5, ...}}
    """
    profile = {
        "genres": {},
        "cast": {},
        "director": {},
        "keywords": {}
    }

    for movie in movies:
        score = movie["Rating"] - 5

        # Score each genre
        for genre in movie.get("Genres", []):
            if genre in profile["genres"]:
                profile["genres"][genre] += score
            else:
                profile["genres"][genre] = score
        # Score each actor
        for actor in movie.get("Cast", []):
            if actor in profile["cast"]:
                profile["cast"][actor] += score
            else:
                profile["cast"][actor] = score
        # Score the director
        director = movie.get("Director")

        if director:
            if director in profile["director"]:
                profile["director"][director] += score
            else:
                profile["director"] = score
        # Score the keywords
        for keyword in movie.get("Keywords", []):
            if keyword in profile["keywords"]:
                profile["keywords"][keyword] += score
            else:
                profile["keywords"][keyword] = score

    return profile
        

def score_movie(candidate, profile):
    """
    Given a candidate movie (dictionary with genres, cast, director, keywords) 
    and profile, return two things:
    - total score: sum of profile scores that match
    - reasons: list of the biggest matches, e.g.
        ["director Christopher Nolan +8", "genre Science Fiction +6"]
    """

    total_score = 0
    reasons = []

    # Check genres
    for genre in candidate["genres"]:
        if genre in profile["genres"]:
            score = profile["genres"][genre]
            total_score += score

            if score != 0:
                reasons.append(f"genre {genre}{score:+}")

    # Check actors
    for actor in candidate["cast"]:
        if actor in profile["cast"]:
            score = profile["cast"][actor]
            total_score += score

            if score != 0:
                reasons.append(f"actor {actor}{score:+}")

    # Check director
    director = candidate["director"]
    if director in profile["director"]:
        score = profile["director"][director]
        total_score += score

        if score != 0:
            reasons.append(f"director {director}{score:+}")

    # Check keywords
    for keyword in candidate["keywords"]:
        if keyword in profile["keywords"]:
            score = profile["keywords"][keyword]
            total_score += score

            if score != 0:
                reasons.append(f"keywords {keyword}{score:+}")

    return total_score, reasons

def recommend(movies, top_n=10):
    """
    1. Build profile from the loop
    2. Get candidate movies (from because_you_liked and/or discover)
    3. Fetch each candidate's details, cast, keywords so they can be scored
    4. Score, sort highest, print top_n with their reasons
    """

    if len(movies) == 0:
        print("Your movie log is empty. Add movies to get recommendations.")
        return

    # Build taste profile
    profile = build_profile(movies)

    # Get candidate movies
    candidates = because_you_liked(movies, min_rating = 0, top_n = 50)

    if not candidates:
        print("No recommendations found.")
        return

    scored_movies = []

    # Fetch candidate's details
    for candidate in candidates:
        tmdb_id = candidate["tmdb_id"]
        
        details = get_details(tmdb_id)
        cast_info = get_cast(tmdb_id)
        keywords = get_keywords(tmdb_id)

        movie_info = {
            "genres": details["Genres"],
            "cast": cast_info["Cast"],
            "keywords": keywords
        }

    total_score, reasons = score_movie(movie_info, profile)
    scored_movies.append({
        "Title": details["Title"],
        "Year": details["Year"],
        "tmdb_id": tmdb_id,
        "Score": total_score,
        "Reasons": reasons
    })

    # Sort by highest score first
    scored_movies.sort(
        key=lambda movie: movie["Score"], 
        reverse = True
    )

    # Print top recommendations
    print("\nMovies recommended for you:")

    for i, movie in enumerate(scored_movies[:top_n], start=1):
        print(f"\n{i}, {movie["Title"]} ({movie["Year"]})")
        print(f"    Taste score: {movie['Score']}")

        if movie["Reasons"]:
            print("     Because you like:")
            for reason in movie["Reasons"][:5]:
                print(f"    - {reason}")

# MENU

def main():
    """
    Load log, then loop forever:
    - print menu options
    - read user's choice
    - call matching function
    - save after anything that changes log
    - break when user chooses Quit
    """
    # Load existing movie log
    movies = load_log()

    while True:
        print("\n==== MOVIE LOG ====")
        print("1. Add a movie")
        print("2. List all movies")
        print("3. Delete a movie")
        print("4. Filter movies by rating")
        print("5. Sort movies")
        print("6. Show statistics")
        print("7. Look up a movie")
        print("8. Because you liked...")
        print("9. Personalized recommendations")
        print("10. Quit")

        choice = input("\nEnter you choices: ")

        if choice == "1":
            add_movie_from_search(movies)
            save_log(movies)
        elif choice == "2":
            list_movies(movies)
        elif choice == "3":
            delete_movie(movies)
            save_log(movies)
        elif choice == "4":
            try:
                min_rating = int(input("Show movies rated at least: "))
                filtered_movies = filter_by_rating(movies, min_rating)
                list_movies(filtered_movies)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "5":
            print("1. Sort by rating (highest first)")
            print("2. Sort by date watched (most recent first)")

            sort_choice = input("Enter your choice: ")

            if sort_choice == "1":
                sorted_movies = sort_movies(movies, "rating")
                list_movies(sorted_movies)

            elif sort_choice == "2":
                sorted_movies = sort_movies(movies, "date watched")
                list_movies(sorted_movies)
            else:
                print("Invalid choice.")
        elif choice == "6":
            show_stats(movies)
        elif choice == "7":
            look_up_movie()
        elif choice == "8":
            recommendations = because_you_liked(movies)

            if recommendations:
                print("\nBecause you liked these movies:")
                for i, movie in enumerate(recommendations, start=1):
                    print(f"{i}. {movie["Title"]} ({movie["Year"]})")

            else:
                print("No recommendations found.")
        elif choice == "9":
            recommend(movies)
        elif choice == "10":
            save_log(movies)
            break
        else:
            print("Invalid choice. Please try again.")
