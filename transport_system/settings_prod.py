"""
Configuration Django pour la PRODUCTION
========================================

Ce fichier hérite de settings.py et ajoute les paramètres de sécurité
nécessaires pour un déploiement en production.

UTILISATION:
-----------
Pour utiliser ces paramètres en production, démarrez Django avec:
    python manage.py runserver --settings=transport_system.settings_prod

Ou définissez la variable d'environnement:
    export DJANGO_SETTINGS_MODULE=transport_system.settings_prod

VARIABLES D'ENVIRONNEMENT REQUISES:
----------------------------------
- SECRET_KEY: Clé secrète Django (minimum 50 caractères aléatoires)
- ALLOWED_HOSTS: Liste des domaines autorisés séparés par des virgules
- DATABASE_URL (optionnel): URL de connexion à la base de données

Exemple:
    export SECRET_KEY="votre-cle-secrete-tres-longue-et-aleatoire-ici-123456789"
    export ALLOWED_HOSTS="example.com,www.example.com"
"""

import os
from .settings import *

# ============================================================================
# SÉCURITÉ
# ============================================================================

# SECRET_KEY doit être fournie via variable d'environnement
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "❌ SECRET_KEY manquante!\n"
        "Générez une clé sécurisée avec:\n"
        "  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'\n"
        "Puis définissez: export SECRET_KEY='votre-cle-generee'"
    )

# DEBUG doit être désactivé en production
DEBUG = False

# ALLOWED_HOSTS doit être configuré
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError(
        "❌ ALLOWED_HOSTS manquant!\n"
        "Définissez les domaines autorisés:\n"
        "  export ALLOWED_HOSTS='votredomaine.com,www.votredomaine.com'"
    )

# ============================================================================
# COOKIES ET SESSIONS SÉCURISÉS (HTTPS)
# ============================================================================

# Les cookies de session ne seront envoyés que via HTTPS
SESSION_COOKIE_SECURE = True

# Les cookies CSRF ne seront envoyés que via HTTPS
CSRF_COOKIE_SECURE = True

# Les cookies de session ne seront pas accessibles via JavaScript
SESSION_COOKIE_HTTPONLY = True

# Les cookies CSRF ne seront pas accessibles via JavaScript
CSRF_COOKIE_HTTPONLY = True

# Durée de vie de la session: 2 semaines
SESSION_COOKIE_AGE = 1209600  # 14 jours en secondes

# ============================================================================
# HTTPS ET SÉCURITÉ SSL/TLS
# ============================================================================

# Rediriger automatiquement HTTP vers HTTPS
SECURE_SSL_REDIRECT = True

# HTTP Strict Transport Security (HSTS)
# Force les navigateurs à utiliser HTTPS pendant 1 an
SECURE_HSTS_SECONDS = 31536000  # 1 an

# Inclure tous les sous-domaines dans HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Pré-charger HSTS dans les navigateurs
SECURE_HSTS_PRELOAD = True

# ============================================================================
# PROTECTION SUPPLÉMENTAIRE
# ============================================================================

# Empêcher l'affichage du site dans une iframe (protection contre clickjacking)
X_FRAME_OPTIONS = 'DENY'

# Forcer le navigateur à respecter le Content-Type déclaré
SECURE_CONTENT_TYPE_NOSNIFF = True

# Activer la protection XSS du navigateur
SECURE_BROWSER_XSS_FILTER = True

# Politique de référent: n'envoyer que l'origine pour les requêtes HTTPS
SECURE_REFERRER_POLICY = 'same-origin'

# ============================================================================
# ADMINS ET GESTIONNAIRES
# ============================================================================

# Recevoir des emails en cas d'erreur 500
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@example.com')),
]

MANAGERS = ADMINS

# ============================================================================
# LOGGING PRODUCTION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_prod.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'transport': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ============================================================================
# BASE DE DONNÉES (optionnel - si vous utilisez DATABASE_URL)
# ============================================================================

# Exemple d'utilisation avec dj-database-url pour PostgreSQL:
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ.get('DATABASE_URL'),
#         conn_max_age=600
#     )
# }

# ============================================================================
# FICHIERS STATIQUES ET MÉDIAS
# ============================================================================

# En production, utilisez WhiteNoise ou servez les fichiers statiques via Nginx
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Sécuriser les uploads
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# ============================================================================
# EMAIL (à configurer selon votre fournisseur)
# ============================================================================

# Exemple avec SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

print("✅ Configuration PRODUCTION chargée avec succès")
print(f"   - DEBUG: {DEBUG}")
print(f"   - ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   - SECURE_SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"   - SESSION_COOKIE_SECURE: {SESSION_COOKIE_SECURE}")
