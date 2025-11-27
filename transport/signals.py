from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ContratTransport, PrestationDeTransports, Cautions, Mission, PaiementMission


@receiver(post_save, sender=ContratTransport)
def creer_workflow_complet_contrat(sender, instance, created, **kwargs):  # noqa: ARG001
    """
    Quand un contrat est créé, créer automatiquement:
    1. PrestationDeTransports
    2. Cautions
    3. Mission
    4. PaiementMission
    """
    if created:  # Seulement lors de la création
        print(f"🔄 Création automatique du workflow pour le contrat {instance.pk_contrat}")

        # Vérifier que les champs essentiels existent
        if not instance.camion:
            print(f"⚠️ Attention: Le contrat n'a pas de camion assigné")
        if not instance.client:
            print(f"⚠️ Attention: Le contrat n'a pas de client")
        if not instance.transitaire:
            print(f"⚠️ Attention: Le contrat n'a pas de transitaire")
        if not instance.chauffeur:
            print(f"⚠️ Attention: Le contrat n'a pas de chauffeur")

        # 1. Créer la PrestationDeTransports
        try:
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
            print(f"✅ Prestation créée: {prestation.pk_presta_transport}")
        except Exception as e:
            print(f"❌ Erreur création prestation: {e}")
            return

        # 2. Créer la Caution
        try:
            caution = Cautions.objects.create(
                conteneur=instance.conteneur,
                contrat=instance,
                transitaire=instance.transitaire,
                client=instance.client,
                chauffeur=instance.chauffeur,
                camion=instance.camion,
                montant=instance.caution,
                non_rembourser=False,
                est_rembourser=False,  # Pas encore remboursée
                montant_rembourser=0
            )
            print(f"✅ Caution créée: {caution.pk_caution}")
        except Exception as e:
            print(f"❌ Erreur création caution: {e}")
            return

        # 3. Créer la Mission
        try:
            # Déterminer l'origine depuis le contrat si disponible
            origine = "À définir"
            if hasattr(instance, 'lieu_chargement') and instance.lieu_chargement:
                origine = instance.lieu_chargement
            elif instance.client and hasattr(instance.client, 'adresse'):
                origine = instance.client.adresse or "À définir"

            # Destination
            destination = instance.destinataire if instance.destinataire else "À définir"

            mission = Mission.objects.create(
                prestation_transport=prestation,
                contrat=instance,
                date_depart=instance.date_debut,
                date_retour=None,  # Sera rempli plus tard
                origine=origine,
                destination=destination,
                frais_trajet=None,  # À définir par l'utilisateur
                statut='en cours'
            )
            print(f"✅ Mission créée: {mission.pk_mission}")
        except Exception as e:
            print(f"❌ Erreur création mission: {e}")
            return

        # 4. Créer le PaiementMission (prérempli mais non validé)
        try:
            # Calculer la commission du transitaire si disponible
            commission = 0
            if instance.transitaire and hasattr(instance.transitaire, 'commission_percentage'):
                # Si le transitaire a un pourcentage de commission
                commission = (instance.montant_total * instance.transitaire.commission_percentage) / 100

            paiement = PaiementMission.objects.create(
                mission=mission,
                caution=caution,
                prestation=prestation,
                montant_total=instance.montant_total,
                commission_transitaire=commission,
                caution_est_retiree=False,  # Pas encore validé
                mode_paiement='',
                observation='Paiement créé automatiquement - En attente de validation après fin de mission',
                est_valide=False,  # Pas encore validé
                date_validation=None
            )
            print(f"✅ Paiement créé: {paiement.pk_paiement} (Commission: {commission}€)")
            print(f"🎉 Workflow complet créé avec succès!")
        except Exception as e:
            print(f"❌ Erreur création paiement: {e}")
            return
