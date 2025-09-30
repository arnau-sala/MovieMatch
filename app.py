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

# Impactful header with clear purpose - centered and compact
st.markdown('''
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 4rem; font-weight: 800; color: #ffffff; margin-bottom: 0.5rem; 
               background: linear-gradient(135deg, #ffffff 0%, #4f46e5 50%, #06b6d4 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
               background-clip: text; letter-spacing: -0.02em; margin: 0;">
        MOVIEMATCH
    </h1>
    <p style="color: #cbd5e1; font-size: 1.2rem; font-weight: 500; margin: 0.5rem 0 0 0;">
        Discover your next favorite movie with intelligent recommendations
    </p>
</div>
''', unsafe_allow_html=True)

# Centered search bar - clean and simple
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    search_query = st.text_input("Search Movies", placeholder="Type a movie name...", label_visibility="collapsed")

# Add spacing between search bar and buttons
st.markdown('<div style="margin: 3rem 0;"></div>', unsafe_allow_html=True)

# Action buttons - single centered row
# Centered buttons with proper spacing
col_space1, col1, col_gap1, col2, col_gap2, col3, col_gap3, col4, col_gap4, col5, col_gap5, col6, col_gap6, col7, col_space2 = st.columns([0.5, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1, 0.5])

with col1:
    if st.button("Popular Movies", key="popular"):
        st.session_state.current_page = 'popular'

with col2:
    if st.button("Now Playing", key="now_playing"):
        st.session_state.current_page = 'now_playing'

with col3:
    if st.button("Top Rated", key="top_rated"):
        st.session_state.current_page = 'top_rated'

with col4:
    if st.button("Coming Soon", key="coming_soon"):
        st.session_state.current_page = 'coming_soon'

with col5:
    if st.button("By Genre", key="by_genre"):
        st.session_state.current_page = 'by_genre'

with col6:
    if st.button("AI Recommendations", key="ai_recs"):
        st.session_state.current_page = 'ai_recommendations'

with col7:
    if st.button("Random Pick", key="random"):
        st.session_state.current_page = 'random'

# Function to display movies in a professional format

def display_movies(movies, title):
    if movies:
        st.markdown(f'''
        <div style="margin-top: 3rem; margin-bottom: 2rem;">
            <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.8rem; font-weight: 600; color: #ffffff; 
                       text-align: center; padding-bottom: 0.5rem; border-bottom: 1px solid #2a2a3a; margin: 0;">
                {title}
            </h2>
        </div>
        ''', unsafe_allow_html=True)
        # Arrange movies in rows of 3 cards per row, cards much wider, minimal spacing
        cards_per_row = 3
        for i in range(0, min(len(movies), 12), cards_per_row):
            row_movies = movies[i:i+cards_per_row]
            cols = st.columns([0.01, 0.32, 0.01, 0.32, 0.01, 0.32, 0.01])
            for idx, movie in enumerate(row_movies):
                col_idx = 1 + idx * 2
                with cols[col_idx]:
                    details = tmdb.get_movie_details(movie['id']) if 'id' in movie else movie
                    poster_url = tmdb.get_poster_url(details.get('poster_path'))
                    runtime = details.get('runtime')
                    genres = details.get('genres')
                    # Build stats and provider pills
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
                                # Limitar plataformas y géneros
                                if provider_list:
                                    # Priorizar flatrate, luego rent, luego buy
                                    all_platforms = []
                                    for key in ['flatrate', 'rent', 'buy']:
                                        if key in us:
                                            all_platforms += us[key]
                                    # Filtrar solo 'Netflix' y eliminar variantes como 'Netflix sin anuncios'
                                    filtered_providers = [p for p in all_platforms if p.get('provider_name') == 'Netflix']
                                    # Añadir otros que no sean variantes de Netflix ni Amazon Prime Video with Ads
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
                    # Render providers and genres only if they have content
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
                            <h3 style='font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center;'>{details.get('title', movie.get('title', ''))}</h3>
                            {stats_html}
                            {extra_info}
                        </div>
                    </div>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)

# Navigation logic: show movies based on selected page
if st.session_state.current_page == 'home':
    with st.spinner("Loading featured movies..."):
        popular_movies = tmdb.get_popular_movies()[:6]
    if popular_movies:
        display_movies(popular_movies, "Featured Movies")
    else:
        st.info("Welcome to MovieMatch! Use the search bar or explore different categories to discover great movies.")

elif st.session_state.current_page == 'popular':
    with st.spinner("Loading popular movies..."):
        popular_movies = tmdb.get_popular_movies()
    display_movies(popular_movies, "Popular Movies")

elif st.session_state.current_page == 'now_playing':
    with st.spinner("Loading now playing movies..."):
        now_playing_movies = tmdb.get_now_playing_movies()
    display_movies(now_playing_movies, "Now Playing in Theaters")

elif st.session_state.current_page == 'top_rated':
    with st.spinner("Loading top rated movies..."):
        top_movies = tmdb.get_top_rated_movies()
    display_movies(top_movies, "Top Rated Movies")

elif st.session_state.current_page == 'coming_soon':
    with st.spinner("Loading upcoming movies..."):
        upcoming_movies = tmdb.get_upcoming_movies()
    display_movies(upcoming_movies, "Coming Soon")

elif st.session_state.current_page == 'random':
    with st.spinner("Finding your random pick..."):
        popular_movies = tmdb.get_popular_movies()
        if popular_movies:
            random_movie = random.choice(popular_movies)
            display_movies([random_movie], "Your Random Pick")
        else:
            st.error("Unable to get random movie at this time.")

elif st.session_state.current_page == 'by_genre':
    st.markdown('''
    <div style="margin-top: 3rem; margin-bottom: 2rem;">
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 1.8rem; font-weight: 600; color: #ffffff; 
                   text-align: center; padding-bottom: 0.5rem; border-bottom: 1px solid #2a2a3a; margin: 0;">
            Browse by Genre
        </h2>
    </div>
    ''', unsafe_allow_html=True)
    with st.spinner("Loading genres..."):
        genres = tmdb.get_genres()
    if genres:
        genre_names = [genre['name'] for genre in genres]
        selected_genre = st.selectbox("Choose a genre:", genre_names)
        if selected_genre:
            selected_genre_id = next(genre['id'] for genre in genres if genre['name'] == selected_genre)
            with st.spinner(f"Loading {selected_genre} movies..."):
                genre_movies = tmdb.get_movies_by_genre(selected_genre_id)
            display_movies(genre_movies, f"{selected_genre} Movies")