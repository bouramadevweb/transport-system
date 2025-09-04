from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import Entreprise, Utilisateur,Chauffeur,Camion,Affectation,Transitaire,Client,CompagnieConteneur,Conteneur,ContratTransport,PrestationDeTransports,Cautions,FraisTrajet,Mission


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
            'conteneur', 'client', 'transitaire', 'entreprise', 
            'camion', 'chauffeur', 'date_debut', 'date_limite_retour',
            'caution', 'statut_caution', 'commentaire',
            'signature_chauffeur', 'signature_client', 'signature_transitaire'
        ]
        widgets = {
            'conteneur': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'transitaire': forms.Select(attrs={'class': 'form-select'}),
            'entreprise': forms.Select(attrs={'class': 'form-select'}),
            'camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_limite_retour': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'caution': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut_caution': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'signature_chauffeur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'signature_transitaire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }   

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
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'non_rembourser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_rembourser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'montant_rembourser': forms.NumberInput(attrs={'class': 'form-control'}),
        }
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # Pour tous les champs simples
            field.widget.attrs['class'] = 'form-control'
            # Pour les checkbox (ex: BooleanField)
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'  

class ConnexionForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
