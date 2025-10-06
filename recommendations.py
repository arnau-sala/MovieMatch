# Ruta global para caché de películas
import math
import os
import json
# Ruta global para caché de películas
MOVIE_CACHE_PATH = os.path.join(os.path.dirname(__file__), 'movie_cache.json')
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')


# --- UNIVERSO DE CANDIDATAS ---
# Mantiene y actualiza el universo de películas recomendadas (máx. 50)
universo = []

def actualizar_universo(tmdb, watched_ids, ratings, searches, patterns, preferencias, user_id):
    # Crear la array top15_ids solo la primera vez que se calculan los pesos
    if user_id:
        try:
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if user_id in data:
                if 'top15_ids' not in data[user_id] or not isinstance(data[user_id]['top15_ids'], list):
                    data[user_id]['top15_ids'] = []
                    with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error creando top15_ids en user_data.json: {e}")
    else:print("          No se puede crear top15_ids sin user_id")

    global universo
    print('[DEBUG] paso 1')
    actuales = universo.copy() if universo else []
    nuevos = set()
    # a) Similares a películas valoradas
    for r in ratings:
        movie_id = r.get('movie_id')
        if movie_id:
            similares = tmdb.get_similar_movies(movie_id)
            for m in similares:
                if m.get('id') not in watched_ids:
                    nuevos.add(m['id'])
    print('[DEBUG] paso 2')
    for cat, threshold, max_count in [('directors', 0.40, 5), ('actors', 0.40, 5), ('genres', 0.30, 5)]:
        if cat in patterns and sum(patterns[cat].values()) > 0:
            destacados = [k for k, v in patterns.get(cat, {}).items() if v / sum(patterns[cat].values()) >= threshold]
        else:
            destacados = []
        for nombre in destacados:
            populares = tmdb.get_popular_by_pattern(cat, nombre, max_count)
            for m in populares:
                if m.get('id') not in watched_ids:
                    nuevos.add(m['id'])
    print('[DEBUG] paso 3')
    total_searches = sum(s.get('count', 1) for s in searches)
    for s in searches:
        if total_searches > 0 and s.get('count', 1) / total_searches >= 0.3:
            m = tmdb.get_movie_details(s['movie_id'])
            if m and m.get('id') is not None and m.get('id') not in watched_ids:
                nuevos.add(m['id'])
    print('[DEBUG] paso 4')
    ids_actuales = set(m['id'] for m in actuales)
    todos_ids = list(ids_actuales | nuevos)
    # Limitar a máximo 30 candidatos
    todos_ids = todos_ids[:30]
    todas_peliculas = []
    cache = load_movie_cache()
    for mid in todos_ids:
        m = get_movie_details_with_cache(tmdb, mid, cache)
        if m and m.get('id') not in watched_ids:
            todas_peliculas.append(m)
    import time
    print('[DEBUG] paso 5')
    t0 = time.time()
    # Medir tiempo de cálculo de scores
    t_api_start = time.time()
    scored = []
    for m in todas_peliculas:
        t1 = time.time()
        score = score_movie(m, tmdb, watched_ids, ratings, searches, patterns)
        t2 = time.time()
        scored.append((m, score))
        # Opcional: print(f"Tiempo score_movie para ID {m.get('id')}: {t2-t1:.3f}s")
    t_api_end = time.time()
    print(f"[DEBUG] Tiempo total score_movie: {t_api_end-t_api_start:.3f}s para {len(todas_peliculas)} películas")
    t_sort_start = time.time()
    scored.sort(key=lambda x: x[1], reverse=True)
    t_sort_end = time.time()
    print(f"[DEBUG] Tiempo ordenación: {t_sort_end-t_sort_start:.3f}s")
    universo = [m for m, s in scored[:50]]
    t_print_start = time.time()
    print('[DEBUG] paso 6')
    print("Universo de recomendaciones:")
    for m, s in scored[:50]:
        print(f"{m.get('title', 'Unknown')} (ID: {m.get('id')}) - Score: {s:.2f}")
    t_print_end = time.time()
    print(f"[DEBUG] Tiempo prints: {t_print_end-t_print_start:.3f}s")
    print(f"[DEBUG] Tiempo total paso 5: {t_print_end-t0:.3f}s")
    # Guardar universo y top15 en user_data.json si user_id está disponible
    if user_id:
        try:
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if user_id in data:
                data[user_id]['universo'] = universo
                # Guardar los 15 primeros por puntuación (solo id)
                top15_ids = [m.get('id') for m, s in scored[:15] if m.get('id') is not None]
                # Si no existe la array top15, crearla
                if 'top15' not in data[user_id] or not isinstance(data[user_id]['top15'], dict):
                    data[user_id]['top15'] = {"ids": []}
                # Vaciar la array antes de rellenarla
                data[user_id]['top15']['ids'].clear()
                data[user_id]['top15']['ids'].extend(top15_ids)
                with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando universo en user_data.json: {e}")

