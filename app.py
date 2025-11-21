import streamlit as st
import pandas as pd
import pickle
import requests
from rapidfuzz import process, fuzz
import os

# --- API KEY CONFIGURATION ---
# Replace this with your key. If you leave it, images won't show.
TMDB_API_KEY = "YOUR_TMDB_API_KEY_HERE"

# --- LOAD DATA ---
MODEL_DIR = 'model'
DF_FILE = os.path.join(MODEL_DIR, 'kingmove_df.pkl')
SIM_MATRIX_FILE = os.path.join(MODEL_DIR, 'similarity_matrix.pkl')

@st.cache_resource
def load_data():
    try:
        df = pd.read_pickle(DF_FILE)
        with open(SIM_MATRIX_FILE, 'rb') as f:
            sim = pickle.load(f)
        return df, sim
    except:
        return None, None

df, similarity_matrix = load_data()

# --- HELPER: FETCH POSTER ---
def fetch_poster(title):
    if TMDB_API_KEY == "YOUR_TMDB_API_KEY_HERE": return "https://via.placeholder.com/500x750?text=No+Key"
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={title}"
        data = requests.get(url).json()
        if data['results'] and data['results'][0].get('poster_path'):
            return f"https://image.tmdb.org/t/p/w500/{data['results'][0]['poster_path']}"
    except: pass
    return "https://via.placeholder.com/500x750?text=No+Image"

# --- UI SETUP ---
if df is not None:
    st.set_page_config(layout="wide", page_title="King Move AI")
    st.markdown("<style>.stApp {background-color: #0e1117;}</style>", unsafe_allow_html=True)
    
    st.title("👑 King Move AI Recommender")
    
    # Sidebar
    with st.sidebar:
        st.header("Filters")
        m_type = st.radio("Type", ['movie', 'tv'])
        lang = st.selectbox("Language", ['Any'] + sorted(df['lang'].unique().tolist()))
        # Genre Filter
        all_genres = sorted(list(set([g for sublist in df['genres_list'] for g in sublist])))
        genres = st.multiselect("Genre", all_genres)
        num = st.slider("Count", 5, 20, 10)

    # Main Search
    query = st.text_input("Enter Title", "RRR")
    
    if st.button("Recommend", type="primary"):
        # Logic
        titles = df['title'].tolist()
        match = process.extractOne(query, titles, scorer=fuzz.WRatio)
        
        if match and match[1] >= 60:
            matched_title = match[0]
            idx = df[df['title'] == matched_title].index[0]
            scores = sorted(list(enumerate(similarity_matrix[idx])), key=lambda x: x[1], reverse=True)
            
            results = []
            for i in [x[0] for x in scores[1:50]]:
                row = df.iloc[i]
                if len(results) >= num: break
                
                # Apply Filters
                if row['type'] != m_type: continue
                if lang != 'Any' and row['lang'] != lang: continue
                if genres and not any(g in row['genres_list'] for g in genres): continue
                
                results.append(row)
            
            # Display
            st.success(f"Found: {matched_title}")
            cols = st.columns(5)
            for i, row in enumerate(results):
                with cols[i % 5]:
                    st.image(fetch_poster(row['title']), use_column_width=True)
                    st.caption(row['title'])
        else:
            st.error("Movie not found.")
