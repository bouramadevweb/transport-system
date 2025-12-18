from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.core.exceptions import ValidationError
from .models import Entreprise, Utilisateur,Chauffeur,Camion,Affectation,Transitaire,Client,CompagnieConteneur,Conteneur,ContratTransport,PrestationDeTransports,Cautions,FraisTrajet,Mission,MissionConteneur,PaiementMission,Mecanicien,Fournisseur, Reparation,ReparationMecanicien,PieceReparee


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom', 'secteur_activite', 'email_contact', 'telephone_contact', 'date_creation', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'entreprise'}),
            'secteur_activite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secteur d\'activité'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email de contact'}),
            'telephone_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone de contact'}),
            'date_creation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'statut':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class InscriptionUtilisateurForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['nom_utilisateur', 'email', 'role', 'entreprise', 'password1', 'password2']

        widgets = {
            'nom_utilisateur': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'entreprise': forms.Select(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        # pour satisfaire les dépendances héritées de AbstractUser
        user.username = user.email  
        if commit:
            user.save()
        return user
    


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

        if Chauffeur.objects.filter(
            nom=nom, prenom=prenom, email=email, entreprise=entreprise
        ).exists():
            raise forms.ValidationError("❌ Ce chauffeur existe déjà pour cette entreprise.")

        return cleaned_data



class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['entreprise', 'immatriculation', 'modele', 'capacite_tonnes']
        widgets = {
            'entreprise': forms.Select(attrs={'class': 'form-select'}),
            'immatriculation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ABC-123'}),
            'modele': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Volvo FH'}),
            'capacite_tonnes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 10.5'}),
        }

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

            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date_debut',
                'onchange': 'calculerDateLimiteRetour()'
            }),
            'date_limite_retour': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date_limite_retour',
                'readonly': True,
                'style': 'background-color: #e9ecef;'
            }),

            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            'signature_chauffeur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_transitaire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrer pour afficher uniquement les camions disponibles (pas en mission en cours)
        from .models import Camion, Mission, ContratTransport

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

class MecanicienForm(forms.ModelForm):
    class Meta:
        model = Mecanicien
        fields = ['nom', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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

class ReparationForm(forms.ModelForm):
    # Champ pour sélectionner les mécaniciens directement dans le formulaire
    mecaniciens = forms.ModelMultipleChoiceField(
        queryset=Mecanicien.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Mécaniciens assignés",
        help_text="Sélectionnez au moins un mécanicien pour cette réparation"
    )

    class Meta:
        model = Reparation
        fields = ['camion', 'chauffeur', 'date_reparation', 'cout', 'description']
        widgets = {
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'date_reparation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cout': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            from .models import Reparation
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

class ConnexionForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
