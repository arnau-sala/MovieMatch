def enrich_single_pattern(patterns, movie_id, weight, tmdb):
    """
    Actualiza los patrones del usuario (directors, actors, genres, countries, companies, languages) usando los datos de la película.
    weight: factor de incremento para cada coincidencia encontrada.
    """
    details = tmdb.get_movie_details(movie_id)
    # Directores
    if 'credits' in details and 'crew' in details['credits']:
        for crew in details['credits']['crew']:
            if crew.get('job') == 'Director':
                name = crew.get('name')
                if name:
                    patterns['directors'][name] = patterns['directors'].get(name, 0) + weight
    # Actores
    if 'credits' in details and 'cast' in details['credits']:
        for cast in details['credits']['cast'][:5]:
            name = cast.get('name')
            if name:
                patterns['actors'][name] = patterns['actors'].get(name, 0) + weight
    # Géneros
    if 'genres' in details:
        for g in details['genres']:
            name = g.get('name')
            if name:
                patterns['genres'][name] = patterns['genres'].get(name, 0) + weight
    # Países
    if 'production_countries' in details:
        for c in details['production_countries']:
            name = c.get('name')
            if name:
                patterns['countries'][name] = patterns['countries'].get(name, 0) + weight
    # Compañías
    if 'production_companies' in details:
        for comp in details['production_companies']:
            name = comp.get('name')
            if name:
                patterns['companies'][name] = patterns['companies'].get(name, 0) + weight
    # Idiomas
    if 'original_language' in details:
        lang = details['original_language']
        patterns['languages'][lang] = patterns['languages'].get(lang, 0) + weight
    return patterns
