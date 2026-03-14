"""
Vehicle Forms.Py

Formulaires pour vehicle
"""

from django import forms
from django.core.exceptions import ValidationError

from ..models import (
    Camion, Conteneur, Reparation, ReparationMecanicien, PieceReparee,
    Mecanicien, Fournisseur, Chauffeur
)

class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['entreprise', 'immatriculation', 'modele', 'capacite_tonnes', 'date_entree', 'date_sortie']
        widgets = {
            'entreprise': forms.Select(attrs={'class': 'form-select'}),
            'immatriculation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ABC-123'}),
            'modele': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Volvo FH'}),
            'capacite_tonnes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 10.5'}),
            'date_entree': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_sortie': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

class ConteneurForm(forms.ModelForm):
    class Meta:
        model = Conteneur
        fields = ['numero_conteneur', 'compagnie', 'type_conteneur', 'poids', 'client', 'transitaire']
        widgets = {
            'numero_conteneur': forms.TextInput(attrs={'class': 'form-control'}),
            'compagnie': forms.Select(attrs={'class': 'form-select'}),
            'type_conteneur': forms.TextInput(attrs={'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'transitaire': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from ..models import Client, Transitaire
        entreprise = getattr(self.user, 'entreprise', None)
        if entreprise:
            self.fields['client'].queryset = Client.objects.filter(entreprise=entreprise)
            self.fields['transitaire'].queryset = Transitaire.objects.filter(entreprise=entreprise)
        else:
            self.fields['client'].queryset = Client.objects.none()
            self.fields['transitaire'].queryset = Transitaire.objects.none()

class ReparationForm(forms.ModelForm):
    # Champ pour sélectionner les mécaniciens directement dans le formulaire
    mecaniciens = forms.ModelMultipleChoiceField(
        queryset=Mecanicien.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Mécaniciens assignés",
        help_text="Sélectionnez les mécaniciens pour cette réparation"
    )

    class Meta:
        model = Reparation
        fields = ['camion', 'chauffeur', 'date_reparation', 'cout', 'description']
        widgets = {
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'date_reparation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'cout': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        entreprise = getattr(self.user, 'entreprise', None)
        if entreprise:
            self.fields['camion'].queryset = Camion.objects.filter(entreprise=entreprise)
            self.fields['chauffeur'].queryset = Chauffeur.objects.filter(entreprise=entreprise)
            mecaniciens_qs = Mecanicien.objects.filter(entreprise=entreprise)
            if not mecaniciens_qs.exists():
                mecaniciens_qs = Mecanicien.objects.filter(entreprise__isnull=True)
            self.fields['mecaniciens'].queryset = mecaniciens_qs

        # Ajouter les attributs pour la sélection automatique bidirectionnelle
        self.fields['camion'].widget.attrs.update({
            'id': 'id_camion',
            'onchange': 'chargerChauffeurAffecte()'
        })

        self.fields['chauffeur'].widget.attrs.update({
            'id': 'id_chauffeur',
            'onchange': 'chargerCamionAffecte()'
        })

        # Si on est en mode édition, pré-remplir les mécaniciens déjà assignés
        if self.instance and self.instance.pk:
            self.fields['mecaniciens'].initial = self.instance.get_mecaniciens()

    def save(self, commit=True):
        # Sauvegarder d'abord la réparation
        reparation = super().save(commit=commit)

        if commit:
            # Supprimer les anciennes relations mécanicien
            ReparationMecanicien.objects.filter(reparation=reparation).delete()

            # Créer les nouvelles relations mécanicien
            mecaniciens = self.cleaned_data.get('mecaniciens')
            if mecaniciens:
                for mecanicien in mecaniciens:
                    ReparationMecanicien.objects.create(
                        reparation=reparation,
                        mecanicien=mecanicien
                    )

        return reparation

class ReparationMecanicienForm(forms.ModelForm):
    class Meta:
        model = ReparationMecanicien
        fields = ['reparation', 'mecanicien']
        widgets = {
            'reparation': forms.Select(attrs={'class': 'form-select'}),
            'mecanicien': forms.Select(attrs={'class': 'form-select'}),
        }

class PieceRepareeForm(forms.ModelForm):
    class Meta:
        model = PieceReparee
        fields = [
            'reparation', 'nom_piece', 'categorie', 'reference',
            'quantite', 'cout_unitaire', 'fournisseur'
        ]
        widgets = {
            'reparation': forms.Select(attrs={'class': 'form-select', 'id': 'id_reparation'}),
            'nom_piece': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'cout_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # Extraire reparation_id des kwargs
        reparation_id = kwargs.pop('reparation_id', None)
        super().__init__(*args, **kwargs)

        # Si une réparation est pré-sélectionnée
        if reparation_id:
            try:
                reparation = Reparation.objects.get(pk_reparation=reparation_id)
                # Pré-remplir le champ réparation
                self.fields['reparation'].initial = reparation
                # Filtrer le queryset pour ne montrer que cette réparation
                self.fields['reparation'].queryset = Reparation.objects.filter(pk_reparation=reparation_id)
                # Désactiver complètement le champ pour empêcher toute modification
                self.fields['reparation'].disabled = True
                self.fields['reparation'].widget.attrs['style'] = 'background-color: #e9ecef;'
                self.fields['reparation'].widget.attrs['title'] = '🔒 Réparation verrouillée'
                self.fields['reparation'].help_text = "🔒 Réparation verrouillée - Cette pièce sera ajoutée à cette réparation"
            except Reparation.DoesNotExist:
                pass

