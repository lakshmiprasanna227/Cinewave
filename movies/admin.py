"""
Django Admin configuration for CineWave movies app.

This module registers the models with Django admin
for easy management through the admin interface.
"""

from django.contrib import admin
from .models import Movie, WatchList, WatchHistory


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Admin interface for Movie model.
    
    Features:
    - List display: title, genre, rating, year, is_featured
    - Search: title, description
    - Filtering: genre, year, is_featured
    - Ordering: created_at
    """
    
    list_display = ['title', 'genre', 'rating', 'year', 'is_featured', 'created_at']
    list_filter = ['genre', 'year', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'rating']
    ordering = ['-created_at']
    
    # Fields to show in the detail view
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'genre', 'year')
        }),
        ('Media', {
            'fields': ('thumbnail', 'video_url', 'video_file')
        }),
        ('Details', {
            'fields': ('rating', 'duration', 'is_featured')
        }),
    )


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    """
    Admin interface for WatchList model.
    
    Features:
    - List display: user, movie, added_at
    - Filtering: user, added_at
    """
    
    list_display = ['user', 'movie', 'added_at']
    list_filter = ['user', 'added_at']
    search_fields = ['user__username', 'movie__title']
    ordering = ['-added_at']


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for WatchHistory model.
    
    Features:
    - List display: user, movie, progress, completed, watched_at
    - Filtering: user, completed
    """
    
    list_display = ['user', 'movie', 'progress', 'completed', 'watched_at']
    list_filter = ['user', 'completed', 'watched_at']
    search_fields = ['user__username', 'movie__title']
    ordering = ['-watched_at']
