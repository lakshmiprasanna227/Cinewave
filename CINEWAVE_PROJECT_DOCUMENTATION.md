# CineWave - Complete Project Documentation

## Executive Summary

CineWave is a Netflix-inspired streaming web application built with **Django** (Python web framework). It provides a platform for users to browse, stream movies, manage personal watchlists, and track viewing progress. The application features a modern dark-themed UI similar to major streaming platforms.

---

## 1. Technology Stack

### Backend
- **Framework**: Django 4.2+
- **Language**: Python 3.x
- **Database**: SQLite (db.sqlite3)
- **Server**: Django's built-in development server (WSGI)

### Frontend
- **HTML5**: Template-based rendering with Django Template Engine
- **CSS3**: Custom Netflix-inspired stylesheet
- **JavaScript**: Vanilla JavaScript (ES6+)
- **External Libraries**:
  - Font Awesome 6.4.0 (icons)
  - Google Fonts - Roboto (typography)
  - Optional: React (for dynamic components)

### External APIs
- **TMDB (TheMovieDB)**: Primary movie metadata source
  - API Base URL: `https://api.themoviedb.org/3`
  - Image Base URL: `https://image.tmdb.org/t/p/`
- **OMDB (Open Movie Database)**: Secondary movie metadata source
  - Used as fallback

---

## 2. Project Structure

```
cinewave/
├── manage.py                 # Django management script
├── db.sqlite3              # SQLite database file
├── cinewave/               # Django project settings
│   ├── __init__.py
│   ├── settings.py         # Main configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py            # WSGI entry point
├── movies/                 # Main application
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── forms.py           # Form classes
│   ├── models.py          # Database models
│   ├── urls.py             # URL routing
│   ├── views.py            # View functions
│   ├── tmdb.py             # TMDB API integration
│   ├── omdb.py             # OMDB API integration
│   ├── migrations/         # Database migrations
│   │   └── 0001_initial.py
│   └── management/
│       └── commands/
│           └── seed_movies.py  # Seed database command
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── home.html          # Homepage
│   ├── movie.html        # Movie detail page
│   ├── video.html        # Video player page
│   ├── watchlist.html    # User watchlist
│   ├── login.html        # Login page
│   └── register.html    # Registration page
├── static/                # Static files
│   ├── css/
│   │   ├── style.css    # Main stylesheet
│   │   ├── home.css     # Homepage styles
│   │   ├── video.css    # Video player styles
│   │   └── ... (other CSS files)
│   └── js/
│       ├── main.js      # Main JavaScript
│       ├── home.js     # Homepage JavaScript
│       └── video.js    # Video player JavaScript
└── media/
    └── thumbnails/      # Movie poster images
```

---

## 3. Database Architecture

### Models

#### Movie Model
Represents a film in the database.

```
Attributes:
- title: CharField(max_length=200) - Movie name
- description: TextField - Synopsis/summary
- genre: CharField - Category (action, comedy, drama, horror, sci-fi, romance, thriller, animation, documentary)
- thumbnail: ImageField - Poster image (stored in media/thumbnails/)
- video_url: URLField - URL to video (YouTube or external)
- video_file: FileField - Local video file upload
- rating: DecimalField - User rating (0-10 scale)
- year: IntegerField - Release year
- duration: IntegerField - Duration in minutes
- created_at: DateTimeField - When added to database
- updated_at: DateTimeField - Last modification
- is_featured: BooleanField - Show in hero banner

Properties:
- youtube_video_id: Extracts YouTube video ID from URL
- poster_url: Returns thumbnail URL or YouTube thumbnail fallback
```

#### WatchList Model
Stores user's favorite movies.

```
Attributes:
- user: ForeignKey(User) - Owner of the watchlist
- movie: ForeignKey(Movie) - Movie in watchlist
- added_at: DateTimeField - When added

Constraints:
- unique_together: ['user', 'movie'] - No duplicates
```

#### WatchHistory Model
Tracks user's viewing progress.

```
Attributes:
- user: ForeignKey(User) - Viewer
- movie: ForeignKey(Movie) - Movie watched
- watched_at: DateTimeField - Last watch time
- progress: IntegerField - Progress in seconds
- completed: BooleanField - Marked as completed

Constraints:
- unique_together: ['user', 'movie'] - One record per user-movie
```

