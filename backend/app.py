from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
from collections import deque

app = Flask(__name__)
CORS(app, resources={r"/recommend": {"origins": "http://localhost:3000"}})

# Store up to 10 recently recommended anime IDs to avoid repeats
recent_anime = deque(maxlen=10)

# Mood to genre mapping
MOOD_GENRE_MAP = {
    'happy': ['Comedy', 'Slice of Life', 'Romance'],
    'sad': ['Drama', 'Psychological', 'Tragedy'],
    'adventurous': ['Adventure', 'Action', 'Fantasy'],
    'relaxing': ['Slice of Life', 'Iyashikei'],
    'thrilling': ['Thriller', 'Mystery', 'Psychological'],
    'excited': ['Action', 'Sports', 'Shounen'],
    'chill': ['Slice of Life', 'Iyashikei', 'Comedy'],
    'romantic': ['Romance', 'Drama'],
    'nostalgic': ['Slice of Life', 'Drama', 'Historical'],
    'mysterious': ['Mystery', 'Psychological', 'Supernatural'],
    'thoughtful': ['Psychological', 'Drama', 'Slice of Life'],
    'energetic': ['Action', 'Shounen', 'Sports'],
    'relaxed': ['Slice of Life', 'Iyashikei', 'Comedy'],
    'melancholic': ['Drama', 'Tragedy', 'Psychological'],
    'inspired': ['Adventure', 'Fantasy', 'Shounen'],
    'anxious': ['Psychological', 'Mystery', 'Drama'],
    'determined': ['Shounen', 'Sports', 'Action']
}

# Jikan API base URL
JIKAN_API = "https://api.jikan.moe/v4"

def fetch_anime_by_genre(genre_name, limit=10):
    """Fetch anime from Jikan API by genre name."""
    genre_map = {
        'Comedy': 4,
        'Slice of Life': 36,
        'Romance': 22,
        'Drama': 8,
        'Psychological': 40,
        'Tragedy': 41,
        'Adventure': 2,
        'Action': 1,
        'Fantasy': 10,
        'Iyashikei': 23,
        'Thriller': 39,
        'Mystery': 7,
        'Sports': 30,
        'Shounen': 27,
        'Historical': 13,
        'Supernatural': 37
    }
    
    genre_id = genre_map.get(genre_name)
    if not genre_id:
        return []

    try:
        response = requests.get(f"{JIKAN_API}/anime", params={'genres': genre_id, 'limit': limit, 'min_score': 6})
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except requests.RequestException as e:
        print(f"Error fetching anime for genre {genre_name}: {e}")
        return []

@app.route('/recommend', methods=['POST'])
def recommend_anime():
    """Endpoint to recommend one anime based on user mood."""
    data = request.get_json()
    mood = data.get('mood', '').lower()

    if not mood or mood not in MOOD_GENRE_MAP:
        return jsonify({'error': 'Invalid or missing mood. Choose from: ' + ', '.join(MOOD_GENRE_MAP.keys())}), 400

    # Get genres for the mood
    genres = MOOD_GENRE_MAP[mood]
    
    # Fetch anime for each genre
    recommendations = []
    for genre in genres:
        anime_list = fetch_anime_by_genre(genre, limit=10)
        for anime in anime_list:
            # Skip recently recommended anime
            if anime['mal_id'] not in recent_anime:
                recommendations.append({
                    'title': anime['title'],
                    'synopsis': anime['synopsis'],
                    'image_url': anime['images']['jpg']['image_url'],
                    'mal_id': anime['mal_id'],
                    'score': anime.get('score', 'N/A'),
                    'episodes': anime.get('episodes', 'N/A')
                })

    # Return one random recommendation or error if none found
    if not recommendations:
        # Clear recent_anime if no new recommendations are available
        recent_anime.clear()
        return jsonify({'error': 'No new anime found for this mood. Try again.'}), 404

    recommendation = random.choice(recommendations)
    # Add to recent_anime to avoid repeats
    recent_anime.append(recommendation['mal_id'])
    return jsonify({'recommendation': recommendation})

@app.route('/')
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'Backend is running'})

if __name__ == '__main__':
    app.run(debug=True)