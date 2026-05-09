"""
Management command to seed Kannada movies with YouTube URLs for reliable thumbs/videos.
"""

from django.core.management.base import BaseCommand
from movies.models import Movie

KANNADA_MOVIES = [
    {
        'title': 'Shhh!',
        'description': 'Kannada thriller movie.',
        'video_url': 'https://www.youtube.com/watch?v=Iq8NlxJsG8g',
        'genre': 'thriller',
        'rating': 7.5,
        'year': 2000,
        'duration': 150,
        'is_featured': False,
    },
    {
        'title': 'Yuga Purusha',
        'description': 'Kannada drama movie.',
        'video_url': 'https://www.youtube.com/watch?v=0t5tKpK8zqM',
        'genre': 'drama',
        'rating': 8.0,
        'year': 2014,
        'duration': 160,
        'is_featured': False,
    },
    {
        'title': 'Lifeu Ishtene',
        'description': 'Kannada romantic movie.',
        'video_url': 'https://www.youtube.com/watch?v=4XKX5p7kXjQ',
        'genre': 'romance',
        'rating': 8.2,
        'year': 2011,
        'duration': 145,
        'is_featured': False,
    },
    {
        'title': 'Googly',
        'description': 'Popular Kannada romantic comedy.',
        'video_url': 'https://www.youtube.com/watch?v=Hc6rX9mXK5A',
        'genre': 'romance',
        'rating': 7.8,
        'year': 2013,
        'duration': 150,
        'is_featured': True,
    },
    # Add other movies without 'thumbnail' - uses YouTube thumbs
    {
        'title': 'Endendigu',
        'description': 'Kannada drama.',
        'video_url': 'https://www.youtube.com/watch?v=icvr4vBDLMU',
        'genre': 'drama',
        'rating': 7.0,
        'year': 2015,
        'duration': 140,
        'is_featured': False,
    },
    {
        'title': 'Tagaru Palya',
        'description': 'Kannada action.',
        'video_url': 'https://www.youtube.com/watch?v=PyAZtkvN5gI',
        'genre': 'action',
        'rating': 7.2,
        'year': 2016,
        'duration': 155,
        'is_featured': False,
    },
    {
        'title': 'Thamas',
        'description': 'Kannada movie.',
        'video_url': 'https://www.youtube.com/watch?v=nazwDbR248E',
        'genre': 'drama',
        'rating': 7.4,
        'year': 2018,
        'duration': 130,
        'is_featured': False,
    },
    {
        'title': 'Dharmasya',
        'description': 'Kannada epic.',
        'video_url': 'https://www.youtube.com/watch?v=o3xIMTIIYHU',
        'genre': 'action',
        'rating': 7.6,
        'year': 2019,
        'duration': 165,
        'is_featured': False,
    },
    {
        'title': 'Milana',
        'description': 'Kannada romantic drama.',
        'video_url': 'https://www.youtube.com/watch?v=WWDBGOoDKe8',
        'genre': 'romance',
        'rating': 8.1,
        'year': 2007,
        'duration': 160,
        'is_featured': False,
    },
    {
        'title': 'Kotigobba',
        'description': 'Kannada action.',
        'video_url': 'https://www.youtube.com/watch?v=s1LqXWHpCb0',
        'genre': 'action',
        'rating': 7.0,
        'year': 2016,
        'duration': 170,
        'is_featured': False,
    },
    {
        'title': 'Suryavamsha',
        'description': 'Kannada drama.',
        'video_url': 'https://www.youtube.com/watch?v=yiYMDyyGZLE',
        'genre': 'drama',
        'rating': 7.3,
        'year': 1999,
        'duration': 155,
        'is_featured': False,
    },
    {
        'title': 'Keralida Simha',
        'description': 'Kannada action.',
        'video_url': 'https://www.youtube.com/watch?v=7UGBwGznSpU',
        'genre': 'action',
        'rating': 6.8,
        'year': 1981,
        'duration': 140,
        'is_featured': False,
    },
    {
        'title': 'Jeevnane Natka Samy',
        'description': 'Kannada comedy.',
        'video_url': 'https://www.youtube.com/watch?v=4PmggNjJ8cc',
        'genre': 'comedy',
        'rating': 7.1,
        'year': 2013,
        'duration': 135,
        'is_featured': False,
    },
    {
        'title': 'Mavana Magalu',
        'description': 'Kannada family drama.',
        'video_url': 'https://www.youtube.com/watch?v=IQqGVRrtLxM',
        'genre': 'drama',
        'rating': 7.5,
        'year': 2016,
        'duration': 150,
        'is_featured': False,
    },
    {
        'title': 'Beat',
        'description': 'Kannada youth movie.',
        'video_url': 'https://www.youtube.com/watch?v=WkMogjriz9I',
        'genre': 'drama',
        'rating': 7.2,
        'year': 2008,
        'duration': 145,
        'is_featured': False,
    },
    {
        'title': 'Harom Hara',
        'description': 'Kannada action thriller.',
        'video_url': 'https://www.youtube.com/watch?v=idFFYxiZurc',
        'genre': 'action',
        'rating': 7.4,
        'year': 2024,
        'duration': 160,
        'is_featured': False,
    },
]

class Command(BaseCommand):
    help = 'Seed Kannada movies with YouTube embeds - reliable thumbs/videos'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Kannada movies with YouTube thumbnails...')
        
        Movie.objects.all().delete()
        self.stdout.write('Cleared existing movies')
        
        for index, movie_info in enumerate(KANNADA_MOVIES):
            movie = Movie.objects.create(
                **movie_info
            )
            thumb = movie.poster_url
            self.stdout.write(self.style.SUCCESS(f'Created: {movie.title} ({movie.genre}) - {movie.video_url} - Thumb: {thumb}'))
        
        total = Movie.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\nTotal movies: {total} - Thumbs from YouTube hqdefault'))
        self.stdout.write('Googly featured. Reload server page to see.')

