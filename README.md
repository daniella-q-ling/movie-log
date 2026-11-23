# 🎬 movie-log
A command-line movie journal in Python. 
Log the movies you watch, look up details and reviews from TMDB, and get personalized recommendations based on your own ratings.

## Features
- Movie log: add, list, and delete movies with your rating, date watched, and notes (saved to a JSON file)
- Stats: total movies watched, average rating, top rated, sort by rating/date
- Movie lookup: search any movie to see its runtime, genres, director, cast, themes, plot, TMDB rating, and reviews
- Auto-fill: pick a movie from search results and its details are saved to your log automatically
- Filtered Discovery: find movies by genre, maximum runtime, release year, actor, or theme
- "Because you liked...": recommendations drawn from the movies you rated highly
- Taste-profile recommender: custom scoring algorithm that explains why each movie is being recommended

## How the Recommender Works
1. Build a taste profile. For every movie in the log, its genres, actors, director, and keywords gets (_your rating_ - 5) added to its score. Movies you loved push those scores up, and movies you disliked pull them down.
2. Gather candidates from TMDB's recommendations for your top-rated movies and from filtered searches, skipping anything already logged.
3. Score each candidate by adding up the profile scores of its genres, cast, director, and themes.
4. Rank and explain. Show the highest-scoring movies with the reasons behind them (for instance, _director Christopher Nolan +8, genre Science Fiction +6."_

## Setup
Requires Python 3 and a free TMDB API key.

## Project Structure
| File | What it does |
|---|---|
| 'movie_log.py' | Menu, log, save/load, stats, and recommendation logic. |
| 'tmdb.py' | All TMDB API calls: search, details, cast, reviews, keywords, discover, recommendations. |

## Credits
This product uses the TMDB API but is not endorsed or certified by TMDB.

Movie data from [The Movie Database(TMDB)](https://www.themoviedb.org/)
