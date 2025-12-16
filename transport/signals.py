from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

from .models import ContratTransport, PrestationDeTransports, Cautions, Mission, PaiementMission

# Configuration du logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=ContratTransport)
def creer_workflow_complet_contrat(sender, instance, created, **kwargs):  # noqa: ARG001
    """
    Quand un contrat est créé, créer automatiquement:
    1. PrestationDeTransports
    2. Cautions
    3. Mission
    4. PaiementMission

    Utilise une transaction atomique pour garantir la cohérence des données.
    """
    if created:  # Seulement lors de la création
        logger.info(f"🔄 Création automatique du workflow pour le contrat {instance.pk_contrat}")

        # Vérifier que les champs essentiels existent
        champs_manquants = []
        if not instance.camion:
            champs_manquants.append("camion")
        if not instance.client:
            champs_manquants.append("client")
        if not instance.transitaire:
            champs_manquants.append("transitaire")
        if not instance.chauffeur:
            champs_manquants.append("chauffeur")

        if champs_manquants:
            logger.error(f"❌ Création du workflow impossible: champs manquants - {', '.join(champs_manquants)}")
            return

        # Vérifier que le camion et le chauffeur ne sont pas déjà affectés à une mission en cours
        missions_en_cours_camion = Mission.objects.filter(
            contrat__camion=instance.camion,
            statut='en cours'
        ).exclude(contrat=instance)

        missions_en_cours_chauffeur = Mission.objects.filter(
            contrat__chauffeur=instance.chauffeur,
            statut='en cours'
        ).exclude(contrat=instance)

        if missions_en_cours_camion.exists():
            logger.warning(f"⚠️ Le camion {instance.camion.immatriculation} est déjà affecté à une mission en cours")

        if missions_en_cours_chauffeur.exists():
            logger.warning(f"⚠️ Le chauffeur {instance.chauffeur.nom} {instance.chauffeur.prenom} est déjà affecté à une mission en cours")

        # Utiliser une transaction atomique pour garantir la cohérence
        try:
            with transaction.atomic():
                # 1. Créer la PrestationDeTransports
                prestation = PrestationDeTransports.objects.create(
                    contrat_transport=instance,
                    camion=instance.camion,
                    client=instance.client,
                    transitaire=instance.transitaire,
                    prix_transport=instance.montant_total,
                    avance=instance.avance_transport,
                    caution=instance.caution,
                    solde=instance.reliquat_transport,
                    date=timezone.now()
                )
                logger.info(f"✅ Prestation créée: {prestation.pk_presta_transport}")

                # 2. Créer la Caution
                caution = Cautions.objects.create(
                    conteneur=instance.conteneur,
                    contrat=instance,
                    transitaire=instance.transitaire,
                    client=instance.client,
                    chauffeur=instance.chauffeur,
                    camion=instance.camion,
                    montant=instance.caution,
                    non_rembourser=False,
                    est_rembourser=False,
                    montant_rembourser=0
                )
                logger.info(f"✅ Caution créée: {caution.pk_caution}")

                # 3. Créer la Mission
                # Déterminer l'origine depuis le contrat si disponible
                origine = "À définir"
                if hasattr(instance, 'lieu_chargement') and instance.lieu_chargement:
                    origine = instance.lieu_chargement
                elif instance.client and hasattr(instance.client, 'adresse'):
                    origine = instance.client.adresse or "À définir"

                # Destination
                destination = instance.destinataire if instance.destinataire else "À définir"

                # Créer un itinéraire par défaut
                itineraire = f"Itinéraire : {origine} → {destination}\n"
                itineraire += f"Camion: {instance.camion.immatriculation}\n"
                itineraire += f"Chauffeur: {instance.chauffeur.nom} {instance.chauffeur.prenom}\n"
                itineraire += f"Conteneur: {instance.conteneur.numero_conteneur}\n"
                itineraire += f"Date de départ prévue: {instance.date_debut}\n"
                itineraire += f"Date de retour prévue: {instance.date_limite_retour}\n"
                itineraire += "\n--- Veuillez compléter les détails de l'itinéraire ---"

                mission = Mission.objects.create(
                    prestation_transport=prestation,
                    contrat=instance,
                    date_depart=instance.date_debut,
                    date_retour=None,
                    origine=origine,
                    destination=destination,
                    itineraire=itineraire,
                    frais_trajet=None,
                    statut='en cours'
                )
                logger.info(f"✅ Mission créée: {mission.pk_mission}")

                # 4. Créer le PaiementMission (prérempli mais non validé)
                # Calculer la commission du transitaire si disponible
                commission = 0
                if instance.transitaire and hasattr(instance.transitaire, 'commission_percentage'):
                    commission = (instance.montant_total * instance.transitaire.commission_percentage) / 100

                paiement = PaiementMission.objects.create(
                    mission=mission,
                    caution=caution,
                    prestation=prestation,
                    montant_total=instance.montant_total,
                    commission_transitaire=commission,
                    caution_est_retiree=False,
                    mode_paiement='',
                    observation='Paiement créé automatiquement - En attente de validation après fin de mission',
                    est_valide=False,
                    date_validation=None
                )
                logger.info(f"✅ Paiement créé: {paiement.pk_paiement} (Commission: {commission})")
                logger.info(f"🎉 Workflow complet créé avec succès pour le contrat {instance.pk_contrat}")

        except Exception as e:
            logger.error(f"❌ Erreur lors de la création du workflow pour le contrat {instance.pk_contrat}: {str(e)}")
            # La transaction sera automatiquement annulée (rollback)
            raise
