// Offline Mode Manager
// Handles service worker registration, offline detection, and cached path tracking

(function() {
  'use strict';

  var OfflineManager = {
    isOnline: navigator.onLine,
    serviceWorkerRegistered: false,

    /**
     * Initialize offline mode functionality
     */
    init: function() {
      // Register service worker for offline support
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
          .then(function(registration) {
            console.log('Service Worker registered successfully');
            OfflineManager.serviceWorkerRegistered = true;
          })
          .catch(function(error) {
            console.warn('Service Worker registration failed:', error);
          });
      }

      // Listen for online/offline events
      window.addEventListener('online', OfflineManager.handleOnline);
      window.addEventListener('offline', OfflineManager.handleOffline);

      // Show offline banner if already offline
      if (!navigator.onLine) {
        OfflineManager.showOfflineBanner();
      }

      // Track visited paths for offline access
      OfflineManager.trackCurrentPath();
    },

    /**
     * Handle when user comes online
     */
    handleOnline: function() {
      OfflineManager.isOnline = true;
      console.log('Back online');
      OfflineManager.hideOfflineBanner();

      // Notify user they're back online
      OfflineManager.showNotification('You are back online!', 'success');
    },

    /**
     * Handle when user goes offline
     */
    handleOffline: function() {
      OfflineManager.isOnline = false;
      console.log('Gone offline');
      OfflineManager.showOfflineBanner();

      // Notify user they're offline
      OfflineManager.showNotification('You are offline. Some features may be limited.', 'warning');
    },

    /**
     * Show offline notification banner at top of page
     */
    showOfflineBanner: function() {
      var banner = document.getElementById('offline-banner');

      if (!banner) {
        banner = document.createElement('div');
        banner.id = 'offline-banner';
        banner.className = 'offline-banner';
        banner.innerHTML = '<span>📡 You are offline - Some features may be unavailable</span>';
        banner.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: #ffa500;
          color: white;
          padding: 12px;
          text-align: center;
          z-index: 9999;
          font-size: 14px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        document.body.insertBefore(banner, document.body.firstChild);

        // Adjust body padding to account for banner
        document.body.style.paddingTop = '44px';
      }

      banner.style.display = 'block';
    },

    /**
     * Hide offline notification banner
     */
    hideOfflineBanner: function() {
      var banner = document.getElementById('offline-banner');
      if (banner) {
        banner.style.display = 'none';
        document.body.style.paddingTop = '0';
      }
    },

    /**
     * Show temporary notification to user
     */
    showNotification: function(message, type) {
      // Create notification element
      var notification = document.createElement('div');
      notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : '#ff9800'};
        color: white;
        padding: 16px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9998;
        animation: slideIn 0.3s ease;
      `;
      notification.textContent = message;
      document.body.appendChild(notification);

      // Add animation styles if not present
      if (!document.getElementById('offline-animations')) {
        var style = document.createElement('style');
        style.id = 'offline-animations';
        style.textContent = `
          @keyframes slideIn {
            from {
              transform: translateX(400px);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `;
        document.head.appendChild(style);
      }

      // Remove notification after 4 seconds
      setTimeout(function() {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(function() {
          document.body.removeChild(notification);
        }, 300);
      }, 4000);
    },

    /**
     * Track current learning path for offline access
     */
    trackCurrentPath: function() {
      // Extract path info from current page
      var pathElement = document.querySelector('[data-path-id]');

      if (pathElement) {
        var pathId = pathElement.getAttribute('data-path-id');
        var pathName = pathElement.getAttribute('data-path-name') || 'Learning Path';
        var pathUrl = window.location.pathname;

        OfflineManager.saveCachedPath({
          id: pathId,
          name: pathName,
          url: pathUrl,
          accessedAt: new Date().toISOString()
        });
      }
    },

    /**
     * Save path to cached paths list in localStorage
     */
    saveCachedPath: function(path) {
      try {
        var cached = localStorage.getItem('devpath_cached_paths') || '[]';
        var paths = JSON.parse(cached);

        // Remove if already exists to avoid duplicates
        paths = paths.filter(function(p) {
          return p.id !== path.id;
        });

        // Add new path to beginning of list
        paths.unshift(path);

        // Keep only last 10 visited paths
        paths = paths.slice(0, 10);

        localStorage.setItem('devpath_cached_paths', JSON.stringify(paths));
      } catch (error) {
        console.warn('Could not save cached path:', error);
      }
    },

    /**
     * Get cached paths from localStorage
     */
    getCachedPaths: function() {
      try {
        var cached = localStorage.getItem('devpath_cached_paths') || '[]';
        return JSON.parse(cached);
      } catch (error) {
        console.warn('Could not retrieve cached paths:', error);
        return [];
      }
    },

    /**
     * Check if user is currently online
     */
    isCurrentlyOnline: function() {
      return navigator.onLine && OfflineManager.isOnline;
    },

    /**
     * Get offline status information
     */
    getStatus: function() {
      return {
        online: OfflineManager.isCurrentlyOnline(),
        serviceWorkerRegistered: OfflineManager.serviceWorkerRegistered,
        cachedPaths: OfflineManager.getCachedPaths()
      };
    }
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      OfflineManager.init();
    });
  } else {
    OfflineManager.init();
  }

  // Export for external use
  window.OfflineManager = OfflineManager;
})();
