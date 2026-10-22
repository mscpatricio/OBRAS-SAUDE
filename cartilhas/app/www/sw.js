/* Service worker: deixa o app disponível sem internet (cache de todos os arquivos). */
const CACHE = 'dentista-tea-v1';
const FILES = [
  './', './index.html', './app.css', './app.js', './data.js', './manifest.webmanifest',
  './shared/ill.js',
  './shared/fonts/Baloo2-800.ttf', './shared/fonts/Baloo2-600.ttf',
  './shared/fonts/ComicNeue-400.ttf', './shared/fonts/ComicNeue-700.ttf',
  './shared/fonts/Nunito-400.ttf', './shared/fonts/Nunito-700.ttf', './shared/fonts/Nunito-800.ttf',
  './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png', './icons/apple-touch-icon.png',
];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then((hit) => hit || fetch(e.request).then((res) => {
    const copy = res.clone();
    caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
    return res;
  }).catch(() => caches.match('./index.html'))));
});
