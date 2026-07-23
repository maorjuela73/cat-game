var GHPATH = '/cat-game';
var APP_PREFIX = 'michislot_';
var VERSION = 'version_01';

var URLS = [
  GHPATH + '/',
  GHPATH + '/index.html',
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(VERSION).then(function (cache) {
      return cache.addAll(URLS);
    })
  );
});

self.addEventListener('fetch', function (e) {
  e.respondWith(
    caches.match(e.request).then(function (response) {
      return response || fetch(e.request);
    })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keyList) {
      return Promise.all(
        keyList.map(function (key) {
          if (key !== VERSION) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});
