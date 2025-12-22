"""
User.Py

Modèles pour user
"""

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from .choices import *
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L’email est obligatoire')
        
        email = self.normalize_email(email)

        # Génération automatique du pk_utilisateur si non fourni
        if not extra_fields.get('pk_utilisateur'):
            base = slugify(email.split('@')[0])
            extra_fields['pk_utilisateur'] = f"{base}-{uuid4().hex[:8]}"

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('actif', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Entreprise(models.Model):
    pk_entreprise = models.CharField(max_length=250, primary_key=True, editable=False)
    nom = models.CharField(max_length=100)
    secteur_activite = models.CharField(max_length=100, blank=True, null=True)
    email_contact = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    telephone_contact = models.CharField(max_length=20, blank=True, null=True)
    date_creation = models.DateField(default=now)
    statut = models.CharField(max_length=10, choices=STATUT_ENTREPRISE_CHOICES, default='active')

    def save(self, *args, **kwargs):
        if not self.pk_entreprise:
           base = f"{self.nom}{self.secteur_activite or ''}{self.email_contact or ''}{self.date_creation}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           self.pk_entreprise = slugify(base)[:250]  # s'assurer que ça tient dans 250 caractères
        super().save(*args, **kwargs)

    # class Meta:
    #     unique_together = ('nom', 'secteur_activite', 'email_contact', 'date_creation')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'secteur_activite', 'email_contact', 'date_creation'],
                name='unique_entreprise'
            )
        ]    

    def __str__(self):
        return (f"{self.nom}, {self.secteur_activite or ''}")

class Utilisateur(AbstractUser):
    pk_utilisateur = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey("Entreprise", on_delete=models.CASCADE,null=True, blank=True)
    nom_utilisateur = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_UTILISATEUR_CHOICES, default='utilisateur')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    username = None  # Supprimer les champs non utilisés
    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UtilisateurManager()

    class Meta:
        db_table = 'Utilisateur'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.email} ({self.role})"

