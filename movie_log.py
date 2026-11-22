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
    