// Offline support for Digital Beaver Apps.
// The page and icons come from the cache first; releases.json from the network first,
// so a new version shows up as soon as you're online. APK downloads are never cached.
const CACHE = "dba-v8";
const SHELL = [
  "./",
  "index.html",
  "releases.json",
  "manifest.webmanifest",
  "icons/icon.svg",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/until.svg",
  "icons/hdstatus.svg",
  "icons/futureme.svg",
  "icons/folio.svg",
  "icons/passwordvault.svg",
  "icons/mylibrary.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return; // GitHub downloads, fonts: straight to the network

  const fresh = req.mode === "navigate" || url.pathname.endsWith("releases.json");
  if (fresh) {
    // Network first, cached copy when offline.
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match("index.html"))),
    );
    return;
  }
  // Cache first for icons and the rest of the shell.
  event.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy));
      return res;
    })),
  );
});
