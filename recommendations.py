import os
import json
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')
# --- UNIVERSO DE CANDIDATAS ---
# Mantiene y actualiza el universo de películas recomendadas (máx. 50)
universo = []

def actualizar_universo(tmdb, watched_ids, ratings, searches, patterns, preferencias):
    global universo
    # 1. Candidatas actuales
    actuales = universo.copy() if universo else []
    # 2. Buscar 20 nuevos candidatos relevantes
    nuevos = set()
    # a) Similares a películas valoradas
    for r in ratings:
        movie_id = r.get('movie_id')
        if movie_id:
            similares = tmdb.get_similar_movies(movie_id)
            for m in similares:
                if m.get('id') not in watched_ids:
                    nuevos.add(m['id'])
    # b) Populares de patrones destacados
    for cat, threshold, max_count in [('directors', 0.40, 5), ('actors', 0.40, 5), ('genres', 0.30, 5)]:
        destacados = [k for k, v in patterns.get(cat, {}).items() if v / sum(patterns[cat].values()) >= threshold and sum(patterns[cat].values()) > 0]
        for nombre in destacados:
            populares = tmdb.get_popular_by_pattern(cat, nombre, max_count)
            for m in populares:
                if m.get('id') not in watched_ids:
                    nuevos.add(m['id'])
    # c) Películas que superan el 30% de búsquedas
    total_searches = sum(s.get('count', 1) for s in searches)
    for s in searches:
        if total_searches > 0 and s.get('count', 1) / total_searches >= 0.3:
            m = tmdb.get_movie_details(s['movie_id'])
            if m and m.get('id') not in watched_ids:
                nuevos.add(m['id'])
    # 3. Combinar actuales y nuevos (máx. 70)
    ids_actuales = set(m['id'] for m in actuales)
    todos_ids = list(ids_actuales | nuevos)
    # 4. Obtener detalles de todas las películas
    todas_peliculas = []
    for mid in todos_ids:
        m = tmdb.get_movie_details(mid)
        if m and m.get('id') not in watched_ids:
            todas_peliculas.append(m)
    # 5. Calcular score y seleccionar las 50 mejores
    scored = [(m, score_movie(m, tmdb, watched_ids, ratings, searches, patterns)) for m in todas_peliculas]
    scored.sort(key=lambda x: x[1], reverse=True)
    universo = [m for m, s in scored[:50]]
def enrich_single_pattern(profile_patterns, movie_id, weight, tmdb):
    """
    Efficiently update profile_patterns for a single movie.
    profile_patterns: dict to update
    movie_id: id of the movie to enrich
    weight: rating/10 for ranked, 0.5 for searched
    tmdb: TMDBClient instance
    """
    if not movie_id:
        return profile_patterns
    details = tmdb.get_movie_details(movie_id)
    # Director
    if 'credits' in details and 'crew' in details['credits']:
        for crew in details['credits']['crew']:
            if crew.get('job') == 'Director':
                name = crew.get('name')
                profile_patterns['directors'][name] = profile_patterns['directors'].get(name, 0) + weight
    # Main actors
    if 'credits' in details and 'cast' in details['credits']:
        for cast in details['credits']['cast'][:3]:
            name = cast.get('name')
            profile_patterns['actors'][name] = profile_patterns['actors'].get(name, 0) + weight
    # Country
    if 'production_countries' in details:
        for c in details['production_countries']:
            name = c.get('name')
            profile_patterns['countries'][name] = profile_patterns['countries'].get(name, 0) + weight
    # Genre
    if 'genres' in details:
        for g in details['genres']:
            name = g.get('name')
            profile_patterns['genres'][name] = profile_patterns['genres'].get(name, 0) + weight
    # Production companies
    if 'production_companies' in details:
        for comp in details['production_companies']:
            name = comp.get('name')
            profile_patterns['companies'][name] = profile_patterns['companies'].get(name, 0) + weight
    # Language
    if 'original_language' in details:
        lang = details['original_language']
        profile_patterns['languages'][lang] = profile_patterns['languages'].get(lang, 0) + weight
    return profile_patterns
