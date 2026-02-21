from django.shortcuts import redirect
from django.urls import reverse


class CsrfExemptAPIMiddleware:
    """Exempte uniquement les endpoints d'auth JWT de la vérification CSRF.

    Les apps mobiles envoient le token JWT dans le header Authorization,
    elles n'ont pas de cookie de session donc pas besoin de CSRF sur ces routes.
    Les autres routes /api/ gardent la protection CSRF.
    """

    # Seuls les endpoints d'authentification sont exemptés
    CSRF_EXEMPT_PATHS = [
        '/api/v1/auth/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.CSRF_EXEMPT_PATHS):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)


class LoginRequiredMiddleware:
    """Bloque l’accès à tout le site sauf pour les pages publiques comme la connexion et l’inscription."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Chemins autorisés sans être connecté
        public_paths = [
            reverse('connexion'),
            reverse('inscription_utilisateur'),
        ]

        # Autorise aussi les fichiers statiques, médias, l'admin Django et l'API REST
        if (request.path.startswith('/static/') or
            request.path.startswith('/media/') or
            request.path.startswith('/api/') or
            request.path.startswith('/admin/')):
            return self.get_response(request)

        # Si pas connecté et pas sur une page publique → redirection
        if not request.user.is_authenticated and request.path not in public_paths:
            return redirect('connexion')

        return self.get_response(request)
