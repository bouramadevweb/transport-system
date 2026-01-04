"""
Personnel Forms.Py

Formulaires pour personnel
"""

from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from ..models import (
    Chauffeur, Affectation, Mecanicien, Camion
)

class ChauffeurForm(forms.ModelForm):
    class Meta:
        model = Chauffeur
        fields = ["entreprise", "nom", "prenom", "email", "telephone"]
        widgets = {
            "entreprise": forms.Select(attrs={"class": "form-control"}),
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
            "prenom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Téléphone"}),
        }
        labels = {
            "nom": "Nom du chauffeur",
            "prenom": "Prénom",
            "email": "Adresse email",
            "telephone": "Numéro de téléphone",
            "entreprise": "Entreprise associée"
        }

    def clean(self):
        """
        Validation personnalisée pour éviter les doublons avant l'IntegrityError.
        """
        cleaned_data = super().clean()
        nom = cleaned_data.get("nom")
        prenom = cleaned_data.get("prenom")
        email = cleaned_data.get("email")
        entreprise = cleaned_data.get("entreprise")

        # Créer une requête de base
        chauffeurs = Chauffeur.objects.filter(
            nom=nom, prenom=prenom, email=email, entreprise=entreprise
        )

        # En mode édition, exclure l'instance actuelle
        if self.instance and self.instance.pk:
            chauffeurs = chauffeurs.exclude(pk=self.instance.pk)

        if chauffeurs.exists():
            raise forms.ValidationError("❌ Ce chauffeur existe déjà pour cette entreprise.")

        return cleaned_data

class AffectationForm(forms.ModelForm):
    class Meta:
        model = Affectation
        fields = ['chauffeur', 'camion', 'date_affectation', 'date_fin_affectation']
        widgets = {
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'date_affectation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin_affectation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'chauffeur': 'Chauffeur',
            'camion': 'Camion',
            'date_affectation': 'Date d\'affectation',
            'date_fin_affectation': 'Date de fin d\'affectation (optionnel)',
        }
        help_texts = {
            'chauffeur': 'Seuls les chauffeurs disponibles sont affichés',
            'camion': 'Seuls les camions disponibles sont affichés',
            'date_fin_affectation': 'Laissez vide si l\'affectation est toujours active',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrer les chauffeurs pour n'afficher que ceux disponibles
        if self.instance and self.instance.pk:
            # Mode édition : inclure le chauffeur actuellement affecté
            chauffeurs_disponibles = Chauffeur.objects.filter(
                models.Q(est_affecter=False) | models.Q(pk=self.instance.chauffeur.pk_chauffeur)
            )
        else:
            # Mode création : seulement les chauffeurs non affectés
            chauffeurs_disponibles = Chauffeur.objects.filter(est_affecter=False)

        self.fields['chauffeur'].queryset = chauffeurs_disponibles

        # Ajouter des messages si aucun chauffeur n'est disponible
        if not chauffeurs_disponibles.exists():
            self.fields['chauffeur'].help_text = '⚠️ Aucun chauffeur disponible. Tous les chauffeurs sont déjà affectés.'
            self.fields['chauffeur'].widget.attrs['disabled'] = True

        # Filtrer les camions pour n'afficher que ceux disponibles
        if self.instance and self.instance.pk:
            # Mode édition : inclure le camion actuellement affecté
            camions_disponibles = Camion.objects.filter(
                models.Q(est_affecter=False) | models.Q(pk=self.instance.camion.pk_camion)
            )
        else:
            # Mode création : seulement les camions non affectés
            camions_disponibles = Camion.objects.filter(est_affecter=False)

        self.fields['camion'].queryset = camions_disponibles

        # Ajouter des messages si aucun camion n'est disponible
        if not camions_disponibles.exists():
            self.fields['camion'].help_text = '⚠️ Aucun camion disponible. Tous les camions sont déjà affectés.'
            self.fields['camion'].widget.attrs['disabled'] = True

class MecanicienForm(forms.ModelForm):
    class Meta:
        model = Mecanicien
        fields = ['nom', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

