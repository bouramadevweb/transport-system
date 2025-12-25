"""
Middleware pour capturer automatiquement les actions importantes et les enregistrer dans l'audit
"""

from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware pour enregistrer automatiquement certaines actions dans l'historique d'audit
    """

    def process_request(self, request):
        """Stocker la requête pour l'utiliser plus tard dans les vues"""
        request._audit_middleware_active = True
        return None

    def process_response(self, request, response):
        """Enregistrer les actions POST/PUT/DELETE dans l'audit si nécessaire"""

        # Ne traiter que les requêtes authentifiées
        if not request.user.is_authenticated:
            return response

        # Ne traiter que les méthodes de modification
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return response

        # Ignorer les requêtes AJAX et les uploads de fichiers
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return response

        # Ignorer certains chemins (admin, static, media, api)
        ignored_paths = ['/admin/', '/static/', '/media/', '/api/', '/audit/']
        if any(request.path.startswith(path) for path in ignored_paths):
            return response

        # Enregistrer uniquement si le statut est succès (2xx ou 3xx)
        if response.status_code >= 400:
            return response

        return response

    @staticmethod
    def get_client_ip(request):
        """Récupérer l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_user_agent(request):
        """Récupérer le user agent du client"""
        return request.META.get('HTTP_USER_AGENT', '')[:500]
