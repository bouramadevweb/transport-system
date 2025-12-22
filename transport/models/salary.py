"""
Salary.Py

Modèles pour salary
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

class Salaire(models.Model):
    """
    Modèle pour gérer les bulletins de salaire des employés (chauffeurs et autres)
    """
    pk_salaire = models.CharField(max_length=255, primary_key=True)
    
    # Employé (soit chauffeur, soit utilisateur)
    chauffeur = models.ForeignKey(
        Chauffeur,
        on_delete=models.CASCADE,
        related_name='salaires',
        null=True,
        blank=True
    )
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='salaires_employe',
        null=True,
        blank=True
    )
    
    # Période
    mois = models.IntegerField(choices=MOIS_CHOICES)
    annee = models.IntegerField()
    
    # Salaire de base et heures supplémentaires
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    heures_supplementaires = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    taux_heure_supp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totaux calculés
    total_primes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Paiement
    date_paiement = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_SALAIRE_CHOICES, default='brouillon')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_SALAIRE_CHOICES, null=True, blank=True)
    
    # Métadonnées
    notes = models.TextField(blank=True, default='')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        related_name='salaires_crees',
        null=True
    )
    
    class Meta:
        verbose_name = 'Salaire'
        verbose_name_plural = 'Salaires'
        ordering = ['-annee', '-mois']
        indexes = [
            models.Index(fields=['mois', 'annee']),
            models.Index(fields=['statut']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(chauffeur__isnull=False) | models.Q(utilisateur__isnull=False),
                name='salaire_has_employee'
            )
        ]
    
    def save(self, *args, **kwargs):
        if not self.pk_salaire:
            # Générer un ID unique
            employe_id = ''
            if self.chauffeur:
                employe_id = f"C-{self.chauffeur.pk_chauffeur[:8]}"
            elif self.utilisateur:
                employe_id = f"U-{self.utilisateur.pk_utilisateur[:8]}"
            
            self.pk_salaire = f"SAL-{self.annee}{self.mois:02d}-{employe_id}-{uuid4().hex[:6].upper()}"
        
        # Calculer le salaire net
        self.calculer_salaire_net()
        
        super().save(*args, **kwargs)
    
    def calculer_salaire_net(self):
        """Calcule le salaire net en fonction du salaire de base, heures supp, primes et déductions"""
        montant_heures_supp = self.heures_supplementaires * self.taux_heure_supp
        salaire_brut = self.salaire_base + montant_heures_supp + self.total_primes
        self.salaire_net = salaire_brut - self.total_deductions
    
    def get_employe_nom(self):
        """Retourne le nom de l'employé"""
        if self.chauffeur:
            return f"{self.chauffeur.nom} {self.chauffeur.prenom}"
        elif self.utilisateur:
            return self.utilisateur.nom_utilisateur or self.utilisateur.email
        return "Employé inconnu"
    
    def get_periode(self):
        """Retourne la période sous forme lisible"""
        mois_nom = dict(MOIS_CHOICES).get(self.mois, '')
        return f"{mois_nom} {self.annee}"
    
    def __str__(self):
        return f"Salaire {self.get_employe_nom()} - {self.get_periode()}"

class Prime(models.Model):
    """
    Modèle pour gérer les primes et bonus
    """
    pk_prime = models.CharField(max_length=255, primary_key=True)
    salaire = models.ForeignKey(Salaire, on_delete=models.CASCADE, related_name='primes')
    type_prime = models.CharField(max_length=100)  # ex: Prime de performance, Prime d'ancienneté, etc.
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    date_attribution = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Prime'
        verbose_name_plural = 'Primes'
    
    def save(self, *args, **kwargs):
        if not self.pk_prime:
            self.pk_prime = f"PRIME-{uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
        
        # Mettre à jour le total des primes du salaire
        self.salaire.total_primes = sum(p.montant for p in self.salaire.primes.all())
        self.salaire.save()
    
    def delete(self, *args, **kwargs):
        salaire = self.salaire
        super().delete(*args, **kwargs)
        
        # Mettre à jour le total des primes du salaire
        salaire.total_primes = sum(p.montant for p in salaire.primes.all())
        salaire.save()
    
    def __str__(self):
        return f"{self.type_prime} - {self.montant} FCFA"

class Deduction(models.Model):
    """
    Modèle pour gérer les déductions et retenues sur salaire
    """
    pk_deduction = models.CharField(max_length=255, primary_key=True)
    salaire = models.ForeignKey(Salaire, on_delete=models.CASCADE, related_name='deductions')
    type_deduction = models.CharField(max_length=100)  # ex: Avance, CSS, IPRES, etc.
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    date_deduction = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Déduction'
        verbose_name_plural = 'Déductions'
    
    def save(self, *args, **kwargs):
        if not self.pk_deduction:
            self.pk_deduction = f"DED-{uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
        
        # Mettre à jour le total des déductions du salaire
        self.salaire.total_deductions = sum(d.montant for d in self.salaire.deductions.all())
        self.salaire.save()
    
    def delete(self, *args, **kwargs):
        salaire = self.salaire
        super().delete(*args, **kwargs)
        
        # Mettre à jour le total des déductions du salaire
        salaire.total_deductions = sum(d.montant for d in salaire.deductions.all())
        salaire.save()
    
    def __str__(self):
        return f"{self.type_deduction} - {self.montant} FCFA"

