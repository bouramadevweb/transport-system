"""
Système de Notifications Email
================================

Ce module gère l'envoi de notifications par email pour les événements importants :
- Missions en retard
- Paiements validés
- Cautions débloquées
- Alertes administrateur

Usage:
    from transport.email_notifications import EmailNotifier

    notifier = EmailNotifier()
    notifier.send_mission_retard(mission, jours_retard=5)
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Classe pour gérer l'envoi de notifications email
    """

    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@transport-system.com')
        self.admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@transport-system.com')

    def _send_email(self, subject, html_content, recipient_list, fail_silently=True):
        """
        Méthode interne pour envoyer un email HTML

        Args:
            subject: Sujet de l'email
            html_content: Contenu HTML
            recipient_list: Liste des destinataires
            fail_silently: Si True, ne lève pas d'exception en cas d'erreur
        """
        try:
            # Créer la version texte (sans HTML)
            text_content = strip_tags(html_content)

            # Créer l'email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=recipient_list
            )

            # Ajouter le contenu HTML
            email.attach_alternative(html_content, "text/html")

            # Envoyer
            email.send(fail_silently=fail_silently)

            logger.info(f"✅ Email envoyé: {subject} → {', '.join(recipient_list)}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {str(e)}")
            if not fail_silently:
                raise
            return False

    def send_mission_retard(self, mission, jours_retard, penalite=0):
        """
        Notification de mission en retard

        Args:
            mission: Instance Mission
            jours_retard: Nombre de jours de retard
            penalite: Montant de la pénalité (optionnel)
        """
        # Destinataires
        recipients = []

        # Email du chauffeur
        if mission.contrat and mission.contrat.chauffeur and mission.contrat.chauffeur.email:
            recipients.append(mission.contrat.chauffeur.email)

        # Email du client
        if mission.contrat and mission.contrat.client and mission.contrat.client.email:
            recipients.append(mission.contrat.client.email)

        # Toujours notifier l'admin
        recipients.append(self.admin_email)

        # Si pas de destinataires, abandonner
        if not recipients:
            logger.warning(f"⚠️ Aucun email pour mission en retard: {mission.pk_mission}")
            return False

        # Contexte pour le template
        context = {
            'mission': mission,
            'jours_retard': jours_retard,
            'penalite': penalite,
            'chauffeur': mission.contrat.chauffeur if mission.contrat else None,
            'camion': mission.contrat.camion if mission.contrat else None,
            'conteneur': mission.contrat.conteneur if mission.contrat else None,
        }

        # Render template
        html_content = render_to_string('transport/emails/mission_retard.html', context)

        # Sujet
        subject = f"⚠️ URGENT - Mission en retard ({jours_retard} jours) - {mission.pk_mission[:15]}"

        # Envoyer
        return self._send_email(subject, html_content, recipients)

    def send_paiement_valide(self, paiement):
        """
        Notification de paiement validé

        Args:
            paiement: Instance PaiementMission
        """
        # Destinataires
        recipients = []

        # Email du chauffeur
        if paiement.mission and paiement.mission.contrat and paiement.mission.contrat.chauffeur:
            chauffeur = paiement.mission.contrat.chauffeur
            if chauffeur.email:
                recipients.append(chauffeur.email)

        # Email du client
        if paiement.mission and paiement.mission.contrat and paiement.mission.contrat.client:
            client = paiement.mission.contrat.client
            if client.email:
                recipients.append(client.email)

        # Admin
        recipients.append(self.admin_email)

        if not recipients:
            logger.warning(f"⚠️ Aucun email pour paiement validé: {paiement.pk_paiement}")
            return False

        # Contexte
        context = {
            'paiement': paiement,
            'mission': paiement.mission,
            'chauffeur': paiement.mission.contrat.chauffeur if paiement.mission and paiement.mission.contrat else None,
            'montant_total': paiement.montant_total,
            'commission': paiement.commission_transitaire,
            'date_validation': paiement.date_validation,
        }

        # Render
        html_content = render_to_string('transport/emails/paiement_valide.html', context)

        # Sujet
        subject = f"✅ Paiement validé - {paiement.montant_total} FCFA - Mission {paiement.mission.pk_mission[:15] if paiement.mission else 'N/A'}"

        # Envoyer
        return self._send_email(subject, html_content, recipients)

    def send_caution_debloquee(self, caution):
        """
        Notification de caution débloquée/remboursée

        Args:
            caution: Instance Cautions
        """
        # Destinataires
        recipients = []

        # Email du chauffeur
        if caution.chauffeur and caution.chauffeur.email:
            recipients.append(caution.chauffeur.email)

        # Email du client
        if caution.client and caution.client.email:
            recipients.append(caution.client.email)

        # Admin
        recipients.append(self.admin_email)

        if not recipients:
            logger.warning(f"⚠️ Aucun email pour caution débloquée: {caution.pk_caution}")
            return False

        # Contexte
        context = {
            'caution': caution,
            'montant': caution.montant,
            'montant_rembourse': caution.montant_rembourser,
            'statut': caution.get_statut_display(),
            'chauffeur': caution.chauffeur,
            'client': caution.client,
            'conteneur': caution.conteneur,
        }

        # Render
        html_content = render_to_string('transport/emails/caution_debloquee.html', context)

        # Sujet
        subject = f"💰 Caution remboursée - {caution.montant_rembourser} FCFA"

        # Envoyer
        return self._send_email(subject, html_content, recipients)

    def send_alerte_admin(self, titre, message, data=None):
        """
        Notification générique pour l'administrateur

        Args:
            titre: Titre de l'alerte
            message: Message descriptif
            data: Données supplémentaires (dict)
        """
        recipients = [self.admin_email]

        context = {
            'titre': titre,
            'message': message,
            'data': data or {},
        }

        html_content = render_to_string('transport/emails/alerte_admin.html', context)

        subject = f"🔔 Alerte Système - {titre}"

        return self._send_email(subject, html_content, recipients)

    def send_mission_terminee(self, mission):
        """
        Notification de mission terminée

        Args:
            mission: Instance Mission
        """
        recipients = []

        # Email du chauffeur
        if mission.contrat and mission.contrat.chauffeur and mission.contrat.chauffeur.email:
            recipients.append(mission.contrat.chauffeur.email)

        # Admin
        recipients.append(self.admin_email)

        if not recipients:
            return False

        # Vérifier s'il y a eu retard
        jours_retard = 0
        penalite = 0
        if mission.date_retour and mission.contrat:
            if mission.date_retour > mission.contrat.date_limite_retour:
                jours_retard = (mission.date_retour - mission.contrat.date_limite_retour).days
                penalite = jours_retard * 25000

        context = {
            'mission': mission,
            'chauffeur': mission.contrat.chauffeur if mission.contrat else None,
            'jours_retard': jours_retard,
            'penalite': penalite,
            'date_retour': mission.date_retour,
        }

        html_content = render_to_string('transport/emails/mission_terminee.html', context)

        if jours_retard > 0:
            subject = f"⚠️ Mission terminée avec {jours_retard}j de retard - {mission.pk_mission[:15]}"
        else:
            subject = f"✅ Mission terminée à temps - {mission.pk_mission[:15]}"

        return self._send_email(subject, html_content, recipients)


# Instance globale
email_notifier = EmailNotifier()


def send_mission_retard_notification(mission, jours_retard, penalite=0):
    """Helper function pour notification mission en retard"""
    return email_notifier.send_mission_retard(mission, jours_retard, penalite)


def send_paiement_valide_notification(paiement):
    """Helper function pour notification paiement validé"""
    return email_notifier.send_paiement_valide(paiement)


def send_caution_debloquee_notification(caution):
    """Helper function pour notification caution débloquée"""
    return email_notifier.send_caution_debloquee(caution)


def send_alerte_admin_notification(titre, message, data=None):
    """Helper function pour alerte admin"""
    return email_notifier.send_alerte_admin(titre, message, data)


def send_mission_terminee_notification(mission):
    """Helper function pour mission terminée"""
    return email_notifier.send_mission_terminee(mission)
