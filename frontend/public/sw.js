const CACHE_NAME = 'unnate-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/dashboard',
  '/advisory/business-plan',
  '/advisory/schemes',
  '/advisory/financial',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
