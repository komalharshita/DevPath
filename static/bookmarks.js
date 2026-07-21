// Bookmark management for resources and topics
// Supports both authenticated users (database) and guests (localStorage)

(function() {
  'use strict';

  var BookmarkManager = {
    /**
     * Toggle bookmark status for a resource
     */
    toggleBookmark: function(resourceType, resourceId, resourceName, userId) {
      if (userId) {
        BookmarkManager.toggleAuthenticatedBookmark(
          resourceType,
          resourceId,
          resourceName,
          userId
        );
      } else {
        BookmarkManager.toggleLocalBookmark(
          resourceType,
          resourceId,
          resourceName
        );
      }
    },

    /**
     * Toggle bookmark for authenticated user (server-side)
     */
    toggleAuthenticatedBookmark: function(resourceType, resourceId, resourceName, userId) {
      var isBookmarked = BookmarkManager.isBookmarked(
        resourceType,
        resourceId,
        userId
      );

      var endpoint = isBookmarked
        ? '/bookmarks/remove'
        : '/bookmarks/add';

      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          resource_type: resourceType,
          resource_id: resourceId,
          resource_name: resourceName
        })
      })
        .then(function(response) {
          if (!response.ok) throw new Error('Bookmark operation failed');
          return response.json();
        })
        .then(function(data) {
          if (data.success) {
            BookmarkManager.updateBookmarkUI(
              resourceType,
              resourceId,
              !isBookmarked
            );
            var message = isBookmarked
              ? 'Bookmark removed'
              : 'Bookmark added';
            BookmarkManager.showNotification(message, 'success');
          }
        })
        .catch(function(error) {
          console.error('Error toggling bookmark:', error);
          BookmarkManager.showNotification(
            'Failed to update bookmark',
            'error'
          );
        });
    },

    /**
     * Toggle bookmark for guest user (localStorage)
     */
    toggleLocalBookmark: function(resourceType, resourceId, resourceName) {
      var bookmarks = BookmarkManager.getLocalBookmarks();
      var key = resourceType + '_' + resourceId;
      var isBookmarked = key in bookmarks;

      if (isBookmarked) {
        delete bookmarks[key];
        BookmarkManager.showNotification('Bookmark removed', 'success');
      } else {
        bookmarks[key] = {
          resourceType: resourceType,
          resourceId: resourceId,
          resourceName: resourceName,
          savedAt: new Date().toISOString()
        };
        BookmarkManager.showNotification('Bookmark added', 'success');
      }

      try {
        localStorage.setItem(
          'devpath_bookmarks',
          JSON.stringify(bookmarks)
        );
        BookmarkManager.updateBookmarkUI(
          resourceType,
          resourceId,
          !isBookmarked
        );
      } catch (error) {
        console.error('localStorage error:', error);
      }
    },

    /**
     * Get all local bookmarks from localStorage
     */
    getLocalBookmarks: function() {
      try {
        var stored = localStorage.getItem('devpath_bookmarks') || '{}';
        return JSON.parse(stored);
      } catch (error) {
        console.warn('Error reading localStorage:', error);
        return {};
      }
    },

    /**
     * Check if resource is bookmarked
     */
    isBookmarked: function(resourceType, resourceId, userId) {
      if (userId) {
        // For authenticated users, check via API
        var isBookmarked = document.querySelector(
          '[data-resource-type="' + resourceType + '"][data-resource-id="' + resourceId + '"][data-bookmarked="true"]'
        );
        return isBookmarked !== null;
      } else {
        // For guests, check localStorage
        var bookmarks = BookmarkManager.getLocalBookmarks();
        var key = resourceType + '_' + resourceId;
        return key in bookmarks;
      }
    },

    /**
     * Update bookmark button UI state
     */
    updateBookmarkUI: function(resourceType, resourceId, isBookmarked) {
      var button = document.querySelector(
        'button[data-resource-type="' + resourceType + '"][data-resource-id="' + resourceId + '"]'
      );

      if (button) {
        if (isBookmarked) {
          button.classList.add('bookmarked');
          button.setAttribute('data-bookmarked', 'true');
          button.textContent = '★ Bookmarked';
        } else {
          button.classList.remove('bookmarked');
          button.setAttribute('data-bookmarked', 'false');
          button.textContent = '☆ Bookmark';
        }
      }
    },

    /**
     * Show toast notification
     */
    showNotification: function(message, type) {
      var notification = document.createElement('div');
      notification.style.cssText =
        'position: fixed; top: 20px; right: 20px; ' +
        'padding: 12px 16px; border-radius: 4px; ' +
        'color: white; z-index: 9999; ' +
        'background: ' + (type === 'success' ? '#4caf50' : '#f44336');
      notification.textContent = message;
      document.body.appendChild(notification);

      setTimeout(function() {
        document.body.removeChild(notification);
      }, 3000);
    },

    /**
     * Initialize bookmark buttons on page
     */
    init: function() {
      var buttons = document.querySelectorAll('[data-bookmark-btn]');
      buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
          e.preventDefault();
          var resourceType = button.getAttribute(
            'data-resource-type'
          );
          var resourceId = button.getAttribute('data-resource-id');
          var resourceName = button.getAttribute(
            'data-resource-name'
          );
          var userId = button.getAttribute('data-user-id');

          BookmarkManager.toggleBookmark(
            resourceType,
            resourceId,
            resourceName,
            userId
          );
        });
      });
    }
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      BookmarkManager.init();
    });
  } else {
    BookmarkManager.init();
  }

  // Export for external use
  window.BookmarkManager = BookmarkManager;
})();
