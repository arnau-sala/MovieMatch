import streamlit as st
from dotenv import load_dotenv
import os
import random
from utils import TMDBClient

# Professional page configuration
st.set_page_config(
    page_title="MovieMatch - Curated Cinema Discovery",
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
    /* Global dark theme with clean aesthetics */
    .stApp {
        background: #0f0f23;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #0a0a1a;
        border-right: 1px solid #2a2a3a;
    }
    
    .main-header {
        text-align: center;
        padding: 4rem 2rem;
        background: #161629;
        border: 1px solid #2a2a3a;
        border-radius: 12px;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #4f46e5, #06b6d4, #10b981);
    }
    
    .main-title {
        font-size: 3.2rem;
        font-weight: 300;
        margin-bottom: 0.8rem;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }
    
    .search-container {
        background: #161629;
        border: 1px solid #2a2a3a;
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 3rem;
    }
    
    .search-container h2 {
        color: #e2e8f0 !important;
        font-weight: 500;
        font-size: 1.5rem;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }
    
    .movie-card {
        background: #161629;
        border: 1px solid #2a2a3a;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #4f46e5, transparent);
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .movie-card:hover {
        border-color: #4f46e5;
        transform: translateY(-2px);
    }
    
    .movie-card:hover::before {
        opacity: 1;
    }
    
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        border-radius: 8px;
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.01em;
    }
    
    .stButton > button:hover {
        background: #4f46e5;
        border-color: #4f46e5;
        color: #ffffff;
        transform: translateY(-1px);
    }
    
    /* Clean input styling */
    .stTextInput > div > div > input {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4f46e5 !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
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
    
    /* Clean typography */
    .stMarkdown {
        color: #e2e8f0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 500 !important;
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
    
    /* Section titles */
    .section-title {
        font-size: 1.8rem;
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2a2a3a;
    }
</style>
""", unsafe_allow_html=True)

# Professional header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">MovieMatch</h1>
    <p class="main-subtitle">Curated cinema discovery platform</p>
</div>
""", unsafe_allow_html=True)

# Professional search section
st.markdown("""
<div class="search-container">
    <h2>Search & Discover</h2>
</div>
""", unsafe_allow_html=True)

search_query = st.text_input("", placeholder="Search for movies...", label_visibility="collapsed")

# Navigation buttons with clean design
st.markdown("### Explore Collections")

col1, col2, col3, col4, col5 = st.columns(5)

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
    if st.button("Random Pick", key="random"):
        st.session_state.current_page = 'random'

with col5:
    if st.button("AI Recommendations", key="ai_recs"):
        st.session_state.current_page = 'ai_recommendations'

# Additional sections
col6, col7 = st.columns(2)

with col6:
    if st.button("By Genre", key="by_genre"):
        st.session_state.current_page = 'by_genre'

with col7:
    if st.button("Coming Soon", key="coming_soon"):
        st.session_state.current_page = 'coming_soon'

# Function to display movies in a professional format
def display_movies(movies, title):
    if movies:
        st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)
        
        for movie in movies[:12]:  # Show up to 12 movies
            # Professional movie card
            st.markdown("""<div class="movie-card">""", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                poster_url = tmdb.get_poster_url(movie.get('poster_path'))
                if poster_url:
                    st.image(poster_url, width=200)
                else:
                    st.markdown("**No Image Available**")
            
            with col2:
                st.markdown(f"### {movie['title']}")
                
                # Movie metadata
                meta_col1, meta_col2 = st.columns(2)
                
                with meta_col1:
                    if movie.get('release_date'):
                        st.markdown(f"**Year:** {movie['release_date'][:4]}")
                    if movie.get('vote_average'):
                        st.markdown(f"<span class='rating'>**Rating:** {movie['vote_average']}/10</span>", unsafe_allow_html=True)
                
                with meta_col2:
                    if movie.get('vote_count'):
                        st.markdown(f"**Votes:** {movie['vote_count']:,}")
                    if movie.get('popularity'):
                        st.markdown(f"**Popularity:** {movie['popularity']:.1f}")
                
                # Overview
                if movie.get('overview'):
                    overview = movie['overview']
                    if len(overview) > 280:
                        overview = overview[:280] + "..."
                    st.markdown(f"**Overview:** {overview}")
            
            st.markdown("""</div>""", unsafe_allow_html=True)
    else:
        st.warning("No movies found.")

# Handle search functionality
if search_query:
    with st.spinner("Searching movies..."):
        results = tmdb.search_movies(search_query)
    
    if results:
        display_movies(results, f"Search Results for '{search_query}'")
    else:
        st.warning("No movies found for your search.")

# Handle navigation
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
    st.markdown('<h2 class="section-title">Browse by Genre</h2>', unsafe_allow_html=True)
    
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

elif st.session_state.current_page == 'ai_recommendations':
    st.markdown('<h2 class="section-title">AI-Powered Recommendations</h2>', unsafe_allow_html=True)
    
    with st.spinner("Generating smart recommendations..."):
        # Mix different types for diverse recommendations
        popular = tmdb.get_popular_movies()[:3]
        top_rated = tmdb.get_top_rated_movies()[:3]
        now_playing = tmdb.get_now_playing_movies()[:2]
        
        mixed_recommendations = popular + top_rated + now_playing
        random.shuffle(mixed_recommendations)
    
    display_movies(mixed_recommendations[:8], "Smart Recommendations for You")

else:
    # Home page - show popular movies by default
    with st.spinner("Loading featured movies..."):
        popular_movies = tmdb.get_popular_movies()[:6]  # Show fewer on home page
    
    if popular_movies:
        display_movies(popular_movies, "Featured Movies")
    else:
        st.info("Welcome to MovieMatch! Use the search bar or explore different categories to discover great movies.")