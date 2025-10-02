
import os
import uuid
import json

# --- Backend: gestión de usuario anónimo y datos ---
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')

def get_user_id():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def load_user_data():
    try:
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return {"users": {}}

def save_user_data(data):
    with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_user_profile():
    user_id = get_user_id()
    data = load_user_data()
    if user_id not in data["users"]:
        data["users"][user_id] = {"preferences": [], "searches": []}
        save_user_data(data)
    return data["users"][user_id]

def update_user_profile(profile):
    user_id = get_user_id()
    data = load_user_data()
    data["users"][user_id] = profile
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


# Pantalla de perfil como modal de pantalla completa
def show_profile_modal():
    # Color de fondo normal de Streamlit (por defecto: #0f172a)
    background_color = "#0f172a"
    st.markdown(
        f'''
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: {background_color}; z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="width: 100%; max-width: 400px; padding: 2rem; border-radius: 18px; box-shadow: 0 4px 32px rgba(0,0,0,0.12); background: transparent;">
                <h2 style="text-align:center; color:#fff; margin-bottom:1.5rem;">Perfil de Usuario</h2>
                <form>
                    <label for="nombre" style="font-weight:600;color:#fff;">Nombre</label><br>
                    <input id="nombre" name="nombre" type="text" style="width:100%;margin-bottom:1rem;padding:0.5rem;border-radius:8px;border:1px solid #ccc;background:#222;color:#fff;"><br>
                    <label for="edad" style="font-weight:600;color:#fff;">Edad</label><br>
                    <input id="edad" name="edad" type="number" min="0" max="120" style="width:100%;margin-bottom:1rem;padding:0.5rem;border-radius:8px;border:1px solid #ccc;background:#222;color:#fff;"><br>
                    <label for="email" style="font-weight:600;color:#fff;">Email</label><br>
                    <input id="email" name="email" type="email" style="width:100%;margin-bottom:1rem;padding:0.5rem;border-radius:8px;border:1px solid #ccc;background:#222;color:#fff;"><br>
                    <label style="font-weight:600;color:#fff;">Géneros favoritos</label><br>
                    <select multiple style="width:100%;margin-bottom:1rem;padding:0.5rem;border-radius:8px;border:1px solid #ccc;background:#222;color:#fff;">
                        <option>Acción</option>
                        <option>Aventura</option>
                        <option>Comedia</option>
                        <option>Drama</option>
                        <option>Fantasía</option>
                        <option>Terror</option>
                        <option>Romance</option>
                        <option>Ciencia Ficción</option>
                        <option>Thriller</option>
                        <option>Animación</option>
                    </select><br>
                    <button type="button" style="width:100%;padding:0.7rem;background:#6366f1;color:#fff;border:none;border-radius:8px;font-weight:700;">Guardar (no funcional)</button>
                </form>
                <div style="text-align:center;margin-top:1.5rem;">
                    <form method="post">
                        <button type="submit" name="volver" style="padding:0.5rem 1.2rem;background:#6366f1;color:#fff;border:none;border-radius:8px;font-weight:600;">Volver</button>
                    </form>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Estado para mostrar pantalla de perfil
if "show_profile" not in st.session_state:
    st.session_state["show_profile"] = False

col_nav1, col_nav2 = st.columns([1, 8])
with col_nav1:
    if st.button("Perfil", key="btn_perfil"):
        st.session_state["show_profile"] = True

if st.session_state["show_profile"]:
    # Botón de retorno funcional con Streamlit
    import streamlit as st
    show_profile_modal()
    if st.session_state.get("volver_click", False):
        st.session_state["show_profile"] = False
        st.session_state["volver_click"] = False
    if "volver" in st.experimental_get_query_params():
        st.session_state["show_profile"] = False
else:
    # ...contenido principal de la app...
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

    # Centered search bar - clean and simple
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_query = st.text_input("Search Movies", placeholder="Type a movie name...", label_visibility="collapsed")
        if search_query:
            pass

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

# Function to display movies in a professional format

def display_movies(movies, title):
    if movies:
        st.markdown(f'''
        <div style="margin-top: 3rem; margin-bottom: 2rem;"></div>
        ''', unsafe_allow_html=True)
        cards_per_row = 3
        total_rows = (min(len(movies), 12) + cards_per_row - 1) // cards_per_row
        loader_style = """
        <style>
        @keyframes dotFade { 0% { opacity: 0.15; } 20% { opacity: 0.5; } 40% { opacity: 0.15; } 100% { opacity: 0.15; } }
        .dot-loader span { animation: dotFade 1.2s infinite; font-size:1.1em; color:#888; letter-spacing:0.2em; }
        </style>
        """
        loader_html = "<div style='width:100%;display:flex;justify-content:center;align-items:center;margin:0.7rem 0;'><span class='dot-loader'><span>●</span> <span>●</span> <span>●</span></span></div>" + loader_style
        loader_placeholder = st.empty()
        loader_shown = False
        for row_idx in range(total_rows):
            start = row_idx * cards_per_row
            end = start + cards_per_row
            row_movies = movies[start:end]
            if not loader_shown:
                loader_placeholder.markdown(loader_html, unsafe_allow_html=True)
                loader_shown = True
            row_loader_placeholder = st.empty()
            if row_idx == 0:
                loader_placeholder.empty()
                row_loader_placeholder.markdown(loader_html, unsafe_allow_html=True)
            else:
                row_loader_placeholder.markdown(loader_html, unsafe_allow_html=True)
            row_details = []
            for fetch_idx, movie in enumerate(row_movies):
                detail = tmdb.get_movie_details(movie['id']) if 'id' in movie else movie
                row_details.append(detail)
            row_loader_placeholder.empty()
            cols = st.columns([0.01, 0.32, 0.01, 0.32, 0.01, 0.32, 0.01])
            for idx, details in enumerate(row_details):
                col_idx = 1 + idx * 2
                with cols[col_idx]:
                    movie = row_movies[idx]
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
                    # --- Botón de preferencia ---

                    info_html = f"""
                    <div class='movie-info-wrapper' style='width: 100%; height: 320px; display: flex; flex-direction: row; align-items: flex-start; justify-content: flex-start; gap: 1.2rem; padding: 1rem; margin-bottom: 2.5rem; position: relative;'>
                        <div style='flex-shrink:0;'>
                            {f'<img src="{poster_url}" alt="Poster" style="width: 170px; height: 255px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 12px #0002;" />' if poster_url else '<div style="width:170px;height:255px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888;">No Image</div>'}
                        </div>
                        <div style='flex:1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;'>
                            <h3 style='font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center;'>{details.get('title', movie.get('title', ''))}</h3>
                            {stats_html}
                            {extra_info}
                        </div>
                    </div>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)

# Navigation logic: show movies based on selected page
if st.session_state.current_page == 'home':
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