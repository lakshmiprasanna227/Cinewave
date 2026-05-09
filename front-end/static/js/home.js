/**
 * CineWave - Homepage JavaScript
 * Movie rows, scrolling, and dynamic content
 * ==============================
 * This file must be safe to load multiple times.
 */
(function cinewaveHomeJsIIFE() {
    if (window.__CINEWAVE_HOME_JS_LOADED__) {
        return;
    }
    window.__CINEWAVE_HOME_JS_LOADED__ = true;

    // API endpoints
    const API = {
        movies: '/api/movies/',
        recommendations: '/api/recommendations/',
        watchlist: '/api/watchlist/'
    };

    function showLoading(elementId) {
        const el = typeof elementId === 'string' ? document.getElementById(elementId) : elementId;
        if (el) {
            el.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
        }
    }

    window.MovieRow = window.MovieRow || class MovieRow {
        constructor(containerId, options = {}) {
            this.container = document.getElementById(containerId);
            this.title = options.title || '';
            this.genre = options.genre || null;
            this.apiEndpoint = options.apiEndpoint || API.movies;
            this.scrollAmount = options.scrollAmount || 200;
        }

        async load() {
            if (!this.container) return;

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

        render(movies) {
            if (!this.container) return;

            this.container.innerHTML = '';

            if (!movies || movies.length === 0) {
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

            const imgSrc = (movie.thumbnail && movie.thumbnail !== 'N/A') ? movie.thumbnail : '';
            const fallbackSrc = `/poster/${movieId}/fallback.svg`;

            const imgHtml = imgSrc
                ? `<img src="${imgSrc}" alt="${movie.title}" onerror="this.onerror=null;this.src='${fallbackSrc}';">`
                : `<img src="${fallbackSrc}" alt="${movie.title}" onerror="this.onerror=null;">`;

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
    };

    function scrollRow(rowId, direction = 'left') {
        const container = document.getElementById(`${rowId}-row`) ||
            document.getElementById(`${rowId}-content`);

        if (!container) return;

        const scrollAmount = direction === 'left' ? -400 : 400;
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }

    async function initHomePage() {
        // Load recommendations
        const recommendationsContainer = document.getElementById('recommendations-content');
        if (recommendationsContainer) {
            const recRow = new window.MovieRow('recommendations-content', {
                title: 'Recommended',
                apiEndpoint: API.recommendations
            });
            recRow.load();
        }

        // Load watchlist if logged in
        const watchlistContainer = document.getElementById('my-list-content');
        if (watchlistContainer) {
            const watchlistRow = new window.MovieRow('my-list-content', {
                title: 'My List',
                apiEndpoint: API.watchlist
            });
            watchlistRow.load();
        }
    }

    window.scrollRow = window.scrollRow || scrollRow;
    window.initHomePage = window.initHomePage || initHomePage;

    document.addEventListener('DOMContentLoaded', window.initHomePage);
})();

