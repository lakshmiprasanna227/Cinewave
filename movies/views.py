"""
Views for CineWave application.

This module contains all the views including:
- Template views (HTML pages)
- API views (JSON responses)
- Authentication views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import re
import os
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Count
from django.utils.html import escape
import json
import requests
from io import BytesIO
from urllib.parse import parse_qs, urlencode, urlparse

from .models import Movie, WatchList, WatchHistory
from .forms import UserProfileForm, PasswordChangeForm, UserSettingsForm


# =====================================================
# TEMPLATE VIEWS (HTML Pages)
# =====================================================

def get_youtube_embed_url(url, origin=None, widget_referrer=None):
    """Return a YouTube embed URL for supported YouTube video URLs."""
    if not url:
        return None

    parsed = urlparse(url)
    host = parsed.netloc.lower().replace('www.', '')
    video_id = None

    if host in ('youtube.com', 'm.youtube.com'):
        if parsed.path == '/watch':
            video_id = parse_qs(parsed.query).get('v', [None])[0]
        elif parsed.path.startswith('/embed/'):
            video_id = parsed.path.split('/embed/', 1)[1].split('/')[0]
        elif parsed.path.startswith('/shorts/'):
            video_id = parsed.path.split('/shorts/', 1)[1].split('/')[0]
    elif host == 'youtu.be':
        video_id = parsed.path.strip('/').split('/')[0]

    if not video_id:
        return None

    params = {
        'rel': '0',
        'modestbranding': '1',
        'enablejsapi': '1',
    }
    if origin:
        params['origin'] = origin
    if widget_referrer:
        params['widget_referrer'] = widget_referrer

    return f'https://www.youtube.com/embed/{video_id}?{urlencode(params)}'


def is_direct_video_url(url):
    """Return True when the URL points to a browser-playable video file."""
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.path.lower().endswith(('.mp4', '.webm', '.ogg', '.mov', '.m4v'))


def fallback_poster(request, movie_id):
    """Serve a local SVG poster so broken external posters never leave blank cards."""
    movie = get_object_or_404(Movie, id=movie_id)
    title = escape(movie.title)
    genre = escape(movie.get_genre_display())
    initials = ''.join(part[0] for part in movie.title.split()[:3]).upper() or 'CW'
    initials = escape(initials[:3])
    palettes = {
        'action': ('#b91c1c', '#111827'),
        'comedy': ('#ca8a04', '#1f2937'),
        'drama': ('#7c3aed', '#111827'),
        'horror': ('#374151', '#020617'),
        'sci-fi': ('#0e7490', '#111827'),
        'romance': ('#be185d', '#111827'),
        'thriller': ('#4f46e5', '#111827'),
        'animation': ('#16a34a', '#111827'),
        'documentary': ('#475569', '#111827'),
    }
    accent, bg = palettes.get(movie.genre, ('#e50914', '#141414'))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="750" viewBox="0 0 500 750" role="img" aria-label="{title} poster">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{accent}"/>
      <stop offset="0.52" stop-color="{bg}"/>
      <stop offset="1" stop-color="#050505"/>
    </linearGradient>
  </defs>
  <rect width="500" height="750" fill="url(#bg)"/>
  <rect x="32" y="32" width="436" height="686" rx="18" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="3"/>
  <circle cx="250" cy="238" r="92" fill="rgba(255,255,255,.12)"/>
  <text x="250" y="263" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="72" font-weight="700" fill="#fff">{initials}</text>
  <text x="250" y="514" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="700" fill="#fff">
    <tspan x="250">{title[:24]}</tspan>
  </text>
  <text x="250" y="568" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="22" fill="rgba(255,255,255,.78)">{movie.year}  |  {genre}</text>
  <text x="250" y="666" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" letter-spacing="5" fill="rgba(255,255,255,.55)">CINEWAVE</text>
</svg>'''
    return HttpResponse(svg, content_type='image/svg+xml')

def home(request):
    """
    Homepage view displaying the Netflix-style interface.
    
    Shows:
    - Featured movie (hero banner)
    - Multiple movie rows by genre
    - Trending movies
    """
    # Get featured movie for hero banner
    featured = Movie.objects.filter(is_featured=True).first()
    if not featured:
        featured = Movie.objects.first()
    
    # Get movies by genre
    action_movies = Movie.objects.filter(genre='action')[:10]
    comedy_movies = Movie.objects.filter(genre='comedy')[:10]
    drama_movies = Movie.objects.filter(genre='drama')[:10]
    sci_fi_movies = Movie.objects.filter(genre='sci-fi')[:10]
    horror_movies = Movie.objects.filter(genre='horror')[:10]
    trending_movies = Movie.objects.order_by('-rating')[:10]
    new_popular_movies = Movie.objects.order_by('-year', '-rating')[:10]
    
    # Get all genres for filtering
    genres = dict(Movie.GENRE_CHOICES)
    
    # Helper function to get thumbnail URL or placeholder
    def get_thumbnail_url(movie):
        if movie.poster_url:
            return movie.poster_url
        return f"https://picsum.photos/seed/{movie.id}/300/450"
    
    def get_hero_image_url(movie):
        if movie.poster_url:
            return movie.poster_url
        return f"https://picsum.photos/seed/{movie.id}/1280/720"
    
    context = {
        'featured': featured,
        'featured_thumbnail': get_hero_image_url(featured) if featured else None,
        'action_movies': action_movies,
        'comedy_movies': comedy_movies,
        'drama_movies': drama_movies,
        'sci_fi_movies': sci_fi_movies,
        'horror_movies': horror_movies,
        'trending_movies': trending_movies,
        'new_popular_movies': new_popular_movies,
        'genres': genres,
    }
    return render(request, 'home.html', context)


def movie_detail(request, movie_id):
    """
    Movie detail page view.
    
    Displays:
    - Full movie information
    - Play button
    - Add to watchlist button
    - Similar movies
    """
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Get similar movies (same genre)
    similar_movies = Movie.objects.filter(genre=movie.genre).exclude(id=movie.id)[:6]
    
    # Check if movie is in user's watchlist
    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = WatchList.objects.filter(user=request.user, movie=movie).exists()
    
    context = {
        'movie': movie,
        'similar_movies': similar_movies,
        'in_watchlist': in_watchlist,
    }
    return render(request, 'movie.html', context)


def watch_video(request, movie_id):
    """
    Video streaming page view.
    
    Displays:
    - HTML5 video player
    - Movie information
    - Playback controls
    """
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Get watch history for resuming
    watch_history = None
    if request.user.is_authenticated:
        watch_history = WatchHistory.objects.filter(user=request.user, movie=movie).first()
    start_position = watch_history.progress if watch_history else 0
    origin = f'{request.scheme}://{request.get_host()}'
    
    youtube_embed_url = get_youtube_embed_url(
        movie.video_url,
        origin=origin,
        widget_referrer=request.build_absolute_uri(),
    )

    video_source_url = None
    if not youtube_embed_url:
        if movie.video_file:
            video_source_url = request.build_absolute_uri(movie.video_file.url)

    context = {
        'movie': movie,
        'start_position': start_position,
        'youtube_embed_url': youtube_embed_url,
        'video_source_url': video_source_url,
    }
    return render(request, 'video.html', context)


def stream_video(request, movie_id):
    """
    Video streaming endpoint - handles both local files and external videos.
    Proxies external videos through Django to bypass CORS restrictions.
    """
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Use local video file if available
    if movie.video_file:
        video_path = movie.video_file.path
        try:
            file_size = os.path.getsize(video_path)
            range_header = request.headers.get('Range')
            start = 0
            end = file_size - 1
            status_code = 200

            if range_header:
                match = re.match(r'bytes=(\d*)-(\d*)', range_header)
                if match:
                    if match.group(1):
                        start = int(match.group(1))
                    if match.group(2):
                        end = int(match.group(2))
                    if end >= file_size:
                        end = file_size - 1
                    if start > end:
                        return HttpResponse(status=416)
                    status_code = 206

            length = end - start + 1
            with open(video_path, 'rb') as video_file:
                video_file.seek(start)
                response = StreamingHttpResponse(
                    video_file.read(length),
                    content_type='video/mp4',
                    status=status_code
                )
                response['Content-Disposition'] = f'inline; filename="{movie.title}.mp4"'
                response['Accept-Ranges'] = 'bytes'
                response['Content-Length'] = str(length)
                if status_code == 206:
                    response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                # Add CORS headers
                response['Access-Control-Allow-Origin'] = '*'
                return response
        except IOError:
            return JsonResponse({'error': 'Video file not found'}, status=404)
    
    # Proxy external video URL
    elif movie.video_url:
        if not is_direct_video_url(movie.video_url):
            return JsonResponse({'error': 'This video URL is not a direct playable file'}, status=400)

        try:
            # Fetch external video with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            range_header = request.headers.get('Range')
            if range_header:
                headers['Range'] = range_header
            
            response = requests.get(
                movie.video_url,
                headers=headers,
                stream=True,
                timeout=60,
                allow_redirects=True,
                verify=False
            )
            
            if response.status_code not in (200, 206):
                return JsonResponse(
                    {'error': f'Remote server returned status {response.status_code}'}, 
                    status=response.status_code
                )
            
            # Extract content type
            content_type = response.headers.get('content-type', 'video/mp4')
            content_length = response.headers.get('content-length', '')
            
            # Stream the content
            def generate():
                try:
                    for chunk in response.iter_content(chunk_size=65536):
                        if chunk:
                            yield chunk
                finally:
                    response.close()
            
            streaming_response = StreamingHttpResponse(
                generate(),
                content_type=content_type,
                status=response.status_code
            )
            streaming_response['Accept-Ranges'] = 'bytes'
            if content_length:
                streaming_response['Content-Length'] = content_length
            if response.headers.get('content-range'):
                streaming_response['Content-Range'] = response.headers['content-range']
            # Add CORS headers to allow cross-origin playback
            streaming_response['Access-Control-Allow-Origin'] = '*'
            streaming_response['Cross-Origin-Resource-Policy'] = 'cross-origin'
            return streaming_response
            
        except requests.exceptions.RequestException as e:
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {'error': f'Failed to fetch video: {str(e)}'}, 
                status=502
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {'error': f'Stream error: {str(e)}'}, 
                status=500
            )
    
    return JsonResponse({'error': 'No video available'}, status=404)


def login_view(request):
    """
    Login page view.
    
    Handles user authentication.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def register_view(request):
    """
    Registration page view.
    
    Handles new user registration.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    """
    Logout view.
    
    Logs out the user and redirects to home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def watchlist_page(request):
    """
    Watchlist page view.
    
    Displays user's saved movies.
    """
    watchlist = WatchList.objects.filter(user=request.user).select_related('movie')
    
    context = {
        'watchlist': watchlist,
    }
    return render(request, 'watchlist.html', context)


