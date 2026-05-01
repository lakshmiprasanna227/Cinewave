import requests
from django.conf import settings

TMDB_API_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/'


def get_api_key():
    return getattr(settings, 'TMDB_API_KEY', '')


def search_movie(title, year=None):
    api_key = get_api_key()
    if not api_key:
        return None

    params = {
        'api_key': api_key,
        'query': title,
        'language': 'en-US',
        'include_adult': False,
    }
    if year:
        params['year'] = year

    response = requests.get(f'{TMDB_API_BASE_URL}/search/movie', params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    results = data.get('results', [])
    if not results:
        return None
    return results[0]


def get_poster_url(poster_path, size='w500'):
    if not poster_path:
        return None
    return f'{TMDB_IMAGE_BASE_URL}{size}{poster_path}'


def download_image(url):
    response = requests.get(url, stream=True, timeout=15)
    response.raise_for_status()
    return response.content
