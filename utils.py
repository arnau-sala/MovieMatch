import requests
import os
from typing import List, Dict, Optional

# Se han eliminado todas las referencias a iconos y custom_icons

class TMDBClient:
    """Cliente para interactuar con la API de The Movie Database (TMDB)"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Realizar petición a la API de TMDB con manejo robusto de errores"""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        params['region'] = 'ES'
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as e:
                print(f"Error al decodificar JSON: {e}")
                return {"error": "Respuesta no válida del servidor"}
        except requests.exceptions.Timeout:
            print("Error: Tiempo de espera agotado al conectar con TMDB")
            return {"error": "timeout"}
        except requests.exceptions.ConnectionError:
            print("Error: No se pudo conectar con TMDB. Verifica tu conexión a internet")
            return {"error": "connection_error"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("Error: API Key inválida o expirada")
                return {"error": "invalid_api_key"}
            elif e.response.status_code == 404:
                print("Error: Recurso no encontrado")
                return {"error": "not_found"}
            elif e.response.status_code == 429:
                print("Error: Límite de peticiones excedido")
                return {"error": "rate_limit"}
            else:
                print(f"Error HTTP {e.response.status_code}: {e}")
                return {"error": f"http_error_{e.response.status_code}"}
        except requests.exceptions.RequestException as e:
            print(f"Error general al realizar petición: {e}")
            return {"error": "request_failed"}
    
    def search_movies(self, query: str, page: int = 1, include_adult: bool = False) -> List[Dict]:
        """Buscar películas por título"""
        if not query or not query.strip():
            return []
        
        if page < 1:
            page = 1
        
        endpoint = "/search/movie"
        params = {
            "query": query.strip(),
            "page": min(page, 1000),  # TMDB limita a 1000 páginas
            "include_adult": include_adult
        }
        
        response = self._make_request(endpoint, params)
        
        # Manejar errores específicos
        if "error" in response:
            return []
            
        return response.get('results', [])
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Obtener detalles completos de una película"""
        if not movie_id or movie_id <= 0:
            return {}
            
        endpoint = f"/movie/{movie_id}"
        params = {"append_to_response": "credits,videos,similar,recommendations"}
        
        response = self._make_request(endpoint, params)
        
        # Manejar errores específicos
        if "error" in response:
            return {}
            
        return response
    
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Obtener películas populares"""
        endpoint = "/movie/popular"
        params = {"page": page}
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_top_rated_movies(self, page: int = 1) -> List[Dict]:
        """Obtener películas mejor valoradas"""
        endpoint = "/movie/top_rated"
        params = {"page": page}
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_now_playing_movies(self, page: int = 1) -> List[Dict]:
        """Obtener películas en cines actualmente"""
        endpoint = "/movie/now_playing"
        params = {"page": page}
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_upcoming_movies(self, page: int = 1) -> List[Dict]:
        """Obtener próximos estrenos"""
        endpoint = "/movie/upcoming"
        params = {"page": page}
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_genres(self) -> List[Dict]:
        """Obtener lista de géneros"""
        endpoint = "/genre/movie/list"
        
        response = self._make_request(endpoint)
        return response.get('genres', [])
    
    def discover_movies(self, 
                       genre_ids: List[int] = None,
                       year: int = None,
                       min_rating: float = None,
                       sort_by: str = "popularity.desc",
                       page: int = 1) -> List[Dict]:
        """Descubrir películas con filtros"""
        endpoint = "/discover/movie"
        params = {
            "sort_by": sort_by,
            "page": page
        }
        
        if genre_ids:
            params["with_genres"] = ",".join(map(str, genre_ids))
        if year:
            params["year"] = year
        if min_rating:
            params["vote_average.gte"] = min_rating
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_similar_movies(self, movie_id: int, page: int = 1) -> List[Dict]:
        """Obtener películas similares"""
        endpoint = f"/movie/{movie_id}/similar"
        params = {"page": page}
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_recommendations(self, movie_id: int, page: int = 1) -> List[Dict]:
        """Obtener recomendaciones basadas en una película"""
        endpoint = f"/movie/{movie_id}/recommendations"
        params = {"page": page}
        
        response = self._make_request(endpoint, params)
        return response.get('results', [])
    
    def get_poster_url(self, poster_path: str, size: str = "w500") -> str:
        """Generar URL completa para posters"""
        if not poster_path:
            return None
        return f"{self.image_base_url}/{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = "w1280") -> str:
        """Generar URL completa para fondos"""
        if not backdrop_path:
            return None
        return f"{self.image_base_url}/{size}{backdrop_path}"


def format_movie_info(movie: Dict) -> Dict:
    """Formatear información básica de una película"""
    return {
        'id': movie.get('id'),
        'title': movie.get('title', 'Sin título'),
        'original_title': movie.get('original_title', ''),
        'overview': movie.get('overview', 'Sin descripción disponible'),
        'release_date': movie.get('release_date', 'Fecha no disponible'),
        'vote_average': movie.get('vote_average', 0),
        'vote_count': movie.get('vote_count', 0),
        'popularity': movie.get('popularity', 0),
        'poster_path': movie.get('poster_path'),
        'backdrop_path': movie.get('backdrop_path'),
        'genre_ids': movie.get('genre_ids', []),
        'adult': movie.get('adult', False),
        'original_language': movie.get('original_language', 'Unknown'),
    }


def format_rating(rating: float) -> str:
    """Formatear puntuación con estrellas"""
    if rating == 0:
        return "Sin puntuación"
    
    # Simple text version for compatibility
    stars = "⭐" * int(rating // 2)
    return f"{stars} {rating}/10"





def format_runtime(runtime: int) -> str:
    """Formatear duración en horas y minutos"""
    if not runtime:
        return "Duración no disponible"
    
    hours = runtime // 60
    minutes = runtime % 60
    
    if hours > 0:
        return f"{hours}h {minutes}min"
    else:
        return f"{minutes}min"


def get_genre_names(genre_ids: List[int], genres_list: List[Dict]) -> List[str]:
    """Convertir IDs de géneros a nombres"""
    genre_dict = {genre['id']: genre['name'] for genre in genres_list}
    return [genre_dict.get(genre_id, 'Desconocido') for genre_id in genre_ids]
