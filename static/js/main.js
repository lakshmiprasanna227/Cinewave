/**
 * CineWave - Main JavaScript
 * Core utilities and functionality
 * ==============================
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('CineWave loaded successfully');
    initNavScroll();
    initTooltips();
});

function initNavScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    window.addEventListener('scroll', function() {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
}

function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.getAttribute('data-tooltip'));
        });
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(element, text) {
    let tooltip = document.querySelector('.custom-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        Object.assign(tooltip.style, {
            position: 'fixed', background: '#141414', color: '#fff', padding: '8px 12px',
            borderRadius: '4px', fontSize: '12px', zIndex: 9999, pointerEvents: 'none',
            opacity: 0, transition: 'opacity 0.2s'
        });
        document.body.appendChild(tooltip);
    }
    tooltip.textContent = text;
    const rect = element.getBoundingClientRect();
    tooltip.style.left = (rect.left + rect.width / 2) + 'px';
    tooltip.style.top = (rect.top - 40) + 'px';
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.opacity = '1';
}

function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) tooltip.style.opacity = '0';
}

function toggleSearch() {
    const dropdown = document.getElementById('searchDropdown');
    if (dropdown) dropdown.classList.toggle('active');
}

let searchTimeout;
function handleSearch(event) {
    const query = event.target.value.trim();
    if (query.length < 2) {
        clearSearchResults();
        return;
    }
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => performSearch(query), 300);
}

async function performSearch(query) {
    const container = document.getElementById('searchResults');
    if (!container) return;
    try {
        const response = await fetch(`/api/movies/?search=${encodeURIComponent(query)}`);
        const data = await response.json();
        displaySearchResults(data.movies || [], container);
    } catch (error) {
        console.error('Search error:', error);
    }
}

function displaySearchResults(movies, container) {
    if (!container) return;
    container.innerHTML = '';
    if (movies.length === 0) {
        container.innerHTML = '<p style="padding:16px;color:#808080">No results found</p>';
        return;
    }
    movies.slice(0, 8).forEach(movie => {
        const item = document.createElement('a');
        item.href = `/movie/${movie.id}/`;
        item.style.cssText = 'display:flex;align-items:center;gap:12px;padding:8px 16px;color:#fff;transition:background 0.2s';
        item.innerHTML = movie.thumbnail 
            ? `<img src="${movie.thumbnail}" style="width:40px;height:60px;object-fit:cover;border-radius:4px"><div><div style="font-weight:600">${movie.title}</div><div style="font-size:12px;color:#808080">${movie.genre} • ${movie.year}</div></div>`
            : `<div style="width:40px;height:60px;background:#0b0b0b;border-radius:4px"></div><div><div style="font-weight:600">${movie.title}</div><div style="font-size:12px;color:#808080">${movie.genre} • ${movie.year}</div></div>`;
        item.addEventListener('mouseenter', () => item.style.background = 'rgba(255,255,255,0.1)');
        item.addEventListener('mouseleave', () => item.style.background = 'transparent');
        container.appendChild(item);
    });
}

function clearSearchResults() {
    const container = document.getElementById('searchResults');
    if (container) container.innerHTML = '';
}

function closeSearch() {
    const dropdown = document.getElementById('searchDropdown');
    if (dropdown) dropdown.classList.remove('active');
}

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

function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return h > 0 ? `${h}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}` : `${m}:${s.toString().padStart(2,'0')}`;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

// Close dropdowns on outside click
document.addEventListener('click', function(event) {
    const search = document.querySelector('.search-container');
    const dropdown = document.getElementById('searchDropdown');
    if (search && dropdown && !search.contains(event.target)) dropdown.classList.remove('active');
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeSearch();
        document.querySelectorAll('.modal.active').forEach(m => m.classList.remove('active'));
    }
});

window.CineWave = { toggleSearch, handleSearch, showToast, formatTime, formatDate };
