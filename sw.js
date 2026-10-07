// 離線閱讀：網頁與資料「網路優先、離線用快取」；簡報圖片看過一次後即可離線
const CACHE = 'audit-v1';
const CORE = [
  './', 'index.html', 'data.js', 'manifest.webmanifest', 'favicon.ico',
  'icons/favicon-32.png', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  const put = res => {
    if (res.status === 200) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  };
  const isSlide = new URL(req.url).pathname.endsWith('.webp');
  e.respondWith(isSlide
    ? caches.match(req).then(hit => hit || fetch(req).then(put))
    : fetch(req).then(put).catch(() => caches.match(req, {ignoreSearch: true}).then(hit => hit || caches.match('index.html'))));
});
