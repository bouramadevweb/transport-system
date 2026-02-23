from django.core.management.base import BaseCommand
from django.utils import timezone
from transport.models import Mission, Notification, Utilisateur
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Vérifie les missions en retard et crée des notifications'

    def handle(self, *args, **options):
        """
        Commande qui vérifie toutes les missions en cours et crée des notifications
        pour celles qui sont en retard (date_retour dépassée).

        Cette commande peut être exécutée quotidiennement via cron:
        0 9 * * * cd /path/to/project && python manage.py check_missions_retard
        """
        today = timezone.now().date()

        # Trouver toutes les missions en cours dont la date de retour est dépassée
        # Inclure l'entreprise dans le select_related pour filtrer les notifications par entreprise
        missions_en_retard = Mission.objects.filter(
            statut='en cours',
            date_retour__lt=today
        ).select_related('contrat__entreprise', 'contrat__chauffeur', 'contrat__chauffeur__utilisateur')

        if not missions_en_retard.exists():
            self.stdout.write(self.style.SUCCESS('✅ Aucune mission en retard trouvée'))
            logger.info('✅ Aucune mission en retard trouvée')
            return

        notifications_created = 0

        for mission in missions_en_retard:
            # Calculer le nombre de jours de retard
            jours_retard = (today - mission.date_retour).days

            # Vérifier qu'une notification récente n'existe pas déjà pour cette mission
            # (éviter de spammer si la commande tourne plusieurs fois par jour)
            recent_notification = Notification.objects.filter(
                mission=mission,
                type_notification='mission_retard',
                created_at__date=today
            ).exists()

            if recent_notification:
                continue  # Notification déjà créée aujourd'hui pour cette mission

            # Trouver les utilisateurs à notifier (uniquement de l'entreprise concernée)
            users_to_notify = []
            mission_entreprise = mission.contrat.entreprise if mission.contrat else None

            # 1. Admins et managers de l'entreprise de la mission uniquement
            if mission_entreprise:
                admins_managers = Utilisateur.objects.filter(
                    role__in=['admin', 'manager'],
                    entreprise=mission_entreprise
                )
                users_to_notify.extend(list(admins_managers))

            # 2. Chauffeur de la mission
            if mission.contrat and mission.contrat.chauffeur:
                chauffeur = mission.contrat.chauffeur
                if hasattr(chauffeur, 'utilisateur') and chauffeur.utilisateur:
                    users_to_notify.append(chauffeur.utilisateur)

            # Créer les notifications
            for user in users_to_notify:
                Notification.objects.create(
                    utilisateur=user,
                    type_notification='mission_retard',
                    title=f"Mission en retard - {mission.destination}",
                    message=f"La mission vers {mission.destination} (#{mission.pk_mission[:8]}) est en retard de {jours_retard} jour(s). Date de retour prévue: {mission.date_retour.strftime('%d/%m/%Y')}. Veuillez vérifier son statut.",
                    icon='exclamation-triangle',
                    color='warning',
                    mission=mission
                )
                notifications_created += 1

            logger.info(f"⚠️ Notifications créées pour la mission #{mission.pk_mission} ({jours_retard} jours de retard)")

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {notifications_created} notification(s) créée(s) pour {missions_en_retard.count()} mission(s) en retard'
            )
        )
        logger.info(f"✅ Commande check_missions_retard terminée: {notifications_created} notifications créées")
