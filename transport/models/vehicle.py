"""
Vehicle.Py

Modèles pour vehicle
"""

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from .choices import *

class Camion(models.Model):
    pk_camion = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey("Entreprise", on_delete=models.CASCADE)
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=50, blank=True, null=True)
    capacite_tonnes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    est_affecter = models.BooleanField(default=False)
    date_entree = models.DateField(null=True, blank=True, verbose_name="Date d'entrée dans la flotte")
    date_sortie = models.DateField(null=True, blank=True, verbose_name="Date de sortie de la flotte")

    def save(self, *args, **kwargs):
        if not self.pk_camion:
            base = f"{self.immatriculation}{self.modele}{self.entreprise.pk_entreprise}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_camion = slugify(base)[:250]
        super().save(*args, **kwargs)

    # class Meta:
    #     unique_together = ('immatriculation', 'modele', 'entreprise')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['immatriculation', 'modele', 'entreprise'],
                name='unique_camion'
            )
        ]    

    def __str__(self):
        return f"{self.immatriculation}  {self.modele}"

class CompagnieConteneur(models.Model):
    """
    les compagnies de contneur """
    pk_compagnie = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=250, blank=True, null=True )
    def save(self,*args, **kwargs):
        """
        creation de clée composite"""
        if not self.pk_compagnie:
            base = f"{self.nom}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_compagnie = slugify(base)[:250]
        super().save(*args, **kwargs)   

    # class Meta:   
    #         unique_together = (("nom",),)  

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom'],
                name='unique_compagnie'
            )
        ]

    def __str__(self):
        return f"{self.nom}"

class Conteneur(models.Model):
    pk_conteneur = models.CharField(max_length=250, primary_key=True)
    numero_conteneur = models.CharField(max_length=30, unique=True)
    compagnie = models.ForeignKey("CompagnieConteneur", on_delete=models.CASCADE)
    type_conteneur = models.CharField(max_length=50, blank=True, null=True)
    poids = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    transitaire = models.ForeignKey("Transitaire", on_delete=models.CASCADE)

    # Statut du conteneur pour éviter les attributions multiples
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CONTENEUR_CHOICES,
        default='au_port',
        help_text="Statut actuel du conteneur"
    )

    def save(self, *args, **kwargs):
        if not self.pk_conteneur:
            base = f"{self.numero_conteneur}{self.compagnie.nom}{self.compagnie.pk_compagnie}{self.client.nom}{self.client.pk_client}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_conteneur = slugify(base)[:250]
        super().save(*args, **kwargs)

    # class Meta:
    #     unique_together = ("numero_conteneur","compagnie","client")  

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['numero_conteneur', 'compagnie', 'client'],
                name='unique_conteneur'
            )
        ]  

    def __str__(self):
        return f"{self.numero_conteneur} - {self.compagnie.nom}"

    def est_disponible(self):
        """Vérifie si le conteneur est disponible pour une nouvelle mission"""
        return self.statut == 'au_port'

    def mettre_en_mission(self):
        """Marque le conteneur comme étant en mission"""
        self.statut = 'en_mission'
        self.save(update_fields=['statut'])

    def retourner_au_port(self):
        """Marque le conteneur comme retourné au port (disponible)"""
        self.statut = 'au_port'
        self.save(update_fields=['statut'])

    def get_mission_en_cours(self):
        """Retourne la mission en cours pour ce conteneur (si existe)"""
        from .mission import Mission
        return Mission.objects.filter(
            contrat__conteneur=self,
            statut='en cours'
        ).first()

class Reparation(models.Model):
    pk_reparation = models.CharField(max_length=250, primary_key=True)
    camion = models.ForeignKey("Camion", on_delete=models.CASCADE)
    chauffeur = models.ForeignKey("Chauffeur", on_delete=models.SET_NULL, blank=True, null=True)
    date_reparation = models.DateField()
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_reparation:
            base = f"{self.camion_id or ''}{self.chauffeur_id or ''}{self.date_reparation}".replace('-', '')
            slug = slugify(base)[:240]
            self.pk_reparation = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def has_mecaniciens(self):
        """Vérifie si la réparation a au moins un mécanicien assigné"""
        return ReparationMecanicien.objects.filter(reparation=self).exists()

    def get_mecaniciens(self):
        """Retourne la liste des mécaniciens assignés à cette réparation"""
        from .personnel import Mecanicien
        return Mecanicien.objects.filter(
            reparationmecanicien__reparation=self
        )

    def get_cout_total(self):
        """Calcule le coût total (coût de base + pièces)"""
        cout_pieces = PieceReparee.objects.filter(reparation=self).aggregate(
            total=models.Sum(models.F('quantite') * models.F('cout_unitaire'))
        )['total'] or 0
        return self.cout + cout_pieces

    def __str__(self):
        return f"Réparation {self.pk_reparation} - {self.camion}"

class ReparationMecanicien(models.Model):
    reparation = models.ForeignKey("Reparation", on_delete=models.CASCADE)
    mecanicien = models.ForeignKey("Mecanicien", on_delete=models.CASCADE)

    # class Meta:
    #     unique_together = ('reparation', 'mecanicien')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['reparation','mecanicien'],
                name='unique_reparation_mecanicien'
            )
        ]

    def __str__(self):
        return f"{self.reparation} - {self.mecanicien}"

class PieceReparee(models.Model):

    CATEGORIES = [
        ('moteur', 'Moteur'),
        ('transmission', 'Transmission'),
        ('suspension', 'Suspension & Direction'),
        ('freinage', 'Freinage'),
        ('electrique', 'Éléments électriques'),
        ('eclairage', 'Éclairage & Signalisation'),
        ('auxiliaire', 'Systèmes auxiliaires'),
        ('carrosserie', 'Carrosserie & Structure'),
        ('pneumatique', 'Pneumatiques & Roues'),
        ('alimentation', "Système d'alimentation"),
    ]
    pk_piece = models.CharField(max_length=250, primary_key=True)
    reparation = models.ForeignKey("Reparation", on_delete=models.CASCADE)
    nom_piece = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    reference = models.CharField(max_length=50, blank=True, null=True, help_text="Référence fabricant")
    quantite = models.PositiveIntegerField(default=1)
    cout_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    fournisseur = models.ForeignKey("Fournisseur", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_piece:
            base = f"{self.nom_piece}{self.reparation.pk_reparation}{self.fournisseur or ''}".replace('-', '')
            slug = slugify(base)[:240]
            self.pk_piece = f"{slug}{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    # class Meta:
    #     unique_together = ("nom_piece", "reparation")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom_piece','reparation'],
                name='unique_piece_reparee'
            )
        ]

    def __str__(self):
        return f"{self.nom_piece} x{self.quantite} ({self.reparation})"

class Fournisseur(models.Model):
    pk_fournisseur = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    fiabilite = models.CharField(max_length=10, choices=FIABILITE_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_fournisseur:
            base = f"{self.nom}{self.telephone or ''}".replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            slug = slugify(base)[:240]
            self.pk_fournisseur = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.telephone or 'N/A'}"

