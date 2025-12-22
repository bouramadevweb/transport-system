"""
Vues CRUD pour la gestion des utilisateurs
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from transport.models import Utilisateur
from transport.permissions import role_required, assign_role_to_user, get_user_role, ROLES
import uuid


@login_required
@role_required('ADMIN')
def utilisateur_list(request):
    """
    Liste de tous les utilisateurs
    """
    utilisateurs = Utilisateur.objects.exclude(
        pk_utilisateur=''
    ).exclude(
        pk_utilisateur__isnull=True
    ).prefetch_related('groups').order_by('nom_utilisateur', 'email')

    # Ajouter les infos de rôle à chaque utilisateur
    for user in utilisateurs:
        user.role_code = get_user_role(user)
        if user.role_code == 'SUPERUSER':
            user.role_display = 'Super Admin'
        elif user.role_code in ROLES:
            user.role_display = ROLES[user.role_code]['name']
        else:
            user.role_display = 'Aucun rôle'
        user.display_name = user.nom_utilisateur or user.email or f"User {user.pk_utilisateur}"

    # Calculer les statistiques
    stats = {
        'actifs': utilisateurs.filter(is_active=True).count(),
        'staff': utilisateurs.filter(is_staff=True).count(),
    }

    context = {
        'utilisateurs': utilisateurs,
        'roles': ROLES,
        'stats': stats,
    }

    return render(request, 'transport/utilisateurs/utilisateur_list.html', context)


@login_required
@role_required('ADMIN')
def utilisateur_create(request):
    """
    Créer un nouvel utilisateur
    """
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = request.POST.get('nom_utilisateur', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        role = request.POST.get('role', '')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'

        # Validation
        errors = []

        if not email:
            errors.append("L'email est obligatoire")
        elif Utilisateur.objects.filter(email=email).exists():
            errors.append("Cet email est déjà utilisé")

        if not password:
            errors.append("Le mot de passe est obligatoire")
        elif len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        elif password != password_confirm:
            errors.append("Les mots de passe ne correspondent pas")

        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'roles': ROLES,
                'form_data': request.POST,
            }
            return render(request, 'transport/utilisateurs/utilisateur_form.html', context)

        try:
            # Créer l'utilisateur
            pk_utilisateur = f'user-{uuid.uuid4().hex[:12]}'

            user = Utilisateur.objects.create(
                pk_utilisateur=pk_utilisateur,
                nom_utilisateur=nom_utilisateur,
                email=email,
                password=make_password(password),
                actif=is_active,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=False
            )

            # Assigner le rôle si spécifié
            if role and role in ROLES:
                assign_role_to_user(user, role)

            messages.success(request, f"✅ Utilisateur '{user.display_name or email}' créé avec succès!")
            return redirect('utilisateur_list')

        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la création: {str(e)}")

    context = {
        'roles': ROLES,
        'form_data': {},
    }

    return render(request, 'transport/utilisateurs/utilisateur_form.html', context)


@login_required
@role_required('ADMIN')
def utilisateur_update(request, pk):
    """
    Modifier un utilisateur existant
    """
    utilisateur = get_object_or_404(Utilisateur, pk_utilisateur=pk)

    if request.method == 'POST':
        # Récupérer les données
        nom_utilisateur = request.POST.get('nom_utilisateur', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        role = request.POST.get('role', '')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'

        # Validation
        errors = []

        if not email:
            errors.append("L'email est obligatoire")
        elif Utilisateur.objects.filter(email=email).exclude(pk_utilisateur=pk).exists():
            errors.append("Cet email est déjà utilisé par un autre utilisateur")

        # Validation du mot de passe seulement s'il est fourni
        if password:
            if len(password) < 8:
                errors.append("Le mot de passe doit contenir au moins 8 caractères")
            elif password != password_confirm:
                errors.append("Les mots de passe ne correspondent pas")

        if errors:
            for error in errors:
                messages.error(request, error)
            current_role = get_user_role(utilisateur)
            context = {
                'utilisateur': utilisateur,
                'roles': ROLES,
                'current_role': current_role,
                'is_update': True,
                'form_data': request.POST,
            }
            return render(request, 'transport/utilisateurs/utilisateur_form.html', context)

        try:
            # Mettre à jour l'utilisateur
            utilisateur.nom_utilisateur = nom_utilisateur
            utilisateur.email = email
            utilisateur.actif = is_active
            utilisateur.is_active = is_active
            utilisateur.is_staff = is_staff

            # Changer le mot de passe seulement s'il est fourni
            if password:
                utilisateur.password = make_password(password)

            utilisateur.save()

            # Mettre à jour le rôle
            if role == 'NONE':
                utilisateur.groups.clear()
            elif role in ROLES:
                assign_role_to_user(utilisateur, role)

            messages.success(request, f"✅ Utilisateur '{utilisateur.display_name or email}' modifié avec succès!")
            return redirect('utilisateur_list')

        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la modification: {str(e)}")

    # GET: afficher le formulaire
    current_role = get_user_role(utilisateur)
    utilisateur.display_name = utilisateur.nom_utilisateur or utilisateur.email or f"User {utilisateur.pk_utilisateur}"

    context = {
        'utilisateur': utilisateur,
        'roles': ROLES,
        'current_role': current_role,
        'is_update': True,
        'form_data': {
            'nom_utilisateur': utilisateur.nom_utilisateur,
            'email': utilisateur.email,
            'is_active': utilisateur.is_active,
            'is_staff': utilisateur.is_staff,
        },
    }

    return render(request, 'transport/utilisateurs/utilisateur_form.html', context)


@login_required
@role_required('ADMIN')
def utilisateur_delete(request, pk):
    """
    Supprimer un utilisateur
    """
    utilisateur = get_object_or_404(Utilisateur, pk_utilisateur=pk)

    # Empêcher la suppression du superuser principal
    if utilisateur.is_superuser and utilisateur.email == 'bcoul2002@yahoo.fr':
        messages.error(request, "❌ Impossible de supprimer le super administrateur principal!")
        return redirect('utilisateur_list')

    # Empêcher l'auto-suppression
    if utilisateur.pk_utilisateur == request.user.pk_utilisateur:
        messages.error(request, "❌ Vous ne pouvez pas supprimer votre propre compte!")
        return redirect('utilisateur_list')

    utilisateur.display_name = utilisateur.nom_utilisateur or utilisateur.email or f"User {utilisateur.pk_utilisateur}"

    if request.method == 'POST':
        try:
            display_name = utilisateur.display_name
            utilisateur.delete()
            messages.success(request, f"✅ Utilisateur '{display_name}' supprimé avec succès!")
            return redirect('utilisateur_list')
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la suppression: {str(e)}")

    context = {
        'utilisateur': utilisateur,
    }

    return render(request, 'transport/utilisateurs/utilisateur_confirm_delete.html', context)
