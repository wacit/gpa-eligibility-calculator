// GPA & Athletic Eligibility Calculator — Service Worker
// Bump CACHE_VERSION whenever shipping a new app build so users get the update.
const CACHE_VERSION = 'gpa-v2026-07-05-2';
const CORE = [
  './',
  './index.html',
  './athletics.json',
  './manifest.webmanifest',
  './favicon.ico',
  './favicon-16.png',
  './favicon-32.png',
  './favicon-48.png',
  './apple-touch-icon.png',
  './icon-512.png',
  './gpa_template.csv',
  './gpa_example_full.csv'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_VERSION).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

// Network-first for navigations and the app shell so they always get the latest when online;
// cache-first for everything else so the app loads instantly + offline.
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Don't try to cache cross-origin API calls (Scorecard, BMC, etc.) — let the browser handle them.
  if (url.origin !== location.origin) return;

  const isShell = req.mode === 'navigate' ||
                  url.pathname.endsWith('/') ||
                  url.pathname.endsWith('/index.html');

  if (isShell) {
    // Network-first with cache fallback for the page shell.
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE_VERSION).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match(req).then((m) => m || caches.match('./index.html')))
    );
    return;
  }

  // Cache-first for static assets.
  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((res) => {
      // Only cache successful, basic responses.
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone();
        caches.open(CACHE_VERSION).then((c) => c.put(req, copy)).catch(() => {});
      }
      return res;
    }))
  );
});
