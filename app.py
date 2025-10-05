def save_search_and_update_patterns(user_id, data, tmdb):
    from recommendations import enrich_single_pattern
    searches = data[user_id].get("searches", [])
    if searches:
        last_search = searches[-1]
        movie_id = last_search.get("movie_id")
        patterns = data[user_id].get("profile_patterns", {
            "directors": {}, "actors": {}, "countries": {}, "genres": {}, "companies": {}, "languages": {}
        })
    updated = enrich_single_pattern(patterns, movie_id, 0.5, tmdb)
    data[user_id]["profile_patterns"] = updated
    save_user_data(data)
    from recommendations import enrich_user_profile
    enriched = enrich_user_profile(data[user_id], tmdb)
    data[user_id]["profile_patterns"] = enriched
    save_user_data(data)
user_id_global = None

import os
import json
import random
import string
import streamlit as st
from user_utils import get_user_id, USER_DATA_PATH

def load_user_data():
    try:
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return {}

def save_user_data(data):
    import sys
    print("[DEBUG] Guardando datos en user_data.json:", data, file=sys.stderr)
    with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_user_profile():
    user_id = get_user_id(suffix="_profile")
    if not user_id:
        with st.spinner("Cargando perfil de usuario..."):
            st.stop()
    data = load_user_data()
    # Solo crear el usuario si no existe y solo al entrar
    if user_id not in data:
        data[user_id] = {"preferences": [], "searches": [], "ratings": []}
        save_user_data(data)
    return data[user_id]

def update_user_profile(profile):
    user_id = get_user_id(suffix="_update_profile")
    data = load_user_data()
    if user_id not in data:
        # No crear usuario aquí, solo actualizar si existe
        return
    data[user_id] = profile
    
    # Actualizar profile_patterns tras guardar búsqueda
    try:
        from recommendations import enrich_user_profile
        tmdb_api_key = os.getenv("TMDB_API_KEY")
        tmdb = TMDBClient(tmdb_api_key)
        save_search_and_update_patterns(user_id, data, tmdb)
    except Exception as e:
        print(f"Error updating profile_patterns after search: {e}")
    save_user_data(data)
import streamlit as st
from dotenv import load_dotenv
import os
import random
from utils import TMDBClient
# Professional page configuration
st.set_page_config(
    page_title="MovieMatch - Discover Your Next Favorite Movie",
    page_icon="🎬",
    layout="wide"
)

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Verify API key exists
if not TMDB_API_KEY:
    st.error("⚠️ Please configure your TMDB_API_KEY in the .env file")
    st.stop()

# Initialize TMDB client
@st.cache_resource
def init_tmdb_client():
    return TMDBClient(TMDB_API_KEY)

