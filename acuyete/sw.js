// Состояние, которое пропадает без сети, — не предмет, а страница. Поэтому весь
// магазин целиком лежит в кэше: после первого захода он открывается в самолёте.
//
// Стратегия: сеть первой, кэш как страховка. Так витрину можно править и
// выкатывать, не заставляя людей вычищать данные приложения; при этом любой
// сбой сети незаметен.

const CACHE = "acuyete-v1";
const SHELL = [
  "./",
  "./index.html",
  "./app.css",
  "./app.js",
  "./object.js",
  "./data.js",
  "./manifest.webmanifest",
  "./icons/mark.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;

  e.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      })
      .catch(() =>
        caches.match(req).then((hit) => hit || caches.match("./index.html")),
      ),
  );
});
