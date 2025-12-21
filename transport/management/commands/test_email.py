"""
Commande de test pour le système de notifications par email
Usage: python manage.py test_email [type] [--email destinataire@example.com]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from transport.models import Mission, PaiementMission, Cautions
from transport.email_notifications import (
    send_mission_retard_notification,
    send_mission_terminee_notification,
    send_paiement_valide_notification,
    send_caution_debloquee_notification,
    send_alerte_admin_notification
)


class Command(BaseCommand):
    help = 'Teste le système de notifications par email'

    def add_arguments(self, parser):
        parser.add_argument(
            'type',
            nargs='?',
            type=str,
            default='all',
            help='Type de notification à tester: mission_retard, mission_terminee, paiement, caution, alerte, all'
        )
        parser.add_argument(
            '--email',
            type=str,
            default=None,
            help='Email de destination pour le test'
        )

    def handle(self, *args, **options):
        type_notif = options['type']
        email_dest = options['email']

        self.stdout.write(self.style.SUCCESS('\n🔔 SYSTÈME DE TEST DES NOTIFICATIONS EMAIL\n'))
        self.stdout.write('=' * 60)

        # Récupérer des données de test
        try:
            mission = Mission.objects.filter(statut='terminee').first()
            paiement = PaiementMission.objects.filter(est_valide=True).first()
            caution = Cautions.objects.filter(statut='remboursee').first()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors de la récupération des données: {str(e)}'))
            self.stdout.write(self.style.WARNING('\nAssurez-vous d\'avoir des données dans la base.'))
            return

        # Test mission en retard
        if type_notif in ['mission_retard', 'all']:
            self.stdout.write('\n📧 Test: Mission en retard...')
            if mission:
                try:
                    send_mission_retard_notification(mission, jours_retard=5, penalite=125000)
                    self.stdout.write(self.style.SUCCESS('   ✅ Email mission_retard envoyé'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {str(e)}'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Aucune mission disponible pour le test'))

        # Test mission terminée
        if type_notif in ['mission_terminee', 'all']:
            self.stdout.write('\n📧 Test: Mission terminée...')
            if mission:
                try:
                    send_mission_terminee_notification(mission)
                    self.stdout.write(self.style.SUCCESS('   ✅ Email mission_terminee envoyé'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {str(e)}'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Aucune mission disponible pour le test'))

        # Test paiement validé
        if type_notif in ['paiement', 'all']:
            self.stdout.write('\n📧 Test: Paiement validé...')
            if paiement:
                try:
                    send_paiement_valide_notification(paiement)
                    self.stdout.write(self.style.SUCCESS('   ✅ Email paiement_valide envoyé'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {str(e)}'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Aucun paiement disponible pour le test'))

        # Test caution débloquée
        if type_notif in ['caution', 'all']:
            self.stdout.write('\n📧 Test: Caution débloquée...')
            if caution:
                try:
                    send_caution_debloquee_notification(caution)
                    self.stdout.write(self.style.SUCCESS('   ✅ Email caution_debloquee envoyé'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {str(e)}'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Aucune caution disponible pour le test'))

        # Test alerte admin
        if type_notif in ['alerte', 'all']:
            self.stdout.write('\n📧 Test: Alerte administrateur...')
            try:
                send_alerte_admin_notification(
                    titre='Test Système Email',
                    message='Ceci est un test du système de notifications par email.',
                    data={
                        'Type': 'Test Automatique',
                        'Date': timezone.now().strftime('%d/%m/%Y %H:%M'),
                        'Statut': 'Système Fonctionnel'
                    }
                )
                self.stdout.write(self.style.SUCCESS('   ✅ Email alerte_admin envoyé'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {str(e)}'))

        # Récapitulatif
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ Tests terminés !'))

        if email_dest:
            self.stdout.write(self.style.WARNING(f'\n📮 Emails envoyés à: {email_dest}'))
        else:
            self.stdout.write(self.style.WARNING('\n📮 Mode console: vérifiez les emails ci-dessus'))

        self.stdout.write('\n💡 Pour tester avec un vrai email:')
        self.stdout.write('   python manage.py test_email --email votre-email@example.com\n')

        self.stdout.write('💡 Pour tester un type spécifique:')
        self.stdout.write('   python manage.py test_email mission_retard')
        self.stdout.write('   python manage.py test_email paiement')
        self.stdout.write('   python manage.py test_email caution')
        self.stdout.write('   python manage.py test_email alerte\n')
