# CineWave - Complete Setup & Run Guide

## Project Status: ✅ FIXED & READY TO RUN

All issues have been resolved:
- ✅ Missing posters now use YouTube thumbnails or placeholder images  
- ✅ Video player implemented with proper streaming
- ✅ All 16 movies configured with working sample videos
- ✅ Database properly initialized

---

## Quick Start (Windows PowerShell)

### Step 1: Navigate to Project Directory
```powershell
cd c:\Users\rlaks\Desktop\cinewave
```

### Step 2: Check Django Setup
```powershell
python manage.py check
```
Expected output: `System check identified no issues (0 silenced).`

### Step 3: Apply Database Migrations  
```powershell
python manage.py migrate
```
Expected output: `No migrations to apply.`

### Step 4: Start Development Server
```powershell
python manage.py runserver 0.0.0.0:8000
```

Server will start at: `http://localhost:8000`

### Step 5: Access in Browser
- Open: `http://localhost:8000`
- Browse movies with working posters and descriptions
- Click Play to watch sample videos
- Click any movie for details

---

## Features Working

### Homepage
- Netflix-style hero banner with featured movie
- Movie rows organized by genre (Action, Comedy, Drama, etc.)
- Movie cards with YouTube or placeholder thumbnails
- Responsive layout

### Movie Details
- Full movie information (title, year, rating, duration, genre)
- Director and cast information
- Similar movies recommendations
- Play and More Info buttons

### Video Player
- HTML5 video player with full controls
- Play/Pause, Volume, Seek, Fullscreen
- Custom progress bar with thumbnail scrubbing
- Keyboard shortcuts (Space=Play, F=Fullscreen, M=Mute, Arrows=Skip)
- Video progress tracking and resumption
- Supports YouTube and direct MP4 streams

### Sample Videos
All 16 movies are configured with working sample videos:
- Big Buck Bunny
- Elephant's Dream
- For Bigger Blazes
- For Bigger Escapes
- Sintel

These are public domain/Creative Commons videos from Google Cloud Storage.

---

## Database Content

### Movies Available
- Harom Hara (Romance)
- Beat (Music)
- Mavana Magalu (Romance)
- Jeevnane Natka Samy (Comedy)
- Keralida Simha (Action)
- Suryavamsha (Drama)
- Kotigobba (Thriller)
- Milana (Romance)
- Dharmasya (Yada Yada Hi Dharmasya) (Action)
- Thamas (Drama)
- Tagaru Palya (Kannada)
- Endendigu (Comedy)
- Googly (Romance)
- Lifeu Ishtene (Romance)
- Yuga Purusha (Action)
- Shhh! (Comedy)

---

## Project Structure

```
cinewave/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database (auto-created)
├── requirements.txt         # Python dependencies
│
├── cinewave/                # Django project settings
│   ├── settings.py          # Main Django config
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI application
│
├── movies/                  # Django app
│   ├── models.py            # Movie, WatchList, WatchHistory models
│   ├── views.py             # All view logic
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Django admin config
│   └── forms.py             # User forms
│
├── front-end/               # Frontend files
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base template
│   │   ├── home.html        # Homepage
│   │   ├── movie.html       # Movie detail page
│   │   ├── video.html       # Video player page
│   │   ├── login.html       # Login page
│   │   ├── register.html    # Registration page
│   │   └── ...
│   └── static/              # CSS, JS, Images
│       ├── css/             # Stylesheets
│       └── js/              # JavaScript files
│
└── media/                   # User uploads (auto-created)
```

---

## Configuration Details

### Settings (cinewave/settings.py)
- **DEBUG**: True (for development)
- **DATABASE**: SQLite at `db.sqlite3`
- **MEDIA_URL**: `/media/` - Serves user uploads
- **STATIC_URL**: `/static/` - Serves CSS/JS
- **MEDIA_ROOT**: `media/` folder
- **ALLOWED_HOSTS**: All hosts allowed (*)

### Video Sources
Movies now use working video URLs from Google Cloud Storage:
- All videos are public domain/Creative Commons
- Properly optimized for streaming
- Support range requests for seeking

---

## Troubleshooting

### Issue: "System check identified issues"
**Solution**: Ensure Python 3.8+ and all requirements are installed:
```powershell
pip install -r requirements.txt
```

### Issue: Database errors
**Solution**: Reset database and re-migrate:
```powershell
Remove-Item db.sqlite3
python manage.py migrate
```

### Issue: Static files not loading
**Solution**: Collect static files:
```powershell
python manage.py collectstatic --noinput
```

### Issue: Video won't play
**Solution**: Check browser console for CORS errors. Videos should stream from `/stream/<id>/` endpoint.

### Issue: Movies don't appear
**Solution**: Ensure movies are in database:
```powershell
python manage.py shell -c "from movies.models import Movie; print(f'Total: {Movie.objects.count()}')"
```

---

## Adding New Movies

### Via Django Admin
1. Start server: `python manage.py runserver`
2. Go to: `http://localhost:8000/admin/`
3. Create superuser first (if needed):
   ```powershell
   python manage.py createsuperuser
   ```
4. Add movies through admin interface

### Via Management Command
Create a script to programmatically add movies to the database.

### Via ORM
```python
python manage.py shell
>>> from movies.models import Movie
>>> Movie.objects.create(
...     title="New Movie",
...     description="Description here",
...     genre="action",
...     year=2024,
...     duration=120,
...     rating=7.5,
...     video_url="https://your-video-url.com/video.mp4"
... )
```

---

## Stopping the Server

Press `CTRL + C` in the terminal running the server.

---

## Next Steps

1. **Customize**: Modify templates in `front-end/templates/` for your branding
2. **Add Movies**: Add your own movies with real content
3. **Deploy**: Use Gunicorn + Nginx for production
4. **Database**: Upgrade from SQLite to PostgreSQL for production
5. **Media Storage**: Use AWS S3 or similar for video storage

---

## Requirements Installed

```
Django>=4.2,<5.0
requests>=2.31.0
Pillow>=10.0.0
whitenoise>=6.5.0
djangorestframework>=3.14.0
gunicorn>=21.0.0
```

---

## Support & Help

All features are working. If you encounter any issues:
1. Check server terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify database connection: `python manage.py dbshell`
4. Review Django logs for request errors

---

**Version**: 1.0  
**Last Updated**: 2026-05-08  
**Status**: Production Ready for Development
