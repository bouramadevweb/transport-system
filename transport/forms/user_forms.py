"""
User Forms.Py

Formulaires pour user
"""

from django import forms
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm
from ..models import (
    Entreprise, Utilisateur
)

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom', 'secteur_activite', 'email_contact', 'telephone_contact', 'date_creation', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'entreprise'}),
            'secteur_activite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secteur d\'activité'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email de contact'}),
            'telephone_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone de contact'}),
            'date_creation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
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

    def clean_email(self):
        """Valide l'email: unicité et format"""
        email = self.cleaned_data.get('email', '').lower().strip()

        # Vérifier que l'email n'est pas déjà utilisé
        if Utilisateur.objects.filter(email__iexact=email).exists():
            raise ValidationError("Un compte avec cet email existe déjà.")

        # Vérifier le format de l'email
        if not email or '@' not in email:
            raise ValidationError("Veuillez entrer une adresse email valide.")

        # Vérifier que le domaine n'est pas un domaine jetable commun
        domaines_interdits = ['tempmail.com', 'throwaway.com', 'mailinator.com', 'guerrillamail.com']
        domaine = email.split('@')[-1]
        if domaine in domaines_interdits:
            raise ValidationError("Les adresses email temporaires ne sont pas autorisées.")

        return email

    def clean_nom_utilisateur(self):
        """Valide le nom d'utilisateur"""
        nom = self.cleaned_data.get('nom_utilisateur', '').strip()

        if len(nom) < 2:
            raise ValidationError("Le nom d'utilisateur doit contenir au moins 2 caractères.")

        return nom

    def save(self, commit=True):
        user = super().save(commit=False)
        # Normaliser l'email en minuscules
        user.email = user.email.lower().strip()
        # pour satisfaire les dépendances héritées de AbstractUser
        user.username = user.email
        if commit:
            user.save()
        return user

class ConnexionForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

