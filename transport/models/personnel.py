"""
Personnel.Py

Modèles pour personnel
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

class Chauffeur(models.Model):
    pk_chauffeur = models.CharField(max_length=250, primary_key=True, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    est_affecter = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk_chauffeur:
            base = f"{self.nom}{self.prenom}{self.email or ''}{self.entreprise.pk_entreprise}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_chauffeur = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'prenom', 'email', 'entreprise'],
                name='unique_chauffeur'
            )
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom}  {self.email}"

class Mecanicien(models.Model):
    pk_mecanicien = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_mecanicien:
            base = f"{self.nom}{self.telephone}".replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            slug = slugify(base)[:240]
            self.pk_mecanicien = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.telephone}"

class Affectation(models.Model):
    pk_affectation = models.CharField(max_length=250, primary_key=True, editable=False)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    date_affectation = models.DateField(default=now)
    date_fin_affectation = models.DateField(blank=True, null=True)

    def clean(self):
        """Validation avant sauvegarde"""
        from django.core.exceptions import ValidationError

        # Vérifier si le chauffeur est déjà affecté (affectation active)
        affectations_chauffeur_actives = Affectation.objects.filter(
            chauffeur=self.chauffeur,
            date_fin_affectation__isnull=True
        ).exclude(pk=self.pk_affectation if self.pk_affectation else None)

        if affectations_chauffeur_actives.exists():
            affectation_existante = affectations_chauffeur_actives.first()
            raise ValidationError(
                f"Le chauffeur {self.chauffeur.nom} {self.chauffeur.prenom} est déjà affecté au camion {affectation_existante.camion.immatriculation} "
                f"depuis le {affectation_existante.date_affectation}. "
                f"Veuillez d'abord terminer cette affectation avant d'en créer une nouvelle."
            )

        # Vérifier si le camion est déjà affecté (affectation active)
        affectations_camion_actives = Affectation.objects.filter(
            camion=self.camion,
            date_fin_affectation__isnull=True
        ).exclude(pk=self.pk_affectation if self.pk_affectation else None)

        if affectations_camion_actives.exists():
            affectation_existante = affectations_camion_actives.first()
            raise ValidationError(
                f"Ce camion {self.camion.immatriculation} est déjà affecté au chauffeur {affectation_existante.chauffeur.nom} {affectation_existante.chauffeur.prenom} "
                f"depuis le {affectation_existante.date_affectation}. "
                f"Veuillez d'abord terminer cette affectation avant d'en créer une nouvelle."
            )

    def save(self, *args, **kwargs):
        # Générer la clé primaire
        if not self.pk_affectation:
            base = f"{self.chauffeur.pk_chauffeur}_{self.camion.pk_camion}_{self.date_affectation}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_affectation = slugify(base)[:250]

        # Valider avant de sauvegarder
        self.full_clean()

        # Mettre à jour le statut du chauffeur et du camion
        if self.date_fin_affectation is None:
            # Affectation active - marquer le chauffeur et le camion comme affectés
            self.chauffeur.est_affecter = True
            self.chauffeur.save(update_fields=['est_affecter'])

            self.camion.est_affecter = True
            self.camion.save(update_fields=['est_affecter'])
        else:
            # Affectation terminée - vérifier s'il y a d'autres affectations actives pour le chauffeur
            autres_affectations_chauffeur = Affectation.objects.filter(
                chauffeur=self.chauffeur,
                date_fin_affectation__isnull=True
            ).exclude(pk=self.pk_affectation).exists()

            if not autres_affectations_chauffeur:
                self.chauffeur.est_affecter = False
                self.chauffeur.save(update_fields=['est_affecter'])

            # Vérifier s'il y a d'autres affectations actives pour le camion
            autres_affectations_camion = Affectation.objects.filter(
                camion=self.camion,
                date_fin_affectation__isnull=True
            ).exclude(pk=self.pk_affectation).exists()

            if not autres_affectations_camion:
                self.camion.est_affecter = False
                self.camion.save(update_fields=['est_affecter'])

        super().save(*args, **kwargs)

    def terminer_affectation(self, date_fin=None):
        """Méthode pour terminer proprement une affectation"""
        from django.utils import timezone

        if date_fin is None:
            date_fin = timezone.now().date()

        self.date_fin_affectation = date_fin
        self.save()

    # class Meta:
    #     unique_together = ('chauffeur', 'camion', 'date_affectation')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['chauffeur', 'camion', 'date_affectation'],
                name='unique_affectation'
            )
        ]

    def __str__(self):
        statut = "Active" if self.date_fin_affectation is None else f"Terminée le {self.date_fin_affectation}"
        return f"{self.chauffeur} → {self.camion} ({statut})"

