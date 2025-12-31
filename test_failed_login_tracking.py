#!/usr/bin/env python
"""
Test du tracking des tentatives de connexion échouées
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
django.setup()

from django.test import Client
from transport.models import AuditLog, Utilisateur

def test_failed_login_tracking():
    """Test le tracking des tentatives de connexion échouées"""

    print("\n" + "=" * 80)
    print("TEST DU TRACKING DES TENTATIVES DE CONNEXION ÉCHOUÉES")
    print("=" * 80)

    # Compter les logs avant le test
    failed_login_count_before = AuditLog.objects.filter(action='FAILED_LOGIN').count()

    print(f"\n📊 État initial:")
    print(f"   - Logs FAILED_LOGIN: {failed_login_count_before}")

    # Récupérer un utilisateur existant
    existing_user = Utilisateur.objects.filter(is_active=True).first()

    if not existing_user:
        print("\n❌ Erreur: Aucun utilisateur actif trouvé")
        return

    print(f"\n👤 Utilisateur de test: {existing_user.email}")

    # Créer un client de test
    client = Client()

    # Test 1: Tentative avec email existant mais mauvais mot de passe
    print("\n" + "=" * 80)
    print("TEST 1: Tentative avec email EXISTANT et mauvais mot de passe")
    print("=" * 80)

    response = client.post('/connexion/', {
        'email': existing_user.email,
        'password': 'wrong_password_12345'
    })

    failed_login_count_after_test1 = AuditLog.objects.filter(action='FAILED_LOGIN').count()
    new_logs_test1 = failed_login_count_after_test1 - failed_login_count_before

    print(f"✓ Nouveaux logs FAILED_LOGIN: {new_logs_test1}")

    if new_logs_test1 > 0:
        print("✅ SUCCÈS: Un log a été créé pour cette tentative échouée")
        latest_log = AuditLog.objects.filter(action='FAILED_LOGIN').order_by('-timestamp').first()
        print(f"\n   Détails du log:")
        print(f"   - Utilisateur cible: {latest_log.utilisateur.email if latest_log.utilisateur else 'N/A'}")
        print(f"   - Object repr: {latest_log.object_repr}")
        print(f"   - IP: {latest_log.ip_address or 'N/A'}")
    else:
        print("❌ ÉCHEC: Aucun log créé")

    # Test 2: Tentative avec email inexistant
    print("\n" + "=" * 80)
    print("TEST 2: Tentative avec email INEXISTANT")
    print("=" * 80)

    fake_email = "hacker123@fake-domain.com"
    response = client.post('/connexion/', {
        'email': fake_email,
        'password': 'any_password'
    })

    failed_login_count_after_test2 = AuditLog.objects.filter(action='FAILED_LOGIN').count()
    new_logs_test2 = failed_login_count_after_test2 - failed_login_count_after_test1

    print(f"✓ Nouveaux logs FAILED_LOGIN: {new_logs_test2}")

    if new_logs_test2 > 0:
        print("✅ SUCCÈS: Un log a été créé pour cette tentative avec email inexistant")
        latest_log = AuditLog.objects.filter(action='FAILED_LOGIN').order_by('-timestamp').first()
        print(f"\n   Détails du log:")
        print(f"   - Utilisateur cible: {latest_log.utilisateur.email if latest_log.utilisateur else 'Aucun (email inexistant)'}")
        print(f"   - Object repr: {latest_log.object_repr}")
        print(f"   - IP: {latest_log.ip_address or 'N/A'}")
    else:
        print("❌ ÉCHEC: Aucun log créé")

    # Vérifier le code
    print("\n" + "=" * 80)
    print("VÉRIFICATION DU CODE")
    print("=" * 80)

    import inspect
    from transport.views.auth_views import connexion_utilisateur

    source_connexion = inspect.getsource(connexion_utilisateur)
    has_failed_login = 'FAILED_LOGIN' in source_connexion

    print(f"✓ Tracking FAILED_LOGIN dans connexion_utilisateur: {'✅ OUI' if has_failed_login else '❌ NON'}")

    # Vérifier que l'action existe dans le modèle
    from transport.models.audit import AuditLog as AuditModel
    action_choices = dict(AuditModel.ACTION_CHOICES)
    has_action = 'FAILED_LOGIN' in action_choices

    print(f"✓ Action FAILED_LOGIN définie dans le modèle: {'✅ OUI' if has_action else '❌ NON'}")
    if has_action:
        print(f"  Label: {action_choices['FAILED_LOGIN']}")

    # Statistiques globales
    print("\n" + "=" * 80)
    print("STATISTIQUES - TENTATIVES DE CONNEXION")
    print("=" * 80)

    total_login = AuditLog.objects.filter(action='LOGIN').count()
    total_failed = AuditLog.objects.filter(action='FAILED_LOGIN').count()

    if total_login + total_failed > 0:
        success_rate = (total_login / (total_login + total_failed)) * 100
    else:
        success_rate = 0

    print(f"\n   Connexions RÉUSSIES:    {total_login:>6}")
    print(f"   Connexions ÉCHOUÉES:    {total_failed:>6}")
    print(f"   {'-' * 35}")
    print(f"   TOTAL:                  {total_login + total_failed:>6}")
    print(f"   Taux de réussite:       {success_rate:>6.1f}%")

    # Afficher les dernières tentatives échouées
    print("\n" + "=" * 80)
    print("DERNIÈRES TENTATIVES ÉCHOUÉES (Top 10)")
    print("=" * 80)

    latest_failed = AuditLog.objects.filter(action='FAILED_LOGIN').order_by('-timestamp')[:10]

    if latest_failed.count() == 0:
        print("   Aucune tentative échouée enregistrée")
    else:
        for i, log in enumerate(latest_failed, 1):
            print(f"\n   {i}. {log.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"      Email tenté: {log.object_repr}")
            print(f"      Compte cible: {log.utilisateur.email if log.utilisateur else '❌ Inexistant'}")
            print(f"      IP: {log.ip_address or 'N/A'}")

    # Analyse de sécurité
    print("\n" + "=" * 80)
    print("ANALYSE DE SÉCURITÉ")
    print("=" * 80)

    # Vérifier les tentatives multiples depuis la même IP
    from django.db.models import Count
    suspicious_ips = AuditLog.objects.filter(
        action='FAILED_LOGIN'
    ).values('ip_address').annotate(
        attempts=Count('pk_audit')
    ).filter(attempts__gte=3).order_by('-attempts')

    if suspicious_ips.count() > 0:
        print(f"\n⚠️  IPs avec multiples tentatives échouées (≥3):")
        for ip_data in suspicious_ips:
            ip = ip_data['ip_address'] or 'Unknown'
            attempts = ip_data['attempts']
            print(f"   - {ip}: {attempts} tentatives")
    else:
        print("\n✅ Aucune IP suspecte détectée (< 3 tentatives)")

    # Vérifier les comptes ciblés
    targeted_accounts = AuditLog.objects.filter(
        action='FAILED_LOGIN',
        utilisateur__isnull=False
    ).values('utilisateur__email').annotate(
        attempts=Count('pk_audit')
    ).filter(attempts__gte=2).order_by('-attempts')

    if targeted_accounts.count() > 0:
        print(f"\n⚠️  Comptes avec multiples tentatives échouées (≥2):")
        for account in targeted_accounts:
            email = account['utilisateur__email']
            attempts = account['attempts']
            print(f"   - {email}: {attempts} tentatives échouées")
    else:
        print("\n✅ Aucun compte ciblé détecté")

    # Instructions
    print("\n" + "=" * 80)
    print("COMMENT TESTER MANUELLEMENT")
    print("=" * 80)
    print("\n1. Ouvrez http://127.0.0.1:8000/connexion/")
    print("2. Essayez de vous connecter avec:")
    print("   - Un email existant et un MAUVAIS mot de passe")
    print("   - Un email qui N'EXISTE PAS")
    print("3. Allez sur http://127.0.0.1:8000/audit/logs/")
    print("4. Filtrez par action 'Tentative de connexion échouée'")
    print("5. Vous devriez voir:")
    print("   - 🔴 Badge rouge avec icône triangle d'avertissement")
    print("   - L'email utilisé dans la tentative")
    print("   - Votre IP")
    print("   - Timestamp de la tentative")

    print("\n" + "=" * 80)
    print("💡 UTILITÉ POUR LA SÉCURITÉ")
    print("=" * 80)
    print("✓ Détection d'attaques par force brute")
    print("✓ Identification des comptes ciblés")
    print("✓ Traçage des IPs suspectes")
    print("✓ Analyse des tentatives avec emails inexistants")
    print("✓ Aide à la mise en place de mesures de protection (rate limiting, etc.)")

    print("\n" + "=" * 80)
    print("✅ TEST TERMINÉ")
    print("=" * 80)

if __name__ == '__main__':
    test_failed_login_tracking()
