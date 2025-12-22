"""
Commercial.Py

Modèles pour commercial
"""

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from .choices import *

class Transitaire(models.Model):
    pk_transitaire = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk_transitaire:
            base = f"{self.nom}{self.telephone}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_transitaire = slugify(base)[:250]
        super().save(*args, **kwargs)
    # class Meta:
    #     unique_together = ('nom', 'telephone')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'telephone'],
                name='unique_transitaire'
            )
        ]

    def __str__(self):
        return f"{self.nom}"

class Client(models.Model):
    pk_client = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    type_client = models.CharField(max_length=50, choices=TYPE_CLIENT_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

    def save(self,*args, **kwargs):
        if not self.pk_client:
            base = f"{self.nom}{self.type_client}{self.telephone}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_client =slugify(base)[:250]
        super().save(*args, **kwargs) 

    # class Meta:
    #       unique_together = ("nom","type_client","telephone") 

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'type_client', 'telephone'],
                name='unique_client'
            )
        ]

    def __str__(self):
        return f"{self.nom}"

