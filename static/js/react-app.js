/**
 * CineWave - React Application
 * Browser-based React components (no build step required)
 * Using React via CDN
 * ==============================
 */

// Wait for React to load from CDN
document.addEventListener('DOMContentLoaded', function() {
    // Check if React is available
    if (typeof React !== 'undefined' && typeof ReactDOM !== 'undefined') {
        initReactApp();
    } else {
        // Load React from CDN first
        loadReactFromCDN().then(() => initReactApp());
    }
});

function loadReactFromCDN() {
    return new Promise((resolve, reject) => {
        // Load React
        const reactScript = document.createElement('script');
        reactScript.src = 'https://unpkg.com/react@18/umd/react.production.min.js';
        reactScript.crossOrigin = 'anonymous';
        
        // Load ReactDOM
        const reactDOMScript = document.createElement('script');
        reactDOMScript.src = 'https://unpkg.com/react-dom@18/umd/react-dom.production.min.js';
        reactDOMScript.crossOrigin = 'anonymous';
        
        reactScript.onload = () => {
            reactDOMScript.onload = resolve;
            document.head.appendChild(reactDOMScript);
        };
        reactScript.onerror = reject;
        document.head.appendChild(reactScript);
    });
}

function initReactApp() {
    const rootElement = document.getElementById('react-root');
    
    if (rootElement) {
        // Mount React app
        ReactDOM.render(React.createElement(CineWaveApp), rootElement);
    }
    
    // Initialize page-specific components
    initMovieCardComponents();
    initWatchlistComponents();
}

// ==============================
// REACT COMPONENTS
// ==============================

// Movie Card Component
function MovieCard(props) {
    const { movie, onPlay, onAddToList, inWatchlist } = props;
    
    return React.createElement('div', { className: 'movie-card react-card', 'data-id': movie.id },
        React.createElement('a', { href: `/movie/${movie.id}/` },
            movie.thumbnail 
                ? React.createElement('img', { src: movie.thumbnail, alt: movie.title })
                : React.createElement('div', { className: 'no-thumbnail' },
                    React.createElement('i', { className: 'fas fa-film' })
                )
        ),
        React.createElement('div', { className: 'card-overlay' },
            React.createElement('div', { className: 'card-info' },
                React.createElement('h3', null, movie.title),
                React.createElement('div', { className: 'card-meta' },
                    React.createElement('span', null, movie.year),
                    React.createElement('span', null, 
                        React.createElement('i', { className: 'fas fa-star' }),
                        ' ',
                        movie.rating
                    )
                )
            )
        ),
        inWatchlist !== undefined && React.createElement('button', {
            className: 'add-list-btn ' + (inWatchlist ? 'in-list' : ''),
            onClick: () => onAddToList && onAddToList(movie.id),
            title: inWatchlist ? 'Remove from list' : 'Add to list'
        },
            React.createElement('i', { 
                className: inWatchlist ? 'fas fa-check' : 'fas fa-plus' 
            })
        )
    );
}