def load_movie_cache():
    if os.path.exists(MOVIE_CACHE_PATH):
        with open(MOVIE_CACHE_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def get_movie_details_with_cache(tmdb_client, movie_id, cache):
    key = str(movie_id)
    if key in cache:
        return cache[key]
    details = tmdb_client.get_movie_details(movie_id)
    filtered = {
        'id': details.get('id'),
        'title': details.get('title'),
        'vote_average': details.get('vote_average'),
        'popularity': details.get('popularity'),
        'genres': details.get('genres'),
        'release_date': details.get('release_date'),
    }
    cache[key] = filtered
    try:
        with open(MOVIE_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return filtered
# Global path for movie cache
import math
import os
import json
MOVIE_CACHE_PATH = os.path.join(os.path.dirname(__file__), 'movie_cache.json')
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')




universe = []

def actualizar_universo(tmdb, watched_ids, ratings, searches, patterns, preferencias, user_id):
    global universe
    print('[DEBUG] step 1')
    current = universe.copy() if universe else []
    new_candidates = set()
    # a) Similar to rated movies
    for r in ratings:
        movie_id = r.get('movie_id')
        if movie_id:
            similars = tmdb.get_similar_movies(movie_id)
            for m in similars:
                if m.get('id') not in watched_ids:
                    new_candidates.add(m['id'])
    for cat, threshold, max_count in [('directors', 0.40, 5), ('actors', 0.40, 5), ('genres', 0.30, 5)]:
        if cat in patterns and sum(patterns[cat].values()) > 0:
            highlights = [k for k, v in patterns.get(cat, {}).items() if v / sum(patterns[cat].values()) >= threshold]
        else:
            highlights = []
        for name in highlights:
            populars = tmdb.get_popular_by_pattern(cat, name, max_count)
            for m in populars:
                if m.get('id') not in watched_ids:
                    new_candidates.add(m['id'])
    total_searches = sum(s.get('count', 1) for s in searches)
    for s in searches:
        if total_searches > 0 and s.get('count', 1) / total_searches >= 0.3:
            m = tmdb.get_movie_details(s['movie_id'])
            if m and m.get('id') is not None and m.get('id') not in watched_ids:
                new_candidates.add(m['id'])
    all_ids = list(new_candidates)
    all_ids = all_ids[:30]
    all_movies = []
    cache = load_movie_cache()
    for mid in all_ids:
        m = get_movie_details_with_cache(tmdb, mid, cache)
        if m and m.get('id') not in watched_ids:
            all_movies.append(m)
    scored = []
    for m in all_movies:
        score = score_movie(m, tmdb, watched_ids, ratings, searches, patterns, preferencias)
        scored.append((m, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    universe_scored = []
    ratings_dict = {r['movie_id']: r['rating'] for r in ratings}
    for m, s in scored[:15]:
        mid = m.get('id')
        score = ratings_dict.get(mid, s)
        universe_scored.append([mid, score])
    if user_id:
        try:
            from datetime import datetime
            today = datetime.now().date().isoformat()
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if user_id in data:
                data[user_id]['universe'] = universe_scored
                data[user_id]['universe_last_update'] = today
                if 'top15' in data[user_id]:
                    del data[user_id]['top15']
                if 'universe_top15' in data[user_id]:
                    del data[user_id]['universe_top15']
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                import re
                def compact_universe(json_str):
                    pattern = r'("universe"\s*:\s*)\[(.*?)\](,?)'
                    def replacer(match):
                        prefix = match.group(1)
                        content = match.group(2)
                        suffix = match.group(3)
                        pairs = re.findall(r'\[\s*(\d+),\s*(null|\d+(?:\.\d+)?)\s*\]', content.replace("\n", " "), re.DOTALL)
                        if not pairs:
                            return match.group(0)
                        compact = ",\n  ".join([f"[{id_}, {score}]" for id_, score in pairs])
                        return f'{prefix}[\n  {compact}\n]{suffix}'
                    return re.sub(pattern, replacer, json_str, flags=re.DOTALL)
                json_str_compact = compact_universe(json_str)
                with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                    f.write(json_str_compact)
        except Exception as e:
            print(f"Error saving universe in user_data.json: {e}")
import streamlit as st
from utils import TMDBClient, format_movie_info, format_rating
from user_utils import get_user_id
from movie_display import display_movies


def show_recommendations_page(tmdb: TMDBClient):
    """Intelligent recommendations system page"""
    show_ai_recommendations(tmdb)

def show_ai_recommendations(tmdb: TMDBClient):
    user_id = get_user_id()
    st.markdown(f'**User ID activo:** `{user_id}`')
    from datetime import datetime
    today = datetime.now().date().isoformat()
    # Cargar perfil
    try:
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        profile = data.get(user_id, None)
        print(f"[DEBUG] Perfil cargado para user_id {user_id}: {profile is not None}")
    except Exception as e:
        st.warning(f'Error al acceder a user_data.json: {e}')
        profile = None

    if not profile:
        st.warning(f'No existe perfil para el usuario: {user_id}')
        return

    universe = profile.get('universe', [])
    last_update = profile.get('universe_last_update', None)

    def get_titles_from_universe(universe, tmdb):
        cache = load_movie_cache()
        titles = []
        for mid, score in sorted(universe, key=lambda x: x[1], reverse=True)[:15]:
            m = get_movie_details_with_cache(tmdb, mid, cache)
            title = m.get('title', f'ID {mid}')
            titles.append(f"{title} ({score:.2f})" if isinstance(score, (int, float)) else title)
        return titles

    if universe and len(universe) > 0 and last_update == today:
        st.markdown('**Tus recomendaciones de hoy:**')
        titles = get_titles_from_universe(universe, tmdb)
        for t in titles:
            st.markdown(f"- {t}")
    else:
        st.markdown('**Calculando recomendaciones...**')
        with st.spinner('Generando recomendaciones personalizadas...'):
            patterns = profile.get('profile_patterns', {'directors': {}, 'actors': {}, 'countries': {}, 'genres': {}, 'companies': {}, 'languages': {}})
            searches = profile.get('searches', [])
            ratings = profile.get('ratings', [])
            preferences = profile.get('preferences', [])
            watched_ids = set(r['movie_id'] for r in ratings)
            actualizar_universo(tmdb, watched_ids, ratings, searches, patterns, preferences, user_id)
            # Recargar perfil actualizado
            try:
                with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                profile = data.get(user_id, None)
            except Exception as e:
                st.warning(f'Error al acceder a user_data.json tras recalcular: {e}')
                return
            universe = profile.get('universe', [])
            if universe:
                st.markdown('**Tus recomendaciones de hoy:**')
                titles = get_titles_from_universe(universe, tmdb)
                for t in titles:
                    st.markdown(f"- {t}")
            else:
                st.warning('No se pudieron generar recomendaciones.')

def score_movie(movie, tmdb, watched_ids, ratings, searches, patterns, preferences=None):
    score = 0
    mid = movie.get('id')
    if mid in watched_ids:
        return 0
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
    # Preferencias: cada género suma 1 punto si está en la película
    if preferences and 'genres' in details:
        for g in details['genres']:
            if g.get('name') in preferences:
                score += 1
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
    # If you need to update the universe, call actualizar_universo externally.
    # If you need top N, use sorted(universe, key=...)[:N] externally.


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
                # ...existing code...


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