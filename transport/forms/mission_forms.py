"""
Mission Forms.Py

Formulaires pour mission
"""

from django import forms
from django.core.exceptions import ValidationError

from ..models import (
    Mission, MissionConteneur, FraisTrajet
)

class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = '__all__'
        widgets = {
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_retour': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'itineraire': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Décrivez l\'itinéraire détaillé de la mission...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Appliquer les classes sauf si déjà définies dans widgets
            if field_name not in ['date_depart', 'date_retour', 'itineraire']:
                # Pour tous les champs simples
                field.widget.attrs['class'] = 'form-control'
                # Pour les checkbox (ex: BooleanField)
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'form-check-input'

    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()

        # Créer une instance temporaire pour valider avec le modèle
        if self.instance and self.instance.pk:
            # Mode édition
            temp_instance = self.instance
        else:
            # Mode création
            temp_instance = Mission(**cleaned_data)

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

class MissionConteneurForm(forms.ModelForm):
    class Meta:
        model = MissionConteneur
        fields = ['mission', 'conteneur']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class FraisTrajetForm(forms.ModelForm):
    class Meta:
        model = FraisTrajet
        fields = '__all__'
        widgets = {
            'origine': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'frais_route': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_carburant': forms.NumberInput(attrs={'class': 'form-control'}),
        }