# =====================================================
# API VIEWS (JSON Responses)
# =====================================================

def api_movies(request):
    """
    API endpoint to get all movies.
    
    Query Parameters:
    - genre: Filter by genre
    - search: Search by title
    
    Returns:
    - JSON list of movies with full media URLs
    """
    movies = Movie.objects.all()
    
    # Filter by genre if provided
    genre = request.GET.get('genre')
    if genre:
        movies = movies.filter(genre=genre)
    
    # Search by title if provided
    search = request.GET.get('search')
    if search:
        movies = movies.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    # Limit results
    movies = movies[:50]
    
    # Serialize movie data with full URLs
    movie_data = []
    for movie in movies:
        # Get thumbnail URL with full domain
        thumbnail_url = movie.poster_url or f"https://picsum.photos/seed/{movie.id}/300/450"
        if thumbnail_url.startswith('/'):
            thumbnail_url = request.build_absolute_uri(thumbnail_url)
        
        movie_data.append({
            'id': movie.id,
            'title': movie.title,
            'description': movie.description[:100] + '...' if len(movie.description) > 100 else movie.description,
            'genre': movie.get_genre_display(),
            'genre_key': movie.genre,
            'thumbnail': thumbnail_url,
            'rating': float(movie.rating),
            'year': movie.year,
            'duration': movie.duration,
        })
    
    return JsonResponse({'movies': movie_data})


