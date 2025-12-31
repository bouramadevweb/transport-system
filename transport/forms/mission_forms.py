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
        fields = ['mission', 'contrat', 'type_trajet', 'date_trajet', 'origine', 'destination', 'frais_route', 'frais_carburant']
        widgets = {
            'mission': forms.Select(attrs={'class': 'form-control'}),
            'contrat': forms.Select(attrs={'class': 'form-control'}),
            'type_trajet': forms.Select(attrs={'class': 'form-control'}),
            'date_trajet': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'origine': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Abidjan'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Bouaké'
            }),
            'frais_route': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant en FCFA',
                'min': '0'
            }),
            'frais_carburant': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant en FCFA',
                'min': '0'
            }),
        }
        labels = {
            'mission': 'Mission',
            'contrat': 'Contrat',
            'type_trajet': 'Type de trajet',
            'date_trajet': 'Date du trajet',
            'origine': 'Ville de départ',
            'destination': 'Ville d\'arrivée',
            'frais_route': 'Frais de route (FCFA)',
            'frais_carburant': 'Frais de carburant (FCFA)',
        }

    def __init__(self, *args, **kwargs):
        # Récupérer les valeurs initiales pour origine et destination
        origine = kwargs.pop('origine', None)
        destination = kwargs.pop('destination', None)

        super().__init__(*args, **kwargs)

        # Pré-remplir les champs si fournis
        if origine and not self.instance.pk:
            self.fields['origine'].initial = origine
            self.fields['origine'].widget.attrs['readonly'] = True

        if destination and not self.instance.pk:
            self.fields['destination'].initial = destination
            self.fields['destination'].widget.attrs['readonly'] = True

        # Ajouter des attributs data pour la liaison mission-contrat
        self.fields['mission'].widget.attrs['data-linked-field'] = 'contrat'
        self.fields['contrat'].widget.attrs['data-linked-field'] = 'mission'

        # Filtrer les missions ET contrats disponibles selon le type de trajet pour éviter les doublons
        if not self.instance.pk:  # Seulement en mode création
            from ..models import Mission

            # Récupérer toutes les missions qui ont déjà un frais aller
            missions_avec_aller = FraisTrajet.objects.filter(
                type_trajet='aller'
            ).values_list('mission_id', flat=True)

            # Récupérer toutes les missions qui ont déjà un frais retour
            missions_avec_retour = FraisTrajet.objects.filter(
                type_trajet='retour'
            ).values_list('mission_id', flat=True)

            # 🆕 Récupérer tous les contrats qui ont déjà un frais aller
            contrats_avec_aller = FraisTrajet.objects.filter(
                type_trajet='aller'
            ).values_list('contrat_id', flat=True)

            # 🆕 Récupérer tous les contrats qui ont déjà un frais retour
            contrats_avec_retour = FraisTrajet.objects.filter(
                type_trajet='retour'
            ).values_list('contrat_id', flat=True)

            # Préparer les help_text
            self.fields['mission'].help_text = "Seules les missions sans frais du type sélectionné sont affichées"
            self.fields['contrat'].help_text = "Seuls les contrats sans frais du type sélectionné sont affichés"
            self.fields['type_trajet'].help_text = "Changez le type pour voir les missions/contrats disponibles pour ce type"

            # Note: Le filtrage dynamique sera fait en JavaScript car le type peut changer
            # On stocke les missions déjà utilisées dans des attributs data
            self.fields['mission'].widget.attrs['data-missions-avec-aller'] = ','.join(map(str, missions_avec_aller))
            self.fields['mission'].widget.attrs['data-missions-avec-retour'] = ','.join(map(str, missions_avec_retour))

            # 🆕 Stocker les contrats déjà utilisés dans des attributs data
            self.fields['contrat'].widget.attrs['data-contrats-avec-aller'] = ','.join(map(str, contrats_avec_aller))
            self.fields['contrat'].widget.attrs['data-contrats-avec-retour'] = ','.join(map(str, contrats_avec_retour))

    def clean(self):
        """Validation et synchronisation mission-contrat"""
        cleaned_data = super().clean()
        mission = cleaned_data.get('mission')
        contrat = cleaned_data.get('contrat')
        type_trajet = cleaned_data.get('type_trajet')

        # Si mission est fournie mais pas contrat, utiliser le contrat de la mission
        if mission and not contrat:
            cleaned_data['contrat'] = mission.contrat

        # Si contrat est fourni mais pas mission, vérifier la cohérence
        elif contrat and mission:
            # Vérifier que le contrat correspond bien à la mission
            if mission.contrat != contrat:
                raise ValidationError({
                    'contrat': f'Le contrat sélectionné ne correspond pas à la mission. La mission est liée au contrat {mission.contrat.pk_contrat}.'
                })

        # ✅ VALIDATION CRITIQUE 1: Vérifier qu'il n'existe pas déjà un frais de ce type pour cette mission
        if mission and type_trajet and not self.instance.pk:
            # Vérifier si un frais de ce type existe déjà pour cette mission
            frais_existant = FraisTrajet.objects.filter(
                mission=mission,
                type_trajet=type_trajet
            ).exists()

            if frais_existant:
                type_label = 'ALLER' if type_trajet == 'aller' else 'RETOUR'
                raise ValidationError({
                    'mission': f'Cette mission a déjà un trajet {type_label}. Une mission ne peut avoir qu\'un seul trajet aller et un seul trajet retour.'
                })

        # 🆕 VALIDATION CRITIQUE 2: Vérifier qu'il n'existe pas déjà un frais de ce type pour ce contrat avec une AUTRE mission
        # Note: La contrainte DB permet plusieurs frais du même type pour le même contrat SI les missions sont différentes
        # Cette validation empêche les doublons pour le même (contrat, type_trajet) avec différentes missions
        if contrat and type_trajet and mission and not self.instance.pk:
            # Récupérer le contrat final (soit fourni, soit via mission)
            contrat_final = cleaned_data.get('contrat')

            if contrat_final:
                # Vérifier si un frais de ce type existe déjà pour ce contrat avec une AUTRE mission
                frais_existant_contrat = FraisTrajet.objects.filter(
                    contrat=contrat_final,
                    type_trajet=type_trajet
                ).exclude(mission=mission).exists()

                if frais_existant_contrat:
                    type_label = 'ALLER' if type_trajet == 'aller' else 'RETOUR'
                    raise ValidationError({
                        'contrat': f'Ce contrat a déjà un trajet {type_label} pour une autre mission. Un contrat avec plusieurs missions ne peut pas avoir plusieurs trajets du même type.'
                    })

        return cleaned_data

