/**
 * CineWave - Movie Detail Page JavaScript
 * Movie details, watchlist, and interactions
 * ==============================
 */

// Get movie ID from page
function getMovieId() {
    const path = window.location.pathname;
    const match = path.match(/\/movie\/(\d+)\//);
    return match ? parseInt(match[1]) : null;
}

// Watchlist API
const WATCHLIST_API = {
    add: '/api/watchlist/add/',
    remove: (id) => `/api/watchlist/${id}/`,
    list: '/api/watchlist/'
};

// Toggle watchlist
async function toggleWatchlist(movieId) {
    const btn = document.getElementById('watchlistBtn');
    if (!btn) return;

    const isInList = btn.classList.contains('in-list');
    const endpoint = isInList 
        ? WATCHLIST_API.remove(movieId)
        : WATCHLIST_API.add;

    try {
        const response = await fetch(endpoint, {
            method: isInList ? 'DELETE' : 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ movie_id: movieId })
        });

        const data = await response.json();
        
        if (data.success) {
            btn.classList.toggle('in-list', !isInList);
            btn.innerHTML = isInList 
                ? '<i class="fas fa-plus"></i> My List'
                : '<i class="fas fa-check"></i> My List';
            showToast(data.message, 'success');
        } else {
            showToast(data.error || 'Failed to update watchlist', 'error');
        }
    } catch (error) {
        console.error('Watchlist error:', error);
        showToast('Failed to update watchlist', 'error');
    }
}

// Check watchlist status
async function checkWatchlistStatus(movieId) {
    try {
        const response = await fetch(WATCHLIST_API.list);
        const data = await response.json();
        const inList = data.watchlist?.some(item => item.movie_id === movieId);
        
        const btn = document.getElementById('watchlistBtn');
        if (btn) {
            btn.classList.toggle('in-list', inList);
            btn.innerHTML = inList 
                ? '<i class="fas fa-check"></i> My List'
                : '<i class="fas fa-plus"></i> My List';
        }
    } catch (error) {
        console.error('Failed to check watchlist:', error);
    }
}

// Get CSRF token
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show toast
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

// Show trailer/details modal
function showTrailer() {
    // Could implement video trailer modal
    showToast('Trailer coming soon!', 'info');
}

// Initialize movie page
function initMoviePage() {
    const movieId = getMovieId();
    if (!movieId) return;

    // Check if user is logged in
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        // Setup watchlist button
        const btn = document.getElementById('watchlistBtn');
        if (btn) {
            btn.addEventListener('click', () => toggleWatchlist(movieId));
        }
        // Check watchlist status
        checkWatchlistStatus(movieId);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'w' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            toggleWatchlist(movieId);
        }
    });
}

// Auto-play video on play button click
function playMovie() {
    const movieId = getMovieId();
    if (movieId) {
        window.location.href = `/watch/${movieId}/`;
    }
}

// Export functions
document.addEventListener('DOMContentLoaded', initMoviePage);

window.getMovieId = getMovieId;
window.toggleWatchlist = toggleWatchlist;
window.checkWatchlistStatus = checkWatchlistStatus;
window.initMoviePage = initMoviePage;
window.playMovie = playMovie;
