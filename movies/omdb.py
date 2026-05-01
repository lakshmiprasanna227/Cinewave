import requests
from django.conf import settings

OMDB_API_BASE_URL = 'https://www.omdbapi.com/'


def get_api_key():
    return getattr(settings, 'OMDB_API_KEY', '')


def search_movie(title, year=None):
    api_key = get_api_key()
    if not api_key:
        return None

    params = {
        'apikey': api_key,
        't': title,
        'type': 'movie',
        'plot': 'short',
        'r': 'json',
    }
    if year:
        params['y'] = year

    response = requests.get(OMDB_API_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    if data.get('Response') != 'True':
        return None
    return data


def get_poster_url(poster_url):
    if not poster_url or poster_url == 'N/A':
        return None
    return poster_url
