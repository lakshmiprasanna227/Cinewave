#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

movie = Movie.objects.get(id=68)
print(f"Movie: {movie.title}")
print(f"  - video_url: {movie.video_url}")
print(f"  - youtube_video_id: {movie.youtube_video_id}")
print(f"  - video_file: {movie.video_file}")

# Check a few more movies
print("\nAll movies:")
for m in Movie.objects.all()[:5]:
    print(f"- {m.title}: video_url={m.video_url}, video_id={m.youtube_video_id}")
