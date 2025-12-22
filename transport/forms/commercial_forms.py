"""
Commercial Forms.Py

Formulaires pour commercial
"""

from django import forms
from django.core.exceptions import ValidationError

from ..models import (
    Transitaire, Client, CompagnieConteneur, Fournisseur
)

class TransitaireForm(forms.ModelForm):
    class Meta:
        model = Transitaire
        fields = ['nom', 'telephone', 'email', 'score_fidelite', 'etat_paiement', 'commentaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'score_fidelite': forms.NumberInput(attrs={'class': 'form-control'}),
            'etat_paiement': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'type_client', 'telephone', 'email', 'score_fidelite', 'etat_paiement', 'commentaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_client': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'score_fidelite': forms.NumberInput(attrs={'class': 'form-control'}),
            'etat_paiement': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CompagnieConteneurForm(forms.ModelForm):
    class Meta:
        model = CompagnieConteneur
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'email', 'adresse', 'fiabilite', 'commentaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fiabilite': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