def api_movie_detail(request, movie_id):
    """
    API endpoint to get a single movie by ID.
    
    Returns:
    - JSON object with movie details with full URLs
    """
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Build full URLs for media files
    thumbnail_url = movie.poster_url or f"https://picsum.photos/seed/{movie.id}/300/450"
    if thumbnail_url.startswith('/'):
        thumbnail_url = request.build_absolute_uri(thumbnail_url)
    
    video_url = None
    if movie.video_url:
        video_url = movie.video_url
    elif movie.video_file:
        video_url = request.build_absolute_uri(movie.video_file.url)
    
    movie_data = {
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'genre': movie.get_genre_display(),
        'genre_key': movie.genre,
        'thumbnail': thumbnail_url,
        'video_url': video_url,
        'rating': float(movie.rating),
        'year': movie.year,
        'duration': movie.duration,
        'created_at': movie.created_at.isoformat(),
    }
    
    return JsonResponse({'movie': movie_data})


@login_required
@require_http_methods(["POST"])
def api_watchlist_add(request):
    """
    API endpoint to add a movie to watchlist.
    
    Request Body (JSON):
    - movie_id: ID of the movie to add
    
    Returns:
    - JSON success message
    """
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        
        if not movie_id:
            return JsonResponse({'error': 'Movie ID is required'}, status=400)
        
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Check if already in watchlist
        if WatchList.objects.filter(user=request.user, movie=movie).exists():
            return JsonResponse({'error': 'Movie already in watchlist'}, status=400)
        
        # Add to watchlist
        watchlist_item = WatchList.objects.create(user=request.user, movie=movie)
        
        return JsonResponse({
            'success': True,
            'message': f'{movie.title} added to watchlist',
            'watchlist_id': watchlist_item.id
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
@require_http_methods(["DELETE"])
def api_watchlist_remove(request, movie_id):
    """
    API endpoint to remove a movie from watchlist.
    
    Path Parameters:
    - movie_id: ID of the movie to remove
    
    Returns:
    - JSON success message
    """
    movie = get_object_or_404(Movie, id=movie_id)
    
    try:
        watchlist_item = WatchList.objects.get(user=request.user, movie=movie)
        watchlist_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{movie.title} removed from watchlist'
        })
    except WatchList.DoesNotExist:
        return JsonResponse({'error': 'Movie not in watchlist'}, status=404)


