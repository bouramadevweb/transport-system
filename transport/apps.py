from django.apps import AppConfig


class TransportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transport'

    def ready(self):
        """Importer les signaux au démarrage de l'application"""
        import transport.signals  # noqa