import streamlit as st
from utils import TMDBClient, format_movie_info, format_rating
from user_utils import get_user_id
from movie_display import display_movies


def show_recommendations_page(tmdb: TMDBClient):
    """Intelligent recommendations system page"""
    show_ai_recommendations(tmdb)

def show_ai_recommendations(tmdb: TMDBClient):
    # 1. Obtener el user_id primero
    user_id = get_user_id()
    st.markdown(f'**User ID activo:** `{user_id}`')
    # 2. Abrir el JSON y acceder al perfil solo con la clave correcta
    profile = None
    try:
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if user_id in data:
            profile = data[user_id]
        else:
            st.warning(f'No existe perfil para el usuario: {user_id}')
    except Exception as e:
        st.warning(f'Error al acceder a user_data.json: {e}')
    # 3. Acceder a languages solo si existe el perfil
    languages = profile.get('profile_patterns', {}).get('languages', {}) if profile else {}
    st.markdown(f"**Languages en perfil:** {languages}")
    # Mostrar el top 50 en pantalla debajo del in progress
    top_50_lines = []
    if len(universo) > 0:
        for m in universo[:50]:
            s = score_movie(m, tmdb, watched_ids, ratings, searches, patterns)
            top_50_lines.append(f"{m.get('title', 'Unknown')} (ID: {m.get('id')}) - Score: {s:.2f}")
        st.code('\n'.join(top_50_lines), language='text')
    else:
        st.warning('No hay películas en el universo de recomendaciones.')
    st.markdown('### IA Recommendations')
    st.info('in progress...')
    print("[DEBUG] Entrando en IA recommendations...")
    user_id = get_user_id()
    print(f"[DEBUG] user_id detectado: {user_id}")
    st.markdown(f"<span style='color:orange'>[DEBUG] user_id detectado: {user_id}</span>", unsafe_allow_html=True)
    data = None
    try:
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar user_data.json: {e}")
        st.markdown(f"<span style='color:red'>[ERROR] No se pudo cargar user_data.json: {e}</span>", unsafe_allow_html=True)
    if not user_id or not data or user_id not in data:
        print(f"[ERROR] No se encontró data para el usuario: {user_id}")
        st.markdown(f"<span style='color:red'>[ERROR] No se encontró data para el usuario: {user_id}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:red'>[DEBUG] Claves en user_data.json: {list(data.keys()) if data else 'None'}</span>", unsafe_allow_html=True)
        return
    profile = data[user_id]
    print(f"[DEBUG] Perfil cargado para usuario {user_id}: {profile.keys()}")
    st.markdown(f"<span style='color:orange'>[DEBUG] Perfil cargado para usuario {user_id}: {list(profile.keys())}</span>", unsafe_allow_html=True)
    patterns = profile.get('profile_patterns', {'directors': {}, 'actors': {}, 'countries': {}, 'genres': {}, 'companies': {}, 'languages': {}})
    searches = profile.get('searches', [])
    ratings = profile.get('ratings', [])
    preferences = profile.get('preferences', [])
    watched_ids = set(r['movie_id'] for r in ratings)
    print(f"[DEBUG] Universo antes de actualizar: {len(universo)}")
    actualizar_universo(tmdb, watched_ids, ratings, searches, patterns, preferences)
    print(f"[DEBUG] Universo después de actualizar: {len(universo)}")
    if len(universo) > 0:
        print("TOP 50 películas por score:")
        for m in universo[:50]:
            s = score_movie(m, tmdb, watched_ids, ratings, searches, patterns)
            print(f"{m.get('title', 'Unknown')} (ID: {m.get('id')}) - Score: {s}")
    else:
        print("[ERROR] El universo de películas está vacío.")
    import json
    def load_user_data():
        try:
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}


    # ...existing code...
    user_id = get_user_id()
    data = load_user_data()
    if not user_id or user_id not in data:
        st.warning("No user data found.")
        return
    profile = data[user_id]
    # Always update profile_patterns before recommendations
    patterns = data[user_id].get('profile_patterns', {
        'directors': {}, 'actors': {}, 'countries': {}, 'genres': {}, 'companies': {}, 'languages': {}
    })
    # Enriquecer patrones con la última búsqueda y valoración
    from recommendations import enrich_single_pattern
    if profile.get('searches'):
        last_search = profile['searches'][-1]
        movie_id = last_search.get('movie_id')
        patterns = enrich_single_pattern(patterns, movie_id, 0.5, tmdb)
    if profile.get('ratings'):
        last_rating = profile['ratings'][-1]
        movie_id = last_rating.get('movie_id')
        weight = float(last_rating.get('rating', 0)) / 10
        patterns = enrich_single_pattern(patterns, movie_id, weight, tmdb)
    data[user_id]['profile_patterns'] = patterns
    try:
        with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving enriched profile: {e}")

    # You should also update profile_patterns right after any code that adds a search or rating elsewhere in your app (e.g. after adding a new search or rating in app.py or other modules).
    searches = profile.get('searches', [])
    ratings = profile.get('ratings', [])
    preferences = profile.get('preferences', [])
    patterns = data[user_id].get('profile_patterns', {})
    st.info("The following movies have been selected based on your recent searches.")
    with st.spinner("Loading AI recommendations ..."):
        # Gather candidate movies
        rated_ids = set(r['movie_id'] for r in ratings)
        watched_ids = rated_ids.copy()
        # Solo usar SIMILARES de películas vistas/valoradas
        recommended = []
        for r in ratings:
            movie_id = r.get('movie_id')
            if movie_id:
                similar = tmdb.get_similar_movies(movie_id)
                if similar:
                    recommended.extend(similar)
        # Remove duplicates
        seen = set()
        unique_recommended = []
        for m in recommended:
            if m['id'] not in seen:
                seen.add(m['id'])
                unique_recommended.append(m)
        # Scoring system
        from datetime import datetime, timedelta
        now = datetime.now()

