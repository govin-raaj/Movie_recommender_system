from flask import Flask, request, jsonify
import pickle
import pandas as pd
import requests

app = Flask(__name__)


movies_dict = pickle.load(open('movies_dic.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))



def fetch_poster(movieId):
    try:
        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'application/json,text/plain,*/*',
    'Referer': 'https://www.themoviedb.org/',
    'Connection': 'keep-alive'
}
        url = f"https://api.themoviedb.org/3/movie/{movieId}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url,headers=headers ,timeout=5)
        response.raise_for_status()
        data = response.json()
        
        poster_path = data.get('poster_path')
        
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
        
    except requests.exceptions.RequestException as e:
        print(f"Poster fetch failed for {movieId}: {e}")
        return "https://imgs.search.brave.com/MVs_TQ7UIbmuD1zzNHKr2TXcRR8-yBW4UN1tIvQiklw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZG4u/cGl4YWJheS5jb20v/cGhvdG8vMjAyNC8w/Ni8yMi8xNi81NS9h/aS1nZW5lcmF0ZWQt/ODg0NjY3Ml82NDAu/anBn"


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
