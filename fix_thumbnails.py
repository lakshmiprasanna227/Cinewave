#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

# Clear all bad thumbnail references since files don't exist
# The poster_url property will fall back to YouTube or placeholder
movies = Movie.objects.all()
count = movies.update(thumbnail=None)
print(f"Cleared thumbnails from {count} movies")

# Verify
for movie in Movie.objects.all()[:3]:
    print(f"- {movie.title}: poster_url = {movie.poster_url}")
