import streamlit as st
import pandas as pd
import pickle
import requests
from rapidfuzz import process, fuzz
import os

# --- 1. API KEY CONFIGURATION ---
TMDB_API_KEY = "YOUR_TMDB_API_KEY_HERE"  # <--- PASTE KEY HERE

# --- 2. LOAD DATA ---
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

# --- 3. FETCH POSTER FUNCTION ---
def fetch_poster(title):
    fallback = "https://via.placeholder.com/500x750?text=No+Image"
    if TMDB_API_KEY == "YOUR_TMDB_API_KEY_HERE": return "https://via.placeholder.com/500x750?text=Add+API+Key"
    
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

# --- 4. CORE LOGIC ---
def recommend(title, media_type, lang=None, selected_genres=[], num_recommendations=10):
    # Filters
    mask = (df['type'] == media_type)
    if lang and lang != 'Any': mask &= (df['lang'] == lang)
    if selected_genres: mask &= (df['genres_list'].apply(lambda x: any(g in x for g in selected_genres)))
    
    # Match
    titles = df[mask]['title'].tolist() if not df[mask].empty else df['title'].tolist()
    match = process.extractOne(title, titles, scorer=fuzz.WRatio)
    
    if not match or match[1] < 80: return None, None
        
    matched_title = match[0]
    idx = df[df['title'] == matched_title].index[0]
    
    # Similarity
    scores = sorted(list(enumerate(similarity_matrix[idx])), key=lambda x: x[1], reverse=True)
    
    results = []
    for i in [x[0] for x in scores[1:100]]:
        if len(results) >= num_recommendations: break
        row = df.iloc[i]
        if row['type'] != media_type: continue
        if lang != 'Any' and row['lang'] != lang: continue
        if selected_genres and not any(g in row['genres_list'] for g in selected_genres): continue
        
        results.append({
            'title': row['title'],
            'poster_url': fetch_poster(row['title'])
        })
        
    return matched_title, results

# --- 5. UI SETUP (UPDATED WITH HERO SECTION) ---
if df is not None:
    st.set_page_config(layout="wide", page_title="King Move AI")
    st.markdown("""<style>.stApp {background-color: #0e1117;} img {border-radius: 10px;}</style>""", unsafe_allow_html=True)
    
    st.title("👑 King Move AI Recommender")
    
    with st.sidebar:
        st.header("Filters")
        m_type = st.radio("Type", ['movie', 'tv'])
        lang = st.selectbox("Language", ['Any'] + sorted(df['lang'].unique().tolist()))
        genres = st.multiselect("Genre", sorted(list(set([g for sublist in df['genres_list'] for g in sublist]))))
        num = st.slider("Count", 5, 20, 10)

    query = st.text_input("Enter Title", "RRR")
    
    if st.button("Recommend", type="primary"):
        with st.spinner("Searching..."):
            matched_title, results = recommend(query, m_type, lang, genres, num)
            
            if matched_title:
                # --- NEW HERO SECTION ---
                st.markdown("---")
                col1, col2 = st.columns([1, 4]) # 1 part Image, 4 parts Text
                
                with col1:
                    # Display the poster of the SEARCHED movie
                    st.image(fetch_poster(matched_title), use_container_width=True)
                    
                with col2:
                    st.success(f"✅ Match Found: **{matched_title}**")
                    st.markdown("### 👇 Recommendations for you:")
                    
                    # Display Recommendations Grid inside the second column (or below)
                    rec_cols = st.columns(5)
                    for i, movie in enumerate(results):
                        with rec_cols[i % 5]:
                            st.image(movie['poster_url'], use_container_width=True)
                            st.caption(f"**{movie['title']}**")
            else:
                st.error(f"❌ Movie '{query}' not found (Threshold 80%). Try another title.")
