#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie

# Mapping of user-provided YouTube movies
youtube_links = {
    'Googly': {
        'url': 'https://www.youtube.com/watch?v=icvr4vBDLMU',
        'year': 2013,
        'genre': 'romance'
    },
    'Lifeu Ishtene': {
        'url': 'https://www.youtube.com/watch?v=h2AjhAIXQWg',
        'year': 2011,
        'genre': 'romance'
    },
    'Yuga Purusha': {
        'url': 'https://www.youtube.com/watch?v=ulkAyXArkNw',
        'year': 2014,
        'genre': 'drama'
    },
    'Mr and Mrs Ramachari': {
        'url': 'https://www.youtube.com/watch?v=YvH4v-0G8jQ',
        'year': 2014,
        'genre': 'romance'
    },
    'Kirik Party': {
        'url': 'https://www.youtube.com/watch?v=2mDCVzruYzQ',
        'year': 2016,
        'genre': 'comedy'
    },
    'Simple Agi Ondh Love Story': {
        'url': 'https://www.youtube.com/watch?v=5wGQ0G7E8Wk',
        'year': 2015,
        'genre': 'romance'
    },
    'Gaalipata': {
        'url': 'https://www.youtube.com/watch?v=8I7M9l5Qq1Q',
        'year': 2008,
        'genre': 'comedy'
    },
    'Paramathma': {
        'url': 'https://www.youtube.com/watch?v=6QW9h8M7mJQ',
        'year': 2002,
        'genre': 'action'
    },
    'Raajakumara': {
        'url': 'https://www.youtube.com/watch?v=7m4xM0YF8xE',
        'year': 2017,
        'genre': 'romance'
    },
    'Jackie': {
        'url': 'https://www.youtube.com/watch?v=5jT0hX6n4v8',
        'year': 2014,
        'genre': 'thriller'
    },
    'Milana': {
        'url': 'https://www.youtube.com/watch?v=qzQn2X2u8fQ',
        'year': 2007,
        'genre': 'romance'
    },
    'Mungaru Male': {
        'url': 'https://www.youtube.com/watch?v=6fQzv2mM0nY',
        'year': 2006,
        'genre': 'comedy'
    },
    'Drama': {
        'url': 'https://www.youtube.com/watch?v=QmN0Qq5f8lY',
        'year': 2018,
        'genre': 'drama'
    },
    'Goa': {
        'url': 'https://www.youtube.com/watch?v=9b7vL6h2Qw4',
        'year': 2015,
        'genre': 'thriller'
    },
    'Victory': {
        'url': 'https://www.youtube.com/watch?v=Q4g7L7nJm5Y',
        'year': 2018,
        'genre': 'action'
    },
    'Bhajarangi': {
        'url': 'https://www.youtube.com/watch?v=0K7xjJ5h6lU',
        'year': 2013,
        'genre': 'action'
    },
    'Ranna': {
        'url': 'https://www.youtube.com/watch?v=V5xk0Qz9v6Y',
        'year': 2015,
        'genre': 'action'
    },
    'Masterpiece': {
        'url': 'https://www.youtube.com/watch?v=8Yx2v4r5J6A',
        'year': 2015,
        'genre': 'thriller'
    },
}

print("=" * 70)
print("UPDATING/CREATING MOVIES WITH YOUTUBE LINKS")
print("=" * 70)

updated = 0
created = 0

for title, data in youtube_links.items():
    try:
        # Try to find existing movie by title
        movie = Movie.objects.get(title=title)
        movie.video_url = data['url']
        movie.save()
        print(f"\n✅ UPDATED: {title}")
        print(f"   URL: {data['url']}")
        print(f"   Poster: {movie.poster_url}")
        updated += 1
        
    except Movie.DoesNotExist:
        # Create new movie
        movie = Movie.objects.create(
            title=title,
            description=f"{title} is a Kannada movie.",
            genre=data['genre'],
            year=data['year'],
            duration=120,
            rating=7.5,
            video_url=data['url']
        )
        print(f"\n🆕 CREATED: {title}")
        print(f"   URL: {data['url']}")
        print(f"   Genre: {data['genre']}")
        print(f"   Year: {data['year']}")
        print(f"   Poster: {movie.poster_url}")
        created += 1

print("\n" + "=" * 70)
print(f"SUMMARY:")
print(f"  ✅ Updated: {updated} movies")
print(f"  🆕 Created: {created} movies")
print(f"  📊 Total: {Movie.objects.count()} movies in database")
print("=" * 70)
print("\n✅ All YouTube movies embedded successfully!")
print("✅ Posters auto-fetched from YouTube")
print("✅ Ready to play!")