tmdb = init_tmdb_client()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Professional dark theme CSS styling
st.markdown("""
<style>
    /* Global dark theme with impactful typography */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: #0f0f23;
        color: #ffffff;
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #0a0a1a;
        border-right: 1px solid #2a2a3a;
    }
    
    /* Clean spacing for main content */
    .main-content {
        padding: 2rem 0;
    }
    
    /* Movie info container with background - apply to the actual container */
    .movie-info-wrapper {
        background: #161629 !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        margin: 1.5rem 0 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .movie-info-wrapper:hover {
        border-color: #4f46e5 !important;
        transform: translateY(-2px) !important;
    }
    
    /* Style all content inside the wrapper */
    .movie-info-wrapper .stMarkdown,
    .movie-info-wrapper .stMarkdown p,
    .movie-info-wrapper .stMarkdown h3 {
        background: transparent !important;
        color: inherit !important;
    }
    
    /* Apply the wrapper class to Streamlit containers automatically */
    .stContainer > div:has(.movie-content) {
        background: #161629 !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        margin: 1.5rem 0 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        border-radius: 8px;
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.01em;
        width: 200px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .stButton > button:hover {
        background: #4f46e5;
        border-color: #4f46e5;
        color: #ffffff;
        transform: translateY(-1px);
    }
    
    /* Clean input styling with white placeholder */
    .stTextInput > div > div > input {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
        caret-color: #ffffff !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #ffffff !important;
        opacity: 0.7 !important;
    }
    
    /* AGGRESSIVE focus override - eliminate ALL visual changes */
    .stTextInput > div > div > input:focus,
    .stTextInput > div > div > input:active,
    .stTextInput > div > div > input:focus:valid,
    .stTextInput > div > div > input:focus:invalid,
    .stTextInput > div > div > input[aria-invalid="true"]:focus,
    .stTextInput > div > div > input[aria-invalid="false"]:focus,
    .stTextInput > div > div > input:focus-visible,
    .stTextInput > div > div > input[data-baseweb="input"]:focus {
        outline: none !important;
        border: 1px solid #334155 !important;
        border-color: #334155 !important;
        box-shadow: none !important;
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Override any BaseWeb/Streamlit specific styling */
    [data-baseweb="input"]:focus,
    [data-baseweb="input"]:active {
        border-color: #334155 !important;
        box-shadow: none !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > select {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    /* Professional rating display */
    .rating {
        color: #fbbf24;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Enhanced typography with Poppins */
    .stMarkdown {
        color: #e2e8f0;
        font-family: 'Poppins', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Movie title styling */
    .movie-card h3 {
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        line-height: 1.3 !important;
    }
    
    /* Metadata styling */
    .movie-card p {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }
    
    /* Overview text */
    .movie-card p:last-of-type {
        color: #cbd5e1 !important;
        margin-top: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Remove default streamlit styling */
    .stApp > header {
        background: transparent;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: #2a2a3a;
        margin: 2rem 0;
    }
    
    /* Section titles with Poppins - centered with more spacing */
    .section-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 10rem;
        margin-bottom: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2a2a3a;
        text-align: center;
    }
    
    /* COMPREHENSIVE removal of all header anchor links and symbols */
    
    /* Hide all header action elements */
    .stHeaderActionElements,
    [data-testid="stHeaderActionElements"],
    .stMarkdown .stHeaderActionElements {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    /* Hide anchor links in headers */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a,
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
    .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide any link symbols or icons in headers */
    [data-testid="stMarkdownContainer"] h1 > a,
    [data-testid="stMarkdownContainer"] h2 > a,
    [data-testid="stMarkdownContainer"] h3 > a,
    [data-testid="stMarkdownContainer"] h4 > a,
    [data-testid="stMarkdownContainer"] h5 > a,
    [data-testid="stMarkdownContainer"] h6 > a,
    [data-testid="stMarkdownContainer"] h1 .stHeaderActionElements,
    [data-testid="stMarkdownContainer"] h2 .stHeaderActionElements,
    [data-testid="stMarkdownContainer"] h3 .stHeaderActionElements,
    [data-testid="stMarkdownContainer"] h4 .stHeaderActionElements,
    [data-testid="stMarkdownContainer"] h5 .stHeaderActionElements,
    [data-testid="stMarkdownContainer"] h6 .stHeaderActionElements {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Remove any pseudo-elements that might show link symbols */
    h1::after, h2::after, h3::after, h4::after, h5::after, h6::after,
    .stMarkdown h1::after, .stMarkdown h2::after, .stMarkdown h3::after,
    .stMarkdown h4::after, .stMarkdown h5::after, .stMarkdown h6::after {
        display: none !important;
        content: none !important;
    }
    
    /* Force remove any hover states that show link icons */
    h1:hover::after, h2:hover::after, h3:hover::after, 
    h4:hover::after, h5:hover::after, h6:hover::after {
        display: none !important;
        content: none !important;
    }
    
    /* Additional catch-all for any remaining anchor elements */
    .element-container h1 a, .element-container h2 a, .element-container h3 a,
    .element-container h4 a, .element-container h5 a, .element-container h6 a {
        display: none !important;
    }
    
    /* Clean centered search styling */
    .search-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }
    
    /* Remove only auto-generated clickable elements in markdown content */
    [data-testid="stMarkdownContainer"] button:not(.stButton > button),
    [data-testid="stMarkdownContainer"] [role="button"]:not(.stButton > button) {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
</style>
""", unsafe_allow_html=True)

import streamlit as st
# ...existing code...


from movie_display import display_movies

