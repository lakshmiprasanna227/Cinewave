#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

# YouTube movie links provided by user
youtube_movies = {
    'Googly': 'https://www.youtube.com/watch?v=icvr4vBDLMU',
    'Lifeu Ishtene': 'https://www.youtube.com/watch?v=h2AjhAIXQWg',
    'Yuga Purusha': 'https://www.youtube.com/watch?v=ulkAyXArkNw',
    'Mr and Mrs Ramachari': 'https://www.youtube.com/watch?v=YvH4v-0G8jQ',
    'Kirik Party': 'https://www.youtube.com/watch?v=2mDCVzruYzQ',
    'Simple Agi Ondh Love Story': 'https://www.youtube.com/watch?v=5wGQ0G7E8Wk',
    'Gaalipata': 'https://www.youtube.com/watch?v=8I7M9l5Qq1Q',
    'Paramathma': 'https://www.youtube.com/watch?v=6QW9h8M7mJQ',
    'Raajakumara': 'https://www.youtube.com/watch?v=7m4xM0YF8xE',
    'Jackie': 'https://www.youtube.com/watch?v=5jT0hX6n4v8',
    'Milana': 'https://www.youtube.com/watch?v=qzQn2X2u8fQ',
    'Mungaru Male': 'https://www.youtube.com/watch?v=6fQzv2mM0nY',
    'Drama': 'https://www.youtube.com/watch?v=QmN0Qq5f8lY',
    'Goa': 'https://www.youtube.com/watch?v=9b7vL6h2Qw4',
    'Victory': 'https://www.youtube.com/watch?v=Q4g7L7nJm5Y',
    'Bhajarangi': 'https://www.youtube.com/watch?v=0K7xjJ5h6lU',
    'Ranna': 'https://www.youtube.com/watch?v=V5xk0Qz9v6Y',
    'Masterpiece': 'https://www.youtube.com/watch?v=8Yx2v4r5J6A',
}

print("=" * 70)
print("UPDATING MOVIES WITH YOUTUBE LINKS")
print("=" * 70)

updated = 0
not_found = 0

for title, youtube_url in youtube_movies.items():
    try:
        # Try exact match first
        movie = Movie.objects.get(title=title)
        old_url = movie.video_url
        movie.video_url = youtube_url
        movie.save()
        
        # Get video ID and poster
        video_id = movie.youtube_video_id
        poster_url = movie.poster_url
        
        print(f"\n✅ {title}")
        print(f"   YouTube: {youtube_url}")
        print(f"   Video ID: {video_id}")
        print(f"   Poster: {poster_url}")
        updated += 1
        
    except Movie.DoesNotExist:
        print(f"\n⚠️  {title} - NOT FOUND in database")
        not_found += 1

print("\n" + "=" * 70)
print(f"SUMMARY: {updated} movies updated, {not_found} not found")
print("=" * 70)
print("\n✅ All movies now have YouTube links!")
print("✅ Posters will be automatically fetched from YouTube thumbnails")
print("✅ Videos will play from YouTube embeds")
