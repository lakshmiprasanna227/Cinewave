#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

movies = Movie.objects.all()[:5]
for movie in movies:
    print(f"Movie: {movie.title}")
    print(f"  - Has thumbnail: {bool(movie.thumbnail)}")
    print(f"  - Has video_url: {bool(movie.video_url)}")
    print(f"  - Has video_file: {bool(movie.video_file)}")
    print(f"  - poster_url: {movie.poster_url}")
    print()
