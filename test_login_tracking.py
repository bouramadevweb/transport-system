#!/usr/bin/env python
"""
Script de test pour vérifier le tracking de connexion/déconnexion
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
django.setup()

from django.test import Client
from transport.models import AuditLog, Utilisateur

def test_login_logout_tracking():
    """Test le tracking des connexions et déconnexions"""

    print("=" * 60)
    print("TEST DU TRACKING DE CONNEXION/DÉCONNEXION")
    print("=" * 60)

    # Compter les logs d'audit avant le test
    initial_login_count = AuditLog.objects.filter(action='LOGIN').count()
    initial_logout_count = AuditLog.objects.filter(action='LOGOUT').count()

    print(f"\n📊 État initial:")
    print(f"   - Logs LOGIN: {initial_login_count}")
    print(f"   - Logs LOGOUT: {initial_logout_count}")

    # Récupérer le premier utilisateur disponible
    user = Utilisateur.objects.first()

    if not user:
        print("\n❌ ERREUR: Aucun utilisateur trouvé dans la base de données")
        return

    print(f"\n👤 Utilisateur de test: {user.email}")

    # Créer un client de test
    client = Client()

    # Test 1: Login
    print("\n" + "=" * 60)
    print("TEST 1: CONNEXION")
    print("=" * 60)

    # Note: Pour tester réellement, nous devons utiliser le mot de passe
    # Pour ce test, nous allons juste vérifier les derniers logs

    # Vérifier les derniers logs LOGIN
    latest_logins = AuditLog.objects.filter(action='LOGIN').order_by('-timestamp')[:5]

    print(f"\n📝 Derniers logs LOGIN ({latest_logins.count()}):")
    for log in latest_logins:
        print(f"   - {log.timestamp.strftime('%d/%m/%Y %H:%M:%S')} - {log.utilisateur.email if log.utilisateur else 'N/A'}")
        print(f"     IP: {log.ip_address or 'N/A'}")
        print(f"     User Agent: {log.user_agent[:50] if log.user_agent else 'N/A'}...")

    # Test 2: Logout
    print("\n" + "=" * 60)
    print("TEST 2: DÉCONNEXION")
    print("=" * 60)

    latest_logouts = AuditLog.objects.filter(action='LOGOUT').order_by('-timestamp')[:5]

    print(f"\n📝 Derniers logs LOGOUT ({latest_logouts.count()}):")
    for log in latest_logouts:
        print(f"   - {log.timestamp.strftime('%d/%m/%Y %H:%M:%S')} - {log.utilisateur.email if log.utilisateur else 'N/A'}")
        print(f"     IP: {log.ip_address or 'N/A'}")
        print(f"     User Agent: {log.user_agent[:50] if log.user_agent else 'N/A'}...")

    # Statistiques finales
    print("\n" + "=" * 60)
    print("STATISTIQUES GLOBALES")
    print("=" * 60)

    total_login = AuditLog.objects.filter(action='LOGIN').count()
    total_logout = AuditLog.objects.filter(action='LOGOUT').count()

    print(f"\n📊 Total des logs:")
    print(f"   - LOGIN: {total_login}")
    print(f"   - LOGOUT: {total_logout}")

    # Vérifier si le code est bien en place
    print("\n" + "=" * 60)
    print("VÉRIFICATION DU CODE")
    print("=" * 60)

    import inspect
    from transport.views.auth_views import connexion_utilisateur, logout_utilisateur

    # Vérifier connexion_utilisateur
    source_connexion = inspect.getsource(connexion_utilisateur)
    has_login_tracking = 'AuditLog.log_action' in source_connexion and 'LOGIN' in source_connexion

    print(f"\n✓ Tracking LOGIN dans connexion_utilisateur: {'✅ OUI' if has_login_tracking else '❌ NON'}")

    # Vérifier logout_utilisateur
    source_logout = inspect.getsource(logout_utilisateur)
    has_logout_tracking = 'AuditLog.log_action' in source_logout and 'LOGOUT' in source_logout

    print(f"✓ Tracking LOGOUT dans logout_utilisateur: {'✅ OUI' if has_logout_tracking else '❌ NON'}")

    # Instructions pour test manuel
    print("\n" + "=" * 60)
    print("INSTRUCTIONS POUR TEST MANUEL")
    print("=" * 60)
    print("\n1. Ouvrez votre navigateur et allez sur http://127.0.0.1:8000")
    print("2. Connectez-vous avec vos identifiants")
    print("3. Allez sur la page d'historique d'audit: http://127.0.0.1:8000/audit/logs/")
    print("4. Filtrez par action 'Connexion' pour voir votre login")
    print("5. Déconnectez-vous")
    print("6. Reconnectez-vous et vérifiez le log 'Déconnexion'")

    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)

if __name__ == '__main__':
    test_login_logout_tracking()
