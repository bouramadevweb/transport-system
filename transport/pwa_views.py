"""
Vues pour les fichiers PWA (Progressive Web App)

Ces vues servent le manifest.json et le service worker depuis la racine du site
"""

from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os


@cache_control(max_age=86400)  # Cache 24h
def manifest(request):
    """Sert le fichier manifest.json pour la PWA"""
    manifest_path = os.path.join(settings.BASE_DIR, 'transport', 'static', 'manifest.json')

    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return HttpResponse(content, content_type='application/manifest+json')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def service_worker(request):
    """Sert le service worker depuis la racine du site"""
    sw_path = os.path.join(settings.BASE_DIR, 'transport', 'static', 'sw.js')

    with open(sw_path, 'r', encoding='utf-8') as f:
        content = f.read()

    response = HttpResponse(content, content_type='application/javascript')
    # Le service worker doit avoir un scope approprié
    response['Service-Worker-Allowed'] = '/'
    return response


def offline(request):
    """Page hors ligne pour la PWA"""
    html = """
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
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
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
                color: #2563eb;
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
    """
    return HttpResponse(html, content_type='text/html')


def clear_cache(request):
    """Page pour vider le cache du Service Worker et rediriger vers la connexion"""
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Réinitialisation - TransportPro</title>
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
            }
            .spinner {
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255,255,255,0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1.5rem;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            h1 {
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }
            p {
                opacity: 0.9;
            }
            .success {
                color: #4ade80;
            }
            .error {
                color: #f87171;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="spinner" id="spinner"></div>
            <h1 id="status">Réinitialisation en cours...</h1>
            <p id="message">Vidage du cache et du Service Worker</p>
        </div>
        <script>
            async function clearAll() {
                const status = document.getElementById('status');
                const message = document.getElementById('message');
                const spinner = document.getElementById('spinner');

                try {
                    // 1. Vider tous les caches
                    if ('caches' in window) {
                        const cacheNames = await caches.keys();
                        await Promise.all(cacheNames.map(name => caches.delete(name)));
                        console.log('Caches vidés:', cacheNames);
                    }

                    // 2. Désenregistrer tous les Service Workers
                    if ('serviceWorker' in navigator) {
                        const registrations = await navigator.serviceWorker.getRegistrations();
                        await Promise.all(registrations.map(reg => reg.unregister()));
                        console.log('Service Workers désenregistrés:', registrations.length);
                    }

                    // 3. Succès
                    spinner.style.display = 'none';
                    status.textContent = 'Réinitialisation réussie!';
                    status.classList.add('success');
                    message.textContent = 'Redirection vers la page de connexion...';

                    // 4. Rediriger vers la connexion après 2 secondes
                    setTimeout(() => {
                        window.location.href = '/connexion/';
                    }, 2000);

                } catch (error) {
                    console.error('Erreur:', error);
                    spinner.style.display = 'none';
                    status.textContent = 'Erreur lors de la réinitialisation';
                    status.classList.add('error');
                    message.innerHTML = error.message + '<br><br><a href="/connexion/" style="color:white">Cliquez ici pour continuer</a>';
                }
            }

            // Lancer la réinitialisation
            clearAll();
        </script>
    </body>
    </html>
    """
    response = HttpResponse(html, content_type='text/html')
    # Empêcher le cache de cette page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
