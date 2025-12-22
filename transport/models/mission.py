"""
Mission.Py

Modèles pour mission
"""

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from .choices import *
# Imports circulaires gérés dans les méthodes

class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250, primary_key=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_route = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    frais_carburant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )

    # class Meta:
    #     unique_together = ('origine', 'destination')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['origine','destination'],
                name='unique_frais_trajet'
            )
        ]    

    def __str__(self):
        return f"{self.pk_frais}, {self.origine}, {self.destination}, {self.frais_route}, {self.frais_carburant}"

class Mission(models.Model):
    pk_mission = models.CharField(max_length=250, primary_key=True, editable=False)
    prestation_transport = models.ForeignKey(PrestationDeTransports, on_delete=models.CASCADE)
    date_depart = models.DateField()
    date_retour = models.DateField(blank=True, null=True)
    origine = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    itineraire = models.TextField(
        blank=True,
        # default='Itinéraire à compléter',
        help_text="Décrivez l'itinéraire détaillé de la mission"
    )
    frais_trajet = models.ForeignKey(FraisTrajet, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_MISSION_CHOICES, default='en cours')

    def clean(self):
        """Validation des dates par rapport au contrat"""
        super().clean()
        errors = {}

        # Vérifier que les champs obligatoires sont remplis
        if not self.origine or not self.origine.strip():
            errors['origine'] = 'L\'origine est obligatoire'
        if not self.destination or not self.destination.strip():
            errors['destination'] = 'La destination est obligatoire'
        if not self.itineraire or not self.itineraire.strip():
            errors['itineraire'] = 'L\'itinéraire est obligatoire'

        # Vérifier la concordance des dates avec le contrat
        if self.contrat and self.date_depart:
            # La date de départ de la mission doit être >= date_debut du contrat
            if self.date_depart < self.contrat.date_debut:
                errors['date_depart'] = f'La date de départ ({self.date_depart}) doit être >= à la date de début du contrat ({self.contrat.date_debut})'

        # Vérifier la date de retour si elle existe
        if self.date_retour:
            # La date de retour doit être après la date de départ
            if self.date_depart and self.date_retour < self.date_depart:
                errors['date_retour'] = 'La date de retour doit être après la date de départ'

            # La date de retour devrait être <= date_limite_retour du contrat
            if self.contrat and self.date_retour > self.contrat.date_limite_retour:
                errors['date_retour'] = f'⚠️ La date de retour ({self.date_retour}) dépasse la date limite du contrat ({self.contrat.date_limite_retour}). Cela peut entraîner des pénalités.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Générer la clé primaire si elle n'existe pas
        if not self.pk_mission:
            base = (
                f"{self.prestation_transport.pk_presta_transport}_"
                f"{self.contrat.pk_contrat}_"
                f"{self.origine}_{self.destination}_"
                f"{self.date_depart}"
            )
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_mission = slugify(base)[:250]

        # Valider avant de sauvegarder (sauf si validate=False passé en kwargs)
        validate = kwargs.pop('validate', True)
        if validate:
            self.full_clean()

        super().save(*args, **kwargs)

    def terminer_mission(self, date_retour=None, force=False):
        """Méthode pour terminer proprement une mission avec validation de la date

        Args:
            date_retour: Date de retour effective (par défaut aujourd'hui)
            force: Si True, force la terminaison même en retard

        Returns:
            dict: Informations sur la pénalité si en retard
        """
        from django.utils import timezone

        if date_retour is None:
            date_retour = timezone.now().date()

        # Vérifier que la date de retour est cohérente
        if date_retour < self.date_depart:
            raise ValidationError(
                f'❌ La date de retour ({date_retour}) ne peut pas être avant la date de départ ({self.date_depart})'
            )

        info_penalite = {
            'en_retard': False,
            'jours_retard': 0,
            'penalite': 0,
            'message': ''
        }

        # Vérifier si la date dépasse la limite du contrat
        if date_retour > self.contrat.date_limite_retour:
            jours_retard = (date_retour - self.contrat.date_limite_retour).days
            penalite = jours_retard * 25000  # 25 000 FCFA par jour

            info_penalite = {
                'en_retard': True,
                'jours_retard': jours_retard,
                'penalite': penalite,
                'message': f'⚠️ Mission terminée avec {jours_retard} jour(s) de retard. Pénalité: {penalite} FCFA'
            }

            # Si force=False, lever une erreur avec les infos
            if not force:
                raise ValidationError(
                    f'⚠️ ATTENTION: La date de retour ({date_retour}) dépasse la date limite du contrat ({self.contrat.date_limite_retour}) '
                    f'de {jours_retard} jour(s). Pénalité: {penalite} FCFA. '
                    f'Confirmez pour terminer quand même.'
                )

        self.date_retour = date_retour
        self.statut = 'terminée'
        self.save()

        # 🆕 RETOURNER LE CONTENEUR AU PORT
        if self.contrat and self.contrat.conteneur:
            self.contrat.conteneur.retourner_au_port()
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🚢 Conteneur {self.contrat.conteneur.numero_conteneur} retourné au port (disponible)")

        return info_penalite

    def annuler_mission(self, raison=''):
        """Annule une mission et tous les objets liés en cascade

        Args:
            raison: Raison de l'annulation

        Cette méthode annule automatiquement:
        - La mission elle-même
        - Le contrat de transport associé
        - Les cautions associées
        - Les paiements associés
        """
        if self.statut == 'terminée':
            raise ValidationError('❌ Impossible d\'annuler une mission déjà terminée.')

        if self.statut == 'annulée':
            raise ValidationError('⚠️ Cette mission est déjà annulée.')

        from django.utils import timezone
        date_annulation = timezone.now()

        # 1. Annuler la mission
        self.statut = 'annulée'

        # Ajouter la raison dans l'itinéraire si fournie
        if raison:
            if not self.itineraire:
                self.itineraire = ''
            self.itineraire += f'\n\n--- MISSION ANNULÉE ---\nRaison: {raison}\nDate annulation: {date_annulation.strftime("%d/%m/%Y %H:%M")}'
        else:
            if not self.itineraire:
                self.itineraire = ''
            self.itineraire += f'\n\n--- MISSION ANNULÉE ---\nDate annulation: {date_annulation.strftime("%d/%m/%Y %H:%M")}'

        self.save()

        # 2. Annuler le contrat de transport associé
        if self.contrat:
            if not self.contrat.commentaire:
                self.contrat.commentaire = ''
            self.contrat.commentaire += f'\n\n🚫 CONTRAT ANNULÉ\nMission annulée le {date_annulation.strftime("%d/%m/%Y %H:%M")}\nRaison: {raison if raison else "Non spécifiée"}'
            self.contrat.save()

        # 3. Annuler toutes les cautions associées
        from .models import Cautions
        cautions = Cautions.objects.filter(contrat=self.contrat)
        for caution in cautions:
            if caution.statut != 'annulee':
                caution.statut = 'annulee'
                caution.save()

        # 4. Marquer les paiements associés comme annulés
        from .models import PaiementMission
        paiements = PaiementMission.objects.filter(mission=self)
        for paiement in paiements:
            if not paiement.est_valide:  # Seulement si pas encore validé
                if not paiement.observation:
                    paiement.observation = ''
                paiement.observation += f'\n\n❌ PAIEMENT ANNULÉ\nMission annulée le {date_annulation.strftime("%d/%m/%Y %H:%M")}\nRaison: {raison if raison else "Non spécifiée"}'
                paiement.save()

        # 🆕 5. RETOURNER LE CONTENEUR AU PORT (car mission annulée)
        if self.contrat and self.contrat.conteneur:
            self.contrat.conteneur.retourner_au_port()
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🚢 Conteneur {self.contrat.conteneur.numero_conteneur} retourné au port (mission annulée)")

    # class Meta:
    #     unique_together = (
    #         'prestation_transport',
    #         'contrat',
    #         'origine',
    #         'destination',
    #         'date_depart',
    #     )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['prestation_transport','contrat','origine','destination','date_depart'],
                name='unique_mission'
            )
        ]

    def __str__(self):
        return (f"{self.pk_mission}"
                 f"{self.date_depart}" 
                 f" {self.date_retour}" 
                f"{self.origine}"
                 f"{self.destination}"
                    f"{self.frais_trajet} "
                f"{self.contrat}"
                 f"{self.statut}")

# ici nest pas encore faite

class MissionConteneur(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)

    class Meta:
        # Supprime l'ID auto
        managed = True
        #unique_together = ('mission', 'conteneur')
        # Ou, en Django 4.1+, tu peux utiliser constraints :
        constraints = [
            models.UniqueConstraint(fields=['mission', 'conteneur'], name='unique_mission_conteneur')
        ]
    
    def __str__(self):
        return f"{self.mission}, {self.conteneur}"

