#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

# Update all movies with working fallback video URLs from archive.org or similar
# Using Big Buck Bunny as a test video
working_video_urls = [
    'https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4',
    'https://commondatastorage.googleapis.com/gtv-videos-library/sample/ElephantsDream.mp4',
    'https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerBlazes.mp4',
    'https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerEscapes.mp4',
    'https://commondatastorage.googleapis.com/gtv-videos-library/sample/Sintel.mp4',
]

movies = Movie.objects.all()
for i, movie in enumerate(movies):
    movie.video_url = working_video_urls[i % len(working_video_urls)]
    movie.save()
    print(f"Updated {movie.title}: {movie.video_url}")

print(f"\nTotal movies updated: {movies.count()}")
