# CineWave - Netflix-Style Streaming Platform

A full-featured streaming platform built with Django, featuring movie browsing, watchlist management, video streaming, and progress tracking.

![CineWave](https://via.placeholder.com/800x400/141414/e50914?text=CineWave)

## Features

- 🎬 Netflix-style movie browsing with genre-based categories
- 📺 Video streaming (YouTube embed + direct URL support)
- 📚 Personal watchlist management
- ⏱️ Watch progress tracking with auto-save and resume
- 🔔 Genre-based recommendations
- 👤 User authentication (registration, login, logout)
- 📱 Responsive design (mobile, tablet, desktop)

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (easily switchable to PostgreSQL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **External APIs**: TMDB, OMDB

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Clone the project**
   ```bash
   git clone <your-repo-url>
   cd cinewave
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional - works without for testing)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys from https://www.themoviedb.org and http://www.omdbapi.com
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Seed sample movies**
   ```bash
   python manage.py seed_movies
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Open browser**
   - Website: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Project Structure

```
cinewave/
├── manage.py              # Django management
├── cinewave/            # Project settings
│   ├── settings.py      # Development settings
│   └── settings_production.py  # Production settings
├── movies/             # Main app
│   ├── models.py      # Database models
│   ├── views.py     # View functions
│   ├── urls.py      # URL routing
│   └── ...
├── templates/          # HTML templates
├── static/           # CSS, JS, images
└── media/          # User uploads
```

## Deployment

### Heroku

1. **Install Heroku CLI** and login
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
   heroku config:set ALLOWED_HOSTS=yourapp.herokuapp.com
   heroku config:set TMDB_API_KEY=your_key
   heroku config:set OMDB_API_KEY=your_key
   ```

4. **Push to Heroku**
   ```bash
   git push heroku main
   ```

5. **Run migrations**
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py seed_movies
   ```

### Railway

1. **Connect GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy**

### VPS (DigitalOcean, Linode, etc.)

1. **Clone and setup**
   ```bash
   git clone <your-repo>
   cd cinewave
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Use production settings**
   ```bash
   export DJANGO_SETTINGS_MODULE=cinewave.settings_production
   export DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn cinewave.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Setup Nginx** (recommended for SSL)

## Environment Variables

| Variable | Description | Required |
|----------|------------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | Yes (production) |
| `ALLOWED_HOSTS` | Comma-separated domains | Yes (production) |
| `TMDB_API_KEY` | TMDB API key | No |
| `OMDB_API_KEY` | OMDB API key | No |

## API Keys

- **TMDB**: https://www.themoviedb.org/settings/api
- **OMDB**: http://www.omdbapi.com/apikey.aspx

## Testing the Application

1. **Homepage**: Should display hero banner and movie rows
2. **Movie detail**: Click any movie to see details
3. **Video player**: Click play to watch (YouTube or direct)
4. **Registration**: Create a new account
5. **Watchlist**: Add movies to your list
6. **Progress**: Close and reopen video to test resume

## Troubleshooting

### Database locked error
- Close any database connections (DB Browser, etc.)

### Static files not loading
- Run: `python manage.py collectstatic`
- Check STATIC_ROOT in settings

### Video not playing
- Check video URL format
- For YouTube: ensure URL includes video ID

### API errors
- Verify API keys in .env
- Check TMDB/OMDB service status

## License

MIT License

## Credits

- Sample videos from Blender Foundation, Pixabay
- Design inspired by Netflix
- Built with Django