def show_profile_modal():
    import streamlit as st
    genre_list = [
        "Action", "Adventure", "Animation", "Family", "Comedy", "Drama", "Horror",
        "Science Fiction", "Thriller", "Mystery", "Romance", "Documentary"
    ]
    global user_id_global
    if user_id_global is None:
        user_id_global = get_user_id()
    user_id = user_id_global
    try:
        data = load_user_data()
        current_prefs = data.get(user_id, {}).get("preferences", [])
    except Exception:
        current_prefs = []
    st.markdown("## Favorite Genres", unsafe_allow_html=True)
    st.markdown('<span style="color:#b3b3b3; font-size:0.98rem;">Click to select your favorite genres.</span>', unsafe_allow_html=True)
    selected_genres = []
    num_cols = 4
    genre_cols = st.columns(num_cols)
    for row in range(3):
        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < len(genre_list):
                with genre_cols[col]:
                    genre = genre_list[idx]
                    checked = st.checkbox(
                        genre,
                        value=(genre in current_prefs),
                        key=f"profile_genre_{genre}_{user_id}"
                    )
                    if checked:
                        selected_genres.append(genre)
    # Guardar automáticamente solo si la selección no está vacía y ha cambiado
    if selected_genres and set(selected_genres) != set(current_prefs):
        try:
            data = load_user_data()
            if user_id not in data:
                data[user_id] = {"preferences": [], "searches": [], "ratings": []}
            data[user_id]["preferences"] = selected_genres
            save_user_data(data)
        except Exception as e:
            st.error(f"Error saving preferences: {e}")
    st.markdown("---")
    st.markdown("## Watched Movies and Rating", unsafe_allow_html=True)
    # Movie search
    if "reset_search" not in st.session_state:
        st.session_state["reset_search"] = False
    if "reset_rating" not in st.session_state:
        st.session_state["reset_rating"] = False

    search_query = st.text_input("Search movie...", value="" if st.session_state["reset_search"] else None, key="profile_search_movie")
    movie_options = []
    movie_map = {}
    if search_query:
        # Search movies using TMDB
        try:
            from utils import TMDBClient
            tmdb_api_key = os.getenv("TMDB_API_KEY")
            tmdb = TMDBClient(tmdb_api_key)
            results = tmdb.search_movies(search_query)
            for movie in results[:3]:
                title = f"{movie['title']} ({movie.get('release_date', '')[:4]})"
                movie_options.append(title)
                movie_map[title] = movie
        except Exception as e:
            st.error(f"Error searching movies: {e}")
    selected_movie = st.selectbox("Select a movie", movie_options, key="profile_select_movie")
    rating = st.slider("Rating", min_value=0.0, max_value=10.0, value=5.0 if st.session_state["reset_rating"] else 5.0, step=0.5, key="profile_rating")
    if st.button("Save", key="profile_add_rating"):
        # Comprobación previa: mostrar el user_id si existe antes de guardar
        if selected_movie and selected_movie in movie_map:
            movie = movie_map[selected_movie]
            movie_id = movie['id']
            title = movie['title']
            # Solo obtener el user_id si ya existe en localStorage
            
            # Usar el user_id ya guardado en session_state si existe
            user_id = user_id_global
            if not user_id:
                st.error("No se encontró el ID de usuario en session_state. Recarga la página o revisa la configuración del navegador.")
                return
            data = load_user_data()
            profile = data.get(user_id, {"preferences": [], "searches": [], "ratings": []})
            # Evitar duplicados: si ya existe una puntuación para ese movie_id, la actualizamos
            ratings = profile.get("ratings", [])
            found = False
            for r in ratings:
                if r.get("movie_id") == movie_id:
                    r["rating"] = rating
                    found = True
                    break
            if not found:
                ratings.append({"movie_id": movie_id, "title": title, "rating": rating})
            profile["ratings"] = ratings
            data[user_id] = profile
            tmdb_api_key = os.getenv("TMDB_API_KEY")
            tmdb = TMDBClient(tmdb_api_key)
            from recommendations import enrich_single_pattern
            ratings = data[user_id].get("ratings", [])
            if ratings:
                last_rating = ratings[-1]
                movie_id = last_rating.get("movie_id")
                weight = float(last_rating.get("rating", 0)) / 10
                patterns = data[user_id].get("profile_patterns", {
                    "directors": {}, "actors": {}, "countries": {}, "genres": {}, "companies": {}, "languages": {}
                })
                updated = enrich_single_pattern(patterns, movie_id, weight, tmdb)
                data[user_id]["profile_patterns"] = updated
            save_user_data(data)
        else:
            st.warning("Select a valid movie before saving.")
    # Show watched movies list
    user_id = get_user_id(suffix="_list_ratings")
    data = load_user_data()
    profile = data.get(user_id, {"preferences": [], "searches": [], "ratings": []})
    ratings = profile.get("ratings", [])
    if ratings:
        st.markdown("### Watched Movies List")
        import pandas as pd
        df = pd.DataFrame(ratings)
        df_watched = df[["title", "rating"]].rename(columns={"title": "Movie", "rating": "Rating"})
        df_watched["Rating"] = df_watched["Rating"].map(lambda x: f"{x:.1f}")
        df_watched.index = df_watched.index + 1
        styled_df = df_watched.style.set_properties(subset=["Rating"], **{"text-align": "left"})
        st.dataframe(styled_df, width=800)

# Estado para mostrar pantalla de perfil
if "show_profile" not in st.session_state:
    st.session_state["show_profile"] = False


# --- Navegación entre Profile y Main Menu ---


# --- Navegación entre Profile y Main Menu con cambio inmediato ---
if "show_profile" not in st.session_state:
    st.session_state["show_profile"] = False
col_nav2, col_nav1 = st.columns([8, 1])
with col_nav1:
    if st.session_state["show_profile"]:
        if st.button("Main Menu", key="btn_back_main"):
            st.session_state["show_profile"] = False
    else:
        if st.button("Profile", key="btn_profile"):
            st.session_state["show_profile"] = True

