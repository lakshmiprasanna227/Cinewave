/**
 * CineWave - Homepage JavaScript
 * Movie rows, scrolling, and dynamic content
 * ==============================
 */

// API endpoints
const API = {
    movies: '/api/movies/',
    recommendations: '/api/recommendations/',
    watchlist: '/api/watchlist/'
};

// Movie Row Component
class MovieRow {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.title = options.title || '';
        this.genre = options.genre || null;
        this.apiEndpoint = options.apiEndpoint || API.movies;
        this.scrollAmount = options.scrollAmount || 200;
    }

    async load() {
        if (this.container) {
            showLoading(this.container);
            try {
                const url = this.genre 
                    ? `${this.apiEndpoint}?genre=${this.genre}`
                    : this.apiEndpoint;
                const response = await fetch(url);
                const data = await response.json();
                const movies = data.movies || data.recommendations || data.watchlist || [];
                this.render(movies);
            } catch (error) {
                console.error('Failed to load movies:', error);
                this.renderError();
            }
        }
    }

    render(movies) {
        if (!this.container) return;
        this.container.innerHTML = '';
        
        if (movies.length === 0) {
            this.container.innerHTML = '<p style="padding:24px;color:#808080">No movies found</p>';
            return;
        }

        movies.forEach(movie => {
            const card = this.createMovieCard(movie);
            this.container.appendChild(card);
        });
    }

    createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        const movieId = movie.movie_id || movie.id;
        card.dataset.id = movieId;
        
        const imgSrc = movie.thumbnail || '';
        const imgHtml = imgSrc 
            ? `<img src="${imgSrc}" alt="${movie.title}">`
            : '<div class="no-thumbnail"><i class="fas fa-film"></i></div>';

        card.innerHTML = `
            <a href="/movie/${movieId}/">
                ${imgHtml}
                <div class="card-overlay">
                    <div class="card-info">
                        <h3>${movie.title}</h3>
                        <div class="card-meta">
                            <span>${movie.year}</span>
                            <span><i class="fas fa-star"></i> ${movie.rating}</span>
                        </div>
                    </div>
                </div>
            </a>
        `;

        // Add hover effects
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'scale(1.05)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'scale(1)';
        });

        return card;
    }

    renderError() {
        if (this.container) {
            this.container.innerHTML = '<p style="padding:24px;color:#e50914">Failed to load movies</p>';
        }
    }
}

// Scroll functionality
function scrollRow(rowId, direction = 'left') {
    const container = document.getElementById(`${rowId}-row`) || 
                  document.getElementById(`${rowId}-content`);
    if (!container) return;

    const scrollAmount = direction === 'left' ? -400 : 400;
    container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
}

// Initialize rows
async function initHomePage() {
    // Load recommendations if logged in
    const recommendationsContainer = document.getElementById('recommendations-content');
    if (recommendationsContainer) {
        const recRow = new MovieRow('recommendations-content', {
            title: 'Recommended',
            apiEndpoint: API.recommendations
        });
        recRow.load();
    }

    // Load watchlist if logged in
    const watchlistContainer = document.getElementById('my-list-content');
    if (watchlistContainer) {
        const watchlistRow = new MovieRow('my-list-content', {
            title: 'My List',
            apiEndpoint: API.watchlist
        });
        watchlistRow.load();
    }
}

// Movie Card Factory
function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.dataset.id = movie.id;

    const img = movie.thumbnail 
        ? `<img src="${movie.thumbnail}" alt="${movie.title}">`
        : '<div class="no-thumbnail"><i class="fas fa-film"></i></div>';

    card.innerHTML = `
        <a href="/movie/${movie.id}/">
            ${img}
            <div class="card-overlay">
                <div class="card-info">
                    <h3>${movie.title}</h3>
                    <div class="card-meta">
                        <span>${movie.year}</span>
                        <span><i class="fas fa-star"></i> ${movie.rating}</span>
                    </div>
                </div>
            </div>
        </a>
    `;

    return card;
}

// Search Modal
function openSearchModal() {
    const modal = document.getElementById('searchModal');
    if (modal) modal.classList.add('active');
}

function closeSearchModal() {
    const modal = document.getElementById('searchModal');
    if (modal) modal.classList.remove('active');
}

// Loading state
function showLoading(elementId) {
    const el = typeof elementId === 'string' ? document.getElementById(elementId) : elementId;
    if (el) {
        el.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    }
}

document.addEventListener('DOMContentLoaded', initHomePage);

// Export
window.MovieRow = MovieRow;
window.scrollRow = scrollRow;
window.initHomePage = initHomePage;
window.createMovieCard = createMovieCard;
window.openSearchModal = openSearchModal;
window.closeSearchModal = closeSearchModal;
