"""
Contrat Forms.Py

Formulaires pour contrat
"""

from django import forms
from django.core.exceptions import ValidationError

from ..models import (
    ContratTransport, PrestationDeTransports, Conteneur, Camion, Chauffeur,
    Mission
)

class ContratTransportForm(forms.ModelForm):
    class Meta:
        model = ContratTransport
        fields = [
            "numero_bl", "lieu_chargement", "destinataire",
            "conteneur", "client", "transitaire", "entreprise",
            "camion", "chauffeur",
            "montant_total", "avance_transport", "reliquat_transport", "caution",
            "statut_caution",
            "date_debut", "date_limite_retour",
            "commentaire",
            "signature_chauffeur", "signature_client", "signature_transitaire",
        ]

        labels = {
            'destinataire': 'Destination',
            'lieu_chargement': 'Lieu de chargement (Origine)',
        }

        widgets = {
            'numero_bl': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu_chargement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bamako, Port de Dakar, etc.'}),
            'destinataire': forms.TextInput(attrs={'class': 'form-control'}),

            'conteneur': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'transitaire': forms.Select(attrs={'class': 'form-select'}),
            'entreprise': forms.Select(attrs={'class': 'form-select'}),
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),

            'montant_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_montant_total',
                'step': '0.01',
                'min': '0',
                'onchange': 'calculerReliquat()',
                'oninput': 'calculerReliquat()'
            }),
            'avance_transport': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_avance_transport',
                'step': '0.01',
                'min': '0',
                'onchange': 'calculerReliquat()',
                'oninput': 'calculerReliquat()'
            }),
            'reliquat_transport': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_reliquat_transport',
                'readonly': True,
                'style': 'background-color: #e9ecef;'
            }),
            'caution': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut_caution': forms.Select(attrs={'class': 'form-select'}),

            'date_debut': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'id': 'id_date_debut',
                    'onchange': 'calculerDateLimiteRetour()'
                }
            ),
            'date_limite_retour': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'id': 'id_date_limite_retour',
                }
            ),

            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            'signature_chauffeur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_transitaire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Définir le format d'entrée pour les champs de date
        self.fields['date_debut'].input_formats = ['%Y-%m-%d']
        self.fields['date_limite_retour'].input_formats = ['%Y-%m-%d']

        # Filtrer pour afficher uniquement les camions disponibles (pas en mission en cours)
        # Récupérer tous les camions
        all_camions = Camion.objects.all()

        # Récupérer les IDs des camions en mission (statut='en cours')
        camions_en_mission_ids = Mission.objects.filter(
            statut='en cours'
        ).values_list('contrat__camion_id', flat=True).distinct()

        # Si on est en mode édition, autoriser le camion actuel même s'il est en mission
        if self.instance and self.instance.pk and self.instance.camion:
            camions_disponibles = all_camions.exclude(
                pk_camion__in=camions_en_mission_ids
            ) | Camion.objects.filter(pk_camion=self.instance.camion.pk_camion)
        else:
            # Mode création : uniquement les camions libres
            camions_disponibles = all_camions.exclude(pk_camion__in=camions_en_mission_ids)

        # Mettre à jour le queryset du champ camion
        self.fields['camion'].queryset = camions_disponibles

        # Filtrer pour afficher uniquement les chauffeurs disponibles (pas en mission en cours)
        all_chauffeurs = Chauffeur.objects.all()

        # Récupérer les IDs des chauffeurs en mission (statut='en cours')
        chauffeurs_en_mission_ids = Mission.objects.filter(
            statut='en cours'
        ).values_list('contrat__chauffeur_id', flat=True).distinct()

        # Si on est en mode édition, autoriser le chauffeur actuel même s'il est en mission
        if self.instance and self.instance.pk and self.instance.chauffeur:
            chauffeurs_disponibles = all_chauffeurs.exclude(
                pk_chauffeur__in=chauffeurs_en_mission_ids
            ) | Chauffeur.objects.filter(pk_chauffeur=self.instance.chauffeur.pk_chauffeur)
        else:
            # Mode création : uniquement les chauffeurs libres
            chauffeurs_disponibles = all_chauffeurs.exclude(pk_chauffeur__in=chauffeurs_en_mission_ids)

        # Mettre à jour le queryset du champ chauffeur
        self.fields['chauffeur'].queryset = chauffeurs_disponibles

        # Ajouter les attributs pour la sélection automatique bidirectionnelle
        self.fields['camion'].widget.attrs.update({
            'id': 'id_camion',
            'onchange': 'chargerChauffeurAffecte()'
        })

        self.fields['chauffeur'].widget.attrs.update({
            'id': 'id_chauffeur',
            'onchange': 'chargerCamionAffecte()'
        })

    def clean_numero_bl(self):
        """Valide l'unicité du numéro BL"""
        numero_bl = self.cleaned_data.get('numero_bl')

        # Si on est en mode édition (instance existe), exclure l'instance actuelle
        if self.instance and self.instance.pk:
            if ContratTransport.objects.filter(numero_bl=numero_bl).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    f"Le numéro BL '{numero_bl}' existe déjà. Veuillez utiliser un numéro BL unique."
                )
        else:
            # Mode création
            if ContratTransport.objects.filter(numero_bl=numero_bl).exists():
                raise forms.ValidationError(
                    f"Le numéro BL '{numero_bl}' existe déjà. Veuillez utiliser un numéro BL unique."
                )

        return numero_bl

    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()

        # Créer une instance temporaire pour valider avec le modèle
        if self.instance and self.instance.pk:
            # Mode édition
            temp_instance = self.instance
        else:
            # Mode création
            temp_instance = ContratTransport(**cleaned_data)

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

class PrestationDeTransportsForm(forms.ModelForm):
    class Meta:
        model = PrestationDeTransports
        fields = ['contrat_transport', 'camion', 'client', 'transitaire', 'prix_transport', 'avance', 'caution', 'solde', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'prix_transport': forms.NumberInput(attrs={'class': 'form-control'}),
            'avance': forms.NumberInput(attrs={'class': 'form-control'}),
            'caution': forms.NumberInput(attrs={'class': 'form-control'}),
            'solde': forms.NumberInput(attrs={'class': 'form-control'}),
            'contrat_transport': forms.Select(attrs={'class': 'form-select'}),
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'transitaire': forms.Select(attrs={'class': 'form-select'}),
        }

