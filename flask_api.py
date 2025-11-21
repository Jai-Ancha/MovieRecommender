from flask import Flask, request, jsonify
import pandas as pd
import pickle
import os
from rapidfuzz import process, fuzz

app = Flask(__name__)

# --- CONFIGURATION ---
MODEL_DIR = 'model'
DF_FILE = os.path.join(MODEL_DIR, 'kingmove_df.pkl')
SIM_MATRIX_FILE = os.path.join(MODEL_DIR, 'similarity_matrix.pkl')

# --- LOAD DATA ---
try:
    df = pd.read_pickle(DF_FILE)
    with open(SIM_MATRIX_FILE, 'rb') as f:
        similarity_matrix = pickle.load(f)
except Exception as e:
    print(f"Error: {e}")
    df = None

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "King Move API is running"})

@app.route('/recommend', methods=['POST'])
def recommend():
    if df is None: return jsonify({"error": "Model failed to load"}), 500
    
    data = request.json
    title = data.get('title')
    
    # Search Logic
    titles = df['title'].tolist()
    match = process.extractOne(title, titles, scorer=fuzz.WRatio)
    if not match or match[1] < 60:
        return jsonify({"error": "Movie not found"}), 404
    
    matched_title = match[0]
    idx = df[df['title'] == matched_title].index[0]
    
    # Similarity Logic
    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in scores[1:11]]
    
    results = df.iloc[top_indices][['title', 'type', 'lang', 'genres_list']].to_dict(orient='records')
    
    return jsonify({"match": matched_title, "recommendations": results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
