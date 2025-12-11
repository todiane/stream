/**
 * Video Progress Tracking Script - YouTube Only
 * For Stream English (https://streamenglish.co.uk)
 * 
 * Modern, simplified implementation for YouTube videos only.
 * Tracks user progress and saves to server via AJAX.
 * 
 * Updated: 2025 - Removed HTML5/Cloudinary support
 */

// Configuration
const CONFIG = {
  saveInterval: 30000,  // Save progress every 30 seconds
  debug: false,         // Set to true for development debugging
};

// State
let player = null;
let progressInterval = null;
let currentLessonId = null;

// ============================================
// Utility Functions
// ============================================

function log(message, data = null) {
  if (!CONFIG.debug) return;
  console.log(`[VideoTracking] ${message}`, data || '');
}

function logError(message, error = null) {
  console.error(`[VideoTracking Error] ${message}`, error || '');
}

function getCSRFToken() {
  // Try global variable first (set in template)
  if (typeof CSRF_TOKEN !== 'undefined' && CSRF_TOKEN) {
    return CSRF_TOKEN;
  }

  // Try cookie
  const name = 'csrftoken';
  if (document.cookie) {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        return decodeURIComponent(trimmed.substring(name.length + 1));
      }
    }
  }

  // Try meta tag
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    return metaTag.getAttribute('content');
  }

  logError('No CSRF token found');
  return '';
}

// ============================================
// Progress Saving
// ============================================

