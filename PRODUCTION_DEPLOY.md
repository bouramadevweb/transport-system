# 🚀 Guide de Déploiement en Production

Ce guide explique comment déployer le système de gestion de transport de manière sécurisée en production.

## 📋 Pré-requis

- Python 3.10+
- PostgreSQL (recommandé) ou MySQL
- Nginx ou Apache
- Serveur Linux (Ubuntu/Debian recommandé)
- Certificat SSL/TLS (Let's Encrypt gratuit)

## ⚙️ Configuration de Sécurité

### 1. Générer une SECRET_KEY sécurisée

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copiez la clé générée et configurez-la:

```bash
export SECRET_KEY="votre-cle-generee-ici"
```

### 2. Configurer ALLOWED_HOSTS

```bash
export ALLOWED_HOSTS="votredomaine.com,www.votredomaine.com,votre-ip-serveur"
```

### 3. Utiliser les paramètres de production

```bash
export DJANGO_SETTINGS_MODULE=transport_system.settings_prod
```

Ou dans votre commande:

```bash
python manage.py runserver --settings=transport_system.settings_prod
```

## 🔒 Paramètres de Sécurité Activés

Le fichier `settings_prod.py` active automatiquement:

### ✅ Protection HTTPS
- `SECURE_SSL_REDIRECT = True` - Redirection HTTP → HTTPS
- `SESSION_COOKIE_SECURE = True` - Cookies uniquement via HTTPS
- `CSRF_COOKIE_SECURE = True` - Protection CSRF via HTTPS

### ✅ HTTP Strict Transport Security (HSTS)
- `SECURE_HSTS_SECONDS = 31536000` - Force HTTPS pendant 1 an
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` - Inclut les sous-domaines
- `SECURE_HSTS_PRELOAD = True` - Pré-chargement dans les navigateurs

### ✅ Protections additionnelles
- `X_FRAME_OPTIONS = 'DENY'` - Anti-clickjacking
- `SECURE_CONTENT_TYPE_NOSNIFF = True` - Protection type MIME
- `SECURE_BROWSER_XSS_FILTER = True` - Filtre XSS du navigateur
- `DEBUG = False` - Désactive le mode debug

## 📦 Installation Production

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd transport-system
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # Pour PostgreSQL
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
nano .env  # Éditez avec vos valeurs
```

Ou exportez directement:

```bash
export SECRET_KEY="votre-cle-secrete"
export ALLOWED_HOSTS="votredomaine.com"
export DJANGO_SETTINGS_MODULE=transport_system.settings_prod
```

### 5. Préparer la base de données

```bash
python manage.py migrate --settings=transport_system.settings_prod
python manage.py collectstatic --settings=transport_system.settings_prod
python manage.py createsuperuser --settings=transport_system.settings_prod
```

### 6. Tester la configuration

```bash
python manage.py check --deploy --settings=transport_system.settings_prod
```

Cette commande affiche les éventuels problèmes de sécurité.

## 🌐 Déploiement avec Gunicorn

### 1. Créer un fichier de service systemd

```bash
sudo nano /etc/systemd/system/transport.service
```

Contenu:

```ini
[Unit]
Description=Transport System Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/transport-system
Environment="PATH=/path/to/transport-system/venv/bin"
Environment="SECRET_KEY=votre-cle-secrete"
Environment="ALLOWED_HOSTS=votredomaine.com"
Environment="DJANGO_SETTINGS_MODULE=transport_system.settings_prod"
ExecStart=/path/to/transport-system/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          transport_system.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Activer et démarrer le service

```bash
sudo systemctl enable transport
sudo systemctl start transport
sudo systemctl status transport
```

## 🔧 Configuration Nginx

```nginx
server {
    listen 80;
    server_name votredomaine.com www.votredomaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votredomaine.com www.votredomaine.com;

    ssl_certificate /etc/letsencrypt/live/votredomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votredomaine.com/privkey.pem;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/transport-system/staticfiles/;
    }

    location /media/ {
        alias /path/to/transport-system/media/;
    }

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📅 Tâches Automatisées (Cron)

### Vérifier les missions en retard quotidiennement

```bash
crontab -e
```

Ajoutez:

```cron
# Vérifier les missions en retard tous les jours à 9h
0 9 * * * cd /path/to/transport-system && /path/to/venv/bin/python manage.py check_missions_retard --settings=transport_system.settings_prod
```

## 🔍 Monitoring et Logs

Les logs sont enregistrés dans `logs/django_prod.log`.

Surveiller les erreurs:

```bash
tail -f logs/django_prod.log
```

## 📊 Checklist de Sécurité

- [ ] SECRET_KEY générée avec 50+ caractères aléatoires
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configuré correctement
- [ ] HTTPS configuré avec certificat SSL valide
- [ ] Tous les cookies sécurisés (SECURE, HTTPONLY)
- [ ] HSTS activé
- [ ] Fichiers statiques servis via Nginx/WhiteNoise
- [ ] Base de données sécurisée (mot de passe fort)
- [ ] Firewall configuré (ufw/iptables)
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring configuré (logs, erreurs 500)

## 🛡️ Certificat SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votredomaine.com -d www.votredomaine.com
sudo certbot renew --dry-run  # Tester le renouvellement automatique
```

## 🔄 Mise à jour du code

```bash
cd /path/to/transport-system
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=transport_system.settings_prod
python manage.py collectstatic --noinput --settings=transport_system.settings_prod
sudo systemctl restart transport
```

## ⚠️ Problèmes Courants

### Erreur "SECRET_KEY manquante"
Vérifiez que la variable d'environnement est définie:
```bash
echo $SECRET_KEY
```

### Erreur "ALLOWED_HOSTS manquant"
Configurez les domaines autorisés:
```bash
export ALLOWED_HOSTS="votredomaine.com,www.votredomaine.com"
```

### Erreur 500
Consultez les logs:
```bash
tail -100 logs/django_prod.log
```

## 📞 Support

Pour toute question, consultez la documentation Django:
https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
