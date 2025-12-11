/**
 * Video Progress Tracking Script - Production Version
 * For Stream English (https://streamenglish.co.uk)
 * 
 * This script tracks user progress through video lessons and
 * sends updates to the server via AJAX requests.
 */

// Configuration
const SAVE_INTERVAL = 30000; // Save progress every 30 seconds
const DEBUG = true;          // Enable debugging (set to false in production after fixing issues)

// State variables
let progressInterval = null;
let player = null;
let isInitialized = false;

// Debugging helpers
function debugLog(message, data = null) {
  if (!DEBUG) return;
  console.log(`[VideoTracking] ${message}`, data || '');
}

function logError(message, error = null) {
  console.error(`[VideoTracking Error] ${message}`, error || '');
}

// Get CSRF token - use global variable if available, fall back to cookie
function getCSRFToken() {
  // First try global variable set in the template
  if (typeof CSRF_TOKEN !== 'undefined') {
    debugLog('Using CSRF token from global variable');
    return CSRF_TOKEN;
  }

  // Next try cookie
  debugLog('Getting CSRF token from cookie');
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

  if (cookieValue) {
    debugLog('Found CSRF token in cookie');
    return cookieValue;
  }

  // Last try - get from meta tag
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    debugLog('Found CSRF token in meta tag');
    return metaTag.getAttribute('content');
  }

  // If we get here, we couldn't find a token
  logError('No CSRF token found!');
  return '';
}

// Main function to save video progress via AJAX
async function saveVideoProgress(lessonId, currentTime, isCompleted = false) {
  if (!lessonId) {
    logError('Missing lesson ID for progress update');
    return null;
  }

  // Make sure we have valid numbers
  currentTime = Math.floor(parseFloat(currentTime) || 0);

  debugLog('Saving progress:', { lessonId, currentTime, isCompleted });

  try {
    const csrftoken = getCSRFToken();
    if (!csrftoken) {
      throw new Error('Could not get CSRF token');
    }

    const url = `/profiles/mark-video-watched/${lessonId}/`;
    const requestData = {
      current_time: currentTime,
      is_completed: Boolean(isCompleted)
    };

    debugLog('Sending request to:', url);
    debugLog('Request data:', requestData);
    debugLog('Using CSRF token (first 5 chars):', csrftoken.substring(0, 5) + '...');

    // Create the fetch request with proper headers
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken
      },
      credentials: 'same-origin',
      body: JSON.stringify(requestData)
    });

    debugLog('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
    }

    const data = await response.json();
    debugLog('Response data:', data);

    if (data.status === 'success' && data.course_progress !== undefined) {
      updateProgressUI(data.course_progress);
    }

    return data;
  } catch (error) {
    logError('Failed to save progress:', error);
    return null;
  }
}

// Update UI elements with progress information
function updateProgressUI(progress) {
  try {
    const progressBars = document.querySelectorAll('.course-progress');
    debugLog(`Updating ${progressBars.length} progress bars to ${progress}%`);

    progressBars.forEach(bar => {
      bar.style.width = `${progress}%`;
      bar.setAttribute('aria-valuenow', progress);

      // Update text if present
      const textDisplay = bar.parentElement.querySelector('.progress-text');
      if (textDisplay) {
        textDisplay.textContent = `${Math.round(progress)}%`;
      }
    });
  } catch (error) {
    logError('Error updating progress UI:', error);
  }
}

// YouTube integration
function initializeYouTubePlayer() {
  debugLog('Initializing YouTube player');

  const playerElement = document.getElementById('youtube-player');
  if (!playerElement) {
    debugLog('No YouTube player element found');
    return;
  }

  const lessonId = playerElement.dataset.lessonId;
  const videoId = playerElement.dataset.videoId;

  if (!lessonId) {
    logError('YouTube player missing lesson ID attribute');
    return;
  }

  if (!videoId) {
    logError('YouTube player missing video ID attribute');
    return;
  }

  debugLog('Found YouTube player for lesson:', lessonId);
  debugLog('Video ID:', videoId);

  // Make sure the YouTube API is loaded
  if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
    debugLog('YouTube API not yet loaded, waiting...');
    setTimeout(initializeYouTubePlayer, 1000);
    return;
  }

  try {
    player = new YT.Player('youtube-player', {
      videoId: videoId,
      width: '100%',
      height: '100%',
      playerVars: {
        'playsinline': 1,
        'enablejsapi': 1,
        'rel': 0
      },
      events: {
        'onReady': (event) => onPlayerReady(event, lessonId),
        'onStateChange': (event) => onPlayerStateChange(event, lessonId),
        'onError': onPlayerError
      }
    });

    isInitialized = true;
    debugLog('YouTube player initialized successfully');
  } catch (error) {
    logError('Failed to initialize YouTube player:', error);
  }
}