# Funciones de caché global
def load_movie_cache():
    if os.path.exists(MOVIE_CACHE_PATH):
        with open(MOVIE_CACHE_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def filter_movie_fields(details):
    # Extraer director y actores principales de credits
    director = None
    actors = []
    credits = details.get('credits', {})
    # Director (solo uno)
    if 'crew' in credits:
        for crew in credits['crew']:
            if crew.get('job') == 'Director':
                director = crew.get('name')
                break
    # Actores (solo los 3 más importantes)
    if 'cast' in credits:
        actors = [cast.get('name') for cast in credits['cast'][:3]]
    # production_countries solo name
    countries = details.get('production_countries', [])
    countries_names = [c.get('name') for c in countries if c.get('name')]
    # production_companies solo id y name
    companies = details.get('production_companies', [])
    companies_id_name = [
        {'id': comp.get('id'), 'name': comp.get('name')}
        for comp in companies if comp.get('id') and comp.get('name')
    ]
    return {
        'id': details.get('id'),
        'title': details.get('title'),
        'vote_average': details.get('vote_average'),
        'popularity': details.get('popularity'),
        'director': director,
        'actors': actors,
        'genres': details.get('genres'),
        'original_language': details.get('original_language'),
        'production_countries': countries_names,
        'production_companies': companies_id_name,
    }

def save_movie_cache(cache):
    # Guardar solo los campos requeridos bajo el id
    unique = {}
    for k, v in cache.items():
        if k is not None and v.get('title'):
            unique[str(k)] = v
    with open(MOVIE_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

def get_movie_details_with_cache(tmdb_client, movie_id, cache):
    key = str(movie_id)
    if key in cache:
        return cache[key]
    details = tmdb_client.get_movie_details(movie_id)
    filtered = filter_movie_fields(details)
    # Evitar duplicados por título e id
    for v in cache.values():
        if v.get('title') == filtered.get('title'):
            # Si el título ya existe, no lo añadimos de nuevo
            return v
    cache[key] = filtered
    save_movie_cache(cache)
    return filtered

    global universo
    actuales = universo.copy() if universo else []
    nuevos = set()
    # a) Similares a películas valoradas
    for r in ratings:
        movie_id = r.get('movie_id')
        if movie_id:
            similares = tmdb.get_similar_movies(movie_id)
            for m in similares:
                if m.get('id') not in watched_ids:
                    nuevos.add(m['id'])
    for cat, threshold, max_count in [('directors', 0.40, 5), ('actors', 0.40, 5), ('genres', 0.30, 5)]:
        if cat in patterns and sum(patterns[cat].values()) > 0:
            destacados = [k for k, v in patterns.get(cat, {}).items() if v / sum(patterns[cat].values()) >= threshold]
        else:
            destacados = []
        for nombre in destacados:
            populares = tmdb.get_popular_by_pattern(cat, nombre, max_count)
            for m in populares:
                if m.get('id') not in watched_ids:
                    nuevos.add(m['id'])
    total_searches = sum(s.get('count', 1) for s in searches)
    for s in searches:
        if total_searches > 0 and s.get('count', 1) / total_searches >= 0.3:
            m = tmdb.get_movie_details(s['movie_id'])
            if m and m.get('id') is not None and m.get('id') not in watched_ids:
                nuevos.add(m['id'])
    ids_actuales = set(m['id'] for m in actuales)
    todos_ids = list(ids_actuales | nuevos)
    todas_peliculas = []
    cache = load_movie_cache()
    for mid in todos_ids:
        m = get_movie_details_with_cache(tmdb, mid, cache)
        if m and m.get('id') not in watched_ids:
            todas_peliculas.append(m)
    scored = [(m, score_movie(m, tmdb, watched_ids, ratings, searches, patterns)) for m in todas_peliculas]
    scored.sort(key=lambda x: x[1], reverse=True)
    universo = [m for m, s in scored[:30]]
    # Print del universo final con puntuaciones
    print("Universo de recomendaciones:")
    for m, s in scored[:30]:
        print(f"{m.get('title', 'Unknown')} (ID: {m.get('id')}) - Score: {s:.2f}")
    # Guardar universo y top_15_ids en user_data.json si user_id está disponible
    if user_id:
        try:
            from datetime import datetime
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if user_id in data:
                data[user_id]['universo'] = universo
                # Guardar los 15 primeros por puntuación (solo id)
                data[user_id]['top_15_ids'] = [m.get('id') for m, s in scored[:15] if m.get('id') is not None]
                # Guardar campo last_changes con fecha/hora ISO
                data[user_id]['last_changes'] = datetime.now().isoformat()
                with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando universo en user_data.json: {e}", file=sys.stderr)
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
    print("hola")
    show_ai_recommendations(tmdb)

def show_ai_recommendations(tmdb: TMDBClient):
    # Comprobar y crear la array top15_ids cada vez que se entra al modo IA
    user_id = get_user_id()
    try:
        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if user_id in data and ('top15_ids' not in data[user_id] or not isinstance(data[user_id]['top15_ids'], list)):
            data[user_id]['top15_ids'] = []
            print("[DEBUG] Creando top15_ids en user_data.json...")
            with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error creando top15_ids en user_data.json: {e}")
    # Obtener el user_id y cargar el JSON solo una vez
    user_id = get_user_id()
    st.markdown(f'**User ID activo:** `{user_id}`')
    data = None
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
    st.markdown(f"**Languages en perfil (ID: {user_id}):** {profile.get('profile_patterns', {}).get('languages', {}) if profile else 'N/A'}")
    top_50_lines = []
    if profile:
        patterns = profile.get('profile_patterns', {'directors': {}, 'actors': {}, 'countries': {}, 'genres': {}, 'companies': {}, 'languages': {}})
        searches = profile.get('searches', [])
        ratings = profile.get('ratings', [])
        preferences = profile.get('preferences', [])
        watched_ids = set(r['movie_id'] for r in ratings)
        # Definir universo_guardado antes de usarlo
        universo_guardado = profile.get('universo', [])
        top15_ids = profile.get('top15', {}).get('ids', [])
        # Si no se requiere actualización y top15 no es vacío, mostrar sus IDs
        if len(universo_guardado) > 0 and len(top15_ids) > 0:
            st.markdown('**Tus Top 15 actuales:**')
            st.code('\n'.join([str(mid) for mid in top15_ids]), language='text')
        else:
            actualizar_universo(tmdb, watched_ids, ratings, searches, patterns, preferences, user_id)
            # Actualizar top15 con los nuevos IDs tras recalculo
            data = None
            try:
                with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                data = None
            if data and user_id in data:
                universo_nuevo = data[user_id].get('universo', [])
                nuevos_top15_ids = [m.get('id') for m in universo_nuevo[:15] if m.get('id') is not None]
                if 'top15' not in data[user_id] or not isinstance(data[user_id]['top15'], dict):
                    data[user_id]['top15'] = {"ids": nuevos_top15_ids}
                else:
                    data[user_id]['top15']['ids'] = nuevos_top15_ids
                # Guardar el cambio en el JSON
                try:
                    with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"Error guardando top15: {e}")
                top15_ids = nuevos_top15_ids
            if len(top15_ids) > 0:
                st.markdown('**Tus nuevos Top 15:**')
                st.code('\n'.join([str(mid) for mid in top15_ids]), language='text')
            else:
                st.warning('No hay películas en el universo de recomendaciones.')
        # Enriquecer patrones con la última búsqueda y valoración
        from recommendations import enrich_single_pattern
        fecha_actualizada = False
        change_increment = 0
        # Detectar tipo de cambio y sumar al contador
        if profile.get('searches'):
            last_search = profile['searches'][-1]
            movie_id = last_search.get('movie_id')
            patterns = enrich_single_pattern(patterns, movie_id, 0.5, tmdb)
            # Nueva búsqueda o repetida
            if not any(s['movie_id'] == movie_id and s is not last_search for s in profile['searches'][:-1]):
                change_increment += 1  # Nueva búsqueda
            else:
                change_increment += 2  # Búsqueda repetida
            fecha_actualizada = True
        if profile.get('ratings'):
            last_rating = profile['ratings'][-1]
            movie_id = last_rating.get('movie_id')
            weight = float(last_rating.get('rating', 0)) / 10
            patterns = enrich_single_pattern(patterns, movie_id, weight, tmdb)
            change_increment += 3  # Película vista/rankeada
            fecha_actualizada = True
        data[user_id]['profile_patterns'] = patterns
        # Actualizar contador de cambios
        if 'change_counter' not in data[user_id]:
            data[user_id]['change_counter'] = 0
        data[user_id]['change_counter'] += change_increment
        # Recalculo parcial/completo según el contador
        if data[user_id]['change_counter'] >= 10:
            # Recalculo completo: 50 del universo + 10 candidatos nuevos
            print('[DEBUG] Recalculo completo del universo (60 candidatos, guardar 50)')
            watched_ids = set(r['movie_id'] for r in profile.get('ratings', []))
            universo_actual = profile.get('universo', [])
            universo_ids = set(m.get('id') for m in universo_actual)
            # Buscar 10 candidatos nuevos (no en universo)
            nuevos_candidatos = []
            cache = load_movie_cache()
            for mid in cache:
                if mid not in universo_ids and mid not in watched_ids:
                    m = get_movie_details_with_cache(tmdb, mid, cache)
                    if m:
                        nuevos_candidatos.append(m)
                    if len(nuevos_candidatos) >= 10:
                        break
            todos_candidatos = universo_actual[:50] + nuevos_candidatos
            scored = [(m, score_movie(m, tmdb, watched_ids, profile.get('ratings', []), profile.get('searches', []), patterns)) for m in todos_candidatos]
            scored.sort(key=lambda x: x[1], reverse=True)
            universo_nuevo = [m for m, s in scored[:50]]
            data[user_id]['universo'] = universo_nuevo
            # Reiniciar contador
            data[user_id]['change_counter'] = 0
        elif data[user_id]['change_counter'] >= 5:
            # Recalculo parcial: primeros 20 elementos
            print('[DEBUG] Recalculo parcial del universo (20 elementos)')
            watched_ids = set(r['movie_id'] for r in profile.get('ratings', []))
            universo_actual = profile.get('universo', [])
            scored = [(m, score_movie(m, tmdb, watched_ids, profile.get('ratings', []), profile.get('searches', []), patterns)) for m in universo_actual[:20]]
            scored.sort(key=lambda x: x[1], reverse=True)
            # Actualizar solo los primeros 20
            universo_actual[:20] = [m for m, s in scored]
            data[user_id]['universo'] = universo_actual
        # Eliminar actualización de 'last_change' en top15
        if fecha_actualizada:
            if 'top15' in data[user_id] and isinstance(data[user_id]['top15'], dict):
                if 'last_change' in data[user_id]['top15']:
                    del data[user_id]['top15']['last_change']
        try:
            with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving enriched profile: {e}")
        st.info("The following movies have been selected based on your recent searches.")
        with st.spinner("Loading AI recommendations ..."):
            rated_ids = set(r['movie_id'] for r in ratings)
            watched_ids = rated_ids.copy()
            recommended = []
            for r in ratings:
                movie_id = r.get('movie_id')
                if movie_id:
                    similar = tmdb.get_similar_movies(movie_id)
                    if similar:
                        recommended.extend(similar)
            seen = set()
            unique_recommended = []
            for m in recommended:
                if m['id'] not in seen:
                    seen.add(m['id'])
                    unique_recommended.append(m)
            from datetime import datetime, timedelta
            now = datetime.now()
    else:
        st.warning('No hay perfil cargado, no se puede mostrar recomendaciones.')
    st.markdown('### IA Recommendations')
    st.info('in progress...')

def score_movie(movie, tmdb, watched_ids, ratings, searches, patterns):
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
                if user_id:
                    try:
                        with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if user_id in data:
                            data[user_id]['universo'] = universo
                            # Guardar los 15 primeros por puntuación (solo id)
                            top15_ids = [m.get('id') for m in universo[:15] if m.get('id') is not None]
                            # Crear el campo top15_ids si no existe (misma jerarquía que preferences, searches, ratings, profile_patterns)
                            if 'top15_ids' not in data[user_id] or not isinstance(data[user_id]['top15_ids'], list):
                                data[user_id]['top15_ids'] = []
                            else:
                                data[user_id]['top15_ids'].clear()
                            data[user_id]['top15_ids'].extend(top15_ids)
                            with open(USER_DATA_PATH, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        print(f"Error guardando universo en user_data.json: {e}")
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