"""
Finance.Py

Modèles pour finance
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

class Cautions(models.Model):
    pk_caution = models.CharField(max_length=250, primary_key=True)
    conteneur = models.ForeignKey("Conteneur", on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey("ContratTransport", on_delete=models.SET_NULL, blank=True, null=True)
    transitaire = models.ForeignKey("Transitaire", on_delete=models.SET_NULL, blank=True, null=True)
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, blank=True, null=True)
    chauffeur = models.ForeignKey("Chauffeur", on_delete=models.SET_NULL, blank=True, null=True)
    camion = models.ForeignKey("Camion", on_delete=models.SET_NULL, blank=True, null=True)
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CAUTION_CHOICES,
        default='en_attente',
        db_index=True,
        help_text="Statut de la caution"
    )
    montant_rembourser = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )

    def clean(self):
        """Validation personnalisée pour les cautions"""
        super().clean()

        errors = {}

        # Si la caution est marquée comme remboursée, le montant remboursé doit être rempli
        if self.statut == 'remboursee':
            if not self.montant_rembourser or self.montant_rembourser <= 0:
                errors['montant_rembourser'] = (
                    'Le montant remboursé doit être supérieur à 0 si la caution est marquée comme remboursée. '
                    f'Veuillez saisir le montant remboursé (montant de la caution : {self.montant} FCFA)'
                )

        # Vérifier que le montant remboursé ne dépasse pas le montant de la caution
        if self.montant_rembourser and self.montant:
            if self.montant_rembourser > self.montant:
                errors['montant_rembourser'] = (
                    f'Le montant remboursé ({self.montant_rembourser} FCFA) ne peut pas dépasser '
                    f'le montant de la caution ({self.montant} FCFA)'
                )

        # Si la caution n'est pas remboursée, le montant remboursé devrait être 0
        if self.statut not in ['remboursee', 'consommee'] and self.montant_rembourser > 0:
            errors['montant_rembourser'] = (
                f'Le montant remboursé est de {self.montant_rembourser} FCFA mais la caution n\'est pas marquée comme remboursée ou consommée. '
                f'Changez le statut ou mettez le montant à 0.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.pk_caution:
           base = f"{self.conteneur.pk_conteneur if self.conteneur else ''}{self.contrat.pk_contrat if self.contrat else ''}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           slug = slugify(base)[:220]
           self.pk_caution = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.pk_caution}, {self.conteneur}, {self.contrat}, {self.transitaire} {self.client}, {self.chauffeur}, {self.camion}, {self.montant}, {self.statut}, {self.montant_rembourser}"

class PaiementMission(models.Model):
    pk_paiement = models.CharField(max_length=250,primary_key=True)
    mission = models.ForeignKey("Mission", on_delete=models.CASCADE)
    caution = models.ForeignKey("Cautions", on_delete=models.CASCADE)
    prestation = models.ForeignKey("PrestationDeTransports", on_delete=models.CASCADE)

    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Montant total incluant les frais de stationnement"
    )

    # ✅ NOUVEAU: Frais de stationnement (demurrage)
    frais_stationnement = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Frais de stationnement/demurrage (25 000 CFA/jour après 3 jours gratuits)"
    )

    commission_transitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    caution_est_retiree = models.BooleanField(default=False)

    date_paiement = models.DateField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=50, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)

    # Nouveau champ pour valider le paiement
    est_valide = models.BooleanField(default=False)
    date_validation = models.DateTimeField(blank=True, null=True)

    # Statut du paiement (pour gestion annulation)
    statut_paiement = models.CharField(
        max_length=15,
        choices=[
            ('en_attente', 'En attente'),
            ('valide', 'Validé'),
            ('annule', 'Annulé'),
        ],
        default='en_attente',
        help_text="Statut du paiement"
    )

    def clean(self):
        """Validation avant sauvegarde - empêcher la validation si mission non terminée ou caution non remboursée"""
        super().clean()

        # Si on essaie de valider le paiement
        if self.est_valide:
            # Vérifier que la mission est terminée
            if self.mission.statut != 'terminée':
                raise ValidationError(
                    f"❌ Impossible de valider le paiement! "
                    f"La mission est actuellement '{self.mission.statut}'. "
                    f"Vous devez d'abord terminer la mission avant de valider le paiement."
                )

            # Vérifier l'état de la caution
            if self.caution:
                # La caution doit être remboursée ou consommée
                if self.caution.statut not in ['remboursee', 'consommee']:
                    raise ValidationError(
                        f"❌ Impossible de valider le paiement! "
                        f"La caution de {self.caution.montant} FCFA a le statut '{self.caution.get_statut_display()}'. "
                        f"Veuillez mettre à jour le statut de la caution (Remboursée ou Consommée) avant de valider le paiement."
                    )

        # Vérifier que la commission ne dépasse pas le montant total
        if self.commission_transitaire and self.montant_total:
            if self.commission_transitaire > self.montant_total:
                raise ValidationError({
                    'commission_transitaire': 'La commission ne peut pas dépasser le montant total'
                })

        # Vérifier que la commission n'est pas trop élevée (max 30% du montant)
        if self.commission_transitaire and self.montant_total:
            if self.commission_transitaire > self.montant_total * Decimal('0.3'):
                raise ValidationError({
                    'commission_transitaire': 'La commission ne peut pas dépasser 30% du montant total'
                })

    def valider_paiement(self):
        """Méthode pour valider le paiement avec vérification de la mission et de la caution

        IMPORTANT: Cette méthode ne modifie JAMAIS la caution elle-même.
        Elle enregistre seulement l'état de la caution au moment de la validation.
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError

        # Vérifier que la mission est terminée
        if self.mission.statut != 'terminée':
            raise ValidationError(
                f"❌ La mission n'est pas terminée (statut: {self.mission.statut}). "
                f"Vous devez terminer la mission avant de valider le paiement."
            )

        # Vérifier l'état de la caution
        if self.caution:
            # La caution doit être remboursée ou consommée
            if self.caution.statut not in ['remboursee', 'consommee']:
                raise ValidationError(
                    f"❌ Impossible de valider le paiement! "
                    f"La caution de {self.caution.montant} FCFA a le statut '{self.caution.get_statut_display()}'. "
                    f"Veuillez d'abord mettre à jour le statut de la caution (Remboursée ou Consommée)."
                )

        # IMPORTANT: Sauvegarder l'état de la caution AVANT validation pour traçabilité
        # On ne modifie PAS la caution, on enregistre juste son état dans le paiement
        caution_state = {
            'statut': self.caution.statut if self.caution else 'en_attente',
            'montant_rembourser': self.caution.montant_rembourser if self.caution else 0,
            'montant': self.caution.montant if self.caution else 0,
        }

        # Marquer le paiement comme validé
        self.est_valide = True
        self.date_validation = timezone.now()

        # Enregistrer si la caution était remboursée ou consommée au moment de la validation
        # (Ne modifie PAS la caution elle-même!)
        if self.caution and caution_state['statut'] in ['remboursee', 'consommee']:
            self.caution_est_retiree = True

        # Ajouter l'état de la caution dans l'observation pour traçabilité
        observation_caution = (
            f"\n--- État de la caution au moment de la validation ---\n"
            f"Montant caution: {caution_state['montant']} FCFA\n"
            f"Statut: {self.caution.get_statut_display() if self.caution else 'N/A'}\n"
            f"Montant remboursé: {caution_state['montant_rembourser']} FCFA\n"
            f"Date validation: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        )

        if self.observation:
            self.observation += observation_caution
        else:
            self.observation = observation_caution

        # Sauvegarder le paiement (NE TOUCHE PAS À LA CAUTION!)
        self.save()

        # Log pour vérifier que la caution n'est pas modifiée
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Paiement {self.pk_paiement} validé. "
            f"Caution {self.caution.pk_caution if self.caution else 'N/A'} "
            f"PRÉSERVÉE (montant: {caution_state['montant']}, "
            f"statut: {caution_state['statut']})"
        )

    def synchroniser_frais_stationnement(self):
        """
        Synchronise les frais de stationnement depuis la mission

        Cette méthode copie le montant_stationnement de la mission vers ce paiement.
        Elle est appelée automatiquement lors du save().
        """
        if self.mission and self.mission.montant_stationnement:
            self.frais_stationnement = self.mission.montant_stationnement

            # Ajouter une note dans les observations si des frais existent
            if self.frais_stationnement > 0 and self.mission.jours_stationnement_facturables > 0:
                note_stationnement = (
                    f"\n--- Frais de stationnement ---\n"
                    f"Jours facturables: {self.mission.jours_stationnement_facturables}\n"
                    f"Montant: {self.frais_stationnement} CFA\n"
                    f"Date arrivée: {self.mission.date_arrivee.strftime('%d/%m/%Y') if self.mission.date_arrivee else 'N/A'}\n"
                    f"Date déchargement: {self.mission.date_dechargement.strftime('%d/%m/%Y') if self.mission.date_dechargement else 'N/A'}"
                )

                # Ajouter la note seulement si elle n'existe pas déjà
                if self.observation and "Frais de stationnement" not in self.observation:
                    self.observation += note_stationnement
                elif not self.observation:
                    self.observation = note_stationnement

    def save(self, *args, **kwargs):
        if not self.pk_paiement:
            base = f"{self.mission}{self.caution}{self.prestation}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_paiement = slugify(base)[:250]

        # ✅ NOUVEAU: Synchroniser automatiquement les frais de stationnement
        self.synchroniser_frais_stationnement()

        # Valider avant de sauvegarder
        self.full_clean()

        super().save(*args, **kwargs)


    class Meta:
         #unique_together = ('mission', 'caution',"prestation")
         # Simule une clé composite
        constraints = [models.UniqueConstraint(fields=['mission', 'caution','prestation'], name='unique_mission_caution')]  # Alternative

    def __str__(self):
        statut_validation = "✅ Validé" if self.est_valide else "⏳ En attente"
        return (
            f"{self.mission.pk_mission} - {statut_validation} - "
            f"{self.montant_total}€ ({self.mission.statut})"
        )