if st.session_state["show_profile"]:
    show_profile_modal()
    # Logic to exit profile (if needed)
    if st.session_state.get("volver_click", False):
        st.session_state["show_profile"] = False
        st.session_state["volver_click"] = False
    if "volver" in st.query_params:
        st.session_state["show_profile"] = False
    # --- Botón de política de privacidad solo en modo perfil ---
    st.markdown("<div style='height:4rem'></div>", unsafe_allow_html=True)
    if 'show_privacy' not in st.session_state:
        st.session_state['show_privacy'] = False
    if st.button("Privacy Policy", key="btn_privacy_profile"):
        st.session_state['show_privacy'] = not st.session_state['show_privacy']
    if st.session_state['show_privacy']:
        st.markdown("""
        <div style='background:#181826;border-radius:10px;padding:1.2rem 1.5rem;margin:2.5rem 0 0 0;box-shadow:0 2px 12px #0002;'>
            <h4 style='color:#fff;margin-bottom:0.7rem;'>Privacy Policy</h4>
            <div style='color:#cbd5e1;font-size:1rem;'>
                <p><strong>Your privacy and data security are our top priorities.</strong></p>
                <ul style='margin-bottom:1.2rem;'>
                    <li><strong>Anonymous & Confidential:</strong> All data is stored anonymously and securely. No personal information or identifiers are ever collected or linked to you.</li>
                    <li><strong>Device Independence & Security:</strong> Each device and browser is completely independent. Your data is only stored locally and cannot be accessed from other devices or browsers. This method is the safest and means you never need to create an account—your data is never associated with any person.</li>
                    <li><strong>Purpose of Data:</strong> The only reason your data is stored is to enable the AI-powered recommendation system to adapt to your preferences and improve your experience.</li>
                    <li><strong>Types of Data Stored:</strong>
                        <ul>
                            <li>Favorite genres (your selected movie genres)</li>
                            <li>Searches made using the main page search bar</li>
                            <li>Watched and rated movies</li>
                        </ul>
                    </li>
                    <li><strong>Freedom to Delete Your Data:</strong> You are always free to delete your data. To do so, simply remove the MovieMatch key from your browser's local storage (safe storage). <br><br>
                        <em>How to delete your data:</em>
                        <ul>
                            <li>Open your browser's developer tools (usually by pressing F12).</li>
                            <li>Go to the <strong>Application</strong> or <strong>Storage</strong> tab.</li>
                            <li>Find <strong>localStorage</strong> and look for the key named <strong>moviematch_user_id</strong>.</li>
                            <li>Delete this key. All your data will be removed instantly.</li>
                        </ul>
                        <span style='opacity:0.7;'>Note: Each time you visit the page, a new anonymous key will be created automatically.</span>
                        <span style='opacity:0.7;'>Deleting your data only affects the current device and browser.</span>
                    </li>
                    <li><strong>No Third Parties & No Ads:</strong> There are no third-party services, trackers, or advertising on this website. Your data is never shared, sold, or used for any purpose other than providing personalized recommendations.</li>
                    <li><strong>No Option to Deny Usage:</strong> The tool requires data to function. You cannot opt out of data usage, but you can always delete your information as described above.</li>
                    <li><strong>Policy Updates:</strong> If the way your data is handled ever changes, this privacy policy will be updated to reflect those changes.</li>
                </ul>
                <p style='margin-top:1.2rem;'>Everything is handled with maximum security and anonymity.</p>
                <p style='margin-top:0.8rem;'>All movie information is sourced via the TMDB API (The Movie Database). No movie data is stored locally; it is fetched in real time from TMDB.</p>
                <p style='margin-top:0.8rem;'>If you have any questions about your data or privacy, feel free to contact the developer at: <strong>arnausalaaraujo@gmail.com</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Main app content (filters, recommendations, etc.)
    # Todo el contenido principal debe ir dentro de este bloque
    st.markdown('''
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="font-size: 4rem; font-weight: 800; color: #ffffff; margin-bottom: 0.5rem; 
                   background: linear-gradient(135deg, #ffffff 0%, #4f46e5 50%, #06b6d4 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   background-clip: text; letter-spacing: -0.02em; margin: 0;">
            MOVIEMATCH
        </h1>
        <h2 style="color: #cbd5e1; font-size: 1.35rem; font-weight: 600; margin: 0.5rem 0 0 0;">
            Descubre tu próxima película favorita con recomendaciones inteligentes
        </h2>
    </div>
    ''', unsafe_allow_html=True)


    # Centered search bar - funcional e independiente
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_query = st.text_input("Search Movies", placeholder="Type a movie name...", label_visibility="collapsed", key="main_search")

    # Mostrar resultados de búsqueda solo si hay búsqueda activa, sin modificar el estado de los filtros
    if search_query:
        # Guardar búsqueda en el perfil del usuario
        import difflib
        from datetime import datetime
        def similar(a, b):
            return difflib.SequenceMatcher(None, a, b).ratio()

        user_id = get_user_id()
        data = load_user_data()
        if user_id:
            if user_id not in data:
                data[user_id] = {"preferences": [], "searches": [], "ratings": []}
            searches = data[user_id].get("searches", [])
            best_match = None
            best_score = 0.0
            for entry in searches:
                term = entry.get("term", "").lower()
                score = similar(term, search_query.lower())
                if score > 0.8 and score > best_score:
                    best_match = entry
                    best_score = score
                if term == search_query.lower():
                    best_match = entry
                    best_score = 1.0
                    break
            # Usar el primer renderizado (filtered_results[0]) para guardar el id y nombre
            filtered_results = [m for m in tmdb.search_movies(search_query) if m.get('popularity', 0) > 2 and m.get('release_date')]
            render_name = None
            render_id = None
            if filtered_results:
                render_name = filtered_results[0].get('title')
                render_id = filtered_results[0].get('id')
            now_iso = datetime.now().isoformat()
            if best_match:
                best_match["count"] += 1
                best_match["last_search"] = now_iso
                if render_name and best_match["term"].lower() != render_name.lower():
                    best_match["term"] = render_name
                if render_id:
                    best_match["movie_id"] = render_id
            else:
                term_to_save = render_name if render_name else search_query
                searches.append({"term": term_to_save, "count": 1, "movie_id": render_id, "last_search": now_iso})
            data[user_id]["searches"] = searches
            # Enriquecer patrones solo con la última búsqueda
            from recommendations import enrich_single_pattern
            patterns = data[user_id].get("profile_patterns", {
                "directors": {}, "actors": {}, "countries": {}, "genres": {}, "companies": {}, "languages": {}
            })
            last_search = searches[-1] if searches else None
            if last_search:
                movie_id = last_search.get("movie_id")
                tmdb_api_key = os.getenv("TMDB_API_KEY")
                tmdb_local = TMDBClient(tmdb_api_key)
                updated = enrich_single_pattern(patterns, movie_id, 0.5, tmdb_local)
                data[user_id]["profile_patterns"] = updated
            save_user_data(data)
        results = tmdb.search_movies(search_query)
        filtered_results = [m for m in results if m.get('popularity', 0) > 2 and m.get('release_date')]
        st.markdown(f"<div style='margin-top:2rem;'><h3 style='color:#fff;'>Search Results for: <span style='color:#4f46e5'>{search_query}</span></h3></div>", unsafe_allow_html=True)
        if filtered_results:
            cols = st.columns([0.01, 0.32, 0.01, 0.32, 0.01, 0.32, 0.01])
            num_cards = min(len(filtered_results), 15)
            from utils import TMDBClient
            tmdb_api_key = os.getenv("TMDB_API_KEY")
            tmdb_local = TMDBClient(tmdb_api_key)
            # Solo obtener detalles completos para el primer renderizado
            first_details = tmdb_local.get_movie_details(filtered_results[0].get('id')) if filtered_results[0].get('id') else filtered_results[0]
            for i in range(num_cards):
                movie = filtered_results[i]
                col = cols[1 + (i % 3) * 2]
                with col:
                    if i == 0:
                        details = first_details
                    else:
                        details = movie
                    title = details.get('title', movie.get('title', 'Unknown'))
                    year = details.get('release_date', '')[:4] if details.get('release_date') else ''
                    poster_url = details.get('poster_path')
                    runtime = details.get('runtime') if i == 0 else None
                    genres = details.get('genres') if i == 0 else None
                    nota = details.get('vote_average')
                    duration = f"{runtime} min" if runtime else ''
                    genre_html = ''
                    genre_spans = ''
                    # Mostrar géneros si existen, si no mostrar 'Not available' en todos los casos
                    if i == 0 and isinstance(genres, list) and genres:
                        genre_spans = ''.join([f'<span style="background:#23234a;color:#fff;padding:0.3em 0.8em;border-radius:16px;font-size:0.95em;display:inline-block;">{g["name"]}</span>' for g in genres if 'name' in g])
                    elif i > 0 and isinstance(movie.get('genre_ids'), list) and movie.get('genre_ids'):
                        # Si hay genre_ids, mostrar como 'Not available' (no hay nombres)
                        genre_spans = ''
                    if genre_spans:
                        genre_html = f'<div style="margin-top:0.7rem;display:flex;justify-content:center;flex-wrap:wrap;gap:0.5rem;">{genre_spans}</div>'
                    else:
                        genre_html = '<div style="margin-top:0.7rem;color:#94a3b8;text-align:center;font-size:0.95em;">Not available</div>'
                    nota_html = ''
                    if nota is not None:
                        if nota == 0:
                            nota_html = "<span style='color:#fff;font-weight:600;'>-</span>"
                        else:
                            if nota >= 7:
                                nota_color = '#22c55e'
                            elif nota >= 5:
                                nota_color = '#f59e42'
                            else:
                                nota_color = '#ef4444'
                            nota_html = f"<span style='color:{nota_color};font-weight:600;'>{nota}</span>"
                    stats_html = f"<div style='font-size:1.05em;margin-bottom:0.5em;text-align:center;'>{year} &nbsp;|&nbsp; {duration} &nbsp;|&nbsp; {nota_html}</div>"
                    if poster_url:
                        poster_html = f'<img src="{tmdb_local.get_poster_url(poster_url)}" alt="Poster" style="width: 170px; height: 255px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 12px #0002;" />'
                    else:
                        poster_html = '<div style="width:170px;height:255px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888;">No Image</div>'
                    info_html = f"""
                    <div class='movie-info-wrapper' style='width: 100%; height: 340px; display: flex; flex-direction: row; align-items: flex-start; justify-content: flex-start; gap: 1.2rem; padding: 1rem; margin-bottom: 2.5rem;'>
                        <div style='flex-shrink:0;'>
                            {poster_html}
                        </div>
                        <div style='flex:1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow-wrap: break-word;'>
                            <h3 style='font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center; overflow-wrap: break-word;'>{title}</h3>
                            {stats_html}
                            {genre_html}
                        </div>
                    </div>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)
        else:
            st.info("No relevant movies found.")

    # ...resto del contenido de películas y navegación principal...
    st.markdown('<div style="margin: 3rem 0;"></div>', unsafe_allow_html=True)

    # Custom CSS for active button
    st.markdown('''
    <style>
    .stButton > button.active-btn {
        background: #23234a !important;
        color: #fff !important;
        border: 1.5px solid #6366f1 !important;
        font-weight: 600 !important;
        box-shadow: 0 0 0 2px #23234a33;
        transition: background 0.2s, border 0.2s;
    }
    .stButton > button:not(.active-btn):hover {
        border: 1.5px solid #6366f1 !important;
        background: #23234a !important;
        color: #fff !important;
    }

    </style>
    ''', unsafe_allow_html=True)

    # Subtle separator and section title above navigation buttons
    st.markdown('''
    <div style="margin-top: 1.2rem; margin-bottom: 0.7rem;">
        <hr style="border:none;height:1px;background:rgba(120,120,180,0.12);margin-bottom:0.4rem;">
        <h3 style="font-family: 'Poppins', sans-serif; font-size: 1.08rem; font-weight: 500; color: #bfc7d5; text-align: center; margin-bottom: 0.1rem; letter-spacing: 0.01em;">
            Filtered Search
        </h3>
    </div>
    ''', unsafe_allow_html=True)

    def nav_button(label, key, page_name):
        is_active = st.session_state.current_page == page_name
        btn_class = "active-btn" if is_active else ""
        btn_html = f"""
        <button class='{btn_class}' style='width:100%;height:3.5rem;border-radius:8px;background:#1e293b;color:#e2e8f0;border:1px solid #334155;font-weight:500;font-size:0.85rem;transition:all 0.2s cubic-bezier(0.4,0,0.2,1);letter-spacing:0.01em;'>{label}</button>
        """
        clicked = st.markdown(f"<div onclick=\"document.getElementById('{key}').click();\">{btn_html}</div>", unsafe_allow_html=True)
        if st.button(label, key=key):
            if page_name == 'random':
                st.session_state.current_page = 'random'
                st.session_state.random_movie_idx = random.randint(0, 999999)
            elif is_active:
                st.session_state.current_page = 'home'
            else:
                st.session_state.current_page = page_name

    col_space1, col1, col_gap1, col2, col_gap2, col3, col_gap3, col4, col_gap4, col5, col_gap5, col6, col_gap6, col7, col_space2 = st.columns([0.29, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.41])

    with col1:
        nav_button("Popular Movies", "popular", "popular")
    with col2:
        nav_button("Now Playing", "now_playing", "now_playing")
    with col3:
        nav_button("Top Rated", "top_rated", "top_rated")
    with col4:
        nav_button("Coming Soon", "coming_soon", "coming_soon")
    with col5:
        nav_button("By Genre", "by_genre", "by_genre")
    with col6:
        nav_button("AI Recommendations", "ai_recs", "ai_recommendations")
    with col7:
        nav_button("Random Pick", "random", "random")


