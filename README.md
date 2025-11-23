---
title: King Move Recommender
emoji: 👑
colorFrom: gray
colorTo: yellow
sdk: streamlit
sdk_version: 1.40.0
app_file: app.py
pinned: false
license: openrail
---

# 🎬 King Move — AI Movie Recommender

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Flask](https://img.shields.io/badge/Backend-Flask-green)
![ML](https://img.shields.io/badge/Model-Content_Based_Filtering-orange)
![API](https://img.shields.io/badge/TMDB-Image_API-yellow)

**An intelligent Movie & TV Show Recommender with both a clean UI and a full REST API.**

This project uses **Content-Based Similarity**, **Fuzzy Matching**, and **TMDB Posters** to deliver Netflix-style recommendations.

It runs in **two modes**:
- 🎨 **Streamlit UI** (User Interface)
- ⚙️ **Flask API** (Developer Integration)

---

## 🚀 Features

### 🎨 Streamlit Frontend (User App)
- Dynamic **hero poster** of the searched movie  
- **Fuzzy Smart Search** (handles typos like `KgF`, `Baahubli`)  
- **Live TMDB Posters API**  
- Top recommendations in a modern UI grid  
- Clean, minimal **dark theme**

### ⚙️ Flask Backend (REST API)
- `/recommend` → returns JSON recommendations  
- Includes title, poster URL, genres, similarity score  
- Ready for mobile apps / websites / ML pipelines  

---

## 🛠️ Tech Stack

| Layer | Tools |
|------|-------|
| Language | Python |
| Frontend | Streamlit |
| Backend | Flask |
| Model | Scikit-Learn (Cosine Similarity) |
| Search | RapidFuzz |
| Data | Pandas, NumPy |
| Posters | TMDB API |

---

## 📁 Project Structure

```bash
King-Move/
│
├── app.py
├── flask_api.py
└── model/
    ├── kingmove_df.pkl
    └── similarity_matrix.pkl
```
---

## ⚡ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/King-Move.git
cd King-Move
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Project

#### ▶️ Option A — Streamlit Web App
```bash
streamlit run app.py
```
Opens at: **http://localhost:8501**

#### ▶️ Option B — Flask API
```bash
python flask_api.py
```
Runs at: **http://localhost:5000**
```

---




