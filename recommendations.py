import streamlit as st
from utils import TMDBClient, format_movie_info, format_rating
import pandas as pd
from typing import List, Dict


def show_recommendations_page(tmdb: TMDBClient):
    """Página del sistema de recomendaciones"""
    
         st.markdown("# Sistema de Recomendaciones Inteligente")
    
    # Método de recomendación
    recommendation_method = st.selectbox(
        "¿Cómo quieres recibir recomendaciones?",
        [
                    "Basado en una película que te gustó",
                    "Basado en géneros favoritos",
                    "Basado en tus preferencias",
                    "Mezcla aleatoria personalizada"
        ]
    )
    
         if recommendation_method == "Basado en una película que te gustó":
        show_movie_based_recommendations(tmdb)
    
         elif recommendation_method == "Basado en géneros favoritos":
        show_genre_based_recommendations(tmdb)
    
         elif recommendation_method == "Basado en tus preferencias":
        show_preference_based_recommendations(tmdb)
    
         elif recommendation_method == "Mezcla aleatoria personalizada":
        show_random_mix_recommendations(tmdb)


def show_movie_based_recommendations(tmdb: TMDBClient):
    """Recomendaciones basadas en una película específica"""
    
    st.markdown("### Encuentra películas similares a una que te gustó")
    
    # Búsqueda de película base
    search_query = st.text_input("Busca una película que te haya gustado:")
    
    if search_query:
        search_results = tmdb.search_movies(search_query)
        
        if search_results:
            # Seleccionar película
            movie_options = {f"{movie['title']} ({movie.get('release_date', 'N/A')[:4]})": movie 
                           for movie in search_results[:10]}
            
            selected_movie_name = st.selectbox("Selecciona la película:", list(movie_options.keys()))
            selected_movie = movie_options[selected_movie_name]
            
            # Mostrar película seleccionada
            col1, col2 = st.columns([1, 3])
            
            with col1:
                poster_url = tmdb.get_poster_url(selected_movie.get('poster_path'))

                import streamlit as st
                from utils import TMDBClient, format_movie_info, format_rating
                import pandas as pd
                from typing import List, Dict

                def show_recommendations_page(tmdb: TMDBClient):
                    """Página del sistema de recomendaciones"""
                    st.markdown("# Sistema de Recomendaciones Inteligente")
                    recommendation_method = st.selectbox(
                        "¿Cómo quieres recibir recomendaciones?",
                        [
                            "Basado en una película que te gustó",
                            "Basado en géneros favoritos",
                            "Basado en tus preferencias",
                            "Mezcla aleatoria personalizada"
                        ]
                    )
                    if recommendation_method == "Basado en una película que te gustó":
                        show_movie_based_recommendations(tmdb)
                    elif recommendation_method == "Basado en géneros favoritos":
                        show_genre_based_recommendations(tmdb)
                    elif recommendation_method == "Basado en tus preferencias":
                        show_preference_based_recommendations(tmdb)
                    elif recommendation_method == "Mezcla aleatoria personalizada":
                        show_random_mix_recommendations(tmdb)

                def show_movie_based_recommendations(tmdb: TMDBClient):
                    st.markdown("### Encuentra películas similares a una que te gustó")
                    search_query = st.text_input("Busca una película que te haya gustado:")
                    if search_query:
                        search_results = tmdb.search_movies(search_query)
                        if search_results:
                            movie_options = {f"{movie['title']} ({movie.get('release_date', 'N/A')[:4]})": movie for movie in search_results[:10]}
                            selected_movie_name = st.selectbox("Selecciona la película:", list(movie_options.keys()))
                            selected_movie = movie_options[selected_movie_name]
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                poster_url = tmdb.get_poster_url(selected_movie.get('poster_path'))
                                if poster_url:
                                    st.image(poster_url, width=200)
                            with col2:
                                st.markdown(f"**{selected_movie['title']}**")
                                st.write(selected_movie.get('overview', 'Sin descripción'))
                                st.markdown(f"**{selected_movie.get('vote_average', 0)}/10**")
                            if st.button("Generar Recomendaciones", type="primary"):
                                with st.spinner("Generando recomendaciones..."):
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
                                        st.markdown("### Películas Recomendadas")
                                        cols = st.columns(3)
                                        for i, movie in enumerate(unique_recommendations[:12]):
                                            with cols[i % 3]:
                                                display_recommendation_card(movie, tmdb)
                                    else:
                                        st.warning("No se encontraron recomendaciones para esta película.")

                def show_genre_based_recommendations(tmdb: TMDBClient):
                    st.markdown("### Descubre películas por géneros")
                    genres = tmdb.get_genres()
                    selected_genres = st.multiselect(
                        "Selecciona géneros:",
                        [genre['name'] for genre in genres]
                    )
                    sort_by = st.selectbox("Ordenar por:", ["Popularidad", "Puntuación", "Fecha de lanzamiento"])
                    min_year = st.number_input("Año mínimo:", min_value=1900, max_value=2100, value=2000)
                    min_rating = st.slider("Puntuación mínima:", 0.0, 10.0, 6.0, 0.1)
                    if selected_genres:
                        genre_ids = [genre['id'] for genre in genres if genre['name'] in selected_genres]
                        sort_mapping = {
                            "Popularidad": "popularity.desc",
                            "Puntuación": "vote_average.desc",
                            "Fecha de lanzamiento": "release_date.desc"
                        }
                        if st.button("Buscar Películas", type="primary"):
                            with st.spinner("Buscando películas..."):
                                recommendations = tmdb.discover_movies(
                                    genre_ids=genre_ids,
                                    year=min_year,
                                    min_rating=min_rating,
                                    sort_by=sort_mapping[sort_by]
                                )
                                if recommendations:
                                    st.markdown(f"### {len(recommendations)} Películas Encontradas")
                                    cols = st.columns(3)
                                    for i, movie in enumerate(recommendations[:15]):
                                        with cols[i % 3]:
                                            display_recommendation_card(movie, tmdb)
                                else:
                                    st.warning("No se encontraron películas con esos criterios.")

                def show_preference_based_recommendations(tmdb: TMDBClient):
                    st.markdown("### Crea tu perfil de preferencias")
                    with st.form("user_preferences"):
                        genres = tmdb.get_genres()
                        genre_cols = st.columns(3)

                        import streamlit as st
                        from utils import TMDBClient, format_movie_info, format_rating
                        import pandas as pd
                        from typing import List, Dict

                        def show_movie_based_recommendations(tmdb: TMDBClient):
                            st.markdown("### Encuentra películas similares a una que te gustó")
                            search_query = st.text_input("Busca una película que te haya gustado:")
                            if search_query:
                                search_results = tmdb.search_movies(search_query)
                                if search_results:
                                    movie_options = {f"{movie['title']} ({movie.get('release_date', 'N/A')[:4]})": movie for movie in search_results[:10]}
                                    selected_movie_name = st.selectbox("Selecciona la película:", list(movie_options.keys()))
                                    selected_movie = movie_options[selected_movie_name]
                                    col1, col2 = st.columns([1, 3])
                                    with col1:
                                        poster_url = tmdb.get_poster_url(selected_movie.get('poster_path'))
                                        if poster_url:
                                            st.image(poster_url, width=200)
                                    with col2:
                                        st.markdown(f"**{selected_movie['title']}**")
                                        st.write(selected_movie.get('overview', 'Sin descripción'))
                                        st.markdown(f"**{selected_movie.get('vote_average', 0)}/10**")
                                    if st.button("Generar Recomendaciones", type="primary"):
                                        with st.spinner("Generando recomendaciones..."):
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
                                                st.markdown("### Películas Recomendadas")
                                                cols = st.columns(3)
                                                for i, movie in enumerate(unique_recommendations[:12]):
                                                    with cols[i % 3]:
                                                        display_recommendation_card(movie, tmdb)
                                            else:
                                                st.warning("No se encontraron recomendaciones para esta película.")

                        def show_genre_based_recommendations(tmdb: TMDBClient):
                            st.markdown("### Descubre películas por géneros")
                            genres = tmdb.get_genres()
                            selected_genres = st.multiselect(
                                "Selecciona géneros:",
                                [genre['name'] for genre in genres]
                            )
                            sort_by = st.selectbox("Ordenar por:", ["Popularidad", "Puntuación", "Fecha de lanzamiento"])
                            min_year = st.number_input("Año mínimo:", min_value=1900, max_value=2100, value=2000)
                            min_rating = st.slider("Puntuación mínima:", 0.0, 10.0, 6.0, 0.1)
                            if selected_genres:
                                genre_ids = [genre['id'] for genre in genres if genre['name'] in selected_genres]
                                sort_mapping = {
                                    "Popularidad": "popularity.desc",
                                    "Puntuación": "vote_average.desc",
                                    "Fecha de lanzamiento": "release_date.desc"
                                }
                                if st.button("Buscar Películas", type="primary"):
                                    with st.spinner("Buscando películas..."):
                                        recommendations = tmdb.discover_movies(
                                            genre_ids=genre_ids,
                                            year=min_year,
                                            min_rating=min_rating,
                                            sort_by=sort_mapping[sort_by]
                                        )
                                        if recommendations:
                                            st.markdown(f"### {len(recommendations)} Películas Encontradas")
                                            cols = st.columns(3)
                                            for i, movie in enumerate(recommendations[:15]):
                                                with cols[i % 3]:
                                                    display_recommendation_card(movie, tmdb)
                                        else:
                                            st.warning("No se encontraron películas con esos criterios.")

                        def show_preference_based_recommendations(tmdb: TMDBClient):
                            st.markdown("### Crea tu perfil de preferencias")
                            with st.form("user_preferences"):
                                genres = tmdb.get_genres()
                                genre_cols = st.columns(3)
                                selected_genres = []
                                for i, genre in enumerate(genres):
                                    with genre_cols[i % 3]:
                                        if st.checkbox(genre['name'], key=f"genre_{genre['id']}"):
                                            selected_genres.append(genre['id'])
                                st.markdown("#### Preferencias de Contenido")
                                col1, col2 = st.columns(2)
                                with col1:
                                    decade = st.selectbox("Década preferida:", ["Sin preferencia", "2020s", "2010s", "2000s", "1990s", "1980s", "Anteriores"])
                                    min_rating = st.slider("Puntuación mínima:", 0.0, 10.0, 6.0, 0.1)
                                with col2:
                                    runtime_pref = st.selectbox("Duración preferida:", ["Sin preferencia", "Cortas (<90min)", "Normales (90-150min)", "Largas (>150min)"])
                                    language_pref = st.selectbox("Idioma:", ["Sin preferencia", "Inglés", "Español", "Otros"])
                                submitted = st.form_submit_button("Generar Mis Recomendaciones", type="primary")
                                if submitted and selected_genres:
                                    with st.spinner("Generando recomendaciones personalizadas..."):
                                        year_filter = None
                                        if decade != "Sin preferencia":
                                            decade_map = {
                                                "2020s": 2020, "2010s": 2010, "2000s": 2000,
                                                "1990s": 1990, "1980s": 1980, "Anteriores": 1900
                                            }
                                            year_filter = decade_map[decade]
                                        all_recommendations = []
                                        main_recs = tmdb.discover_movies(
                                            genre_ids=selected_genres,
                                            year=year_filter,
                                            min_rating=min_rating,
                                            sort_by="popularity.desc"
                                        )
                                        all_recommendations.extend(main_recs[:10])
                                        for genre_id in selected_genres[:3]:
                                            genre_recs = tmdb.discover_movies(
                                                genre_ids=[genre_id],
                                                year=year_filter,
                                                min_rating=min_rating,
                                                sort_by="vote_average.desc"
                                            )
                                            all_recommendations.extend(genre_recs[:5])
                                        seen_ids = set()
                                        unique_recommendations = []
                                        for movie in all_recommendations:
                                            if movie['id'] not in seen_ids:
                                                seen_ids.add(movie['id'])
                                                unique_recommendations.append(movie)
                                        if unique_recommendations:
                                            st.markdown(f"### Tus Recomendaciones Personalizadas")
                                            st.markdown(f"*Basado en {len(selected_genres)} géneros seleccionados*")
                                            cols = st.columns(3)
                                            for i, movie in enumerate(unique_recommendations[:18]):
                                                with cols[i % 3]:
                                                    display_recommendation_card(movie, tmdb)
                                        else:
                                            st.warning("No se encontraron películas con tus preferencias. Intenta ajustar los filtros.")

                        def show_random_mix_recommendations(tmdb: TMDBClient):
                            st.markdown("### Sorpréndeme con una mezcla aleatoria")
                            st.markdown("*Una combinación de películas populares, bien valoradas y clásicos*")
                            mix_type = st.selectbox(
                                "Tipo de mezcla:",
                                [
                                    "Completamente aleatoria",
                                    "Enfoque en populares",
                                    "Enfoque en mejor valoradas",
                                    "Solo estrenos recientes",
                                    "Joyas ocultas (menos conocidas)"
                                ]
                            )
                            if st.button("Generar Mezcla Aleatoria", type="primary"):
                                with st.spinner("Preparando tu mezcla personalizada..."):
                                    all_recommendations = []
                                    if mix_type == "Completamente aleatoria":
                                        popular = tmdb.get_popular_movies()[:5]
                                        top_rated = tmdb.get_top_rated_movies()[:5]
                                        now_playing = tmdb.get_now_playing_movies()[:5]
                                        all_recommendations = popular + top_rated + now_playing
                                    elif mix_type == "Enfoque en populares":
                                        for page in range(1, 4):
                                            popular = tmdb.get_popular_movies(page=page)
                                            all_recommendations.extend(popular[:7])
                                    elif mix_type == "Enfoque en mejor valoradas":
                                        for page in range(1, 4):
                                            top_rated = tmdb.get_top_rated_movies(page=page)
                                            all_recommendations.extend(top_rated[:7])
                                    elif mix_type == "Solo estrenos recientes":
                                        now_playing = tmdb.get_now_playing_movies()
                                        upcoming = tmdb.get_upcoming_movies()
                                        all_recommendations = now_playing + upcoming
                                    elif mix_type == "Joyas ocultas (menos conocidas)":
                                        hidden_gems = tmdb.discover_movies(
                                            min_rating=7.0,
                                            sort_by="vote_average.desc"
                                        )
                                        all_recommendations = hidden_gems
                                    import random
                                    seen_ids = set()
                                    unique_recommendations = []
                                    for movie in all_recommendations:
                                        if movie['id'] not in seen_ids:
                                            seen_ids.add(movie['id'])
                                            unique_recommendations.append(movie)
                                    random.shuffle(unique_recommendations)
                                    if unique_recommendations:
                                        st.markdown(f"### Tu Mezcla Personalizada")
                                        cols = st.columns(3)
                                        for i, movie in enumerate(unique_recommendations[:15]):
                                            with cols[i % 3]:
                                                display_recommendation_card(movie, tmdb)
                                    else:
                                        st.error("Error al generar recomendaciones. Intenta de nuevo.")
        
        # Botón para más detalles
        if st.button("Ver detalles", key=f"rec_{formatted_movie['id']}", type="secondary"):
            st.session_state[f"show_details_{formatted_movie['id']}"] = True
        
        # Mostrar detalles si está activado
        if st.session_state.get(f"show_details_{formatted_movie['id']}", False):
            show_movie_details_popup(formatted_movie['id'], tmdb)
        
        st.markdown("---")


def show_movie_details_popup(movie_id: int, tmdb: TMDBClient):
    """Mostrar detalles de película en popup"""
    
    details = tmdb.get_movie_details(movie_id)
    
    if details:
        st.markdown("#### 📋 Detalles Completos")
        
        # Información adicional en columnas
        col1, col2 = st.columns(2)
        
        with col1:
            if details.get('runtime'):
                from utils import format_runtime
                st.markdown(f"**⏱️ Duración:** {format_runtime(details['runtime'])}")
            
            if details.get('genres'):
                genres = [genre['name'] for genre in details['genres']]
                st.markdown(f"**{get_custom_icon_html('theater', size=16)} Géneros:** {', '.join(genres)}", unsafe_allow_html=True)
        
        with col2:
            if details.get('production_companies'):
                companies = [company['name'] for company in details['production_companies'][:2]]
                st.markdown(f"**🏢 Productoras:** {', '.join(companies)}")
            
            st.markdown(f"**🌍 Idioma:** {details.get('original_language', 'N/A').upper()}")
        
        # Botón para cerrar detalles
        if st.button("Cerrar detalles", key=f"close_{movie_id}"):
            st.session_state[f"show_details_{movie_id}"] = False
            st.rerun()