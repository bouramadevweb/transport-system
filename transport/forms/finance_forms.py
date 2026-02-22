"""
Finance Forms.Py

Formulaires pour finance
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from ..models import (
    Cautions, PaiementMission
)

class CautionsForm(forms.ModelForm):
    class Meta:
        model = Cautions
        fields = '__all__'
        widgets = {
            'conteneur': forms.Select(attrs={'class': 'form-select'}),
            'contrat': forms.Select(attrs={'class': 'form-select'}),
            'transitaire': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_montant',
                'step': '0.01',
                'min': '0'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_statut',
                'onchange': 'gererEtatCaution()'
            }),
            'montant_rembourser': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_montant_rembourser',
                'step': '0.01',
                'min': '0'
            }),
        }

    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()

        # Créer une instance temporaire pour valider avec le modèle
        if self.instance and self.instance.pk:
            # Mode édition
            temp_instance = self.instance
        else:
            # Mode création
            temp_instance = Cautions(**cleaned_data)

        # Mettre à jour les attributs de l'instance temporaire
        for field, value in cleaned_data.items():
            setattr(temp_instance, field, value)

        # Appeler la validation du modèle
        try:
            temp_instance.clean()
        except ValidationError as e:
            # Convertir les erreurs du modèle en erreurs de formulaire
            if hasattr(e, 'error_dict'):
                for field, errors in e.error_dict.items():
                    for error in errors:
                        self.add_error(field, error)
            else:
                raise

        return cleaned_data

class PaiementMissionForm(forms.ModelForm):
    class Meta:
        model = PaiementMission
        fields = [
            'mission',
            'caution',
            'prestation',
            'montant_total',
            'commission_transitaire',
            'caution_est_retiree',
            'mode_paiement',
            'observation',
        ]
        widgets = {
            'mission': forms.Select(attrs={'class': 'form-select'}),
            'caution': forms.Select(attrs={'class': 'form-select'}),
            'prestation': forms.Select(attrs={'class': 'form-select'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'commission_transitaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'caution_est_retiree': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        montant_total = cleaned_data.get('montant_total')
        mission = cleaned_data.get('mission')
        prestation = cleaned_data.get('prestation')

        # Montant doit être positif
        if montant_total is not None and montant_total <= Decimal('0'):
            self.add_error('montant_total', 'Le montant total doit être supérieur à 0.')

        # La prestation doit correspondre à la mission
        if mission and prestation and mission.prestation_transport_id != prestation.pk:
            self.add_error(
                'prestation',
                'La prestation sélectionnée ne correspond pas à cette mission.'
            )

        return cleaned_data

