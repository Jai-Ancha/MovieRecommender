from flask import Flask, request, jsonify
import pandas as pd
import pickle
import requests
import os
from rapidfuzz import process, fuzz

app = Flask(__name__)

# --- 1. CONFIGURATION ---
TMDB_API_KEY = "YOUR_TMDB_API_KEY_HERE" # <--- PASTE SAME KEY HERE
MODEL_DIR = 'model'
DF_FILE = os.path.join(MODEL_DIR, 'kingmove_df.pkl')
SIM_MATRIX_FILE = os.path.join(MODEL_DIR, 'similarity_matrix.pkl')

# --- 2. LOAD DATA ---
try:
    df = pd.read_pickle(DF_FILE)
    with open(SIM_MATRIX_FILE, 'rb') as f:
        similarity_matrix = pickle.load(f)
    print("✅ Models Loaded for API")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    df = None

# --- 3. HELPER: FETCH POSTER FOR API ---
def fetch_poster_url(title):
    """Fetches poster URL for API response"""
    fallback = "https://via.placeholder.com/500x750?text=No+Image"
    if TMDB_API_KEY == "YOUR_TMDB_API_KEY_HERE": return fallback
    
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['results'] and data['results'][0].get('poster_path'):
                return f"https://image.tmdb.org/t/p/w500/{data['results'][0]['poster_path']}"
    except:
        pass
    return fallback

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "message": "👑 King Move AI API is Running", 
        "version": "2.0"
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    if df is None: return jsonify({"error": "Model failed to load"}), 500
    
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Please provide a 'title' in JSON body"}), 400
        
    title = data.get('title')
    
    # --- STRICTER SEARCH LOGIC (Matches app.py) ---
    titles = df['title'].tolist()
    match = process.extractOne(title, titles, scorer=fuzz.WRatio)
    
    # Threshold 80 (Same as UI)
    if not match or match[1] < 80:
        return jsonify({
            "error": "Movie not found",
            "message": "Try another title (Threshold: 80%)"
        }), 404
    
    matched_title = match[0]
    idx = df[df['title'] == matched_title].index[0]
    
    # Similarity Logic
    scores = sorted(list(enumerate(similarity_matrix[idx])), key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in scores[1:11]] # Top 10
    
    # Build Rich Response with POSTERS
    results = []
    for i in top_indices:
        row = df.iloc[i]
        results.append({
            "title": row['title'],
            "type": row['type'],
            "lang": row['lang'],
            "genres": row['genres_list'],
            "poster_url": fetch_poster_url(row['title']) # <--- NOW API GIVES POSTERS!
        })
    
    return jsonify({
        "searched_movie": matched_title,
        "searched_poster": fetch_poster_url(matched_title),
        "recommendations": results
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