def score_movie(movie, tmdb, watched_ids, ratings, searches, patterns):
    score = 0
    mid = movie.get('id')
    if mid in watched_ids:
        return 0
    import math
    for s in searches:
        if s.get('movie_id') and mid == s['movie_id']:
            n = s.get('count', 1)
            factor = 1 - math.exp(-0.7 * n)
            score += 8 * factor
    for r in ratings:
        movie_id = r.get('movie_id')
        rating = r.get('rating', 0)
        if movie_id:
            similar = tmdb.get_similar_movies(movie_id)
            if any(m.get('id') == mid for m in similar):
                score += 4 * (rating / 10)
    if movie.get('vote_average', 0) >= 7:
        score += 2
    try:
        pop = movie.get('popularity', 0)
        popular = tmdb.get_popular_movies(page=1)
        pops = [m.get('popularity', 0) for m in popular]
        if pops and pop >= sorted(pops, reverse=True)[max(1, int(len(pops)*0.1))-1]:
            score += 1
    except Exception:
        pass
    details = tmdb.get_movie_details(mid)
    def coef_relativo(name, category, threshold):
        total = sum(patterns[category].values())
        if total == 0 or name not in patterns[category]:
            return 0
        coef = patterns[category][name] / total
        return coef if coef >= threshold else 0
    if 'credits' in details and 'crew' in details['credits']:
        for crew in details['credits']['crew']:
            if crew.get('job') == 'Director':
                coef = coef_relativo(crew.get('name'), 'directors', 0.15)
                score += 6 * coef
    if 'credits' in details and 'cast' in details['credits']:
        for cast in details['credits']['cast'][:3]:
            coef = coef_relativo(cast.get('name'), 'actors', 0.08)
            score += 4 * coef
    if 'genres' in details:
        for g in details['genres']:
            coef = coef_relativo(g.get('name'), 'genres', 0.18)
            score += 3 * coef
    if 'original_language' in details:
        coef = coef_relativo(details['original_language'], 'languages', 0.25)
        score += 2 * coef
    if 'production_countries' in details:
        for c in details['production_countries']:
            coef = coef_relativo(c.get('name'), 'countries', 0.30)
            score += 1.5 * coef
    if 'production_companies' in details:
        for comp in details['production_companies']:
            coef = coef_relativo(comp.get('name'), 'companies', 0.20)
            score += 1 * coef
    return score
    # Actualizar universo si corresponde (llamar a actualizar_universo en triggers)
    # Calcular top 15 por score, sin renderizado
    universo_filtrado = [m for m in universo if m['id'] not in watched_ids]
    scored = [(m, score_movie(m)) for m in universo_filtrado]
    scored.sort(key=lambda x: x[1], reverse=True)
    top_15 = scored[:15]
    global resultado_top_15
    resultado_top_15 = top_15