// Load saved progress when player is ready
async function onPlayerReady(event, lessonId) {
  debugLog('YouTube player ready for lesson:', lessonId);

  try {
    // Load saved progress
    const response = await fetch(`/profiles/get-video-progress/${lessonId}/`);

    if (!response.ok) {
      throw new Error(`Failed to load progress: ${response.status}`);
    }

    const data = await response.json();
    debugLog('Retrieved saved progress:', data);

    // Seek to saved position if available
    if (data.current_time && data.current_time > 0) {
      debugLog('Seeking to saved position:', data.current_time);
      event.target.seekTo(data.current_time);
    }
  } catch (error) {
    logError('Error loading saved progress:', error);
  }
}

// Handle player state changes
function onPlayerStateChange(event, lessonId) {
  const stateNames = {
    '-1': 'unstarted',
    '0': 'ended',
    '1': 'playing',
    '2': 'paused',
    '3': 'buffering',
    '5': 'video cued'
  };

  debugLog(`Player state changed to ${stateNames[event.data] || event.data}`, { lessonId });

  // Clear existing interval if any
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }

  // Handle different states
  switch (event.data) {
    case YT.PlayerState.PLAYING:
      debugLog('Video playing - starting progress tracking');
      progressInterval = setInterval(() => {
        if (player && typeof player.getCurrentTime === 'function') {
          saveVideoProgress(lessonId, player.getCurrentTime());
        }
      }, SAVE_INTERVAL);
      break;

    case YT.PlayerState.PAUSED:
      debugLog('Video paused - saving current progress');
      if (player && typeof player.getCurrentTime === 'function') {
        saveVideoProgress(lessonId, player.getCurrentTime());
      }
      break;

    case YT.PlayerState.ENDED:
      debugLog('Video ended - marking as completed');
      if (player && typeof player.getCurrentTime === 'function') {
        saveVideoProgress(lessonId, player.getDuration(), true);
      }
      break;
  }
}

// Handle player errors
function onPlayerError(event) {
  const errorMessages = {
    2: 'Invalid parameter',
    5: 'HTML5 player error',
    100: 'Video not found or private',
    101: 'Embedding not allowed',
    150: 'Embedding not allowed'
  };

  const errorMessage = errorMessages[event.data] || `Unknown error code ${event.data}`;
  logError(`YouTube player error: ${errorMessage}`);
}

// HTML5 video integration
function initializeHTML5Video() {
  const videoElement = document.getElementById('html5-player');
  if (!videoElement) {
    return; // No HTML5 video on this page
  }

  const lessonId = videoElement.dataset.lessonId;
  if (!lessonId) {
    logError('HTML5 video player missing lesson ID attribute');
    return;
  }

  debugLog('Found HTML5 video for lesson:', lessonId);

  // Load saved progress
  fetch(`/profiles/get-video-progress/${lessonId}/`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Failed to load progress: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Seek to saved position if available
      if (data.current_time && data.current_time > 0) {
        debugLog('Seeking HTML5 video to saved position:', data.current_time);
        videoElement.currentTime = data.current_time;
      }
    })
    .catch(error => {
      logError('Error loading HTML5 video progress:', error);
    });

  // Set up event listeners
  videoElement.addEventListener('play', function () {
    debugLog('HTML5 video started playing');
    if (progressInterval) clearInterval(progressInterval);

    progressInterval = setInterval(() => {
      saveVideoProgress(lessonId, this.currentTime);
    }, SAVE_INTERVAL);
  });

  videoElement.addEventListener('pause', function () {
    debugLog('HTML5 video paused');
    if (progressInterval) clearInterval(progressInterval);
    saveVideoProgress(lessonId, this.currentTime);
  });

  videoElement.addEventListener('ended', function () {
    debugLog('HTML5 video ended - marking as completed');
    if (progressInterval) clearInterval(progressInterval);
    saveVideoProgress(lessonId, this.duration, true);
  });

  videoElement.addEventListener('error', function (e) {
    const errorMessages = [
      'MEDIA_ERR_ABORTED',
      'MEDIA_ERR_NETWORK',
      'MEDIA_ERR_DECODE',
      'MEDIA_ERR_SRC_NOT_SUPPORTED'
    ];

    const errorCode = this.error ? this.error.code : 0;
    const errorMessage = errorMessages[errorCode - 1] || 'Unknown error';
    logError(`HTML5 video error: ${errorMessage}`);
  });
}

// YouTube API callback
window.onYouTubeIframeAPIReady = function () {
  debugLog('YouTube IFrame API Ready');
  initializeYouTubePlayer();
};

// Initialization
document.addEventListener('DOMContentLoaded', function () {
  debugLog('DOM Content Loaded - Starting video tracking initialization');

  // Check for video elements
  const hasYouTubeVideo = !!document.getElementById('youtube-player');
  const hasHTML5Video = !!document.getElementById('html5-player');

  if (hasYouTubeVideo) {
    debugLog('Found YouTube video - loading API');
    // Load YouTube API if not already loaded
    if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
      const tag = document.createElement('script');
      tag.src = "https://www.youtube.com/iframe_api";
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
      debugLog('YouTube API script added to page');
    } else {
      initializeYouTubePlayer();
    }
  }

  if (hasHTML5Video) {
    debugLog('Found HTML5 video - initializing');
    initializeHTML5Video();
  }

  if (!hasYouTubeVideo && !hasHTML5Video) {
    debugLog('No video elements found on this page');
  }
});