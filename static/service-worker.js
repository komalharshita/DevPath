// Service Worker for offline caching and offline mode support
// Enables users to access recently visited paths while offline

var CACHE_NAME = 'devpath-v1';
var urlsToCache = [
  '/',
  '/static/style.css',
  '/static/script.js',
  '/static/offline.html'
];

// Install event: cache essential resources
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
      .catch(function(error) {
        console.error('Cache installation failed:', error);
      })
  );
  self.skipWaiting();
});

// Activate event: clean up old caches
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event: serve from cache, fall back to network
self.addEventListener('fetch', function(event) {
  var request = event.request;

  // Skip cross-origin requests
  if (!request.url.startsWith(self.location.origin)) {
    return;
  }

  // For GET requests, try cache first
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request)
        .then(function(response) {
          // Return cached response if found
          if (response) {
            return response;
          }

          // Fetch from network if not in cache
          return fetch(request)
            .then(function(networkResponse) {
              // Cache successful responses (but not errors)
              if (networkResponse && networkResponse.status === 200) {
                var responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME)
                  .then(function(cache) {
                    cache.put(request, responseToCache);
                  });
              }
              return networkResponse;
            })
            .catch(function(error) {
              // Return offline page for navigation requests
              if (request.mode === 'navigate') {
                return caches.match('/static/offline.html');
              }
              // Return error response for other requests
              return new Response('Offline', {
                status: 503,
                statusText: 'Service Unavailable'
              });
            });
        })
    );
  }
});

// Message event: handle postMessage from clients
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
