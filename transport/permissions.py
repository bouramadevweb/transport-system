"""
Système de gestion des rôles et permissions
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


# ===== DÉFINITION DES RÔLES =====

ROLES = {
    'ADMIN': {
        'name': 'Administrateur',
        'description': 'Accès complet au système',
        'permissions': '*',  # Toutes les permissions
    },
    'MANAGER': {
        'name': 'Gestionnaire',
        'description': 'Gestion opérationnelle (missions, affectations, conteneurs)',
        'permissions': [
            # Missions
            'view_mission', 'add_mission', 'change_mission', 'delete_mission',
            # Conteneurs
            'view_conteneur', 'add_conteneur', 'change_conteneur',
            # Contrats
            'view_contrattransport', 'add_contrattransport', 'change_contrattransport',
            # Affectations
            'view_affectation', 'add_affectation', 'change_affectation', 'delete_affectation',
            # Chauffeurs
            'view_chauffeur', 'add_chauffeur', 'change_chauffeur',
            # Camions
            'view_camion', 'add_camion', 'change_camion',
            # Clients
            'view_client', 'add_client', 'change_client',
            # Lecture seule finance
            'view_paiementmission', 'view_cautions',
        ],
    },
    'COMPTABLE': {
        'name': 'Comptable',
        'description': 'Gestion financière (paiements, factures, rapports)',
        'permissions': [
            # Paiements
            'view_paiementmission', 'add_paiementmission', 'change_paiementmission',
            # Cautions
            'view_cautions', 'add_cautions', 'change_cautions',
            # Prestations
            'view_prestationdetransports', 'change_prestationdetransports',
            # Lecture seule missions
            'view_mission', 'view_contrattransport',
            # Lecture seule clients
            'view_client', 'view_chauffeur',
            # Frais
            'view_fraistrajet', 'add_fraistrajet', 'change_fraistrajet',
        ],
    },
    'CHAUFFEUR': {
        'name': 'Chauffeur',
        'description': 'Consultation de ses missions et paiements',
        'permissions': [
            # Lecture seule de ses données
            'view_mission',
            'view_paiementmission',
            'view_affectation',
        ],
    },
    'LECTEUR': {
        'name': 'Lecteur',
        'description': 'Lecture seule (stagiaires, auditeurs)',
        'permissions': [
            'view_mission',
            'view_chauffeur',
            'view_camion',
            'view_client',
            'view_conteneur',
            'view_affectation',
        ],
    },
}


# ===== PERMISSIONS PERSONNALISÉES =====

CUSTOM_PERMISSIONS = {
    'Mission': [
        ('terminer_mission', 'Peut terminer une mission'),
        ('annuler_mission', 'Peut annuler une mission'),
        ('exporter_missions', 'Peut exporter les missions'),
    ],
    'PaiementMission': [
        ('valider_paiement', 'Peut valider un paiement'),
        ('annuler_paiement', 'Peut annuler un paiement'),
        ('generer_facture', 'Peut générer des factures'),
    ],
    'Cautions': [
        ('rembourser_caution', 'Peut rembourser une caution'),
    ],
    'Conteneur': [
        ('marquer_maintenance', 'Peut marquer un conteneur en maintenance'),
    ],
}


# ===== FONCTION D'INITIALISATION =====

def init_roles_and_permissions():
    """
    Initialise les groupes et permissions du système
    À exécuter via: python manage.py init_permissions
    """
    from transport.models import (
        Mission, Chauffeur, Camion, Affectation,
        Client, Conteneur, ContratTransport,
        PaiementMission, Cautions, PrestationDeTransports,
        FraisTrajet
    )

    models_map = {
        'Mission': Mission,
        'Chauffeur': Chauffeur,
        'Camion': Camion,
        'Affectation': Affectation,
        'Client': Client,
        'Conteneur': Conteneur,
        'ContratTransport': ContratTransport,
        'PaiementMission': PaiementMission,
        'Cautions': Cautions,
        'PrestationDeTransports': PrestationDeTransports,
        'FraisTrajet': FraisTrajet,
    }

    # 1. Créer les permissions personnalisées
    print("📝 Création des permissions personnalisées...")
    for model_name, perms in CUSTOM_PERMISSIONS.items():
        if model_name in models_map:
            content_type = ContentType.objects.get_for_model(models_map[model_name])
            for codename, name in perms:
                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name}
                )
                if created:
                    print(f"  ✅ Créé: {codename} pour {model_name}")

    # 2. Créer les groupes et assigner les permissions
    print("\n👥 Création des groupes...")
    for role_code, role_data in ROLES.items():
        group, created = Group.objects.get_or_create(name=role_data['name'])

        if created:
            print(f"  ✅ Groupe créé: {role_data['name']}")
        else:
            print(f"  ℹ️  Groupe existant: {role_data['name']}")
            # Nettoyer les anciennes permissions
            group.permissions.clear()

        # Assigner les permissions
        if role_data['permissions'] == '*':
            # Admin: toutes les permissions
            all_permissions = Permission.objects.all()
            group.permissions.set(all_permissions)
            print(f"    → {all_permissions.count()} permissions assignées (TOUTES)")
        else:
            # Autres rôles: permissions spécifiques
            permissions = Permission.objects.filter(
                codename__in=role_data['permissions']
            )
            group.permissions.set(permissions)
            print(f"    → {permissions.count()} permissions assignées")

    print("\n✅ Initialisation terminée!")
    return True


# ===== DÉCORATEURS DE PERMISSIONS =====

def role_required(*roles):
    """
    Décorateur pour restreindre l'accès aux vues par rôle

    Usage:
        @role_required('ADMIN', 'MANAGER')
        def ma_vue(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('connexion')

            # Super admin bypass
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Vérifier si l'utilisateur a un des rôles requis
            user_groups = request.user.groups.values_list('name', flat=True)
            allowed_roles = [ROLES[role]['name'] for role in roles]

            if any(group in allowed_roles for group in user_groups):
                return view_func(request, *args, **kwargs)

            messages.error(request, "⛔ Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('dashboard')

        return wrapper
    return decorator


def permission_required(perm, raise_exception=False):
    """
    Décorateur pour vérifier une permission spécifique

    Usage:
        @permission_required('transport.valider_paiement')
        def valider_paiement(request, pk):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('connexion')

            # Super admin bypass
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Vérifier la permission
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)

            if raise_exception:
                raise PermissionDenied

            messages.error(request, f"⛔ Permission requise: {perm}")
            return redirect('dashboard')

        return wrapper
    return decorator


def can_modify_mission(user, mission):
    """
    Vérifie si un utilisateur peut modifier une mission
    Les chauffeurs ne peuvent voir que leurs propres missions
    """
    if user.is_superuser:
        return True

    # Chauffeurs: seulement leurs missions
    if user.groups.filter(name='Chauffeur').exists():
        try:
            if hasattr(user, 'chauffeur_profile'):
                return mission.contrat.chauffeur == user.chauffeur_profile
        except AttributeError:
            pass
        return False

    # Admin, Manager, Comptable: toutes les missions
    allowed_groups = ['Administrateur', 'Gestionnaire', 'Comptable']
    return user.groups.filter(name__in=allowed_groups).exists()


def can_validate_payment(user):
    """
    Vérifie si un utilisateur peut valider un paiement
    """
    if user.is_superuser:
        return True

    return user.has_perm('transport.valider_paiement') or \
           user.groups.filter(name__in=['Administrateur', 'Comptable']).exists()


def can_generate_invoice(user):
    """
    Vérifie si un utilisateur peut générer une facture
    """
    if user.is_superuser:
        return True

    return user.has_perm('transport.generer_facture') or \
           user.groups.filter(name__in=['Administrateur', 'Comptable']).exists()


# ===== HELPER FUNCTIONS =====

def get_user_role(user):
    """
    Retourne le rôle principal de l'utilisateur
    """
    if user.is_superuser:
        return 'SUPERUSER'

    groups = user.groups.values_list('name', flat=True)

    for role_code, role_data in ROLES.items():
        if role_data['name'] in groups:
            return role_code

    return None


def get_user_permissions_list(user):
    """
    Retourne la liste des permissions de l'utilisateur
    """
    if user.is_superuser:
        return Permission.objects.all()

    return user.user_permissions.all() | \
           Permission.objects.filter(group__user=user)


def assign_role_to_user(user, role_code):
    """
    Assigne un rôle à un utilisateur

    Usage:
        assign_role_to_user(user, 'MANAGER')
    """
    if role_code not in ROLES:
        raise ValueError(f"Rôle invalide: {role_code}")

    role_name = ROLES[role_code]['name']
    group = Group.objects.get(name=role_name)

    # Retirer les autres rôles
    user.groups.clear()

    # Assigner le nouveau rôle
    user.groups.add(group)

    return True
