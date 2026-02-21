"""
Contrat Forms.Py

Formulaires pour contrat
"""

from decimal import Decimal
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

        # L'ID du conteneur est défini pour l'event listener JavaScript
        # (l'event listener est configuré dans contrat-form.js)
        self.fields['conteneur'].widget.attrs.update({
            'id': 'id_conteneur'
        })

        # Ajouter les IDs explicites pour les champs client et transitaire
        self.fields['client'].widget.attrs.update({
            'id': 'id_client'
        })

        self.fields['transitaire'].widget.attrs.update({
            'id': 'id_transitaire'
        })

    def clean_numero_bl(self):
        """Valide l'unicité du numéro BL"""
        numero_bl = self.cleaned_data.get('numero_bl')

        if not numero_bl:
            raise forms.ValidationError("Le numéro BL est obligatoire.")

        # Nettoyer le numéro BL
        numero_bl = numero_bl.strip().upper()

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

    def clean_montant_total(self):
        """Valide le montant total"""
        montant = self.cleaned_data.get('montant_total')

        if montant is None:
            raise forms.ValidationError("Le montant total est obligatoire.")

        if montant <= 0:
            raise forms.ValidationError("Le montant total doit être supérieur à 0.")

        if montant > Decimal('999999999999'):
            raise forms.ValidationError("Le montant total est trop élevé.")

        return montant

    def clean_avance_transport(self):
        """Valide l'avance transport"""
        avance = self.cleaned_data.get('avance_transport')

        if avance is None:
            raise forms.ValidationError("L'avance transport est obligatoire.")

        if avance < 0:
            raise forms.ValidationError("L'avance transport ne peut pas être négative.")

        return avance

    def clean_caution(self):
        """Valide la caution"""
        caution = self.cleaned_data.get('caution')

        if caution is None:
            raise forms.ValidationError("La caution est obligatoire.")

        if caution < 0:
            raise forms.ValidationError("La caution ne peut pas être négative.")

        return caution

    def clean_conteneur(self):
        """Valide que le conteneur n'est pas déjà en mission"""
        conteneur = self.cleaned_data.get('conteneur')

        if not conteneur:
            raise forms.ValidationError("Le conteneur est obligatoire.")

        # Vérifier si le conteneur est déjà en mission
        missions_en_cours = Mission.objects.filter(
            contrat__conteneur=conteneur,
            statut='en cours'
        )

        # Exclure le contrat actuel si on est en mode édition
        if self.instance and self.instance.pk:
            missions_en_cours = missions_en_cours.exclude(contrat__pk_contrat=self.instance.pk)

        if missions_en_cours.exists():
            raise forms.ValidationError(
                f"Le conteneur {conteneur.numero_conteneur} est déjà en mission. "
                "Veuillez terminer la mission en cours avant de créer un nouveau contrat."
            )

        return conteneur

    def clean_destinataire(self):
        """Valide la destination"""
        destinataire = self.cleaned_data.get('destinataire')

        if not destinataire:
            raise forms.ValidationError("La destination est obligatoire.")

        # Nettoyer et capitaliser
        destinataire = destinataire.strip().title()

        if len(destinataire) < 2:
            raise forms.ValidationError("La destination doit contenir au moins 2 caractères.")

        return destinataire

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
            'prix_transport': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'avance': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'caution': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'solde': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'contrat_transport': forms.Select(attrs={'class': 'form-select'}),
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'transitaire': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_prix_transport(self):
        """Valide le prix de transport"""
        prix = self.cleaned_data.get('prix_transport')
        if prix is not None and prix < 0:
            raise forms.ValidationError("Le prix de transport ne peut pas être négatif.")
        return prix

    def clean_avance(self):
        """Valide l'avance"""
        avance = self.cleaned_data.get('avance')
        if avance is not None and avance < 0:
            raise forms.ValidationError("L'avance ne peut pas être négative.")
        return avance

    def clean_caution(self):
        """Valide la caution"""
        caution = self.cleaned_data.get('caution')
        if caution is not None and caution < 0:
            raise forms.ValidationError("La caution ne peut pas être négative.")
        return caution

    def clean(self):
        """Validation globale"""
        cleaned_data = super().clean()
        prix = cleaned_data.get('prix_transport')
        avance = cleaned_data.get('avance')

        if prix and avance and avance > prix:
            self.add_error('avance', "L'avance ne peut pas dépasser le prix de transport.")

        return cleaned_data

