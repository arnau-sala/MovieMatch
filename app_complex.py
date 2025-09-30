import streamlit as st
from dotenv import load_dotenv
import os
from utils import TMDBClient, format_movie_info, format_rating, format_runtime
from ui_enhancements import (
    inject_mobile_css, 
    create_floating_action_buttons, 
    add_movie_quick_actions,
    show_user_stats,
    create_movie_rating_widget
)

# Configuraci�n de la p�gina
st.set_page_config(
    page_title="MovieMatch",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Verificar que existe la API key
if not TMDB_API_KEY:
    warning_msg = "?? Por favor, configura tu TMDB_API_KEY en el archivo .env"
    st.error(warning_msg)
    st.stop()

# Inicializar cliente TMDB
@st.cache_resource
def init_tmdb_client():
    try:
        return TMDBClient(TMDB_API_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente TMDB: {e}")
        return None

tmdb = init_tmdb_client()

if tmdb is None:
    st.stop()

# Inyectar CSS de iconos personalizados
# Estilos CSS removidos - usando emojis simples

# Inyectar CSS m�vil y mejoras
inject_mobile_css()

# Mostrar estad�sticas del usuario en sidebar
show_user_stats()

# Cachear g�neros para mejor rendimiento
@st.cache_data
def get_cached_genres():
    try:
        return tmdb.get_genres()
    except Exception as e:
        st.error("Error al cargar g�neros")
        return []

# Funci�n auxiliar para manejo de errores
def handle_api_error(error_msg: str, exception: Exception = None):
    """Manejar errores de API de manera consistente"""
    error_text = f"? {error_msg}"
    st.error(error_text)
    
    if exception and os.getenv("DEBUG") == "True":
        st.exception(exception)
    
    # Mostrar sugerencias seg�n el tipo de error
    st.info("""
    ?? **Sugerencias:**
    - Verifica tu conexi�n a internet
    - Comprueba que tu API key de TMDB sea v�lida
    - Intenta de nuevo en unos momentos
    """)

# Funci�n para manejar carga de datos con manejo de errores
def safe_load_data(load_function, error_message: str):
    """Cargar datos de manera segura con manejo de errores"""
    try:
        with st.spinner("Cargando..."):
            return load_function()
    except Exception as e:
        handle_api_error(error_message, e)
        return []

# CSS personalizado moderno
st.markdown("""
<style>
    /* Ocultar elementos por defecto de Streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Estilo del header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        color: #f0f0f0;
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 0;
    }
    
    /* Botones de navegaci�n modernos */
    .nav-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
        padding: 0 1rem;
    }
    
    .nav-button {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border: none;
        border-radius: 15px;
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 5px 5px 15px #d1d1d1, -5px -5px 15px #ffffff;
        font-size: 1rem;
        font-weight: 600;
        color: #333;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-button:hover {
        transform: translateY(-3px);
        box-shadow: 8px 8px 25px #d1d1d1, -8px -8px 25px #ffffff;
    }
    
    .nav-button.active {
        background: linear-gradient(145deg, #667eea, #764ba2);
        color: white;
        box-shadow: inset 5px 5px 15px #5a6fd8, inset -5px -5px 15px #7087fc;
    }
    
    /* Barra de b�squeda moderna */
    .search-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .search-input {
        width: 100%;
        padding: 1rem 1.5rem;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        font-size: 1.1rem;
        outline: none;
        transition: all 0.3s ease;
    }
    
    .search-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tarjetas de pel�culas modernas */
    .movie-card {
        background: white;
        border-radius: 20px;
        padding: 0;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        overflow: hidden;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }
    
    .movie-card-content {
        padding: 1.5rem;
    }
    
    .movie-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    
    .movie-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
        align-items: center;
    }
    
    .movie-tag {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .movie-rating {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .movie-year {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .movie-description {
        color: #666;
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    /* Botones de acci�n modernos */
    .action-button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem 0.5rem 0.5rem 0;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .secondary-button {
        background: linear-gradient(135deg, #ffecd2, #fcb69f);
        color: #333;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem 0.5rem 0.5rem 0;
    }
    
    .secondary-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(252, 182, 159, 0.3);
    }
    
    /* Grid de pel�culas */
    .movies-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    /* Secci�n de filtros moderna */
    .filters-section {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .filters-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Toggle buttons para g�neros */
    .genre-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        justify-content: center;
        margin: 1.5rem 0;
    }
    
    .genre-button {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        font-weight: 500;
        color: #333;
    }
    
    .genre-button:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .genre-button.selected {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-color: #667eea;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Loading spinner moderno */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem;
    }
    
    .modern-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .nav-buttons {
            flex-direction: column;
            align-items: center;
        }
        
        .nav-button {
            width: 100%;
            max-width: 300px;
            justify-content: center;
        }
        
        .movies-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Animaciones suaves */
    * {
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Header principal moderno con emojis
st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">?? MovieMatch</h1>
    <p class="main-subtitle">Descubre tu pr�xima pel�cula favorita con IA</p>
</div>
""", unsafe_allow_html=True)

# Sistema de navegaci�n moderno con emojis
st.markdown(f"### ?? �Qu� quieres hacer hoy?", unsafe_allow_html=True)

# Crear botones de navegaci�n modernos con iconos
col1, col2, col3, col4 = st.columns(4)

# Botones de navegaci�n con emojis
search_btn = "?? Buscar Pel�culas"
popular_btn = "?? Populares"
trophy_btn = "?? Mejor Valoradas"
theater_btn = "?? En Cines"
calendar_btn = "?? Pr�ximos Estrenos"
discover_btn = "?? Descubrir"
robot_btn = "?? Recomendaciones IA"
dice_btn = "?? Sorpr�ndeme"

with col1:
    search_movies = st.button(search_btn, key="nav_search", use_container_width=True, help="Busca pel�culas por t�tulo")
    popular_movies = st.button(popular_btn, key="nav_popular", use_container_width=True, help="Las m�s vistas ahora")

with col2:
    top_rated_movies = st.button(trophy_btn, key="nav_top", use_container_width=True, help="Cl�sicos y obras maestras")
    now_playing_movies = st.button(theater_btn, key="nav_cinema", use_container_width=True, help="En cartelera actualmente")

with col3:
    upcoming_movies = st.button(calendar_btn, key="nav_upcoming", use_container_width=True, help="Pr�ximos lanzamientos")
    discover_movies = st.button(discover_btn, key="nav_discover", use_container_width=True, help="Filtros avanzados")

with col4:
    ai_recommendations = st.button(robot_btn, key="nav_ai", use_container_width=True, help="Recomendaciones inteligentes")
    surprise_me = st.button(dice_btn, key="nav_surprise", use_container_width=True, help="Descubre algo inesperado")

# Inicializar estado de sesi�n para navegaci�n
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "search"

# Determinar modo actual basado en botones presionados
if search_movies:
    st.session_state.current_mode = "search"
elif popular_movies:
    st.session_state.current_mode = "popular"
elif top_rated_movies:
    st.session_state.current_mode = "top_rated"
elif now_playing_movies:
    st.session_state.current_mode = "now_playing"
elif upcoming_movies:
    st.session_state.current_mode = "upcoming"
elif discover_movies:
    st.session_state.current_mode = "discover"
elif ai_recommendations:
    st.session_state.current_mode = "ai_recommendations"
elif surprise_me:
    st.session_state.current_mode = "surprise"

navigation_mode = st.session_state.current_mode

# Funci�n moderna para mostrar pel�cula en formato tarjeta
def display_modern_movie_card(movie, show_details=False):
    formatted_movie = format_movie_info(movie)
    
    # Crear contenedor de tarjeta moderna
    card_html = f"""
    <div class="movie-card">
        <div style="display: flex; gap: 1.5rem; align-items: flex-start;">
            <div style="flex-shrink: 0;">
                <img src="{tmdb.get_poster_url(formatted_movie['poster_path']) or 'https://via.placeholder.com/200x300?text=Sin+Poster'}" 
                     style="width: 180px; height: 270px; border-radius: 15px; object-fit: cover; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
            </div>
            <div class="movie-card-content" style="flex: 1;">
                <h3 class="movie-title">{formatted_movie['title']}</h3>
                
                <div class="movie-meta">
                    <span class="movie-year">{formatted_movie['release_date'][:4] if formatted_movie['release_date'] else 'N/A'}</span>
                    <span class="movie-rating">? {formatted_movie['vote_average']}/10</span>
                    <span class="movie-tag">?? {formatted_movie['vote_count']:,} votos</span>
                </div>
                
                <p class="movie-description">{formatted_movie['overview'][:250]}{'...' if len(formatted_movie['overview']) > 250 else ''}</p>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Botones de acci�n modernos
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("?? Ver Detalles", key=f"details_{formatted_movie['id']}", 
                    help="Ver informaci�n completa de la pel�cula"):
            st.session_state[f"show_details_{formatted_movie['id']}"] = True
    
    with col2:
        if st.button("?? Similares", key=f"similar_{formatted_movie['id']}", 
                    help="Encontrar pel�culas similares"):
            show_similar_movies_inline(formatted_movie['id'])
    
    # Acciones r�pidas de usuario
    with st.expander("? Acciones R�pidas", expanded=False):
        add_movie_quick_actions(formatted_movie['id'], formatted_movie['title'])
        
        # Widget de calificaci�n
        create_movie_rating_widget(formatted_movie['id'])
    
    # Mostrar detalles expandidos si est� activado
    if st.session_state.get(f"show_details_{formatted_movie['id']}", False):
        show_modern_movie_details(formatted_movie['id'])

def show_modern_movie_details(movie_id):
    """Mostrar detalles de pel�cula en formato moderno"""
    with st.spinner("?? Cargando detalles..."):
        details = tmdb.get_movie_details(movie_id)
        
        if details:
            # Crear backdrop si est� disponible
            backdrop_url = tmdb.get_backdrop_url(details.get('backdrop_path'))
            if backdrop_url:
                st.markdown(f"""
                <div style="
                    background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('{backdrop_url}');
                    background-size: cover;
                    background-position: center;
                    border-radius: 20px;
                    padding: 3rem;
                    margin: 2rem 0;
                    color: white;
                    text-align: center;
                ">
                    <h2 style="font-size: 2.5rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">
                        {details['title']}
                    </h2>
                    <p style="font-size: 1.2rem; opacity: 0.9;">
                        {details.get('tagline', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Informaci�n detallada en grid moderno
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if details.get('runtime'):
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 1rem;">
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.8;">DURACI�N</h4>
                        <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{format_runtime(details['runtime'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if details.get('budget') and details['budget'] > 0:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb, #f5576c); padding: 1rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 1rem;">
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.8;">PRESUPUESTO</h4>
                        <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">${details['budget']:,}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                if details.get('revenue') and details['revenue'] > 0:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 1rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 1rem;">
                        <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.8;">RECAUDACI�N</h4>
                        <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">${details['revenue']:,}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffecd2, #fcb69f); padding: 1rem; border-radius: 15px; text-align: center; color: #333; margin-bottom: 1rem;">
                    <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.8;">IDIOMA</h4>
                    <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{details.get('original_language', 'N/A').upper()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # G�neros como chips modernos
            if details.get('genres'):
                st.markdown(f"#### ?? G�neros", unsafe_allow_html=True)
                genres_html = "<div class='genre-buttons'>"
                for genre in details['genres']:
                    genres_html += f'<span class="genre-button selected">{genre["name"]}</span>'
                genres_html += "</div>"
                st.markdown(genres_html, unsafe_allow_html=True)
            
            # Trailers integrados de forma moderna
            if details.get('videos', {}).get('results'):
                st.markdown(f"#### ?? Trailers", unsafe_allow_html=True)
                videos = [v for v in details['videos']['results'] if v['site'] == 'YouTube'][:2]
                
                if videos:
                    video_cols = st.columns(len(videos))
                    for i, video in enumerate(videos):
                        with video_cols[i]:
                            st.video(f"https://www.youtube.com/watch?v={video['key']}")
            
            # Bot�n para cerrar detalles
            if st.button("? Cerrar Detalles", key=f"close_details_{movie_id}"):
                st.session_state[f"show_details_{movie_id}"] = False
                st.rerun()

def show_similar_movies_inline(movie_id):
    """Mostrar pel�culas similares de forma inline"""
    similar_movies = tmdb.get_similar_movies(movie_id)
    
    if similar_movies:
        st.markdown(f"#### ?? Pel�culas Similares", unsafe_allow_html=True)
        
        # Mostrar en carrusel horizontal
        cols = st.columns(4)
        for i, movie in enumerate(similar_movies[:4]):
            with cols[i]:
                poster_url = tmdb.get_poster_url(movie.get('poster_path'), size="w300")
                if poster_url:
                    st.image(poster_url, use_column_width=True)
                st.markdown(f"**{movie['title']}**")
                st.markdown(f"? {movie.get('vote_average', 0)}/10", unsafe_allow_html=True)

def show_movie_details(movie_id):
    """Mostrar detalles completos de una pel�cula"""
    with st.spinner("Cargando detalles..."):
        details = tmdb.get_movie_details(movie_id)
        
        if details:
            st.markdown("---")
            st.markdown(f"## ?? Detalles Completos", unsafe_allow_html=True)
            
            # Informaci�n adicional
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if details.get('runtime'):
                    st.markdown(f"**?? Duraci�n: {format_runtime(details['runtime'])}**", unsafe_allow_html=True)
            
            with col2:
                if details.get('budget'):
                    st.markdown(f"**?? Presupuesto: ${details['budget']:,}**", unsafe_allow_html=True)
            
            with col3:
                if details.get('revenue'):
                    st.markdown(f"**?? Recaudaci�n: ${details['revenue']:,}**", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"**?? Idioma: {details.get('original_language', 'N/A').upper()}**", unsafe_allow_html=True)
            
            # G�neros
            if details.get('genres'):
                genres = [genre['name'] for genre in details['genres']]
                st.markdown(f"**?? G�neros: {', '.join(genres)}**", unsafe_allow_html=True)
            
            # Compa��as productoras
            if details.get('production_companies'):
                companies = [company['name'] for company in details['production_companies'][:3]]
                st.markdown(f"**?? Productoras: {', '.join(companies)}**", unsafe_allow_html=True)
            
            # Videos (trailers)
            if details.get('videos', {}).get('results'):
                st.markdown(f"### ?? Trailers", unsafe_allow_html=True)
                for video in details['videos']['results'][:2]:
                    if video['site'] == 'YouTube':
                        st.video(f"https://www.youtube.com/watch?v={video['key']}")
            
            # Pel�culas similares
            if details.get('similar', {}).get('results'):
                st.markdown(f"### ?? Pel�culas Similares", unsafe_allow_html=True)
                similar_movies = details['similar']['results'][:4]
                
                cols = st.columns(4)
                for i, similar_movie in enumerate(similar_movies):
                    with cols[i]:
                        poster_url = tmdb.get_poster_url(similar_movie.get('poster_path'))
                        if poster_url:
                            st.image(poster_url, width=150)
                        st.markdown(f"**{similar_movie['title']}**")
                        st.markdown(f"? {similar_movie.get('vote_average', 0)}/10", unsafe_allow_html=True)

# Separador visual
st.markdown("---")

# Contenido principal basado en el modo seleccionado
if navigation_mode == "search":
    # Header de secci�n con estilo moderno
    st.markdown(f"""
    <div class="search-container">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: #2c3e50; font-weight: 700;">
            ?? Buscar Pel�culas
        </h2>
        <p style="text-align: center; color: #666; margin-bottom: 2rem;">
            Encuentra cualquier pel�cula por su t�tulo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de b�squeda moderna
    query = st.text_input(
        "Buscar pel�cula",
        placeholder="Escribe el nombre de una pel�cula... (Ej: Avengers, Titanic, El Padrino)",
        key="search_input",
        label_visibility="collapsed"
    )
    
    if query:
        with st.spinner("?? Buscando pel�culas..."):
            try:
                results = tmdb.search_movies(query)
                
                if results:
                    st.markdown(f"""
                    <div style="text-align: center; margin: 2rem 0;">
                        <h3 style="color: #667eea; font-weight: 600;">
                             Encontramos {len(results)} pel�culas para '{query}'
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar resultados en grid moderno
                    for movie in results[:8]:  # Mostrar m�ximo 8 resultados
                        display_modern_movie_card(movie)
                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #ffeaa7, #fab1a0); border-radius: 20px; margin: 2rem 0;">
                        <h3 style="color: #2d3436; margin-bottom: 1rem;"> No encontramos resultados</h3>
                        <p style="color: #636e72; margin: 0;">Intenta con otro t�rmino de b�squeda</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                handle_api_error("Error al buscar pel�culas. Por favor, intenta de nuevo.", e)

elif navigation_mode == "popular":
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
            🔥 Películas Populares
        </h2>
        <p style="color: #666; font-size: 1.1rem;">Las más vistas del momento</p>
    </div>
    """, unsafe_allow_html=True)
    
    popular_movies = safe_load_data(
        lambda: tmdb.get_popular_movies(),
        "Error al cargar pel�culas populares"
    )
    
    if popular_movies:
        for movie in popular_movies[:8]:
            display_modern_movie_card(movie)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #ff9a9e, #fecfef); border-radius: 20px; margin: 2rem 0;">
            <h3 style="color: #2d3436; margin-bottom: 1rem;"> No disponible</h3>
            <p style="color: #636e72; margin: 0;">No se pudieron cargar las pel�culas populares en este momento</p>
        </div>
        """, unsafe_allow_html=True)

elif navigation_mode == "top_rated":
    trophy_icon = ""
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #f39c12; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
            {trophy_icon} Mejor Valoradas
        </h2>
        <p style="color: #666; font-size: 1.1rem;">Cl�sicos y joyas cinematogr�ficas</p>
    </div>
    """, unsafe_allow_html=True)
    
    top_rated_movies = safe_load_data(
        lambda: tmdb.get_top_rated_movies(),
        "Error al cargar pel�culas mejor valoradas"
    )
    
    if top_rated_movies:
        for movie in top_rated_movies[:8]:
            display_modern_movie_card(movie)
            st.markdown("<br>", unsafe_allow_html=True)

elif navigation_mode == "now_playing":
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #e74c3c; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
             En Cines
        </h2>
        <p style="color: #666; font-size: 1.1rem;">Estrenos actuales en cartelera</p>
    </div>
    """, unsafe_allow_html=True)
    
    now_playing_movies = safe_load_data(
        lambda: tmdb.get_now_playing_movies(),
        "Error al cargar pel�culas en cines"
    )
    
    if now_playing_movies:
        for movie in now_playing_movies[:8]:
            display_modern_movie_card(movie)
            st.markdown("<br>", unsafe_allow_html=True)

elif navigation_mode == "upcoming":
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #9b59b6; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
             Pr�ximos Estrenos
        </h2>
        <p style="color: #666; font-size: 1.1rem;">Los pr�ximos grandes lanzamientos</p>
    </div>
    """, unsafe_allow_html=True)
    
    upcoming_movies = safe_load_data(
        lambda: tmdb.get_upcoming_movies(),
        "Error al cargar pr�ximos estrenos"
    )
    
    if upcoming_movies:
        for movie in upcoming_movies[:8]:
            display_modern_movie_card(movie)
            st.markdown("<br>", unsafe_allow_html=True)

elif navigation_mode == "discover":
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #00b894; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
             Descubrir Pel�culas
        </h2>
        <p style="color: #666; font-size: 1.1rem;">Encuentra pel�culas perfectas con filtros inteligentes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Secci�n de filtros moderna
    st.markdown("""
    <div class="filters-section">
        <h3 class="filters-title">?? Personaliza tu B�squeda</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # G�neros como botones toggle modernos
    genres = get_cached_genres()
    genre_title = " Selecciona G�neros:"
    st.markdown(f"**{genre_title}**", unsafe_allow_html=True)
    
    # Inicializar g�neros seleccionados en session_state
    if 'selected_genres' not in st.session_state:
        st.session_state.selected_genres = []
    
    # Crear grid de g�neros con botones
    genre_cols = st.columns(4)
    for i, genre in enumerate(genres):
        with genre_cols[i % 4]:
            is_selected = genre['id'] in st.session_state.selected_genres
            
            if st.button(
                f"{'?' if is_selected else '?'} {genre['name']}", 
                key=f"genre_{genre['id']}",
                use_container_width=True
            ):
                if is_selected:
                    st.session_state.selected_genres.remove(genre['id'])
                else:
                    st.session_state.selected_genres.append(genre['id'])
                st.rerun()
    
    # Filtros adicionales en columnas
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year_range = st.select_slider(
            f" Rango de A�os:",
            options=list(range(1950, 2026)),
            value=(2000, 2025),
            format_func=lambda x: str(x)
        )
    
    with col2:
        min_rating = st.slider(
            f" Puntuaci�n M�nima:",
            0.0, 10.0, 6.0, 0.5,
            help="Pel�culas con puntuaci�n igual o superior"
        )
    
    with col3:
        sort_options = {
            f" M�s Populares": "popularity.desc",
            f" Mejor Valoradas": "vote_average.desc",
            f" M�s Recientes": "release_date.desc",
            f" M�s Antiguas": "release_date.asc"
        }
        sort_by = st.selectbox(f" Ordenar por:", list(sort_options.keys()))
    
    # Bot�n de descubrir moderno
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        rocket_btn = " �Descubrir Pel�culas!"
        discover_button = st.button(
            rocket_btn,
            type="primary",
            use_container_width=True,
            help="Buscar pel�culas con los filtros seleccionados"
        )
    
    # Ejecutar b�squeda
    if discover_button:
        # Validar que se hayan seleccionado g�neros
        if not st.session_state.selected_genres:
            st.warning("?? Selecciona al menos un g�nero para comenzar el descubrimiento")
        else:
            with st.spinner(f" Descubriendo pel�culas perfectas para ti..."):
                discovered_movies = tmdb.discover_movies(
                    genre_ids=st.session_state.selected_genres,
                    year=year_range[0] if year_range[0] > 1950 else None,
                    min_rating=min_rating if min_rating > 0 else None,
                    sort_by=sort_options[sort_by]
                )
                
                if discovered_movies:
                    # Header de resultados
                    selected_genre_names = [g['name'] for g in genres if g['id'] in st.session_state.selected_genres]
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #74b9ff, #0984e3); border-radius: 20px; color: white;">
                        <h3 style="margin-bottom: 1rem;">? �Encontramos {len(discovered_movies)} pel�culas perfectas!</h3>
                        <p style="margin: 0; opacity: 0.9;">
                            G�neros: {', '.join(selected_genre_names[:3])}{'...' if len(selected_genre_names) > 3 else ''}
                            � Desde {year_range[0]} � Min. {get_custom_icon_html('star', size=14)}{min_rating}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar resultados
                    for movie in discovered_movies[:12]:
                        display_modern_movie_card(movie)
                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #fdcb6e, #e17055); border-radius: 20px; margin: 2rem 0;">
                        <h3 style="color: #2d3436; margin-bottom: 1rem;">?? Sin Resultados</h3>
                        <p style="color: #636e72; margin: 0;">Intenta ajustar los filtros para encontrar m�s pel�culas</p>
                    </div>
                    """, unsafe_allow_html=True)

elif navigation_mode == "ai_recommendations":
    from recommendations import show_recommendations_page
    show_recommendations_page(tmdb)

elif navigation_mode == "surprise":
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #fd79a8; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
             Sorpr�ndeme
        </h2>
        <p style="color: #666; font-size: 1.1rem;">Descubre algo completamente inesperado</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tipos de sorpresa
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffeaa7, #fab1a0); border-radius: 20px; padding: 2rem; margin: 2rem 0; text-align: center;">
        <h3 style="color: #2d3436; margin-bottom: 1.5rem;"> �Qu� tipo de sorpresa prefieres?</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        random_popular = st.button(f" Algo Popular", use_container_width=True, help="Una pel�cula popular aleatoria")
    
    with col2:
        random_classic = st.button(f" Un Cl�sico", use_container_width=True, help="Una joya cinematogr�fica")
    
    with col3:
        new_btn = " Algo Reciente"
        random_recent = st.button(new_btn, use_container_width=True, help="Un estreno de este a�o")
    
    with col4:
        sparkles_btn = " Joya Oculta"
        random_hidden = st.button(sparkles_btn, use_container_width=True, help="Una pel�cula poco conocida pero genial")
    
    # Ejecutar sorpresa
    if random_popular:
        with st.spinner(f" Seleccionando algo popular..."):
            popular_list = tmdb.get_popular_movies()
            if popular_list:
                import random
                surprise_movie = random.choice(popular_list)
                st.markdown(f"###  Tu Pel�cula Sorpresa:", unsafe_allow_html=True)
                display_modern_movie_card(surprise_movie)
    
    elif random_classic:
        with st.spinner(f" Buscando un cl�sico..."):
            classics = tmdb.get_top_rated_movies()
            if classics:
                import random
                surprise_movie = random.choice(classics)
                st.markdown(f"###  Tu Cl�sico Sorpresa:", unsafe_allow_html=True)
                display_modern_movie_card(surprise_movie)
    
    elif random_recent:
        with st.spinner(f" Encontrando algo reciente..."):
            recent = tmdb.get_now_playing_movies()
            if recent:
                import random
                surprise_movie = random.choice(recent)
                st.markdown(f"###  Tu Estreno Sorpresa:", unsafe_allow_html=True)
                display_modern_movie_card(surprise_movie)
    
    elif random_hidden:
        with st.spinner(f" Descubriendo una joya oculta..."):
            hidden_gems = tmdb.discover_movies(min_rating=7.5, sort_by="vote_average.desc")
            if hidden_gems:
                import random
                # Filtrar por pel�culas menos populares pero bien valoradas
                filtered_gems = [m for m in hidden_gems if m.get('popularity', 0) < 50 and m.get('vote_count', 0) > 100]
                if filtered_gems:
                    surprise_movie = random.choice(filtered_gems)
                    st.markdown(f"###  Tu Joya Oculta:", unsafe_allow_html=True)
                    display_modern_movie_card(surprise_movie)
                else:
                    surprise_movie = random.choice(hidden_gems)
                    st.markdown(f"###  Tu Pel�cula Sorpresa:", unsafe_allow_html=True)
                    display_modern_movie_card(surprise_movie)

# Footer moderno
st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    margin-top: 4rem;
    text-align: center;
    color: white;
">
    <h3 style="margin-bottom: 1rem; font-weight: 700;"> MovieMatch</h3>
    <p style="margin-bottom: 1rem; opacity: 0.9; font-size: 1.1rem;">
        Tu asistente personal para descubrir pel�culas incre�bles
    </p>
    <p style="margin-bottom: 2rem; opacity: 0.8;">
        Desarrollado con  usando Streamlit y la API de TMDB
    </p>
    <div style="
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        opacity: 0.7;
        font-size: 0.9rem;
    ">
        <span> Miles de pel�culas</span>
        <span> IA integrada</span>
        <span> Recomendaciones personalizadas</span>
        <span> Actualizado diariamente</span>
    </div>
    <hr style="margin: 2rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.2);">
    <p style="margin: 0; opacity: 0.6; font-size: 0.85rem;">
        Los datos de pel�culas son proporcionados por 
        <a href="https://www.themoviedb.org/" target="_blank" style="color: #ffeaa7; text-decoration: none;">
            The Movie Database (TMDB)
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

# A�adir botones flotantes para mejor navegaci�n
create_floating_action_buttons()


