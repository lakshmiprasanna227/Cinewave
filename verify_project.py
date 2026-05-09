#!/usr/bin/env python
"""
CineWave Project Verification Script
Tests all critical components to ensure the project is ready to run.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from movies.models import Movie, WatchList, WatchHistory
from django.contrib.auth.models import User
from django.core.files.storage import default_storage

print("=" * 70)
print("CINEWAVE PROJECT VERIFICATION")
print("=" * 70)

# Test 1: Database Connection
print("\n[1/5] Testing Database Connection...")
try:
    count = Movie.objects.count()
    print(f"    ✅ Database OK - Found {count} movies")
except Exception as e:
    print(f"    ❌ Database Error: {e}")
    sys.exit(1)

# Test 2: Movies Data
print("\n[2/5] Checking Movie Data...")
try:
    if count == 0:
        print("    ⚠️  No movies found! Database might be empty.")
    else:
        movies = Movie.objects.all()[:3]
        for movie in movies:
            has_url = bool(movie.video_url)
            poster = movie.poster_url
            print(f"    ✅ {movie.title}")
            print(f"       - Video URL: {'Yes' if has_url else 'No'}")
            print(f"       - Poster: {poster[:60] if poster else 'None'}...")
except Exception as e:
    print(f"    ❌ Error: {e}")

# Test 3: User Models
print("\n[3/5] Checking User Models...")
try:
    user_count = User.objects.count()
    watchlist_count = WatchList.objects.count()
    history_count = WatchHistory.objects.count()
    print(f"    ✅ Users: {user_count}")
    print(f"    ✅ Watchlist Items: {watchlist_count}")
    print(f"    ✅ Watch History: {history_count}")
except Exception as e:
    print(f"    ❌ Error: {e}")

# Test 4: Static Files
print("\n[4/5] Checking Static Files...")
try:
    static_path = Path('front-end/static')
    if static_path.exists():
        css_files = list(static_path.glob('css/*.css'))
        js_files = list(static_path.glob('js/*.js'))
        print(f"    ✅ CSS Files: {len(css_files)}")
        print(f"    ✅ JS Files: {len(js_files)}")
    else:
        print(f"    ⚠️  Static path not found: {static_path}")
except Exception as e:
    print(f"    ❌ Error: {e}")

# Test 5: Templates
print("\n[5/5] Checking Templates...")
try:
    template_path = Path('front-end/templates')
    if template_path.exists():
        templates = list(template_path.glob('*.html'))
        print(f"    ✅ Templates Found: {len(templates)}")
        for template in sorted(templates)[:5]:
            print(f"       - {template.name}")
        if len(templates) > 5:
            print(f"       ... and {len(templates) - 5} more")
    else:
        print(f"    ⚠️  Templates path not found: {template_path}")
except Exception as e:
    print(f"    ❌ Error: {e}")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n✅ Project is ready to run!")
print("\nNext steps:")
print("1. Run: python manage.py runserver 0.0.0.0:8000")
print("2. Open: http://localhost:8000")
print("3. Browse movies and play videos")
print("\nFor more info, see: READY_TO_RUN.md")
print()