@login_required
def api_watchlist(request):
    """
    API endpoint to get user's watchlist.
    
    Returns:
    - JSON list of watchlist items with full media URLs
    """
    watchlist = WatchList.objects.filter(user=request.user).select_related('movie')
    
    watchlist_data = []
    debug_posters = []

    for item in watchlist:
        movie = item.movie

        # Get thumbnail URL with full domain
        thumbnail_url = movie.poster_url or f"https://picsum.photos/seed/{movie.id}/300/450"
        if thumbnail_url.startswith('/'):
            thumbnail_url = request.build_absolute_uri(thumbnail_url)

        watchlist_data.append({
            'id': item.id,
            'movie_id': movie.id,
            'title': movie.title,
            'thumbnail': thumbnail_url,
            'rating': float(movie.rating),
            'year': movie.year,
            'added_at': item.added_at.isoformat(),
        })

        if getattr(settings, 'DEBUG', False) and len(debug_posters) < 5:
            raw_name = ''
            try:
                raw_name = movie.thumbnail.name if movie.thumbnail else ''
            except Exception:
                raw_name = ''
            debug_posters.append({
                'id': movie.id,
                'title': movie.title,
                'thumbnail_name': raw_name,
                'poster_url': getattr(movie, 'poster_url', None),
                'video_url': movie.video_url,
            })

    if getattr(settings, 'DEBUG', False) and debug_posters:
        # Temporary server-side visibility
        print('DEBUG /api/watchlist/ debug_posters:', debug_posters)

        return JsonResponse({
            'watchlist': watchlist_data,
            'debug_posters': debug_posters,
        })

    return JsonResponse({'watchlist': watchlist_data})


