from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import Entreprise, Utilisateur


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
    

class ConnexionForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