# Navigation logic: show movies based on selected page
if st.session_state.current_page == 'home' and not st.session_state.get('show_profile', False):
    import datetime
    with st.spinner("Loading movie of the day..."):
        popular_movies = tmdb.get_popular_movies()
    if popular_movies:
        # Use today's date as seed for deterministic random selection
        today_str = datetime.date.today().isoformat()
        rng = random.Random(today_str)
        random_movie = rng.choice(popular_movies)
        st.markdown('''
        <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
            <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
            <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
                Movie of the Day
            </h2>
        </div>
        ''', unsafe_allow_html=True)
        # Use the same columns layout as other screens, but only fill the center card
        cols = st.columns([0.01, 0.32, 0.01, 0.32, 0.01, 0.32, 0.01])
        with cols[3]:
            details = tmdb.get_movie_details(random_movie['id']) if 'id' in random_movie else random_movie
            poster_url = tmdb.get_poster_url(details.get('poster_path'))
            runtime = details.get('runtime')
            genres = details.get('genres')
            year = details.get('release_date', '')[:4] if details.get('release_date') else ''
            duration = f"{runtime} min" if runtime else ''
            nota = details.get('vote_average')
            if nota is not None:
                if nota >= 7:
                    nota_color = '#22c55e'
                elif nota >= 5:
                    nota_color = '#f59e42'
                else:
                    nota_color = '#ef4444'
                nota_html = f"<span style='color:{nota_color};font-weight:600;'>{nota}</span>"
            else:
                nota_html = ''
            stats_html = f"<div style='font-size:1.05em;margin-bottom:0.5em;text-align:center;'>{year} &nbsp;|&nbsp; {duration} &nbsp;|&nbsp; {nota_html}</div>"
            providers_html = ''
            try:
                import requests
                api_key = tmdb.api_key
                movie_id = details.get('id')
                if movie_id:
                    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
                    resp = requests.get(url, timeout=5)
                    data = resp.json()
                    us = data.get('results', {}).get('US', {})
                    provider_list = []
                    for key in ['flatrate', 'rent', 'buy']:
                        if key in us:
                            provider_list += us[key]
                    if provider_list:
                        all_platforms = []
                        for key in ['flatrate', 'rent', 'buy']:
                            if key in us:
                                all_platforms += us[key]
                        filtered_providers = [p for p in all_platforms if p.get('provider_name') == 'Netflix']
                        extra = [p for p in all_platforms if ('Netflix' not in p.get('provider_name', '') and p.get('provider_name') != 'Amazon Prime Video with Ads')]
                        provider_list = (filtered_providers + extra)[:2]
                        if provider_list:
                            providers_html = '<div style="margin-bottom:0.7rem;display:flex;justify-content:center;flex-wrap:wrap;gap:0.5rem;">' + \
                                ''.join([f'<span style="background:#4f46e5;color:#fff;padding:0.3em 0.8em;border-radius:16px;font-size:0.95em;display:inline-block;">{p["provider_name"]}</span>' for p in provider_list if 'provider_name' in p]) + '</div>'
                        else:
                            providers_html = '<div style="margin-bottom:0.7rem;text-align:center;color:#f59e42;font-size:1em;">Not available right now</div>'
            except Exception:
                pass
            genre_html = ''
            if isinstance(genres, list) and genres:
                genres = genres[:3]
                genre_html = '<div style="margin-top:0.7rem;display:flex;justify-content:center;flex-wrap:wrap;gap:0.5rem;">' + \
                    ''.join([f'<span style="background:#23234a;color:#fff;padding:0.3em 0.8em;border-radius:16px;font-size:0.95em;display:inline-block;">{g["name"]}</span>' for g in genres if 'name' in g]) + '</div>'
            providers_block = providers_html if providers_html else ''
            genre_block = genre_html if genre_html else ''
            extra_info = ''
            if providers_block or genre_block:
                extra_info = f"<div style='margin-top: 0.5rem; font-size: 1rem;'>{providers_block}{genre_block}</div>"
            info_html = f"""
            <div class='movie-info-wrapper' style='width: 100%; height: 320px; display: flex; flex-direction: row; align-items: flex-start; justify-content: flex-start; gap: 1.2rem; padding: 1rem; margin-bottom: 2.5rem;'>
                <div style='flex-shrink:0;'>
                    {f'<img src="{poster_url}" alt="Poster" style="width: 170px; height: 255px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 12px #0002;" />' if poster_url else '<div style="width:170px;height:255px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888;">No Image</div>'}
                </div>
                <div style='flex:1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;'>
                    <h3 style='font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center;'>{details.get('title', random_movie.get('title', ''))}</h3>
                    {stats_html}
                    {extra_info}
                </div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
        # Add the date below the card, outside the card container
        # Format date as MM/DD/YYYY
        today_us = datetime.date.today().strftime('%m/%d/%Y')
        st.markdown(f"<div style='text-align:center;margin-top:-1.2rem;margin-bottom:2.5rem;color:#94a3b8;font-size:0.98em;opacity:0.7;'>Date: {today_us}</div>", unsafe_allow_html=True)
    else:
        st.info("Welcome to MovieMatch! Use the search bar or explore different categories to discover great movies.")

elif st.session_state.current_page == 'popular':
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            Popular Movies
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    with st.spinner("Loading popular movies..."):
        popular_movies = tmdb.get_popular_movies()
    display_movies(popular_movies, "Popular Movies")

elif st.session_state.current_page == 'now_playing':
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            Now Playing in Theaters
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    with st.spinner("Loading now playing movies..."):
        now_playing_movies = tmdb.get_now_playing_movies()
    display_movies(now_playing_movies, "Now Playing in Theaters")

elif st.session_state.current_page == 'top_rated':
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            Top Rated Movies
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    with st.spinner("Loading top rated movies..."):
        top_movies = tmdb.get_top_rated_movies()
    display_movies(top_movies, "Top Rated Movies")

elif st.session_state.current_page == 'coming_soon':
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            Coming Soon
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    with st.spinner("Loading upcoming movies..."):
        upcoming_movies = tmdb.get_upcoming_movies()
    display_movies(upcoming_movies, "Coming Soon")

elif st.session_state.current_page == 'random':
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            Random Movie
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    # No spinner for random movie mode
    popular_movies = tmdb.get_popular_movies()
    if popular_movies:
        idx = getattr(st.session_state, 'random_movie_idx', random.randint(0, len(popular_movies)-1))
        random_movie = popular_movies[idx % len(popular_movies)]
        # Center the random movie card like the daily movie
        cols = st.columns([0.01, 0.32, 0.01, 0.32, 0.01, 0.32, 0.01])
        with cols[3]:
            details = tmdb.get_movie_details(random_movie['id']) if 'id' in random_movie else random_movie
            poster_url = tmdb.get_poster_url(details.get('poster_path'))
            runtime = details.get('runtime')
            genres = details.get('genres')
            year = details.get('release_date', '')[:4] if details.get('release_date') else ''
            duration = f"{runtime} min" if runtime else ''
            nota = details.get('vote_average')
            if nota is not None:
                if nota >= 7:
                    nota_color = '#22c55e'
                elif nota >= 5:
                    nota_color = '#f59e42'
                else:
                    nota_color = '#ef4444'
                nota_html = f"<span style='color:{nota_color};font-weight:600;'>{nota}</span>"
            else:
                nota_html = ''
            stats_html = f"<div style='font-size:1.05em;margin-bottom:0.5em;text-align:center;'>{year} &nbsp;|&nbsp; {duration} &nbsp;|&nbsp; {nota_html}</div>"
            providers_html = ''
            try:
                import requests
                api_key = tmdb.api_key
                movie_id = details.get('id')
                if movie_id:
                    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
                    resp = requests.get(url, timeout=5)
                    data = resp.json()
                    us = data.get('results', {}).get('US', {})
                    provider_list = []
                    for key in ['flatrate', 'rent', 'buy']:
                        if key in us:
                            provider_list += us[key]
                    if provider_list:
                        all_platforms = []
                        for key in ['flatrate', 'rent', 'buy']:
                            if key in us:
                                all_platforms += us[key]
                        filtered_providers = [p for p in all_platforms if p.get('provider_name') == 'Netflix']
                        extra = [p for p in all_platforms if ('Netflix' not in p.get('provider_name', '') and p.get('provider_name') != 'Amazon Prime Video with Ads')]
                        provider_list = (filtered_providers + extra)[:2]
                        if provider_list:
                            providers_html = '<div style="margin-bottom:0.7rem;display:flex;justify-content:center;flex-wrap:wrap;gap:0.5rem;">' + \
                                ''.join([f'<span style="background:#4f46e5;color:#fff;padding:0.3em 0.8em;border-radius:16px;font-size:0.95em;display:inline-block;">{p["provider_name"]}</span>' for p in provider_list if 'provider_name' in p]) + '</div>'
                        else:
                            providers_html = '<div style="margin-bottom:0.7rem;text-align:center;color:#f59e42;font-size:1em;">Not available right now</div>'
            except Exception:
                pass
            genre_html = ''
            if isinstance(genres, list) and genres:
                genres = genres[:3]
                genre_html = '<div style="margin-top:0.7rem;display:flex;justify-content:center;flex-wrap:wrap;gap:0.5rem;">' + \
                    ''.join([f'<span style="background:#23234a;color:#fff;padding:0.3em 0.8em;border-radius:16px;font-size:0.95em;display:inline-block;">{g["name"]}</span>' for g in genres if 'name' in g]) + '</div>'
            providers_block = providers_html if providers_html else ''
            genre_block = genre_html if genre_html else ''
            extra_info = ''
            if providers_block or genre_block:
                extra_info = f"<div style='margin-top: 0.5rem; font-size: 1rem;'>{providers_block}{genre_block}</div>"
            info_html = f"""
            <div class='movie-info-wrapper' style='width: 100%; height: 320px; display: flex; flex-direction: row; align-items: flex-start; justify-content: flex-start; gap: 1.2rem; padding: 1rem; margin-bottom: 2.5rem;'>
                <div style='flex-shrink:0;'>
                    {f'<img src="{poster_url}" alt="Poster" style="width: 170px; height: 255px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 12px #0002;" />' if poster_url else '<div style="width:170px;height:255px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888;">No Image</div>'}
                </div>
                <div style='flex:1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;'>
                    <h3 style='font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center;'>{details.get('title', random_movie.get('title', ''))}</h3>
                    {stats_html}
                    {extra_info}
                </div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
    else:
        st.error("Unable to get random movie at this time.")

