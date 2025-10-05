import streamlit as st
from utils import TMDBClient, format_movie_info, format_rating
from user_utils import get_user_id
from movie_display import display_movies


def show_recommendations_page(tmdb: TMDBClient):
    """Intelligent recommendations system page"""
    show_ai_recommendations(tmdb)

def show_ai_recommendations(tmdb: TMDBClient):
    import os, json
    USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')
    def load_user_data():
        try:
            with open(USER_DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    user_id = get_user_id()
    data = load_user_data()
    if not user_id or user_id not in data:
        st.warning("No user data found.")
        return
    profile = data[user_id]
    searches = profile.get('searches', [])
    st.info("The following movies have been selected based on your recent searches.")
    with st.spinner("Loading AI recommendations ..."):
        movie_ids = [s.get('movie_id') for s in searches if s.get('movie_id')]
        if not movie_ids:
            st.warning("No recent searches with valid movies found. Please search for a movie to get recommendations.")
            return
        recommended = []
        for movie_id in movie_ids:
            similar = tmdb.get_similar_movies(movie_id)
            if similar:
                recommended.extend(similar)
        if not recommended:
            st.warning("No similar movies found for your recent searches. Try searching for other titles.")
            return
        seen = set()
        unique_recommended = []
        for m in recommended:
            if m['id'] not in seen:
                seen.add(m['id'])
                unique_recommended.append(m)
        top_movies = unique_recommended[:9]
        display_movies(top_movies, "AI Recommendations")


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