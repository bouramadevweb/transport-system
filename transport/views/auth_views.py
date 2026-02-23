"""
Auth Views.Py

Vues pour auth
"""

from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from django.core.cache import cache
from ..models import (Utilisateur, AuditLog)
from ..forms import (InscriptionUtilisateurForm, ConnexionForm)


from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def ratelimit(max_attempts=5, timeout=300):
    """
    Décorateur de rate limiting pour protéger contre les attaques par force brute.

    Args:
        max_attempts: Nombre maximum de tentatives autorisées
        timeout: Durée du blocage en secondes (défaut: 5 minutes)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                # Utiliser l'IP comme identifiant
                ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                if not ip:
                    ip = request.META.get('REMOTE_ADDR', 'unknown')

                cache_key = f'ratelimit:{view_func.__name__}:{ip}'
                attempts = cache.get(cache_key, 0)

                if attempts >= max_attempts:
                    messages.error(
                        request,
                        f'Trop de tentatives. Veuillez réessayer dans {timeout // 60} minutes.'
                    )
                    return render(request, 'transport/connexion.html', {
                        'form': ConnexionForm(),
                        'rate_limited': True
                    })

                # Incrémenter le compteur
                cache.set(cache_key, attempts + 1, timeout)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
@login_required
def inscription_utilisateur(request):
    if request.method == 'POST':
        form = InscriptionUtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = InscriptionUtilisateurForm()

    return render(request, 'transport/UserInscription.html', {'form': form})


@ratelimit(max_attempts=5, timeout=300)
def connexion_utilisateur(request):
    form = ConnexionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                # Enregistrer la connexion dans l'audit log
                AuditLog.log_action(
                    utilisateur=user,
                    action='LOGIN',
                    model_name='Utilisateur',
                    object_id=user.pk_utilisateur,
                    object_repr=f"{user.email}",
                    request=request
                )

                return redirect('dashboard')  # Redirige vers une page après connexion
            else:
                # Tentative de connexion échouée
                # Vérifier si l'email existe pour identifier les attaques ciblées
                try:
                    target_user = Utilisateur.objects.get(email=email)
                    # L'email existe - quelqu'un essaie d'accéder à ce compte
                    AuditLog.log_action(
                        utilisateur=target_user,
                        action='FAILED_LOGIN',
                        model_name='Utilisateur',
                        object_id=target_user.pk_utilisateur,
                        object_repr=f"Tentative échouée: {email}",
                        request=request
                    )
                except Utilisateur.DoesNotExist:
                    # L'email n'existe pas - tentative avec un compte inexistant
                    AuditLog.log_action(
                        utilisateur=None,
                        action='FAILED_LOGIN',
                        model_name='Utilisateur',
                        object_id='unknown',
                        object_repr=f"Tentative échouée: {email}",
                        request=request
                    )

                form.add_error(None, "Email ou mot de passe invalide.")

    return render(request, 'transport/connexion.html', {'form': form})

#tableau de bord

@login_required
def logout_utilisateur(request):
    # Enregistrer la déconnexion dans l'audit log avant de déconnecter
    AuditLog.log_action(
        utilisateur=request.user,
        action='LOGOUT',
        model_name='Utilisateur',
        object_id=request.user.pk_utilisateur,
        object_repr=f"{request.user.email}",
        request=request
    )

    logout(request)
    return redirect('connexion')

@login_required
def user_profile(request):
    """
    Affiche le profil de l'utilisateur connecté
    """
    return render(request, 'transport/user/profile.html', {
        'title': 'Mon Profil',
        'user': request.user
    })

@login_required
def user_settings(request):
    """
    Affiche les paramètres du compte utilisateur et gère le changement de mot de passe
    """
    password_form = None

    if request.method == 'POST':
        if 'change_password' in request.POST:
            # Changement de mot de passe
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur

                # Enregistrer le changement de mot de passe dans l'audit log
                AuditLog.log_action(
                    utilisateur=user,
                    action='CHANGE_PASSWORD',
                    model_name='Utilisateur',
                    object_id=user.pk_utilisateur,
                    object_repr=f"{user.email}",
                    request=request
                )

                messages.success(request, '✅ Votre mot de passe a été changé avec succès!')
                return redirect('user_settings')
            else:
                messages.error(request, '❌ Erreur lors du changement de mot de passe. Veuillez vérifier les informations.')

        elif 'update_email' in request.POST:
            # Mise à jour de l'email
            new_email = request.POST.get('email')
            if new_email and new_email != request.user.email:
                from ..models import Utilisateur
                if Utilisateur.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                    messages.error(request, '❌ Cet email est déjà utilisé par un autre compte.')
                else:
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, '✅ Votre email a été mis à jour avec succès!')
                return redirect('user_settings')

    # Créer le formulaire de changement de mot de passe si pas déjà créé
    if not password_form:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'transport/user/settings.html', {
        'title': 'Paramètres',
        'user': request.user,
        'password_form': password_form
    })

def rediriger_vers_connexion(request, exception=None):
    return redirect('connexion')

def rediriger_erreur_serveur(request):
    return redirect('connexion')

# deconnexion

