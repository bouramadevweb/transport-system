"""
Module de vues refactorisé pour l'application transport.

Ce module organise les vues en sous-modules logiques pour une meilleure maintenabilité.
"""

# Import des vues d'authentification
from .auth_views import (
    inscription_utilisateur,
    connexion_utilisateur,
    logout_utilisateur,
    user_profile,
    user_settings,
    rediriger_vers_connexion,
    rediriger_erreur_serveur,
)

# Import des vues entreprise
from .entreprise_views import (
    liste_entreprises,
    ajouter_entreprise,
    modifier_entreprise,
    supprimer_entreprise,
)

# Import des vues personnel
from .personnel_views import (
    create_chauffeur,
    chauffeur_list,
    update_chauffeur,
    chauffeur_delete,
    affectation_list,
    create_affectation,
    update_affectation,
    terminer_affectation,
    delete_affectation,
    mecanicien_list,
    create_mecanicien,
    update_mecanicien,
    delete_mecanicien,
)

# Import des vues véhicules
from .vehicle_views import (
    camion_list,
    create_camion,
    update_camion,
    delete_camion,
    conteneur_list,
    create_conteneur,
    update_conteneur,
    delete_conteneur,
    reparation_list,
    create_reparation,
    update_reparation,
    delete_reparation,
    reparation_mecanicien_list,
    create_reparation_mecanicien,
    update_reparation_mecanicien,
    delete_reparation_mecanicien,
    piece_reparee_list,
    create_piece_reparee,
    update_piece_reparee,
    delete_piece_reparee,
)

# Import des vues commerciales
from .commercial_views import (
    transitaire_list,
    create_transitaire,
    update_transitaire,
    delete_transitaire,
    client_list,
    create_client,
    update_client,
    delete_client,
    compagnie_list,
    create_compagnie,
    update_compagnie,
    delete_compagnie,
    fournisseur_list,
    create_fournisseur,
    update_fournisseur,
    delete_fournisseur,
)

# Import des vues missions
from .mission_views import (
    mission_list,
    create_mission,
    update_mission,
    delete_mission,
    terminer_mission,
    annuler_mission,
    mission_conteneur_list,
    create_mission_conteneur,
    update_mission_conteneur,
    delete_mission_conteneur,
    # Gestion du stationnement
    bloquer_stationnement,
    marquer_dechargement,
    calculer_stationnement,
    preview_frais_stationnement,
)

# Import des vues contrats
from .contrat_views import (
    contrat_list,
    create_contrat,
    update_contrat,
    delete_contrat,
    presta_transport_list,
    create_presta_transport,
    update_presta_transport,
    delete_presta_transport,
    get_conteneur_info,
)

# Import des vues finances
from .finance_views import (
    cautions_list,
    create_caution,
    update_caution,
    delete_caution,
    paiement_mission_list,
    create_paiement_mission,
    update_paiement_mission,
    delete_paiement_mission,
    valider_paiement_mission,
)

# Import des vues frais
from .frais_views import (
    frais_list,
    create_frais,
    update_frais,
    delete_frais,
    missions_data_api,
)

# Import des vues dashboard
from .dashboard_views import (
    dashboard,
    help_page,
    notifications_list,
    mark_all_notifications_read,
    tableau_bord_statistiques,
    audit_log_list,
    audit_log_detail,
    audit_cleanup,
)

# Import des vues AJAX
from .ajax_views import (
    get_chauffeur_from_camion,
    get_camion_from_chauffeur,
)

# Import des vues PDF
from .pdf_views import (
    pdf_contrat,
)

__all__ = [
    # Auth
    'inscription_utilisateur', 'connexion_utilisateur', 'logout_utilisateur',
    'user_profile', 'user_settings', 'rediriger_vers_connexion', 'rediriger_erreur_serveur',

    # Entreprise
    'liste_entreprises', 'ajouter_entreprise', 'modifier_entreprise', 'supprimer_entreprise',

    # Personnel
    'create_chauffeur', 'chauffeur_list', 'update_chauffeur', 'chauffeur_delete',
    'affectation_list', 'create_affectation', 'update_affectation', 'terminer_affectation', 'delete_affectation',
    'mecanicien_list', 'create_mecanicien', 'update_mecanicien', 'delete_mecanicien',

    # Véhicules
    'camion_list', 'create_camion', 'update_camion', 'delete_camion',
    'conteneur_list', 'create_conteneur', 'update_conteneur', 'delete_conteneur',
    'reparation_list', 'create_reparation', 'update_reparation', 'delete_reparation',
    'reparation_mecanicien_list', 'create_reparation_mecanicien', 'update_reparation_mecanicien', 'delete_reparation_mecanicien',
    'piece_reparee_list', 'create_piece_reparee', 'update_piece_reparee', 'delete_piece_reparee',

    # Commercial
    'transitaire_list', 'create_transitaire', 'update_transitaire', 'delete_transitaire',
    'client_list', 'create_client', 'update_client', 'delete_client',
    'compagnie_list', 'create_compagnie', 'update_compagnie', 'delete_compagnie',
    'fournisseur_list', 'create_fournisseur', 'update_fournisseur', 'delete_fournisseur',

    # Missions
    'mission_list', 'create_mission', 'update_mission', 'delete_mission',
    'terminer_mission', 'annuler_mission',
    'mission_conteneur_list', 'create_mission_conteneur', 'update_mission_conteneur', 'delete_mission_conteneur',
    # Stationnement
    'bloquer_stationnement', 'marquer_dechargement', 'calculer_stationnement', 'preview_frais_stationnement',

    # Contrats
    'contrat_list', 'create_contrat', 'update_contrat', 'delete_contrat',
    'presta_transport_list', 'create_presta_transport', 'update_presta_transport', 'delete_presta_transport',
    'get_conteneur_info',

    # Finances
    'cautions_list', 'create_caution', 'update_caution', 'delete_caution',
    'paiement_mission_list', 'create_paiement_mission', 'update_paiement_mission',
    'delete_paiement_mission', 'valider_paiement_mission',

    # Frais
    'frais_list', 'create_frais', 'update_frais', 'delete_frais', 'missions_data_api',

    # Dashboard
    'dashboard', 'help_page', 'notifications_list', 'mark_all_notifications_read',
    'tableau_bord_statistiques', 'audit_log_list', 'audit_log_detail', 'audit_cleanup',

    # AJAX
    'get_chauffeur_from_camion', 'get_camion_from_chauffeur',

    # PDF
    'pdf_contrat',
]
