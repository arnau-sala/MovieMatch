import os
import streamlit as st
from utils import TMDBClient

def display_movies(movies, section_title):
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    tmdb = TMDBClient(tmdb_api_key)
    if not movies:
        st.info("No movies found.")
        return
    cols = st.columns([0.01, 0.32, 0.01, 0.32, 0.01, 0.32, 0.01])
    num_cards = min(len(movies), 15)
    for i in range(num_cards):
        movie = movies[i]
        col = cols[1 + (i % 3) * 2]
        with col:
            details = tmdb.get_movie_details(movie.get('id')) if movie.get('id') else movie
            title = details.get('title', movie.get('title', 'Unknown'))
            year = details.get('release_date', '')[:4] if details.get('release_date') else 'Not Released Yet'
            poster_url = details.get('poster_path')
            runtime = details.get('runtime')
            genres = details.get('genres')
            nota = details.get('vote_average')
            duration = f"{runtime} min" if runtime else ''
            genre_html = ''
            if isinstance(genres, list) and genres:
                genres = genres[:3]
                genre_html = '<div style="margin-top:0.7rem;display:flex;justify-content:center;flex-wrap:wrap;gap:0.5rem;">' + \
                    ''.join([f'<span style="background:#23234a;color:#fff;padding:0.3em 0.8em;border-radius:16px;font-size:0.95em;display:inline-block;">{g["name"]}</span>' for g in genres if 'name' in g]) + '</div>'
            nota_html = ''
            if nota is not None:
                if nota >= 7:
                    nota_color = '#22c55e'
                elif nota >= 5:
                    nota_color = '#f59e42'
                else:
                    nota_color = '#ef4444'
                nota_html = f"<span style='color:{nota_color};font-weight:600;'>{nota}</span>"
            stats_html = f"<div style='font-size:1.05em;margin-bottom:0.5em;text-align:center;'>{year} &nbsp;|&nbsp; {duration} &nbsp;|&nbsp; {nota_html}</div>"
            info_html = f"""
            <div class='movie-info-wrapper' style='width: 100%; height: 340px; display: flex; flex-direction: row; align-items: flex-start; justify-content: flex-start; gap: 1.2rem; padding: 1rem; margin-bottom: 2.5rem;'>
                <div style='flex-shrink:0;'>
                    {f'<img src="{tmdb.get_poster_url(poster_url)}" alt="Poster" style="width: 170px; height: 255px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 12px #0002;" />' if poster_url else '<div style="width:170px;height:255px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888;">No Image</div>'}
                </div>
                <div style='flex:1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow-wrap: break-word;'>
                    <h3 style='font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center; overflow-wrap: break-word;'>{title}</h3>
                    {stats_html}
                    {genre_html}
                </div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
