"""
Contrat.Py

Modèles pour contrat
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from .mission import Mission
from .vehicle import Camion
from .personnel import Chauffeur
from .choices import *
# Imports circulaires gérés dans les méthodes

class ContratTransport(models.Model):
    pk_contrat = models.CharField(max_length=250, primary_key=True, editable=False)

    conteneur = models.ForeignKey("Conteneur", on_delete=models.CASCADE)
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, null=True, blank=True)
    transitaire = models.ForeignKey("Transitaire", on_delete=models.SET_NULL, null=True, blank=True)
    entreprise = models.ForeignKey("Entreprise", on_delete=models.CASCADE)

    camion = models.ForeignKey("Camion", on_delete=models.CASCADE)
    chauffeur = models.ForeignKey("Chauffeur", on_delete=models.CASCADE)

    numero_bl = models.CharField(max_length=100, unique=True, db_index=True)
    lieu_chargement = models.CharField(max_length=200, default='Bamako', help_text="Lieu de chargement / Origine")
    destinataire = models.CharField(max_length=200, db_index=True)

    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    avance_transport = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    reliquat_transport = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )

    caution = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    statut_caution = models.CharField(max_length=10, choices=STATUT_CAUTION_CONTRAT_CHOICES, default='bloquee')

    date_debut = models.DateField(db_index=True)
    date_limite_retour = models.DateField(db_index=True)

    commentaire = models.TextField(blank=True, null=True)

    signature_chauffeur = models.BooleanField(default=False)
    signature_client = models.BooleanField(default=False)
    signature_transitaire = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='contrats/', null=True, blank=True)

    # Statut du contrat (pour gestion annulation)
    statut = models.CharField(
        max_length=10,
        choices=[
            ('actif', 'Actif'),
            ('termine', 'Terminé'),
            ('annule', 'Annulé'),
        ],
        default='actif',
        db_index=True,
        help_text="Statut du contrat"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['conteneur','client','transitaire','entreprise','camion','chauffeur','numero_bl','date_debut'],
                name='unique_contrat_transport'
            )
        ]

    def clean(self):
        """Validation personnalisée des montants et champs obligatoires"""
        super().clean()

        # Calcul automatique de la date limite de retour AVANT validation
        # UNIQUEMENT si on crée un nouveau contrat (pas de pk_contrat)
        # ou si date_limite_retour n'est pas définie
        # En mode édition, on garde la valeur saisie par l'utilisateur
        if self.date_debut and not self.date_limite_retour:
            from datetime import timedelta
            self.date_limite_retour = self.date_debut + timedelta(days=23)

        # Vérifier les champs obligatoires en utilisant les IDs
        errors = {}

        if not self.camion_id:
            errors['camion'] = 'Le camion est obligatoire'
        if not self.chauffeur_id:
            errors['chauffeur'] = 'Le chauffeur est obligatoire'
        if not self.client_id:
            errors['client'] = 'Le client est obligatoire'
        if not self.transitaire_id:
            errors['transitaire'] = 'Le transitaire est obligatoire'

        # Vérifier la disponibilité du camion et du chauffeur
        if self.camion_id and self.chauffeur_id:
            # Vérifier si le camion est déjà affecté à une mission en cours
            missions_camion = Mission.objects.filter(
                contrat__camion_id=self.camion_id,
                statut='en cours'
            )
            # Exclure le contrat actuel si on est en mode édition
            if self.pk_contrat:
                missions_camion = missions_camion.exclude(contrat__pk_contrat=self.pk_contrat)

            if missions_camion.exists():
                # Récupérer l'objet camion pour afficher son immatriculation
                try:
                    camion = Camion.objects.get(pk=self.camion_id)
                    errors['camion'] = f'Le camion {camion.immatriculation} est déjà affecté à une mission en cours'
                except Camion.DoesNotExist:
                    errors['camion'] = 'Le camion sélectionné est déjà affecté à une mission en cours'

            # Vérifier si le chauffeur est déjà affecté à une mission en cours
            missions_chauffeur = Mission.objects.filter(
                contrat__chauffeur_id=self.chauffeur_id,
                statut='en cours'
            )
            # Exclure le contrat actuel si on est en mode édition
            if self.pk_contrat:
                missions_chauffeur = missions_chauffeur.exclude(contrat__pk_contrat=self.pk_contrat)

            if missions_chauffeur.exists():
                # Récupérer l'objet chauffeur pour afficher son nom
                try:
                    chauffeur = Chauffeur.objects.get(pk=self.chauffeur_id)
                    errors['chauffeur'] = f'Le chauffeur {chauffeur.nom} {chauffeur.prenom} est déjà affecté à une mission en cours'
                except Chauffeur.DoesNotExist:
                    errors['chauffeur'] = 'Le chauffeur sélectionné est déjà affecté à une mission en cours'

        # Vérifier que l'avance ne dépasse pas le montant total
        if self.avance_transport and self.montant_total:
            if self.avance_transport > self.montant_total:
                errors['avance_transport'] = 'L\'avance ne peut pas dépasser le montant total'

        # Vérifier que la caution n'est pas trop élevée (max 50% du montant)
        if self.caution and self.montant_total:
            if self.caution > self.montant_total * Decimal('0.5'):
                errors['caution'] = 'La caution ne peut pas dépasser 50% du montant total'

        # Vérifier que la date de retour est après la date de début
        # Note: Cette validation est maintenant redondante car date_limite_retour est auto-calculée ci-dessus
        # mais on la garde pour sécurité au cas où le calcul échoue
        if self.date_debut and self.date_limite_retour:
            if self.date_limite_retour < self.date_debut:
                errors['date_limite_retour'] = 'La date limite de retour doit être après la date de début'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.pk_contrat:
            base = (
                f"{self.conteneur.pk_conteneur}"
                f"{self.client.pk_client if self.client else ''}"
                f"{self.transitaire.pk_transitaire if self.transitaire else ''}"
                f"{self.camion.immatriculation}"
                f"{self.chauffeur.pk_chauffeur}"
                f"{self.numero_bl}"
                f"{self.date_debut}"
            )
            base = base.replace(" ", "").replace("-", "")
            self.pk_contrat = slugify(base)[:250]

        # Calcul automatique de la date limite de retour : date_debut + 23 jours
        # Note: Ce calcul est maintenant fait dans clean() mais on le garde ici
        # comme sécurité au cas où clean() n'est pas appelé (ex: bulk_create, update)
        if self.date_debut and not self.date_limite_retour:
            from datetime import timedelta
            self.date_limite_retour = self.date_debut + timedelta(days=23)

        # Calcul automatique du reliquat
        self.reliquat_transport = Decimal(self.montant_total) - Decimal(self.avance_transport)
        super().save(*args, **kwargs)

    def annuler_contrat(self, raison=''):
        """Annule le contrat et tous les objets liés en cascade

        Args:
            raison: Raison de l'annulation

        Cette méthode annule automatiquement:
        - Le contrat lui-même
        - Toutes les missions associées
        - Toutes les cautions associées
        - Tous les paiements associés (via annulation missions)

        IMPORTANT: Les objets sont ANNULÉS (statut changé),
        pas SUPPRIMÉS - pour garder la traçabilité.

        Returns:
            dict: Nombre d'objets annulés par type
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError

        if self.statut == 'annule':
            raise ValidationError('⚠️ Ce contrat est déjà annulé.')

        date_annulation = timezone.now()

        # 1. Annuler le contrat
        self.statut = 'annule'

        # Ajouter la raison dans le commentaire
        if raison:
            if not self.commentaire:
                self.commentaire = ''
            self.commentaire += (
                f'\n\n🚫 CONTRAT ANNULÉ\n'
                f'Date: {date_annulation.strftime("%d/%m/%Y %H:%M")}\n'
                f'Raison: {raison}'
            )
        else:
            if not self.commentaire:
                self.commentaire = ''
            self.commentaire += (
                f'\n\n🚫 CONTRAT ANNULÉ\n'
                f'Date: {date_annulation.strftime("%d/%m/%Y %H:%M")}'
            )

        self.save()

        # 2. Annuler toutes les missions associées
        from .mission import Mission
        missions = Mission.objects.filter(contrat=self)
        nb_missions = 0

        for mission in missions:
            if mission.statut != 'annulée':
                # Utiliser la méthode annuler_mission existante
                mission.annuler_mission(
                    raison=f"Contrat {self.numero_bl} annulé: {raison if raison else 'Non spécifiée'}"
                )
                nb_missions += 1

        # 3. Annuler toutes les cautions (déjà fait par annuler_mission,
        # mais on le refait pour être sûr)
        from .finance import Cautions
        cautions = Cautions.objects.filter(contrat=self)
        nb_cautions = 0

        for caution in cautions:
            if caution.statut != 'annulee':
                caution.statut = 'annulee'
                caution.save()
                nb_cautions += 1

        # 4. Compter les prestations (pas de statut, juste pour info)
        prestations = PrestationDeTransports.objects.filter(contrat_transport=self)
        nb_prestations = prestations.count()

        # Log pour traçabilité
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Contrat {self.numero_bl} annulé: "
            f"{nb_missions} missions, {nb_cautions} cautions, "
            f"{nb_prestations} prestations affectées"
        )

        return {
            'missions_annulees': nb_missions,
            'cautions_annulees': nb_cautions,
            'prestations': nb_prestations,
        }

    def __str__(self):
        return f"Contrat {self.pk_contrat} | BL: {self.numero_bl}"

class PrestationDeTransports(models.Model):
    pk_presta_transport = models.CharField(max_length=250, primary_key=True)
    contrat_transport = models.ForeignKey("ContratTransport", on_delete=models.CASCADE)
    camion = models.ForeignKey("Camion", on_delete=models.CASCADE)
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    transitaire = models.ForeignKey("Transitaire", on_delete=models.CASCADE)

    prix_transport = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    avance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    caution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    solde = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    date = models.DateTimeField()

    def save(self,*args, **kwargs):
        if not self.pk_presta_transport:
           base = f"{self.camion.immatriculation}{self.contrat_transport.pk_contrat}{self.client.pk_client}{self.transitaire.pk_transitaire}{self.date}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           self.pk_presta_transport = slugify(base)[:250]
        super().save(*args,**kwargs)
    
    # class Meta:
    #     unique_together = ("camion","pk_presta_transport","contrat_transport","client","transitaire")
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['camion', 'contrat_transport', 'client', 'transitaire', 'date'],
                name='unique_presta_transport'
            )
        ]

    def __str__(self):
        return (f"{self.pk_presta_transport}{self.prix_transport}{self.avance}{self.caution}{self.solde}{self.date}")