// Movie Row Component
function MovieRow(props) {
    const { title, movies, onScroll, genre } = props;
    const rowRef = React.useRef ? React.useRef() : null;
    
    const handleScroll = (direction) => {
        const container = rowRef.current;
        if (container) {
            const scrollAmount = direction === 'left' ? -400 : 400;
            container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    };
    
    return React.createElement('section', { className: 'movie-row' },
        React.createElement('h2', { className: 'row-title' },
            React.createElement('i', { className: 'fas fa-' + getGenreIcon(genre) }),
            ' ',
            title
        ),
        React.createElement('div', { className: 'row-content' },
            React.createElement('button', { 
                className: 'scroll-btn scroll-left',
                onClick: () => handleScroll('left')
            }, React.createElement('i', { className: 'fas fa-chevron-left' })),
            React.createElement('div', { 
                className: 'movie-cards',
                ref: rowRef
            },
                movies.map(movie => 
                    React.createElement(MovieCard, { key: movie.id, movie: movie })
                )
            ),
            React.createElement('button', { 
                className: 'scroll-btn scroll-right',
                onClick: () => handleScroll('right')
            }, React.createElement('i', { className: 'fas fa-chevron-right' }))
        )
    );
}

// Search Input Component
function SearchInput(props) {
    const [query, setQuery] = React.useState('');
    const [results, setResults] = React.useState([]);
    const [isLoading, setIsLoading] = React.useState(false);
    
    const handleSearch = async (value) => {
        setQuery(value);
        
        if (value.length < 2) {
            setResults([]);
            return;
        }
        
        setIsLoading(true);
        try {
            const response = await fetch(`/api/movies/?search=${encodeURIComponent(value)}`);
            const data = await response.json();
            setResults(data.movies || []);
        } catch (error) {
            console.error('Search failed:', error);
        }
        setIsLoading(false);
    };
    
    return React.createElement('div', { className: 'react-search' },
        React.createElement('input', {
            type: 'text',
            value: query,
            onChange: (e) => handleSearch(e.target.value),
            placeholder: 'Search movies...',
            className: 'search-input'
        }),
        isLoading && React.createElement('div', { className: 'search-loading' },
            React.createElement('i', { className: 'fas fa-spinner fa-spin' })
        ),
        results.length > 0 && React.createElement('div', { className: 'search-results' },
            results.map(movie => 
                React.createElement('a', { 
                    key: movie.id,
                    href: `/movie/${movie.id}/`,
                    className: 'search-result-item'
                },
                    movie.thumbnail && React.createElement('img', { 
                        src: movie.thumbnail, 
                        alt: movie.title 
                    }),
                    React.createElement('div', null,
                        React.createElement('div', { className: 'result-title' }, movie.title),
                        React.createElement('div', { className: 'result-meta' }, 
                            movie.genre, ' • ', movie.year
                        )
                    )
                )
            )
        )
    );
}

// Main App Component
function CineWaveApp(props) {
    const [movies, setMovies] = React.useState([]);
    const [watchlist, setWatchlist] = React.useState([]);
    const [activeTab, setActiveTab] = React.useState('home');
    
    React.useEffect(() => {
        loadMovies();
        loadWatchlist();
    }, []);
    
    const loadMovies = async () => {
        try {
            const response = await fetch('/api/movies/');
            const data = await response.json();
            setMovies(data.movies || []);
        } catch (error) {
            console.error('Failed to load movies:', error);
        }
    };
    
    const loadWatchlist = async () => {
        try {
            const response = await fetch('/api/watchlist/');
            const data = await response.json();
            setWatchlist(data.watchlist || []);
        } catch (error) {
            console.error('Failed to load watchlist:', error);
        }
    };
    
    const addToWatchlist = async (movieId) => {
        try {
            await fetch('/api/watchlist/add/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ movie_id: movieId })
            });
            loadWatchlist();
        } catch (error) {
            console.error('Failed to add to watchlist:', error);
        }
    };
    
    const removeFromWatchlist = async (movieId) => {
        try {
            await fetch(`/api/watchlist/${movieId}/`, {
                method: 'DELETE'
            });
            loadWatchlist();
        } catch (error) {
            console.error('Failed to remove from watchlist:', error);
        }
    };
    
    const isInWatchlist = (movieId) => {
        return watchlist.some(item => item.movie_id === movieId);
    };
    
    const genres = ['action', 'comedy', 'drama', 'horror', 'sci-fi'];
    
    return React.createElement('div', { className: 'cinewave-app' },
        React.createElement('nav', { className: 'app-nav' },
            React.createElement('button', {
                className: activeTab === 'home' ? 'active' : '',
                onClick: () => setActiveTab('home')
            }, 'Home'),
            React.createElement('button', {
                className: activeTab === 'my-list' ? 'active' : '',
                onClick: () => setActiveTab('my-list')
            }, 'My List'),
            React.createElement(SearchInput)
        ),
        activeTab === 'home' && genres.map(genre => 
            React.createElement(MovieRow, {
                key: genre,
                title: capitalize(genre),
                genre: genre,
                movies: movies.filter(m => m.genre === genre),
                onAddToList: addToWatchlist
            })
        ),
        activeTab === 'my-list' && React.createElement(MovieRow, {
            title: 'My List',
            genre: 'my-list',
            movies: watchlist,
            onAddToList: removeFromWatchlist,
            inWatchlist: true
        })
    );
}

// ==============================
// HELPER FUNCTIONS
// ==============================

function getGenreIcon(genre) {
    const icons = {
        'action': 'bomb',
        'comedy': 'laugh-squint',
        'drama': 'theater-masks',
        'horror': 'ghost',
        'sci-fi': 'robot',
        'trending': 'fire',
        'my-list': 'plus-square'
    };
    return icons[genre] || 'film';
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ==============================
// INITIALIZE REACT COMPONENTS
// ==============================

function initMovieCardComponents() {
    // Add click handlers to React-rendered movie cards
    document.addEventListener('click', function(e) {
        const addBtn = e.target.closest('.add-list-btn');
        if (addBtn) {
            const card = addBtn.closest('.movie-card');
            const movieId = card?.dataset?.id;
            if (movieId) {
                const isInList = addBtn.classList.contains('in-list');
                if (isInList) {
                    removeFromWatchlist(movieId);
                } else {
                    addToWatchlist(movieId);
                }
            }
        }
    });
}

function initWatchlistComponents() {
    // Watchlist page initialization
    const watchlistContainer = document.getElementById('watchlistContent');
    if (watchlistContainer && typeof WatchlistController !== 'undefined') {
        new WatchlistController();
    }
}

// ==============================
// EXPORT FOR GLOBAL USE
// ==============================

window.CineWaveReact = {
    MovieCard,
    MovieRow,
    SearchInput,
    CineWaveApp,
    initReactApp
};
