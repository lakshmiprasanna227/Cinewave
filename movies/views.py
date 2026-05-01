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
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
import json
import requests
from io import BytesIO
from urllib.parse import parse_qs, urlencode, urlparse

from .models import Movie, WatchList, WatchHistory


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
    }
    if origin:
        params['origin'] = origin
    if widget_referrer:
        params['widget_referrer'] = widget_referrer

    return f'https://www.youtube.com/embed/{video_id}?{urlencode(params)}'

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
    
    context = {
        'movie': movie,
        'start_position': start_position,
        'youtube_embed_url': get_youtube_embed_url(
            movie.video_url,
            origin=origin,
            widget_referrer=request.build_absolute_uri(),
        ),
    }
    return render(request, 'video.html', context)


def stream_video(request, movie_id):
    """
    Video streaming endpoint - proxies external video URLs through Django.
    Bypasses CORS restrictions by serving through the Django server.
    """
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Use local video file if available
    if movie.video_file:
        video_path = movie.video_file.path
        try:
            with open(video_path, 'rb') as video_file:
                response = StreamingHttpResponse(
                    video_file.read(),
                    content_type='video/mp4'
                )
                response['Content-Disposition'] = f'inline; filename="{movie.title}.mp4"'
                response['Accept-Ranges'] = 'bytes'
                return response
        except IOError:
            return JsonResponse({'error': 'Video file not found'}, status=404)
    
    # Proxy external video URL
    elif movie.video_url:
        try:
            # Use requests to fetch the external video
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            range_header = request.headers.get('Range')
            if range_header:
                headers['Range'] = range_header
            
            response = requests.get(
                movie.video_url,
                headers=headers,
                stream=True,
                timeout=30,
                allow_redirects=True,
                verify=False  # Disable SSL verification for development
            )
            if response.status_code not in (200, 206):
                response.raise_for_status()
            
            # Extract content type and length
            content_type = response.headers.get('content-type', 'video/mp4')
            content_length = response.headers.get('content-length')
            status = 206 if response.status_code == 206 else 200
            
            def stream_chunks():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            streaming_response = StreamingHttpResponse(
                stream_chunks(),
                content_type=content_type,
                status=status,
            )
            streaming_response['Content-Disposition'] = f'inline; filename="{movie.title}.mp4"'
            streaming_response['Accept-Ranges'] = 'bytes'
            if response.headers.get('content-range'):
                streaming_response['Content-Range'] = response.headers['content-range']
            if content_length:
                streaming_response['Content-Length'] = content_length
            
            return streaming_response
            
        except requests.RequestException as e:
            return JsonResponse(
                {'error': f'Failed to fetch video: {str(e)}'}, 
                status=502
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
    - JSON list of watchlist items
    """
    watchlist = WatchList.objects.filter(user=request.user).select_related('movie')
    
    watchlist_data = []
    for item in watchlist:
        movie = item.movie
        watchlist_data.append({
            'id': item.id,
            'movie_id': movie.id,
            'title': movie.title,
            'thumbnail': movie.poster_url,
            'rating': float(movie.rating),
            'year': movie.year,
            'added_at': item.added_at.isoformat(),
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
    
    Returns:
    - JSON list of recommended movies
    """
    # Get user's watch history to determine preferences
    if request.user.is_authenticated:
        watch_history = WatchHistory.objects.filter(user=request.user).select_related('movie')
        
        if watch_history.exists():
            # Get genres from watched movies
            watched_genres = set(item.movie.genre for item in watch_history)
            
            # Get recommendations based on genres
            recommendations = Movie.objects.filter(genre__in=watched_genres).exclude(
                watch_history__user=request.user
            )[:10]
            
            if recommendations.exists():
                movie_data = []
                for movie in recommendations:
                    movie_data.append({
                        'id': movie.id,
                        'title': movie.title,
                        'thumbnail': movie.poster_url,
                        'rating': float(movie.rating),
                        'genre': movie.get_genre_display(),
                    })
                return JsonResponse({'recommendations': movie_data})
    
    # Default recommendations: top rated movies
    recommendations = Movie.objects.order_by('-rating')[:10]
    
    movie_data = []
    for movie in recommendations:
        movie_data.append({
            'id': movie.id,
            'title': movie.title,
            'thumbnail': movie.poster_url,
            'rating': float(movie.rating),
            'genre': movie.get_genre_display(),
        })
    
    return JsonResponse({'recommendations': movie_data})