def show_movie_based_recommendations(tmdb: TMDBClient):
    """Recommendations based on a specific movie"""
    st.markdown("### Find movies similar to one you liked")
    search_query = st.text_input("Search for a movie you liked:")
    if search_query:
        search_results = tmdb.search_movies(search_query)
        if search_results:
            movie_options = {f"{movie['title']} ({movie.get('release_date', 'N/A')[:4]})": movie for movie in search_results[:10]}
            selected_movie_name = st.selectbox("Select a movie:", list(movie_options.keys()))
            selected_movie = movie_options[selected_movie_name]
            col1, col2 = st.columns([1, 3])
            with col1:
                poster_url = tmdb.get_poster_url(selected_movie.get('poster_path'))
                if poster_url:
                    st.image(poster_url, width=200)
            with col2:
                st.markdown(f"**{selected_movie['title']}**")
                st.write(selected_movie.get('overview', 'No description available'))
                st.markdown(f"**{selected_movie.get('vote_average', 0)}/10**")
            if st.button("Get Recommendations", type="primary"):
                with st.spinner("Loading recommendations..."):
                    similar_movies = tmdb.get_similar_movies(selected_movie['id'])
                    recommendations = tmdb.get_recommendations(selected_movie['id'])
                    all_recommendations = similar_movies + recommendations
                    seen_ids = set()
                    unique_recommendations = []
                    for movie in all_recommendations:
                        if movie['id'] not in seen_ids:
                            seen_ids.add(movie['id'])
                            unique_recommendations.append(movie)
                    if unique_recommendations:
                        st.markdown("### Recommended Movies")
                        cols = st.columns(3)
                        for i, movie in enumerate(unique_recommendations[:12]):
                            with cols[i % 3]:
                                st.write(format_movie_info(movie))
                    else:
                        st.warning("No recommendations found for this movie.")


def show_movie_details_popup(movie_id: int, tmdb: TMDBClient):
    """Show movie details in popup"""
    details = tmdb.get_movie_details(movie_id)
    if details:
        st.markdown("#### 📋 Full Details")
        col1, col2 = st.columns(2)
        with col1:
            if details.get('runtime'):
                from utils import format_runtime
                st.markdown(f"**⏱️ Duration:** {format_runtime(details['runtime'])}")
            if details.get('genres'):
                genres = [genre['name'] for genre in details['genres']]
                st.markdown(f"**Genres:** {', '.join(genres)}")
        with col2:
            if details.get('production_companies'):
                companies = [company['name'] for company in details['production_companies'][:2]]
                st.markdown(f"**🏢 Production Companies:** {', '.join(companies)}")
            st.markdown(f"**🌍 Language:** {details.get('original_language', 'N/A').upper()}")
        if st.button("Close details", key=f"close_{movie_id}"):
            st.session_state[f"show_details_{movie_id}"] = False
            st.rerun()