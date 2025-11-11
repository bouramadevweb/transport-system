from django.shortcuts import redirect
from django.urls import reverse

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

        # Autorise aussi les fichiers statiques et médias
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Si pas connecté et pas sur une page publique → redirection
        if not request.user.is_authenticated and request.path not in public_paths:
            return redirect('connexion')

        return self.get_response(request)