elif st.session_state.current_page == 'ai_recommendations':
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            AI Recommendations
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    from recommendations import show_recommendations_page
    show_recommendations_page(tmdb)
elif st.session_state.current_page == 'by_genre':
    # Separator and title for genre filter section
    st.markdown('''
    <div style="margin-top: 2.5rem; margin-bottom: 1.2rem;">
        <hr style="border:none;height:2px;background:rgba(79,70,229,0.25);margin-bottom:0.7rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.35rem; font-weight: 600; color: #e2e8f0; text-align: center; margin-bottom: 0.2rem; letter-spacing: 0.01em;">
            Filter by Genre
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    with st.spinner("Loading genres..."):
        genres = tmdb.get_genres()
    important_genres = [
        'Action', 'Adventure',
        'Animation', 'Family',
        'Comedy', 'Drama',
        'Horror', 'Science Fiction',
        'Thriller', 'Mystery',
        'Romance', 'Documentary'
    ]
    genre_map = {g['name']: g['id'] for g in genres if g['name'] in important_genres}
    # Track selected genre in session state for persistent selection
    if 'selected_genre' not in st.session_state:
        st.session_state.selected_genre = None
    selected_genre = st.session_state.selected_genre
    fixed_btn_width = 60  # px, reduced width for compact layout
    st.markdown(f"""
    <style>
    .genre-row .stButton > button {{
        width: {fixed_btn_width}px !important;
        min-width: {fixed_btn_width}px !important;
        max-width: {fixed_btn_width}px !important;
        border: 1.5px solid #6366f1 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        border-radius: 8px !important;
        height: 3.2rem !important;
        margin-bottom: 0.7rem !important;
        background: none !important;
        color: #e2e8f0 !important;
        transition: all 0.2s cubic-bezier(0.4,0,0.2,1);
        letter-spacing: 0.01em;
        box-shadow: none !important;
        text-align: center !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    .genre-row .stButton > button:hover {{
        border-color: #4f46e5 !important;
        color: #fff !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    # Split genres into two rows of 6
    row1_genres = important_genres[:6]
    row2_genres = important_genres[6:]
    row_cols = [0.5, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.5]
    with st.container():
        st.markdown('<div class="genre-row">', unsafe_allow_html=True)
        genre_row1 = st.columns(row_cols)
        for idx, genre_name in enumerate(row1_genres):
            col_idx = 1 + idx * 2
            with genre_row1[col_idx]:
                is_active = selected_genre == genre_name
                if st.button(genre_name, key=f"genre_{genre_name}"):
                    if not is_active:
                        st.session_state.selected_genre = genre_name

                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="genre-row">', unsafe_allow_html=True)
        genre_row2 = st.columns(row_cols)
        for idx, genre_name in enumerate(row2_genres):
            col_idx = 1 + idx * 2
            with genre_row2[col_idx]:
                is_active = selected_genre == genre_name
                if st.button(genre_name, key=f"genre_{genre_name}"):
                    if not is_active:
                        st.session_state.selected_genre = genre_name

                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # If a genre is selected, show movies for that genre below the buttons
    if selected_genre:
        selected_genre_id = genre_map[selected_genre]
        st.markdown(f"""
        <div style='margin-top:2.5rem;margin-bottom:0.7rem;'>
            <h3 style='font-family:Poppins,sans-serif;font-size:1.25rem;font-weight:600;color:#fff;text-align:center;margin-bottom:0.2rem;'>
                {selected_genre} Movies
            </h3>
            <hr style='border:none;height:1.5px;background:rgba(79,70,229,0.18);margin:0.7rem 0 1.2rem 0;'>
        </div>
        """, unsafe_allow_html=True)
        with st.spinner(f"Loading {selected_genre} movies..."):
            genre_movies = tmdb.discover_movies([selected_genre_id])
        # Show only 6 movies
        display_movies(genre_movies[:6], f"")