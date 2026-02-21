/**
 * Service Worker - TransportPro PWA
 *
 * Gère le cache et le mode hors ligne
 */

const CACHE_NAME = 'transportpro-v3';
const OFFLINE_URL = '/offline/';

// Ressources STATIQUES uniquement (pas de pages HTML avec CSRF tokens)
const PRECACHE_URLS = [
  '/static/css/table-styles.css',
  '/static/css/skeleton-loaders.css',
  '/static/css/modern-ux.css',
  '/static/js/modern-ux.js',
  '/static/js/skeleton-loaders.js',
  '/static/js/ajax-utils.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Installation...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Mise en cache des ressources statiques');
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => {
        console.log('[SW] Installation terminée');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('[SW] Erreur lors de l\'installation:', error);
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  console.log('[SW] Activation...');

  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => cacheName !== CACHE_NAME)
            .map(cacheName => {
              console.log('[SW] Suppression de l\'ancien cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('[SW] Activation terminée');
        return self.clients.claim();
      })
  );
});

// Interception des requêtes
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorer les requêtes non-GET
  if (request.method !== 'GET') {
    return;
  }

  // Ignorer les requêtes vers des domaines externes (sauf CDN)
  if (url.origin !== location.origin && !isCDN(url.hostname)) {
    return;
  }

  // Stratégie différente selon le type de ressource
  if (isStaticAsset(url.pathname)) {
    // Cache First pour les assets statiques
    event.respondWith(cacheFirst(request));
  } else if (isAPIRequest(url.pathname)) {
    // Network First pour les API
    event.respondWith(networkFirst(request));
  } else {
    // Network First pour les pages HTML (important pour les tokens CSRF)
    event.respondWith(networkFirstHTML(request));
  }
});

// === STRATÉGIES DE CACHE ===

/**
 * Cache First - Utilise le cache en priorité
 */
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);

  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache First erreur:', error);
    return new Response('Ressource non disponible', { status: 503 });
  }
}

/**
 * Network First - Essaie le réseau d'abord
 */
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[SW] Network First: fallback au cache');
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    return new Response(JSON.stringify({ error: 'Hors ligne' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Network First pour HTML - Ne cache PAS les pages HTML (tokens CSRF)
 * Affiche la page offline uniquement si le réseau est indisponible
 */
async function networkFirstHTML(request) {
  try {
    // Toujours essayer le réseau en premier pour les pages HTML
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network First HTML: hors ligne, affichage page offline');
    // Si hors ligne, afficher la page offline
    return createOfflineResponse();
  }
}

/**
 * Crée une réponse hors ligne
 */
function createOfflineResponse() {
  const html = `
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Hors ligne - TransportPro</title>
      <style>
        body {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          margin: 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }
        .container {
          text-align: center;
          padding: 2rem;
        }
        .icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        h1 {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }
        p {
          opacity: 0.9;
          margin-bottom: 1.5rem;
        }
        button {
          background: white;
          color: #667eea;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s;
        }
        button:hover {
          transform: scale(1.05);
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">&#128268;</div>
        <h1>Vous êtes hors ligne</h1>
        <p>Vérifiez votre connexion internet et réessayez.</p>
        <button onclick="location.reload()">Réessayer</button>
      </div>
    </body>
    </html>
  `;

  return new Response(html, {
    status: 503,
    headers: { 'Content-Type': 'text/html' }
  });
}

// === HELPERS ===

function isStaticAsset(pathname) {
  // Ne mettre en cache que les assets vraiment statiques (images, fonts, css)
  // PAS les fichiers JS applicatifs (ils changent lors des déploiements)
  return pathname.endsWith('.css') ||
         pathname.endsWith('.png') ||
         pathname.endsWith('.jpg') ||
         pathname.endsWith('.svg') ||
         pathname.endsWith('.woff2') ||
         pathname.endsWith('.ico');
}

function isAPIRequest(pathname) {
  return pathname.startsWith('/api/') ||
         pathname.includes('/ajax/');
}

function isCDN(hostname) {
  const cdnHosts = [
    'cdn.jsdelivr.net',
    'cdnjs.cloudflare.com',
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'kit.fontawesome.com'
  ];
  return cdnHosts.includes(hostname);
}

// === ÉVÉNEMENTS PUSH (pour futures notifications) ===

self.addEventListener('push', event => {
  if (!event.data) return;

  const data = event.data.json();

  const options = {
    body: data.body || 'Nouvelle notification',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/dashboard/'
    },
    actions: [
      { action: 'open', title: 'Ouvrir' },
      { action: 'close', title: 'Fermer' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'TransportPro', options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'close') return;

  const urlToOpen = event.notification.data?.url || '/dashboard/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        return clients.openWindow(urlToOpen);
      })
  );
});

// === MESSAGE HANDLER (pour vider le cache depuis le client) ===

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    console.log('[SW] Vidage du cache demandé');
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      );
    }).then(() => {
      console.log('[SW] Cache vidé avec succès');
      if (event.ports[0]) {
        event.ports[0].postMessage({ success: true });
      }
    });
  }

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('[SW] Service Worker TransportPro v2 chargé');
