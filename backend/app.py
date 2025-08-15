from flask import Flask, request, jsonify
import pickle
import pandas as pd
import requests
import time
import random

app = Flask(__name__)

# Load movie data & similarity matrix
movies_dict = pickle.load(open('movies_dic.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Persistent requests session to look more like a browser
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/116.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'application/json,text/plain,*/*',
    'Referer': 'https://www.themoviedb.org/',
    'Connection': 'keep-alive'
})

# Cache to avoid refetching posters
poster_cache = {}

def fetch_poster(movieId):
    if movieId in poster_cache:
        return poster_cache[movieId]

    base_url = "https://api.themoviedb.org/3/movie"
    api_key = "8265bd1679663a7ea12ac168da84d2e8"

    for attempt in range(3):
        try:
            url = f"{base_url}/{movieId}?api_key={api_key}&language=en-US"
            response = session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            poster_path = data.get('poster_path')

            if poster_path:
                time.sleep(random.uniform(0.5, 1.3))  # random delay
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                poster_cache[movieId] = poster_url
                return poster_url
            else:
                fallback = ""
                poster_cache[movieId] = fallback
                return fallback

        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            print(f"Poster fetch failed for {movieId} (attempt {attempt+1}): {e}")
            time.sleep(wait_time)

    fallback_error = ""
    poster_cache[movieId] = fallback_error
    return fallback_error


def recommend_movies(movie_name):
    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommendations = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommendations.append({
            "title": movies.iloc[i[0]].title,
            "poster": fetch_poster(movie_id)
        })
    return recommendations


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    movie_name = data.get('movie')
    if not movie_name:
        return jsonify({"error": "Movie name is required"}), 400

    try:
        recommendations = recommend_movies(movie_name)
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    return "Movie Recommender Flask API is running!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