async function saveProgress(lessonId, currentTime, isCompleted = false) {
  if (!lessonId) {
    logError('Missing lesson ID');
    return null;
  }

  currentTime = Math.floor(parseFloat(currentTime) || 0);
  log('Saving progress', { lessonId, currentTime, isCompleted });

  try {
    const response = await fetch(`/profiles/mark-video-watched/${lessonId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        current_time: currentTime,
        is_completed: Boolean(isCompleted),
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    log('Progress saved', data);

    if (data.status === 'success' && data.course_progress !== undefined) {
      updateProgressUI(data.course_progress);
    }

    return data;
  } catch (error) {
    logError('Failed to save progress', error);
    return null;
  }
}

async function loadSavedProgress(lessonId) {
  try {
    const response = await fetch(`/profiles/get-video-progress/${lessonId}/`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    logError('Failed to load progress', error);
    return null;
  }
}

function updateProgressUI(progress) {
  const progressBars = document.querySelectorAll('.course-progress');
  progressBars.forEach(bar => {
    bar.style.width = `${progress}%`;
    bar.setAttribute('aria-valuenow', progress);

    const textDisplay = bar.parentElement?.querySelector('.progress-text');
    if (textDisplay) {
      textDisplay.textContent = `${Math.round(progress)}%`;
    }
  });
}

// ============================================
// YouTube Player
// ============================================

function initializeYouTubePlayer() {
  const container = document.getElementById('youtube-player');
  if (!container) {
    log('No YouTube player container found');
    return;
  }

  const lessonId = container.dataset.lessonId;
  const videoId = container.dataset.videoId;

  if (!lessonId || !videoId) {
    logError('Missing lesson ID or video ID');
    return;
  }

  currentLessonId = lessonId;
  log('Initializing YouTube player', { lessonId, videoId });

  // Check if YT API is ready
  if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
    log('YouTube API not ready, waiting...');
    setTimeout(initializeYouTubePlayer, 500);
    return;
  }

  try {
    player = new YT.Player('youtube-player', {
      videoId: videoId,
      width: '100%',
      height: '100%',
      host: 'https://www.youtube-nocookie.com', // Privacy-enhanced mode
      playerVars: {
        playsinline: 1,
        enablejsapi: 1,
        rel: 0,
        modestbranding: 1,
        origin: window.location.origin,
      },
      events: {
        onReady: onPlayerReady,
        onStateChange: onPlayerStateChange,
        onError: onPlayerError,
      },
    });

    log('YouTube player created');
  } catch (error) {
    logError('Failed to create YouTube player', error);
  }
}

async function onPlayerReady(event) {
  log('Player ready');

  // Load and restore saved progress
  const savedData = await loadSavedProgress(currentLessonId);
  if (savedData?.current_time > 0) {
    log('Restoring position', savedData.current_time);
    event.target.seekTo(savedData.current_time);
  }
}

function onPlayerStateChange(event) {
  const states = {
    [-1]: 'unstarted',
    [0]: 'ended',
    [1]: 'playing',
    [2]: 'paused',
    [3]: 'buffering',
    [5]: 'cued',
  };

  log(`State changed: ${states[event.data] || event.data}`);

  // Clear existing interval
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }

  switch (event.data) {
    case YT.PlayerState.PLAYING:
      // Start periodic saving
      progressInterval = setInterval(() => {
        if (player?.getCurrentTime) {
          saveProgress(currentLessonId, player.getCurrentTime());
        }
      }, CONFIG.saveInterval);
      break;

    case YT.PlayerState.PAUSED:
      // Save immediately on pause
      if (player?.getCurrentTime) {
        saveProgress(currentLessonId, player.getCurrentTime());
      }
      break;

    case YT.PlayerState.ENDED:
      // Mark as completed
      if (player?.getDuration) {
        saveProgress(currentLessonId, player.getDuration(), true);
      }
      break;
  }
}

function onPlayerError(event) {
  const errors = {
    2: 'Invalid video ID',
    5: 'HTML5 player error',
    100: 'Video not found or private',
    101: 'Embedding disabled by owner',
    150: 'Embedding disabled by owner',
  };

  logError(`YouTube error: ${errors[event.data] || `Code ${event.data}`}`);

  // Show user-friendly error message
  const container = document.getElementById('youtube-player');
  if (container) {
    container.innerHTML = `
      <div class="flex items-center justify-center h-full bg-gray-100 rounded-lg">
        <div class="text-center p-8">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">Video unavailable</h3>
          <p class="mt-1 text-sm text-gray-500">This video cannot be played at the moment.</p>
        </div>
      </div>
    `;
  }
}

// ============================================
// Thumbnail Click-to-Load (Lazy Loading)
// ============================================

function initializeThumbnailPlayer() {
  const thumbnail = document.getElementById('video-thumbnail');
  if (!thumbnail) return;

  thumbnail.addEventListener('click', () => {
    const container = thumbnail.closest('.video-container');
    const videoId = thumbnail.dataset.videoId;
    const lessonId = thumbnail.dataset.lessonId;

    if (!container || !videoId) return;

    // Replace thumbnail with player div
    container.innerHTML = `
      <div id="youtube-player" 
           data-lesson-id="${lessonId}"
           data-video-id="${videoId}"
           class="absolute top-0 left-0 w-full h-full">
      </div>
    `;

    // Initialize player
    initializeYouTubePlayer();

    // Auto-play after initialization
    const checkAndPlay = setInterval(() => {
      if (player?.playVideo) {
        player.playVideo();
        clearInterval(checkAndPlay);
      }
    }, 100);

    // Timeout after 5 seconds
    setTimeout(() => clearInterval(checkAndPlay), 5000);
  });
}

// ============================================
// YouTube API Callback & Initialization
// ============================================

window.onYouTubeIframeAPIReady = function () {
  log('YouTube IFrame API Ready');
  initializeYouTubePlayer();
};

document.addEventListener('DOMContentLoaded', () => {
  log('DOM loaded - initializing video tracking');

  const hasPlayer = document.getElementById('youtube-player');
  const hasThumbnail = document.getElementById('video-thumbnail');

  if (hasPlayer) {
    // Load YouTube API if needed
    if (typeof YT === 'undefined') {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      document.head.appendChild(tag);
      log('Loading YouTube API');
    } else {
      initializeYouTubePlayer();
    }
  } else if (hasThumbnail) {
    // Set up click-to-load
    initializeThumbnailPlayer();
    log('Thumbnail click-to-load ready');
  } else {
    log('No video elements on this page');
  }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (progressInterval) {
    clearInterval(progressInterval);
  }
  // Final save attempt
  if (player?.getCurrentTime && currentLessonId) {
    // Use sendBeacon for reliability during unload
    const data = JSON.stringify({
      current_time: Math.floor(player.getCurrentTime()),
      is_completed: false,
    });
    navigator.sendBeacon?.(
      `/profiles/mark-video-watched/${currentLessonId}/`,
      new Blob([data], { type: 'application/json' })
    );
  }
});