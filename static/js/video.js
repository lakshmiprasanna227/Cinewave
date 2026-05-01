/**
 * CineWave - Video Player JavaScript
 * HTML5 video controls and progress saving
 * ==============================
 */

// Video player controller
class VideoPlayer {
    constructor(videoId) {
        this.videoId = videoId;
        this.video = document.getElementById('videoPlayer');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.progressBar = document.getElementById('progressBar');
        this.progressFilled = document.getElementById('progressFilled');
        this.progressThumb = document.getElementById('progressThumb');
        this.progressBuffered = document.getElementById('progressBuffered');
        this.currentTimeEl = document.getElementById('currentTime');
        this.durationEl = document.getElementById('duration');
        this.volumeSlider = document.getElementById('volumeSlider');
        this.volumeIcon = document.getElementById('volumeIcon');
        this.bigPlayBtn = document.getElementById('bigPlayBtn');
        this.loadingEl = document.getElementById('videoLoading');
        this.errorEl = document.getElementById('videoError');
        
        this.storageKey = `cinewave_progress_${videoId}`;
        this.init();
    }

    init() {
        if (!this.video) return;
        
        // Event listeners
        this.video.addEventListener('loadedmetadata', () => this.onLoadedMetadata());
        this.video.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.video.addEventListener('progress', () => this.onProgress());
        this.video.addEventListener('play', () => this.onPlay());
        this.video.addEventListener('pause', () => this.onPause());
        this.video.addEventListener('waiting', () => this.onWaiting());
        this.video.addEventListener('playing', () => this.onPlaying());
        this.video.addEventListener('error', (e) => this.onError(e));
        this.video.addEventListener('ended', () => this.onEnded());
        
        // Control events
        if (this.playPauseBtn) {
            this.playPauseBtn.addEventListener('click', () => this.togglePlay());
        }
        
        if (this.bigPlayBtn) {
            this.bigPlayBtn.addEventListener('click', () => this.playVideo());
        }
        
        if (this.progressBar) {
            this.progressBar.addEventListener('input', (e) => this.seek(e.target.value));
        }
        
        if (this.volumeSlider) {
            this.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
        }
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Restore progress
        this.restoreProgress();
        
        // Click to toggle play on video
        this.video.addEventListener('click', () => this.togglePlay());
        
        console.log('VideoPlayer initialized for video ID:', this.videoId);
    }

    onLoadedMetadata() {
        if (this.durationEl) {
            this.durationEl.textContent = this.formatTime(this.video.duration);
        }
        if (this.bigPlayBtn) {
            this.bigPlayBtn.style.display = 'flex';
        }
        console.log('Metadata loaded, duration:', this.video.duration);
    }

    onTimeUpdate() {
        if (!this.video.duration) return;
        
        const percent = (this.video.currentTime / this.video.duration) * 100;
        
        if (this.progressFilled) {
            this.progressFilled.style.width = `${percent}%`;
        }
        if (this.progressThumb) {
            this.progressThumb.style.left = `${percent}%`;
        }
        if (this.progressBar) {
            this.progressBar.value = percent;
        }
        if (this.currentTimeEl) {
            this.currentTimeEl.textContent = this.formatTime(this.video.currentTime);
        }
        
        // Save progress every 5 seconds
        if (Math.floor(this.video.currentTime) % 5 === 0 && this.video.currentTime > 0) {
            this.saveProgress();
        }
    }

    onProgress() {
        if (this.video.buffered.length > 0 && this.progressBuffered && this.video.duration) {
            const buffered = (this.video.buffered.end(0) / this.video.duration) * 100;
            this.progressBuffered.style.width = `${buffered}%`;
        }
    }

    onPlay() {
        this.updatePlayButton(true);
        if (this.bigPlayBtn) {
            this.bigPlayBtn.classList.add('hidden');
        }
    }

    onPause() {
        this.updatePlayButton(false);
        this.saveProgress();
    }

    onWaiting() {
        if (this.loadingEl) this.loadingEl.classList.add('active');
    }

    onPlaying() {
        if (this.loadingEl) this.loadingEl.classList.remove('active');
        if (this.bigPlayBtn) this.bigPlayBtn.classList.add('hidden');
    }

    onError(e) {
        console.error('Video error:', e);
        console.error('Error code:', this.video.error);
        if (this.loadingEl) this.loadingEl.classList.remove('active');
        if (this.errorEl) this.errorEl.style.display = 'flex';
        if (this.bigPlayBtn) this.bigPlayBtn.style.display = 'none';
    }

    onEnded() {
        this.saveProgress(100, true);
        showToast('Video completed!', 'success');
    }

    updatePlayButton(isPlaying) {
        if (this.playPauseBtn) {
            const icon = isPlaying ? 'fa-pause' : 'fa-play';
            this.playPauseBtn.innerHTML = `<i class="fas ${icon}"></i>`;
        }
    }

    togglePlay() {
        if (this.video.paused) {
            this.video.play().catch(e => console.error('Play error:', e));
        } else {
            this.video.pause();
        }
    }

