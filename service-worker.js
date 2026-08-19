// ============================================
// UNIYO LMS - Service Worker
// ============================================

const CACHE_NAME = 'UNIYO_UI_CACHE_V1';

const UI_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/css/auth.css',
    '/static/css/student_home.css',
    '/static/css/student_lessons.css',
    '/static/css/student_worksheet.css',
    '/static/css/student_vip.css',
    '/static/css/student_settings.css',
    '/static/css/student_certificate.css',
    '/static/css/admin_home.css',
    '/static/css/animations.css',
    '/static/css/responsive.css',
    '/static/js/main.js',
    '/static/js/auth.js',
    '/static/js/student_home.js',
    '/static/js/student_lessons.js',
    '/static/js/student_worksheet.js',
    '/static/js/student_vip.js',
    '/static/js/student_settings.js',
    '/static/js/offline-manager.js',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(UI_ASSETS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    if (event.request.url.includes('/api/')) return;
    
    event.respondWith(
        caches.match(event.request)
            .then((cached) => {
                if (cached) return cached;
                return fetch(event.request)
                    .then((response) => {
                        if (response.ok && event.request.url.includes('/static/')) {
                            const responseClone = response.clone();
                            caches.open(CACHE_NAME).then((cache) => {
                                cache.put(event.request, responseClone);
                            });
                        }
                        return response;
                    })
                    .catch(() => {
                        if (event.request.mode === 'navigate') {
                            return caches.match('/offline.html');
                        }
                        return new Response('', { status: 503, statusText: 'Offline' });
                    });
            })
    );
});
