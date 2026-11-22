"""
tmdb.py: every function that relates to TMDB API is here

API key read from TMDB_API_KEY Codespaces
Never paste key directly into this file.

Every request:
requests.get(BASE_URL + "/some/endpoints", params={"api_key": API_KEY, ...})
Then .json() turns response into a Python dictionary.
"""

import os
import requests

API_KEY = os.environ["TMDB_API_KEY"]
BASE_URL = "https://api.themovieb.org/3"
POSTER_URL = "https://image.tmdb.org/t/p/w500"

# PHASE 2, PART 4: First API call

def search_movie(title):
    """
    Search TMDB for 'title' using the /search/movie endpoint
    (params: api_key, query)

    Returns list of dictionaries
    {"ID": 27205, "Title": "Inception", "Year": "2010"}
    """
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title
    }

    response = requests.get(url, params=params)
    return response.json().get("results", [])

# PHASE 2, PART 5: Movie details
def get_details(tmdb_id):
    """
    Call /movie/{tmdb_id},

    Returns dictionary with:
    title, year, runtime (minutes), genres (list of names),
    overview, rating (vote_average), poster_path
    """
    url = f"{BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {
        "Title": data.get("title"),
        "Year": data.get("release_date", "")[:4],
        "Runtime": data.get("runtime"),
        "Genres": [genre["name"] for genre in data.get("genres", [])],
        "Overview": data.get("overview"),
        "Rating": data.get("vote_average"),
        "Poster Path": data.get("poster_path")
    }

def get_cast(tmdb_id):
    """
    Call /movie/{tmdb_id}/credits

    Returns dictionary with:
    {"cast": [first topn actor names], "director": "Name" or None}
    """
    url = f"{BASE_URL}/movie/{tmdb_id}/credits"
    params = {
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    cast = [member["name"] for member in data.get("cast", [])[:5]]
    director = next((member["name"] for member in data.get("crew", []) if member["job"] == "Director"), None)

    return {
        "Cast": cast,
        "Director": director
    }

def get_reviews(tmdb_id, max_reviews = 5, max_length = 200):
    """
    Call /movie/{tmdb_id}/reviews
    Return list of up to max_reviews dictionaries
    {"author": "Name", "content": "Review text (max max_length chars)"}
    
    Movies with no reviews - return empty list, not an error.
    """
    url = f"{BASE_URL}/movie/{tmdb_id}/reviews"
    params = {
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    reviews = []
    for review in data.get("results", [])[:max_reviews]:
        content = review.get("content", "")
        if len(content) > max_length:
            content = content[:max_length] + "..."
        reviews.append({
            "author": review.get("author"),
            "content": content
        })
    return reviews

def get_keywords(tmdb_id):
    """
    Call /movie/{tmdb_id}/keywords
    Return list of keyword names
    """
    url = f"{BASE_URL}/movie/{tmdb_id}/keywords"
    params = {
        "api_key": API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    return [keyword["name"] for keyword in data.get("keywords", [])]

def show_movie_page(tmdb_id):
    """
    Call get_details, get_cast, get_reviews, get_keywords 
    then print everything as a neat info page

    Inception (2010), 148 min, TMDB 8.4/10
    Genres: Action, Science Fiction, Adventure
    Director: Christopher Nolan
    Cast: Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page, Tom Hardy, Ken Watanabe
    Themes: dream, subconscious, heist, ambiguous ending
    Plot: ...
    Reviews:
    - author: "..."
    """
    details = get_details(tmdb_id)
    cast_info = get_cast(tmdb_id)
    reviews = get_reviews(tmdb_id)
    keywords = get_keywords(tmdb_id)
    
    print(f"{details['Title']} ({details['Year']}), {details['Runtime']} min, TMDB {details['Rating']}/10")
    print(f"Genres: {', '.join(details['Genres'])}")
    print(f"Director: {cast_info['Director']}")
    print(f"Cast: {', '.join(cast_info['Cast'])}")
    print(f"Themes: {', '.join(keywords)}")
    print(f"Plot: {details['Overview']}")
    print("Reviews:")
    
    for review in reviews:
        print(f" - author: \"{review['author']}\"")

# PHASE 3, PART 7: Filtered Discover
 
def get_genre():
    """
    Call /genre/movie/list

    Return dictionary mapping genre name to ID
    {"Action": 28, "Comedy": 35, ...
    Discover needs IDs, not names.}
    """
    url = f"{BASE_URL}/genre/movie/list"
    params = {
        "api_key": API_KEY
    }
        
    response = requests.get(url, params=params)
    data = response.json()

    return {genre["name"]: genre["id"] for genre in data.get("genres", [])}

def find_person(name):
    """
    Call /search/person
    Return ID of top result, or None if nothing is found
    """
    url = f"{BASE_URL}/search/person"
    params = {
        "api_key": API_KEY
    }
        
    response = requests.get(url, params=params)
    data = response.json()

    results = data.get("results", [])
    if results:
        return results[0]["id"]
    return None

def find_keyword(word):
    """
    Call /search/keyword with query = word
    Return ID of top result, or None if nothing is foud.
    (Used for theme filters like "time travel".)
    """
    url = f"{BASE_URL}/search/keyword"
    params = {
        "api_key": API_KEY
    }
            
    response = requests.get(url, params=params)
    data = response.json()

    results = data.get("results", [])
    if results:
        return results[0]["id"]
    return None

def discover(genre_id=None, max_runtime=None, min_year=None, 
             person_id=None, keyword_id=None):
    """
    Call /discover/movie with only the filters that aren't None"
        with_genres, with_runtime.lte, primary_release_date.gte (e.g. "2010-01-01"), 
        with_cast, with_keywords
    
    Return a list of results in the same small format as search_movie/
    """
    url = f"{BASE_URL}/search/keyword"
    params = {
        "api_key": API_KEY
    }

    if genre_id is not None:
        params["with_genres"] = genre_id

    if max_runtime is not None:
        params["with_runtime.lte"] = max_runtime

    if min_year is not None:
        params["primary_released_date.gte"] = f"(min_year)-01-01"

    if person_id is not None:
        params["with_cast"] = person_id

    if keyword_id is not None:
        params["with_keywords"] = keyword_id

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("results", [])

# PHASE 3, PART 8: Recommendations from TMDB

def get_recommended(tmdb_id):
    """
    Call /movie/{tmdb_id}/recommendations
    Returns a list of results in the same small format as search_movie.
    """
    url = f"{BASE_URL}/movie/{tmdb_id}/recommendations"
    params = {
        "api_key": API_KEY
    }
                
    response = requests.get(url, params=params)
    data = response.json()

    return data.get("results", [])