    playVideo() {
        this.video.play().catch(e => console.error('Play error:', e));
    }

    seek(value) {
        if (!this.video.duration) return;
        const time = (value / 100) * this.video.duration;
        this.video.currentTime = time;
    }

    skip(seconds) {
        if (!this.video.duration) return;
        this.video.currentTime = Math.max(0, Math.min(this.video.duration, this.video.currentTime + seconds));
    }

    setVolume(value) {
        this.video.volume = value / 100;
        if (this.volumeSlider) this.volumeSlider.value = value;
        this.updateVolumeIcon(value > 0);
    }

    updateVolumeIcon(isMuted) {
        if (this.volumeIcon) {
            this.volumeIcon.className = isMuted ? 'fas fa-volume-up' : 'fas fa-volume-mute';
        }
    }

    toggleMute() {
        this.video.muted = !this.video.muted;
        this.updateVolumeIcon(!this.video.muted);
    }

    toggleFullscreen() {
        const wrapper = document.getElementById('videoWrapper');
        if (!wrapper) return;
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            wrapper.requestFullscreen();
        }
    }

    togglePiP() {
        if (this.video !== document.pictureInPictureElement) {
            this.video.requestPictureInPicture();
        } else {
            document.exitPictureInPicture();
        }
    }

    toggleCaptions() {
        showToast('Captions coming soon', 'info');
    }

    handleKeyboard(e) {
        switch(e.key) {
            case ' ':
                e.preventDefault();
                this.togglePlay();
                break;
            case 'f':
                this.toggleFullscreen();
                break;
            case 'm':
                this.toggleMute();
                break;
            case 'ArrowLeft':
                this.skip(-10);
                break;
            case 'ArrowRight':
                this.skip(10);
                break;
            case 'ArrowUp':
                this.setVolume(Math.min(100, parseInt(this.volumeSlider?.value || 100) + 10));
                break;
            case 'ArrowDown':
                this.setVolume(Math.max(0, parseInt(this.volumeSlider?.value || 100) - 10));
                break;
        }
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return h > 0 ? `${h}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}` : `${m}:${s.toString().padStart(2,'0')}`;
    }

    async saveProgress(progress = null, completed = false) {
        const currentProgress = progress !== null ? progress : Math.floor(this.video.currentTime);
        
        try {
            await fetch('/api/save-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    movie_id: this.videoId,
                    progress: currentProgress,
                    completed: completed
                })
            });
        } catch (error) {
            console.error('Failed to save progress:', error);
        }
        
        localStorage.setItem(this.storageKey, JSON.stringify({
            progress: currentProgress,
            completed: completed,
            timestamp: Date.now()
        }));
    }

    restoreProgress() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                const data = JSON.parse(saved);
                this.video.currentTime = data.progress || 0;
            } catch(e) {
                console.error('Failed to restore progress:', e);
            }
        }
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

// Global player instance
let videoPlayerInstance = null;

// Initialize video player
function initVideoPlayer() {
    const path = window.location.pathname;
    const match = path.match(/\/watch\/(\d+)\//);
    const videoId = match ? parseInt(match[1]) : null;
    
    if (videoId) {
        console.log('Initializing video player for movie ID:', videoId);
        videoPlayerInstance = new VideoPlayer(videoId);
    } else {
        console.log('No video ID found in path:', path);
    }
}

// Global functions for onclick handlers
function togglePlay() {
    if (videoPlayerInstance) videoPlayerInstance.togglePlay();
}

function playVideo() {
    if (videoPlayerInstance) videoPlayerInstance.playVideo();
}

function skip(seconds) {
    if (videoPlayerInstance) videoPlayerInstance.skip(seconds);
}

function setVolume(value) {
    if (videoPlayerInstance) videoPlayerInstance.setVolume(value);
}

function toggleMute() {
    if (videoPlayerInstance) videoPlayerInstance.toggleMute();
}

function toggleFullscreen() {
    if (videoPlayerInstance) videoPlayerInstance.toggleFullscreen();
}

function togglePiP() {
    if (videoPlayerInstance) videoPlayerInstance.togglePiP();
}

function toggleCaptions() {
    if (videoPlayerInstance) videoPlayerInstance.toggleCaptions();
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

// Show shortcuts modal
function showShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    if (modal) modal.classList.add('active');
}

function closeShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    if (modal) modal.classList.remove('active');
}

// Export to window
window.VideoPlayer = VideoPlayer;
window.initVideoPlayer = initVideoPlayer;
window.togglePlay = togglePlay;
window.playVideo = playVideo;
window.skip = skip;
window.setVolume = setVolume;
window.toggleMute = toggleMute;
window.toggleFullscreen = toggleFullscreen;
window.togglePiP = togglePiP;
window.toggleCaptions = toggleCaptions;
window.showShortcuts = showShortcuts;
window.closeShortcuts = closeShortcuts;
window.showToast = showToast;
