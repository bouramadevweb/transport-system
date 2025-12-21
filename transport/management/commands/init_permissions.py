"""
Commande pour initialiser les rôles et permissions du système
Usage: python manage.py init_permissions
"""
from django.core.management.base import BaseCommand
from transport.permissions import init_roles_and_permissions


class Command(BaseCommand):
    help = 'Initialise les groupes, rôles et permissions du système'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🔐 INITIALISATION DES RÔLES ET PERMISSIONS\n'))
        self.stdout.write('=' * 60)

        try:
            init_roles_and_permissions()
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('\n✅ Initialisation réussie!\n'))

            self.stdout.write('\n📋 Rôles disponibles:')
            self.stdout.write('  • Administrateur - Accès complet')
            self.stdout.write('  • Gestionnaire - Gestion opérationnelle')
            self.stdout.write('  • Comptable - Gestion financière')
            self.stdout.write('  • Chauffeur - Consultation personnelle')
            self.stdout.write('  • Lecteur - Lecture seule')

            self.stdout.write('\n💡 Pour assigner un rôle à un utilisateur:')
            self.stdout.write('   1. Connectez-vous à l\'admin Django')
            self.stdout.write('   2. Allez dans Utilisateurs')
            self.stdout.write('   3. Sélectionnez un utilisateur')
            self.stdout.write('   4. Ajoutez-le à un ou plusieurs groupes\n')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur: {str(e)}\n'))
            raise