@login_required
@require_http_methods(["POST"])
def api_save_progress(request):
    """
    API endpoint to save watch progress.
    
    Request Body (JSON):
    - movie_id: ID of the movie
    - progress: Watch progress in seconds
    - completed: Whether the movie is completed
    
    Returns:
    - JSON success message
    """
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        progress = data.get('progress', 0)
        completed = data.get('completed', False)
        
        if not movie_id:
            return JsonResponse({'error': 'Movie ID is required'}, status=400)
        
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Save or update watch history
        watch_history, created = WatchHistory.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={
                'progress': progress,
                'completed': completed
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Progress saved'
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def api_recommendations(request):
    """
    API endpoint to get movie recommendations.
    
    Uses genre-based and rating-based recommendations.
    For authenticated users: recommends based on watch history genres
    For anonymous users: returns top rated movies
    
    Returns:
    - JSON list of recommended movies with full media URLs
    """
    # Helper function to get thumbnail URL with full domain (never returns empty)
    def get_thumbnail_url(movie):
        try:
            thumbnail_url = movie.poster_url
        except Exception:
            thumbnail_url = None

        if not thumbnail_url or thumbnail_url == 'N/A':
            thumbnail_url = f"https://picsum.photos/seed/{movie.id}/300/450"

        if thumbnail_url.startswith('/'):
            thumbnail_url = request.build_absolute_uri(thumbnail_url)

        return thumbnail_url
    
    # Collect all watched/watchlisted movie IDs for exclusion
    excluded_movie_ids = set()
    watched_genres = set()
    debug_posters = []
    
    def maybe_collect_debug(movie, returned_thumbnail):
        # Temporary debug visibility
        if getattr(settings, 'DEBUG', False) and len(debug_posters) < 5:
            raw_name = ''
            try:
                raw_name = movie.thumbnail.name if movie.thumbnail else ''
            except Exception:
                raw_name = ''
            debug_posters.append({
                'id': movie.id,
                'title': movie.title,
                'thumbnail_name': raw_name,          # closest available to "raw OMDb Poster"
                'poster_url': getattr(movie, 'poster_url', None),
                'thumbnail_returned': returned_thumbnail,
                'video_url': movie.video_url,
            })

    if request.user.is_authenticated:
        # Get user's watch history to determine preferences
        watch_history = WatchHistory.objects.filter(user=request.user).select_related('movie')
        
        if watch_history.exists():
            # Get genres from watched movies
            for item in watch_history:
                watched_genres.add(item.movie.genre)
                excluded_movie_ids.add(item.movie.id)
            
            # Also get watchlist movie IDs to exclude
            watchlist_movies = WatchList.objects.filter(user=request.user).values_list('movie_id', flat=True)
            excluded_movie_ids.update(watchlist_movies)
            
            # Get recommendations based on genres
            if watched_genres:
                recommendations_qs = Movie.objects.filter(genre__in=watched_genres)
                
                # Exclude already watched/watchlisted movies
                if excluded_movie_ids:
                    recommendations_qs = recommendations_qs.exclude(id__in=excluded_movie_ids)
                
                recommendations = list(recommendations_qs.order_by('-rating')[:10])
                
                # If we got genre-based recommendations, return them
                if recommendations:
                    movie_data = []
                    for movie in recommendations:
                        thumb = get_thumbnail_url(movie)
                        movie_data.append({
                            'id': movie.id,
                            'title': movie.title,
                            'thumbnail': thumb,
                            'rating': float(movie.rating),
                            'genre': movie.get_genre_display(),
                        })
                        maybe_collect_debug(movie, thumb)

                    if getattr(settings, 'DEBUG', False) and debug_posters:
                        print('DEBUG /api/recommendations/ debug_posters:', debug_posters)
                        return JsonResponse({'recommendations': movie_data, 'debug_posters': debug_posters})

                    return JsonResponse({'recommendations': movie_data})
    
    # Default recommendations: top rated movies (fallback for all users)
    # Exclude any movies the user has already watched or in watchlist
    recommendations_qs = Movie.objects.all()
    
    if excluded_movie_ids:
        recommendations_qs = recommendations_qs.exclude(id__in=excluded_movie_ids)
    
    recommendations = list(recommendations_qs.order_by('-rating')[:10])
    
    movie_data = []
    for movie in recommendations:
        thumb = get_thumbnail_url(movie)
        movie_data.append({
            'id': movie.id,
            'title': movie.title,
            'thumbnail': thumb,
            'rating': float(movie.rating),
            'genre': movie.get_genre_display(),
        })
        maybe_collect_debug(movie, thumb)
    
    if getattr(settings, 'DEBUG', False) and debug_posters:
        print('DEBUG /api/recommendations/ debug_posters:', debug_posters)
        return JsonResponse({'recommendations': movie_data, 'debug_posters': debug_posters})
    
    return JsonResponse({'recommendations': movie_data})


# =====================================================
# USER ACCOUNT VIEWS (Profile, Settings, Dashboard)
# =====================================================

@login_required
def profile_view(request):
    """
    User profile page view.
    
    Displays and updates user profile information.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def settings_view(request):
    """
    User settings page view.
    
    Displays and updates user application preferences.
    """
    # Get current settings from session or cookies
    current_settings = {
        'theme': request.session.get('theme', 'dark'),
        'language': request.session.get('language', 'en'),
        'autoplay_next': request.session.get('autoplay_next', True),
        'volume_level': request.session.get('volume_level', 50),
        'default_quality': request.session.get('default_quality', 'auto'),
    }
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            # Save settings to session
            request.session['theme'] = form.cleaned_data['theme']
            request.session['language'] = form.cleaned_data['language']
            request.session['autoplay_next'] = form.cleaned_data['autoplay_next']
            request.session['volume_level'] = form.cleaned_data['volume_level']
            request.session['default_quality'] = form.cleaned_data['default_quality']
            
            messages.success(request, 'Settings saved successfully!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserSettingsForm(initial=current_settings)
    
    context = {
        'form': form,
        'current_settings': current_settings,
    }
    return render(request, 'settings.html', context)


@login_required
def password_change_view(request):
    """
    Password change page view.
    
    Allows users to change their password.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, 'Password changed successfully! Please sign in again.')
            logout(request)
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'password_change.html', context)


