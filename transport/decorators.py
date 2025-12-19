"""
Décorateurs personnalisés pour la gestion des permissions par rôle
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Décorateur pour vérifier que l'utilisateur a l'un des rôles spécifiés

    Usage:
        @role_required('admin', 'manager')
        def ma_vue(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Vérifier si l'utilisateur a l'un des rôles requis
            if hasattr(request.user, 'role') and request.user.role in roles:
                return view_func(request, *args, **kwargs)

            # Vérifier si c'est un superuser
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Accès refusé
            messages.error(
                request,
                f"❌ Accès refusé. Cette page est réservée aux rôles: {', '.join(roles)}"
            )
            return redirect('dashboard')

        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Décorateur pour limiter l'accès aux administrateurs uniquement

    Usage:
        @admin_required
        def ma_vue_admin(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "❌ Accès refusé. Cette page est réservée aux administrateurs."
        )
        return redirect('dashboard')

    return _wrapped_view


def manager_or_admin_required(view_func):
    """
    Décorateur pour limiter l'accès aux managers et administrateurs

    Usage:
        @manager_or_admin_required
        def ma_vue_manager(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if hasattr(request.user, 'role') and request.user.role in ['admin', 'manager']:
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "❌ Accès refusé. Cette page est réservée aux managers et administrateurs."
        )
        return redirect('dashboard')

    return _wrapped_view


def can_validate_payment(view_func):
    """
    Décorateur pour vérifier que l'utilisateur peut valider des paiements
    Réservé aux admin et manager uniquement
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if hasattr(request.user, 'role') and request.user.role in ['admin', 'manager']:
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "❌ Vous n'avez pas la permission de valider des paiements."
        )
        return redirect('paiement_mission_list')

    return _wrapped_view


def can_delete_data(view_func):
    """
    Décorateur pour vérifier que l'utilisateur peut supprimer des données
    Réservé aux admin uniquement
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "❌ Vous n'avez pas la permission de supprimer des données."
        )
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    return _wrapped_view


def can_manage_users(view_func):
    """
    Décorateur pour vérifier que l'utilisateur peut gérer d'autres utilisateurs
    Réservé aux admin uniquement
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "❌ Vous n'avez pas la permission de gérer les utilisateurs."
        )
        return redirect('dashboard')

    return _wrapped_view


def own_data_or_manager(view_func):
    """
    Décorateur pour vérifier que l'utilisateur accède à ses propres données
    ou qu'il est manager/admin

    Usage:
        @own_data_or_manager
        def update_chauffeur(request, pk):
            # pk doit correspondre au chauffeur lié à l'utilisateur
            # ou l'utilisateur doit être manager/admin
            ...
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Les admin et manager ont toujours accès
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role in ['admin', 'manager']):
            return view_func(request, *args, **kwargs)

        # Pour les chauffeurs, vérifier qu'ils accèdent à leurs propres données
        pk = kwargs.get('pk')
        if hasattr(request.user, 'chauffeur') and str(request.user.chauffeur.pk_chauffeur) == str(pk):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "❌ Vous ne pouvez accéder qu'à vos propres données."
        )
        return redirect('dashboard')

    return _wrapped_view
