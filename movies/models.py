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
    director = models.CharField(max_length=200, blank=True, default='', help_text="Movie director")
    cast = models.TextField(blank=True, default='', help_text="Main cast members (comma-separated)")
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
    def has_playable_video(self):
        """Return True when the movie has a YouTube embed or uploaded video file."""
        return bool(self.youtube_video_id or self.video_file)

    @property
    def poster_url(self):
        """
        Return a safe poster URL (never returns N/A or empty).

        - Normalizes null/empty/"N/A"
        - Converts http->https
        - Normalizes local media paths to /media/...
        - Uses a deterministic local fallback when invalid.
        """
        local_fallback = '/media/thumbnails/default_poster.jpg'

        def normalize_url(value):
            if value is None:
                return None
            if not isinstance(value, str):
                value = str(value)

            v = value.strip()
            if not v or v.upper() == 'N/A':
                return None

            # Normalize http -> https
            if v.startswith('http://'):
                v = v.replace('http://', 'https://', 1)

            # If it's already under /media/, keep it
            if v.startswith('/media/'):
                return v

            # If it's a relative media path like media/thumbnails/xxx.jpg
            if v.startswith('media/'):
                return f'/{v}'

            # ImageField sometimes yields /thumbnails/<file> or just filename stored
            if v.startswith('thumbnails/') or v.startswith('thumbnail/'):
                if v.startswith('thumbnail/'):
                    v = v.replace('thumbnail/', 'thumbnails/', 1)
                return f'/media/{v}'

            # Filename-only
            if '/' not in v and '.' in v:
                return f'/media/thumbnails/{v}'

            # Remote URL
            if v.startswith('https://') or v.startswith('http://'):
                return v

            return None

        # 1) Local uploaded poster (ImageField)
        if self.thumbnail:
            try:
                candidate = normalize_url(self.thumbnail.url)
                if candidate:
                    return candidate
            except Exception:
                pass

            try:
                name = getattr(self.thumbnail, 'name', '') or ''
                candidate = normalize_url(name)
                if candidate:
                    return candidate
            except Exception:
                pass

        # 2) YouTube thumbnail when video_url is a YouTube link
        video_id = self.youtube_video_id
        if video_id:
            yt_url = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
            candidate = normalize_url(yt_url)
            if candidate:
                return candidate

        # 3) Placeholder image fallback when no local or YouTube poster available
        return self.fallback_poster_url

    @property
    def fallback_poster_url(self):
        """Return a deterministic local fallback poster image."""
        return f'/poster/{self.id}/fallback.svg'


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
