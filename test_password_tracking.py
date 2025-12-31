#!/usr/bin/env python
"""
Test du tracking de changement de mot de passe
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
django.setup()

from transport.models import AuditLog, Utilisateur

def test_password_change_tracking():
    """Test le tracking des changements de mot de passe"""

    print("\n" + "=" * 70)
    print("TEST DU TRACKING DE CHANGEMENT DE MOT DE PASSE")
    print("=" * 70)

    # Compter les logs d'audit avant le test
    password_change_count = AuditLog.objects.filter(action='CHANGE_PASSWORD').count()

    print(f"\n📊 État initial:")
    print(f"   - Logs CHANGE_PASSWORD: {password_change_count}")

    # Vérifier les derniers logs CHANGE_PASSWORD
    latest_password_changes = AuditLog.objects.filter(action='CHANGE_PASSWORD').order_by('-timestamp')[:5]

    print(f"\n📝 Derniers logs CHANGE_PASSWORD ({latest_password_changes.count()}):")
    for log in latest_password_changes:
        print(f"\n   - {log.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"     Utilisateur: {log.utilisateur.email if log.utilisateur else 'N/A'}")
        print(f"     IP: {log.ip_address or 'N/A'}")
        print(f"     User Agent: {log.user_agent[:60] if log.user_agent else 'N/A'}...")

    # Vérifier si le code est bien en place
    print("\n" + "=" * 70)
    print("VÉRIFICATION DU CODE")
    print("=" * 70)

    import inspect
    from transport.views.auth_views import user_settings

    # Vérifier user_settings
    source_settings = inspect.getsource(user_settings)
    has_password_tracking = 'AuditLog.log_action' in source_settings and 'CHANGE_PASSWORD' in source_settings

    print(f"\n✓ Tracking CHANGE_PASSWORD dans user_settings: {'✅ OUI' if has_password_tracking else '❌ NON'}")

    # Vérifier que l'action existe dans le modèle
    from transport.models.audit import AuditLog as AuditModel
    action_choices = dict(AuditModel.ACTION_CHOICES)
    has_action = 'CHANGE_PASSWORD' in action_choices

    print(f"✓ Action CHANGE_PASSWORD définie dans le modèle: {'✅ OUI' if has_action else '❌ NON'}")
    if has_action:
        print(f"  Label: {action_choices['CHANGE_PASSWORD']}")

    # Statistiques globales
    print("\n" + "=" * 70)
    print("STATISTIQUES GLOBALES - SÉCURITÉ")
    print("=" * 70)

    total_login = AuditLog.objects.filter(action='LOGIN').count()
    total_logout = AuditLog.objects.filter(action='LOGOUT').count()
    total_password_change = AuditLog.objects.filter(action='CHANGE_PASSWORD').count()

    print(f"\n📊 Total des logs de sécurité:")
    print(f"   - LOGIN: {total_login}")
    print(f"   - LOGOUT: {total_logout}")
    print(f"   - CHANGE_PASSWORD: {total_password_change}")

    # Vérifier les utilisateurs qui ont changé leur mot de passe
    users_who_changed = AuditLog.objects.filter(
        action='CHANGE_PASSWORD'
    ).values('utilisateur__email').distinct()

    print(f"\n👥 Utilisateurs ayant changé leur mot de passe: {users_who_changed.count()}")
    for user in users_who_changed[:10]:
        email = user['utilisateur__email']
        count = AuditLog.objects.filter(
            action='CHANGE_PASSWORD',
            utilisateur__email=email
        ).count()
        print(f"   - {email}: {count} changement(s)")

    # Instructions pour test manuel
    print("\n" + "=" * 70)
    print("INSTRUCTIONS POUR TEST MANUEL")
    print("=" * 70)
    print("\n1. Ouvrez votre navigateur et allez sur http://127.0.0.1:8000")
    print("2. Connectez-vous avec vos identifiants")
    print("3. Allez sur 'Paramètres' ou http://127.0.0.1:8000/user/settings/")
    print("4. Changez votre mot de passe:")
    print("   - Entrez votre ancien mot de passe")
    print("   - Entrez votre nouveau mot de passe (2 fois)")
    print("   - Cliquez sur 'Changer le mot de passe'")
    print("5. Allez sur http://127.0.0.1:8000/audit/logs/")
    print("6. Filtrez par action 'Changement de mot de passe'")
    print("7. Vous devriez voir votre changement avec:")
    print("   - Badge orange avec icône de clé")
    print("   - Votre email")
    print("   - Timestamp du changement")
    print("   - Votre adresse IP")

    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
    print("=" * 70)

    print("\n💡 Note de sécurité:")
    print("   Le nouveau mot de passe n'est PAS enregistré dans l'audit.")
    print("   Seul l'événement 'changement de mot de passe' est tracé.")
    print("   C'est une bonne pratique de sécurité!")

if __name__ == '__main__':
    test_password_change_tracking()