@login_required
def dashboard_view(request):
    """
    User dashboard page view.
    
    Displays user statistics and activity.
    """
    # Get user statistics
    watchlist_count = WatchList.objects.filter(user=request.user).count()
    watch_history_count = WatchHistory.objects.filter(user=request.user).count()
    completed_count = WatchHistory.objects.filter(
        user=request.user, 
        completed=True
    ).count()
    
    # Get recent activity
    recent_watch_history = WatchHistory.objects.filter(
        user=request.user
    ).select_related('movie').order_by('-watched_at')[:5]
    
    # Get watchlist items
    watchlist_items = WatchList.objects.filter(
        user=request.user
    ).select_related('movie').order_by('-added_at')[:5]
    
    # Get genre preferences from watch history
    genre_stats = WatchHistory.objects.filter(
        user=request.user
    ).values('movie__genre').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Calculate total watch time
    total_watch_time = sum(
        h.progress for h in WatchHistory.objects.filter(user=request.user)
    )
    total_hours = total_watch_time // 3600
    total_minutes = (total_watch_time % 3600) // 60
    
    context = {
        'watchlist_count': watchlist_count,
        'watch_history_count': watch_history_count,
        'completed_count': completed_count,
        'recent_watch_history': recent_watch_history,
        'watchlist_items': watchlist_items,
        'genre_stats': genre_stats,
        'total_watch_time': f'{total_hours}h {total_minutes}m',
    }
    return render(request, 'dashboard.html', context)


@login_required
def delete_account_view(request):
    """
    Delete account view.
    
    Allows users to delete their account.
    """
    if request.method == 'POST':
        # Check for confirmation
        confirmation = request.POST.get('confirmation', '')
        if confirmation == 'DELETE':
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Please type DELETE to confirm.')
    
    return render(request, 'delete_account.html')
