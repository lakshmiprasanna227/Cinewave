/**
 * CineWave - Watchlist Page JavaScript
 * Dynamic watchlist management with React-like patterns
 * ==============================
 */

// Watchlist Controller Class
class WatchlistController {
    constructor() {
        this.container = document.getElementById('watchlistContent');
        this.emptyState = document.getElementById('emptyState');
        this.modal = document.getElementById('removeModal');
        this.confirmBtn = document.getElementById('confirmRemoveBtn');
        this.movies = [];
        this.init();
    }

    init() {
        this.loadWatchlist();
        this.setupEventListeners();
    }

    async loadWatchlist() {
        try {
            const response = await fetch('/api/watchlist/');
            const data = await response.json();
            this.movies = data.watchlist || [];
            this.render();
        } catch (error) {
            console.error('Failed to load watchlist:', error);
            this.showError();
        }
    }

    render() {
        if (!this.container) return;
        
        if (this.movies.length === 0) {
            this.showEmptyState();
            return;
        }

        this.hideEmptyState();
        this.container.innerHTML = '<div class="watchlist-grid" id="watchlistGrid"></div>';
        
        const grid = document.getElementById('watchlistGrid');
        
        this.movies.forEach(item => {
            const card = this.createWatchlistCard(item);
            grid.appendChild(card);
        });
    }

    createWatchlistCard(item) {
        const card = document.createElement('div');
        card.className = 'watchlist-card';
        card.dataset.movieId = item.movie_id;

        const imgHtml = item.thumbnail 
            ? `<img src="${item.thumbnail}" alt="${item.title}">`
            : '<div class="no-thumbnail"><i class="fas fa-film"></i></div>';

        card.innerHTML = `
            <a href="/movie/${item.movie_id}/">${imgHtml}</a>
            <div class="watchlist-info">
                <h3>${item.title}</h3>
                <div class="watchlist-meta">
                    <span>${item.year}</span>
                    <span><i class="fas fa-star"></i> ${item.rating}</span>
                </div>
                <div class="watchlist-actions">
                    <button class="btn-play-watchlist" onclick="playFromWatchlist(${item.movie_id})">
                        <i class="fas fa-play"></i> Play
                    </button>
                    <button class="btn-remove" onclick="showRemoveModal(${item.movie_id})">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
            </div>
        `;

        return card;
    }

    showEmptyState() {
        if (this.container) this.container.style.display = 'none';
        if (this.emptyState) this.emptyState.style.display = 'block';
    }

    hideEmptyState() {
        if (this.container) this.container.style.display = 'block';
        if (this.emptyState) this.emptyState.style.display = 'none';
    }

    showError() {
        if (this.container) {
            this.container.innerHTML = `
                <div class="error-state" style="text-align:center;padding:48px;color:#e50914">
                    <i class="fas fa-exclamation-triangle" style="font-size:48px;margin-bottom:16px"></i>
                    <p>Failed to load watchlist</p>
                </div>
            `;
        }
    }

    setupEventListeners() {
        if (this.confirmBtn) {
            this.confirmBtn.addEventListener('click', () => this.confirmRemove());
        }
    }

    async removeMovie(movieId) {
        try {
            const response = await fetch(`/api/watchlist/${movieId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                this.movies = this.movies.filter(m => m.movie_id !== movieId);
                this.render();
                showToast(data.message, 'success');
            } else {
                showToast(data.error || 'Failed to remove', 'error');
            }
        } catch (error) {
            console.error('Remove error:', error);
            showToast('Failed to remove movie', 'error');
        }
    }

    confirmRemove() {
        const movieId = parseInt(this.confirmBtn.dataset.movieId);
        if (movieId) {
            this.removeMovie(movieId);
        }
        this.closeModal();
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                const [key, value] = cookie.trim().split('=');
                if (key === name) cookieValue = value;
            });
        }
        return cookieValue;
    }
}

// Global functions for template onclick handlers
let watchlistController;

function initWatchlist() {
    watchlistController = new WatchlistController();
}

function showRemoveModal(movieId) {
    const modal = document.getElementById('removeModal');
    const confirmBtn = document.getElementById('confirmRemoveBtn');
    
    if (modal && confirmBtn) {
        confirmBtn.dataset.movieId = movieId;
        modal.classList.add('active');
    }
}

function closeRemoveModal() {
    const modal = document.getElementById('removeModal');
    if (modal) modal.classList.remove('active');
}

function playFromWatchlist(movieId) {
    window.location.href = `/watch/${movieId}/`;
}

// Toast notification
function showToast(message, type = 'info') {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        Object.assign(toast.style, {
            position: 'fixed', bottom: '30px', left: '50%', transform: 'translateX(-50%)',
            padding: '12px 24px', borderRadius: '4px', zIndex: 9999, opacity: 0,
            transition: 'opacity 0.3s', fontWeight: 500
        });
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    const colors = { success: '#46d369', error: '#e50914', info: '#141414' };
    toast.style.background = colors[type] || colors.info;
    toast.style.color = type === 'success' ? '#0b0b0b' : '#fff';
    toast.style.opacity = '1';
    setTimeout(() => toast.style.opacity = '0', 3000);
}

// Export
document.addEventListener('DOMContentLoaded', initWatchlist);

window.WatchlistController = WatchlistController;
window.initWatchlist = initWatchlist;
window.showRemoveModal = showRemoveModal;
window.closeRemoveModal = closeRemoveModal;
window.playFromWatchlist = playFromWatchlist;
