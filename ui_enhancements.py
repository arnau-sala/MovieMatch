"""
Configuración adicional y utilidades para MovieMatch
Este archivo contiene funciones auxiliares para mejorar la experiencia de usuario
Versión limpiada sin dependencias de custom_icons
"""

import streamlit as st
from typing import List, Dict

def inject_mobile_css():
    """Inyectar CSS adicional para mejorar la experiencia móvil"""
    st.markdown("""
    <style>
    /* Mejoras para móvil */
    @media (max-width: 768px) {
        .stSelectbox > div > div {
            font-size: 14px;
        }
        
        .movie-card {
            padding: 0.8rem !important;
        }
        
        .main-header h1 {
            font-size: 1.8rem !important;
        }
        
        .floating-actions {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
    }
    
    /* Estilos generales mejorados */
    .genre-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .genre-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .movie-card {
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_floating_action_buttons():
    """Crear botones de acción flotantes"""
    st.markdown("""
    <div class="floating-actions">
        <button onclick="scrollToTop()" style="
            background: #667eea; 
            color: white; 
            border: none; 
            border-radius: 50%; 
            width: 50px; 
            height: 50px; 
            cursor: pointer;
            margin: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        ">↑</button>
    </div>
    
    <script>
    function scrollToTop() {
        window.scrollTo({top: 0, behavior: 'smooth'});
    }
    </script>
    """, unsafe_allow_html=True)

def add_movie_quick_actions(movie_id: int, movie_title: str):
    """Añadir acciones rápidas para películas con emojis"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("❤️", key=f"fav_{movie_id}", help="Agregar a favoritos"):
            add_to_favorites(movie_id, movie_title)
    
    with col2:
        if st.button("👁️", key=f"watch_{movie_id}", help="Marcar como vista"):
            mark_as_watched(movie_id, movie_title)
    
    with col3:
        if st.button("📋", key=f"list_{movie_id}", help="Agregar a mi lista"):
            add_to_list(movie_id, movie_title)
    
    with col4:
        if st.button("🔗", key=f"share_{movie_id}", help="Compartir película"):
            share_movie(movie_id, movie_title)

def add_to_favorites(movie_id: int, movie_title: str):
    """Agregar película a favoritos"""
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    if movie_id not in st.session_state.favorites:
        st.session_state.favorites.append(movie_id)
        st.success(f"✅ '{movie_title}' agregada a favoritos!")
    else:
        st.info(f"📚 '{movie_title}' ya está en tus favoritos")

def mark_as_watched(movie_id: int, movie_title: str):
    """Marcar película como vista"""
    if 'watched' not in st.session_state:
        st.session_state.watched = []
    
    if movie_id not in st.session_state.watched:
        st.session_state.watched.append(movie_id)
        st.success(f"✅ '{movie_title}' marcada como vista!")
    else:
        st.info(f"👁️ Ya viste '{movie_title}'")

def add_to_list(movie_id: int, movie_title: str):
    """Agregar película a lista personal"""
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if movie_id not in st.session_state.watchlist:
        st.session_state.watchlist.append(movie_id)
        st.success(f"✅ '{movie_title}' agregada a tu lista!")
    else:
        st.info(f"📋 '{movie_title}' ya está en tu lista")

def share_movie(movie_id: int, movie_title: str):
    """Compartir película"""
    share_url = f"https://www.themoviedb.org/movie/{movie_id}"
    st.success(f"🔗 Enlace de '{movie_title}': {share_url}")
    st.info("Puedes copiar este enlace para compartir la película")

def show_user_stats():
    """Mostrar estadísticas del usuario con emojis"""
    with st.sidebar:
        st.markdown(f"### 📊 Tus Estadísticas", unsafe_allow_html=True)
        
        favorites_count = len(st.session_state.get('favorites', []))
        watched_count = len(st.session_state.get('watched', []))
        watchlist_count = len(st.session_state.get('watchlist', []))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("❤️ Favoritas", favorites_count)
        
        with col2:
            st.metric("👁️ Vistas", watched_count)
        
        with col3:
            st.metric("📋 Lista", watchlist_count)

def create_movie_rating_widget(movie_id: int):
    """Crear widget de calificación de película con emojis"""
    st.markdown(f"⭐ Tu Calificación:", unsafe_allow_html=True)
    
    rating = st.slider(
        "Califica esta película", 
        min_value=1, 
        max_value=10, 
        value=5, 
        key=f"rating_{movie_id}",
        help="Desliza para calificar del 1 al 10"
    )
    
    if st.button("💾 Guardar Calificación", key=f"save_rating_{movie_id}"):
        if 'user_ratings' not in st.session_state:
            st.session_state.user_ratings = {}
        
        st.session_state.user_ratings[movie_id] = rating
        st.success(f"✅ Calificación guardada: {rating}/10")