const CACHE_NAME = 'univ-roulette-v1';
const urlsToCache = [
    '/',
    '/static/manifest.json',
    '/static/img/icon-192.png',
    '/static/img/icon-512.png',
    'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});