---

## 4. Core Features

### 4.1 User Authentication
- **Registration**: Custom form with username, email, password
- **Login**: Django AuthenticationForm
- **Session-based auth**: Uses Django's built-in session authentication
- **Login redirects**: To home page after login

### 4.2 Movie Browsing
- **Homepage**: Netflix-style interface with:
  - Hero banner (featured movie)
  - Horizontal scrolling movie rows by genre
  - Trending movies section
  - New & Popular section
- **Genre filtering**: Action, Comedy, Drama, Sci-Fi, Horror, Animation
- **Movie cards**: Display thumbnail, title, year, rating

### 4.3 Video Streaming
Two streaming methods supported:

1. **YouTube Embed**: 
   - Converts YouTube URLs to embed format
   - Supports: youtube.com/watch, youtu.be, youtube.com/embed
   
2. **Direct Video URL**:
   - Proxies external videos through Django server
   - Supports Range requests for seeking
   - Bypasses CORS restrictions

### 4.4 Watchlist Management
- **Add to watchlist**: POST to `/api/watchlist/add/`
- **Remove from watchlist**: DELETE to `/api/watchlist/<movie_id>/`
- **View watchlist**: GET to `/api/watchlist/`

### 4.5 Watch Progress Tracking
- **Auto-save**: Saves every 5 seconds during playback
- **Resume**: Restores last position when reopening
- **Mark as completed**: Automatically marks when finished

### 4.6 Recommendations
Based on:
1. **User's viewing history genres**
2. **Top-rated movies fallback**

---

## 5. URL Routes

### Template Routes
| Path | View | Description |
|------|------|-------------|
| `/` | home | Homepage |
| `/movie/<id>/` | movie_detail | Movie details |
| `/watch/<id>/` | watch_video | Video player |
| `/stream/<id>/` | stream_video | Video stream endpoint |
| `/login/` | login_view | Login page |
| `/register/` | register_view | Registration page |
| `/logout/` | logout_view | Logout |
| `/watchlist/` | watchlist_page | User watchlist |

### API Routes
| Path | Method | Description |
|------|--------|-------------|
| `/api/movies/` | GET | List all movies |
| `/api/movies/<id>/` | GET | Movie details |
| `/api/watchlist/add/` | POST | Add to watchlist |
| `/api/watchlist/<id>/` | DELETE | Remove from watchlist |
| `/api/watchlist/` | GET | Get watchlist |
| `/api/save-progress/` | POST | Save watch progress |
| `/api/recommendations/` | GET | Get recommendations |

---

## 6. Configuration Settings

### Key Settings (settings.py)

```python
# Security
SECRET_KEY = 'django-insecure-cinewave-secret-key-change-in-production-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Django REST Framework
    'movies',          # Local app
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# External APIs
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
OMDB_API_KEY = os.environ.get('OMDB_API_KEY', '')
```

---

## 7. External API Integration

### TMDB API (movies/tmdb.py)

```python
# Functions:
search_movie(title, year=None)  # Search movie by title
get_poster_url(poster_path, size='w500')  # Get poster image URL
download_image(url)  # Download image binary data
```

### OMDB API (movies/omdb.py)

```python
# Functions:
search_movie(title, year=None)  # Search movie by title
get_poster_url(poster_url)  # Get poster URL
```

---

## 8. Data Seeding

### seed_movies Command

The `python manage.py seed_movies` command populates the database with sample movies:

**Process:**
1. Clears existing movies
2. For each sample video:
   - Queries TMDB for metadata (title, description, poster, rating)
   - Falls back to OMDB if TMDB fails
   - Downloads poster images
   - Creates fallback thumbnails if download fails
3. Marks first movie as featured

**Sample Videos Include:**
- Big Buck Bunny
- Elephants Dream
- Sintel
- Tears of Steel
- And 20+ more...

**Video Sources:**
- Blender Foundation (Big Buck Bunny, Sintel)
- Pixabay CDN
- Archive.org

---

## 9. Frontend Architecture

### Base Template (base.html)
- Navbar with logo, navigation links, search, user menu
- Footer with links and copyright
- CSS and JS includes

