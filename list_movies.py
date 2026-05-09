#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

print("Current movies in database:")
movies = Movie.objects.all().values_list('id', 'title', 'genre', 'year')
for movie_id, title, genre, year in movies:
    print(f"{movie_id}. {title} ({genre}, {year})")
