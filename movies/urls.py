"""
URL patterns for CineWave movies app.

Maps URLs to views for:
- Home page
- Movie detail page
- Video player
- Authentication
- API endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    # =====================================================
    # TEMPLATE URLS
    # =====================================================
    
    # Home page
    path('', views.home, name='home'),
    
    # Movie detail page
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    
    # Video player (protected - requires login)
    path('watch/<int:movie_id>/', views.watch_video, name='watch_video'),
    
    # Video streaming endpoint (proxy for external videos)
    path('stream/<int:movie_id>/', views.stream_video, name='stream_video'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
# Watchlist page
    path('watchlist/', views.watchlist_page, name='watchlist'),
    
    # =====================================================
    # API URLS
    # =====================================================
    
    # Movies API
    path('api/movies/', views.api_movies, name='api_movies'),
    path('api/movies/<int:movie_id>/', views.api_movie_detail, name='api_movie_detail'),
    
    # Watchlist API
    path('api/watchlist/add/', views.api_watchlist_add, name='api_watchlist_add'),
    path('api/watchlist/<int:movie_id>/', views.api_watchlist_remove, name='api_watchlist_remove'),
    path('api/watchlist/', views.api_watchlist, name='api_watchlist'),
    
    # Progress API
    path('api/save-progress/', views.api_save_progress, name='api_save_progress'),
    
    # Recommendations API
    path('api/recommendations/', views.api_recommendations, name='api_recommendations'),
]