### CSS System (style.css)
- **CSS Variables**: Colors, typography, spacing, shadows
- **Netflix-inspired design**: Dark theme (#141414 background)
- **Responsive**: Mobile, tablet, desktop breakpoints

### JavaScript Modules

#### home.js
- MovieRow class for dynamic movie loading
- Scroll functionality for horizontal rows
- Search modal handling

#### video.js
- VideoPlayer class:
  - Play/pause controls
  - Progress bar with seeking
  - Volume control
  - Fullscreen, Picture-in-Picture
  - Keyboard shortcuts (Space, F, M, arrows)
  - Auto-save progress every 5 seconds
  - Resume from last position

---

## 10. Key Design Decisions

### Why This Stack?
- **Django**: Robust, built-in admin, ORM, security
- **SQLite**: Simple setup, no configuration needed
- **Vanilla JS**: No build step, fast loading
- **CSS Variables**: Easy theming and updates

### Video Handling
- **YouTube embed**: Reliable, no bandwidth costs
- **Direct proxy**: Bypasses CORS for external videos

### Watch Progress
- **LocalStorage fallback**: Works without login
- **Database sync**: Persists when logged in

### Recommendations
- **Genre-based**: Simple, effective
- **Fallback to top-rated**: Always provides results

---

## 11. Running the Project

### Setup
```bash
# Install dependencies
pip install django requests pillow

# Set API keys (optional)
export TMDB_API_KEY=your_key
export OMDB_API_KEY=your_key

# Run migrations
python manage.py migrate

# Seed database
python manage.py seed_movies

# Start server
python manage.py runserver
```

### Access
- **Website**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

---

## 12. Potential Improvements

### Implemented but Noted
- [ ] Production-ready database (PostgreSQL recommended)
- [ ] Production server (Gunicorn, Nginx)
- [ ] HTTPS configuration
- [ ] Video transcoding for quality options
- [ ] User profiles and Avatar upload
- [ ] Movie ratings by users
- [ ] Comments and reviews
- [ ] Social sharing features
- [ ] Payment integration for premium features
- [ ] Email notifications

### Security Notes
- DEBUG=True in development
- Secret key should be changed in production
- Consider CSRF protection for production
- Implement rate limiting for API endpoints

---

## 13. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Browser   │  │    CSS      │  │  JavaScript │      │
│  │   (HTML)    │  │   (Style)   │  │   (Logic)   │      │
│  └──────┬──────┘  └─────────────┘  └──────┬──────┘      │
│         │                                    │               │
└─────────┼────────────────────────────────────┼──────────────┘
          │           HTTP Requests             │
          │                                    │
┌─────────┼──────────��─────────────────────────┼──────────────┐
│         ▼                                    ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  DJANGO SERVER                       │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────────┐  │   │
│  │  │  Views   │  │   Forms   │  │  URL Router   │  │   │
│  │  └────┬────┘  └───────────┘  └──────┬──────┘  │   │
│  │       │                              │           │   │
│  │  ┌────▼──────────────────────────────▼────┐    │   │
│  │  │               MODELS                    │    │   │
│  │  │  Movie  │  WatchList  │  WatchHistory │    │   │
│  │  └────────────────────────────────────────┘    │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                  │
│              ┌──────▼──────┐                          │
│              │  SQLite DB  │                          │
│              └─────────────┘                          │
└──────────────────┬────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌─────────┐ ┌────────┐ ┌─────────┐
   │  TMDB   │ │  OMDB  │ │  TMDB   │
   │   API   │ │   API  │ │  Images │
   └─────────┘ └────────┘ └─────────┘
```

---

## 14. Testing the Application

### Quick Test Scenarios
1. **Homepage loads** - Hero banner and movie rows visible
2. **Movie browsing** - Scroll through genre categories
3. **Movie detail** - View movie information
4. **Video playback** - Play a movie (YouTube or direct)
5. **User registration** - Create new account
6. **Add to watchlist** - Add movie to personal list
7. **Watch progress** - Close and reopen video, resume works
8. **Search** - Find movies by title

---

## Conclusion

CineWave is a complete, functional streaming platform demonstrating:
- Full-stack web development with Django
- Netflix-inspired UI/UX design
- Database modeling and relationships
- External API integration
- Video streaming handling
- User authentication and session management

The application is production-ready with proper architecture and can be scaled by switching to PostgreSQL and implementing additional features as needed.

---

*Documentation generated for project review*
*Date: Project Review Session*
