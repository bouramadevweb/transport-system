"""
Vues pour la gestion des permissions et rôles
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from transport.models import Utilisateur
from transport.permissions import ROLES, role_required, assign_role_to_user, get_user_role


@login_required
@role_required('ADMIN')
def permissions_dashboard(request):
    """
    Dashboard de gestion des permissions
    """
    users = Utilisateur.objects.all().prefetch_related('groups')
    groups = Group.objects.all().prefetch_related('permissions')

    # Statistiques
    total_users_count = users.count()
    valid_users = users.exclude(pk_utilisateur='').exclude(pk_utilisateur__isnull=True)

    stats = {
        'total_users': total_users_count,
        'users_with_role': valid_users.exclude(groups=None).count(),
        'users_without_role': valid_users.filter(groups=None).count(),
        'total_groups': groups.count(),
        'invalid_users': total_users_count - valid_users.count(),
    }

    # Utilisateurs par rôle
    users_by_role = {}
    for group in groups:
        users_by_role[group.name] = group.user_set.count()

    context = {
        'stats': stats,
        'users_by_role': users_by_role,
        'groups': groups,
        'roles': ROLES,
    }

    return render(request, 'transport/permissions/dashboard.html', context)


@login_required
@role_required('ADMIN')
def user_permissions_list(request):
    """
    Liste des utilisateurs avec leurs rôles
    """
    # Exclure les utilisateurs sans pk_utilisateur (données corrompues)
    users = Utilisateur.objects.exclude(pk_utilisateur='').exclude(pk_utilisateur__isnull=True).prefetch_related('groups').order_by('nom_utilisateur')

    # Ajouter le rôle principal à chaque utilisateur
    for user in users:
        user.main_role = get_user_role(user)
        user.role_display = ROLES.get(user.main_role, {}).get('name', 'Aucun rôle') if user.main_role and user.main_role != 'SUPERUSER' else 'Super Admin' if user.is_superuser else 'Aucun rôle'
        # Ajouter un nom d'affichage
        user.display_name = user.nom_utilisateur or user.email or f"User {user.pk_utilisateur}"

    context = {
        'users': users,
        'roles': ROLES,
    }

    return render(request, 'transport/permissions/user_list.html', context)


@login_required
@role_required('ADMIN')
def assign_user_role(request, user_id):
    """
    Assigner un rôle à un utilisateur
    """
    user = get_object_or_404(Utilisateur, pk=user_id)

    if request.method == 'POST':
        role_code = request.POST.get('role')

        if role_code == 'NONE':
            # Retirer tous les rôles
            user.groups.clear()
            display_name = user.nom_utilisateur or user.email or f"User {user.pk_utilisateur}"
            messages.success(request, f"✅ Tous les rôles ont été retirés pour {display_name}")
        elif role_code in ROLES:
            try:
                assign_role_to_user(user, role_code)
                display_name = user.nom_utilisateur or user.email or f"User {user.pk_utilisateur}"
                messages.success(request, f"✅ Rôle '{ROLES[role_code]['name']}' assigné à {display_name}")
            except Exception as e:
                messages.error(request, f"❌ Erreur: {str(e)}")
        else:
            messages.error(request, "❌ Rôle invalide")

        return redirect('user_permissions_list')

    # GET: afficher le formulaire
    current_role = get_user_role(user)
    user.display_name = user.nom_utilisateur or user.email or f"User {user.pk_utilisateur}"

    context = {
        'user': user,
        'current_role': current_role,
        'roles': ROLES,
    }

    return render(request, 'transport/permissions/assign_role.html', context)


@login_required
@role_required('ADMIN')
def group_details(request, group_id):
    """
    Détails d'un groupe avec ses permissions
    """
    group = get_object_or_404(Group, pk=group_id)

    permissions = group.permissions.all().order_by('content_type__model', 'codename')

    # Organiser par modèle
    permissions_by_model = {}
    for perm in permissions:
        model = perm.content_type.model
        if model not in permissions_by_model:
            permissions_by_model[model] = []
        permissions_by_model[model].append(perm)

    context = {
        'group': group,
        'permissions_by_model': permissions_by_model,
        'total_permissions': permissions.count(),
        'members_count': group.user_set.count(),
        'members': group.user_set.all()[:10],  # Premiers 10 membres
    }

    return render(request, 'transport/permissions/group_details.html', context)


@login_required
def my_permissions(request):
    """
    Afficher les permissions de l'utilisateur connecté
    """
    user = request.user
    user_role = get_user_role(user)

    user_permissions = user.user_permissions.all() | \
                      user.groups.first().permissions.all() if user.groups.exists() else user.user_permissions.all()

    # Organiser par modèle
    permissions_by_model = {}
    for perm in user_permissions:
        model = perm.content_type.model
        if model not in permissions_by_model:
            permissions_by_model[model] = []
        permissions_by_model[model].append(perm)

    context = {
        'user_role': user_role,
        'role_info': ROLES.get(user_role) if user_role else None,
        'permissions_by_model': permissions_by_model,
        'total_permissions': user_permissions.count(),
        'is_superuser': user.is_superuser,
    }

    return render(request, 'transport/permissions/my_permissions.html', context)
