"""
Movie models for CineWave application.

This module defines the database models for movies,
watchlist, and related features.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from urllib.parse import parse_qs, urlparse


class Movie(models.Model):
    """
    Movie model representing a film in the database.
    
    Attributes:
        title: Name of the movie
        description: Brief synopsis of the movie
        genre: Category of the movie (Action, Comedy, Drama, etc.)
        thumbnail: Poster image of the movie
        video_url: URL to the video file (can be local or external)
        rating: User rating (0-10 scale)
        year: Release year
        created_at: When the movie was added to the database
        is_featured: Whether to show in hero banner
    """
    
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('horror', 'Horror'),
        ('sci-fi', 'Sci-Fi'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('animation', 'Animation'),
        ('documentary', 'Documentary'),
    ]
    
    title = models.CharField(max_length=200, help_text="Movie title")
    description = models.TextField(help_text="Movie description/synopsis")
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='action')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Video URL or file path")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    year = models.IntegerField(default=2024, help_text="Release year")
    duration = models.IntegerField(default=0, help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Show in hero banner")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Movies'
    
    def __str__(self):
        return self.title
    
    def get_genre_display(self):
        """Return the genre display name."""
        return dict(self.GENRE_CHOICES).get(self.genre, self.genre)

    @property
    def youtube_video_id(self):
        """Extract the YouTube video id from common YouTube URL formats."""
        if not self.video_url:
            return None

        parsed = urlparse(self.video_url)
        host = parsed.netloc.lower().replace('www.', '')

        if host in ('youtube.com', 'm.youtube.com'):
            if parsed.path == '/watch':
                return parse_qs(parsed.query).get('v', [None])[0]
            if parsed.path.startswith('/embed/'):
                return parsed.path.split('/embed/', 1)[1].split('/')[0]
            if parsed.path.startswith('/shorts/'):
                return parsed.path.split('/shorts/', 1)[1].split('/')[0]
        if host == 'youtu.be':
            return parsed.path.strip('/').split('/')[0]

        return None

    @property
    def poster_url(self):
        """Return a local poster URL, or a YouTube thumbnail when available."""
        if self.thumbnail:
            return self.thumbnail.url

        video_id = self.youtube_video_id
        if video_id:
            return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'

        return None


class WatchList(models.Model):
    """
    WatchList model for storing user's favorite movies.
    
    A user can add multiple movies to their watchlist.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlist')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


class WatchHistory(models.Model):
    """
    WatchHistory model for tracking user's viewing progress.
    
    Stores the last position the user watched in each movie.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watch_history')
    watched_at = models.DateTimeField(auto_now=True)
    progress = models.IntegerField(default=0, help_text="Watch progress in seconds")
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-watched_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.progress}s)"
