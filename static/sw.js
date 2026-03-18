const CACHE_NAME = 'univ-roulette-v4';
const urlsToCache = [
    '/',
    '/manifest.json',
    '/static/img/icon-192.png',
    '/static/img/icon-512.png',
    'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css'
];

self.addEventListener('install', event => {
    // skipWaiting()은 이제 message 이벤트에서 명시적으로 호출합니다.
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

// 클라이언트(페이지)로부터 활성화(업데이트) 요청을 받았을 때 즉시 대기 상태를 건너뜀
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    // API 요청(검색 등)은 캐시하지 않고 항상 네트워크를 통합니다.
    if (event.request.url.includes('/search') || event.request.url.includes('/report_price')) {
        event.respondWith(fetch(event.request));
        return;
    }

    // 정적 자원 및 HTML 화면은 Stale-While-Revalidate 전략 사용
    event.respondWith(
        caches.open(CACHE_NAME).then(cache => {
            return cache.match(event.request).then(response => {
                const fetchPromise = fetch(event.request).then(networkResponse => {
                    // 성공적인 응답만 캐시에 업데이트
                    if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
                        cache.put(event.request, networkResponse.clone());
                    }
                    return networkResponse;
                }).catch(() => {
                    // 오프라인 상태 처리 등을 여기에 추가할 수 있습니다.
                });
                
                // 캐시된 응답이 있으면 즉시 반환하고, 백그라운드에서 네트워크 요청(fetchPromise)을 진행
                return response || fetchPromise;
            });
        })
    );
});
