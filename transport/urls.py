from django.urls import path
from . import views
from . import export_views
from . import pdf_reports
from . import dashboard_views
from . import permissions_views
from . import invoice_views
from . import reports_views
from . import user_crud_views
from . import salary_views
from . import pwa_views
from .views import ajax_views
from .views.annulation_views import (
    annuler_contrat_view,
    annuler_mission_view,
    contrats_annules_list,
    missions_annulees_list,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('inscription_utilisateur/', views.inscription_utilisateur, name='inscription_utilisateur'),
    path('connexion/', views.connexion_utilisateur, name='connexion'),
    # path('ajouter_entreprise/', views.ajouter_entreprise, name='ajouter_entreprise'),
    
    
    path('liste_entreprises/', views.liste_entreprises, name='liste_entreprises'),
    path('entreprises/ajouter/', views.ajouter_entreprise, name='ajouter_entreprise'),
    path('entreprises/modifier/<str:pk>/', views.modifier_entreprise, name='modifier_entreprise'),
    path('entreprises/supprimer/<str:pk>/', views.supprimer_entreprise, name='supprimer_entreprise'),
    # AJAX URLs for entreprises
    path('entreprises/ajax/create/', ajax_views.ajax_entreprise_create, name='ajax_entreprise_create'),
    path('entreprises/<str:pk>/ajax/update/', ajax_views.ajax_entreprise_update, name='ajax_entreprise_update'),


    path("chauffeurs/", views.chauffeur_list, name="chauffeur_list"),
    path("chauffeurs/create/", views.create_chauffeur, name="chauffeur_create"),
    path("chauffeurs/ajax/create/", ajax_views.ajax_chauffeur_create, name="ajax_chauffeur_create"),
    path("chauffeurs/<str:pk>/update/", views.update_chauffeur, name="chauffeur_update"),
    path("chauffeurs/<str:pk>/ajax/update/", ajax_views.ajax_chauffeur_update, name="ajax_chauffeur_update"),
    path("chauffeurs/<str:pk>/delete/", views.chauffeur_delete, name="chauffeur_delete"),

    path('camions/', views.camion_list, name='camion_list'),
    path('camions/create/', views.create_camion, name='create_camion'),
    # AJAX URLs for camions (avant les patterns <str:pk> pour éviter toute ambiguïté)
    path('camions/ajax/create/', ajax_views.ajax_camion_create, name='ajax_camion_create'),
    path('camions/<str:pk>/update/', views.update_camion, name='update_camion'),
    path('camions/<str:pk>/delete/', views.delete_camion, name='delete_camion'),
    path('camions/<str:pk>/ajax/update/', ajax_views.ajax_camion_update, name='ajax_camion_update'),

    path('affectations/', views.affectation_list, name='affectation_list'),
    path('affectations/create/', views.create_affectation, name='create_affectation'),
    path('affectations/<str:pk>/update/', views.update_affectation, name='update_affectation'),
    path('affectations/<str:pk>/delete/', views.delete_affectation, name='delete_affectation'),
    path('affectations/<str:pk>/terminer/', views.terminer_affectation, name='terminer_affectation'),
    # AJAX URLs for affectations
    path('affectations/ajax/create/', ajax_views.ajax_affectation_create, name='ajax_affectation_create'),
    path('affectations/<str:pk>/ajax/update/', ajax_views.ajax_affectation_update, name='ajax_affectation_update'),

    path('transitaires/', views.transitaire_list, name='transitaire_list'),
    path('transitaires/create/', views.create_transitaire, name='create_transitaire'),
    path('transitaires/<str:pk>/update/', views.update_transitaire, name='update_transitaire'),
    path('transitaires/<str:pk>/delete/', views.delete_transitaire, name='delete_transitaire'),
    # AJAX URLs for transitaires
    path('transitaires/ajax/create/', ajax_views.ajax_transitaire_create, name='ajax_transitaire_create'),
    path('transitaires/<str:pk>/ajax/update/', ajax_views.ajax_transitaire_update, name='ajax_transitaire_update'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.create_client, name='create_client'),
    path('clients/ajax/create/', ajax_views.ajax_client_create, name='ajax_client_create'),
    path('clients/<str:pk>/update/', views.update_client, name='update_client'),
    path('clients/<str:pk>/ajax/update/', ajax_views.ajax_client_update, name='ajax_client_update'),
    path('clients/<str:pk>/delete/', views.delete_client, name='delete_client'),

    path('compagnies/', views.compagnie_list, name='compagnie_list'),
    path('compagnies/create/', views.create_compagnie, name='create_compagnie'),
    path('compagnies/<str:pk>/update/', views.update_compagnie, name='update_compagnie'),
    path('compagnies/<str:pk>/delete/', views.delete_compagnie, name='delete_compagnie'),
    # AJAX URLs for compagnies
    path('compagnies/ajax/create/', ajax_views.ajax_compagnie_create, name='ajax_compagnie_create'),
    path('compagnies/<str:pk>/ajax/update/', ajax_views.ajax_compagnie_update, name='ajax_compagnie_update'),

    path('conteneurs/', views.conteneur_list, name='conteneur_list'),
    path('conteneurs/create/', views.create_conteneur, name='create_conteneur'),
    path('conteneurs/<str:pk>/update/', views.update_conteneur, name='update_conteneur'),
    path('conteneurs/<str:pk>/delete/', views.delete_conteneur, name='delete_conteneur'),
    # AJAX URLs for conteneurs
    path('conteneurs/ajax/create/', ajax_views.ajax_conteneur_create, name='ajax_conteneur_create'),
    path('conteneurs/<str:pk>/ajax/update/', ajax_views.ajax_conteneur_update, name='ajax_conteneur_update'),

    path('contrats/', views.contrat_list, name='contrat_list'),
    path('contrats/create/', views.create_contrat, name='create_contrat'),
    path('contrats/<str:pk>/update/', views.update_contrat, name='update_contrat'),
    path('contrats/<str:pk>/delete/', views.delete_contrat, name='delete_contrat'),
    path('contrats/<str:pk>/annuler/', annuler_contrat_view, name='annuler_contrat'),
    path('contrats/annules/', contrats_annules_list, name='contrats_annules_list'),
    path("contrat/pdf/<str:pk>/", views.pdf_contrat, name="pdf_contrat"),
    # AJAX URLs for contrats
    path('contrats/ajax/create/', ajax_views.ajax_contrat_create, name='ajax_contrat_create'),
    path('contrats/<str:pk>/ajax/update/', ajax_views.ajax_contrat_update, name='ajax_contrat_update'),
    # API pour récupérer le chauffeur d'un camion
    path('api/camion/<str:pk_camion>/chauffeur/', views.get_chauffeur_from_camion, name='get_chauffeur_from_camion'),
    # API pour récupérer le camion d'un chauffeur
    path('api/chauffeur/<str:pk_chauffeur>/camion/', views.get_camion_from_chauffeur, name='get_camion_from_chauffeur'),
    # API pour récupérer le client et le transitaire d'un conteneur
    path('api/conteneur/<str:conteneur_id>/info/', views.get_conteneur_info, name='get_conteneur_info'),

    path('prestations/', views.presta_transport_list, name='presta_transport_list'),
    path('prestations/create/', views.create_presta_transport, name='create_presta_transport'),
    path('prestations/<str:pk>/update/', views.update_presta_transport, name='update_presta_transport'),
    path('prestations/<str:pk>/delete/', views.delete_presta_transport, name='delete_presta_transport'),
    # AJAX URLs for prestations
    path('prestations/ajax/create/', ajax_views.ajax_prestation_create, name='ajax_prestation_create'),
    path('prestations/<str:pk>/ajax/update/', ajax_views.ajax_prestation_update, name='ajax_prestation_update'),

    path('cautions/', views.cautions_list, name='cautions_list'),
    path('cautions/create/', views.create_caution, name='create_caution'),
    path('cautions/<str:pk>/update/', views.update_caution, name='update_caution'),
    path('cautions/<str:pk>/delete/', views.delete_caution, name='delete_caution'),

    path('frais/', views.frais_list, name='frais_list'),
    path('frais/create/', views.create_frais, name='create_frais'),
    path('frais/<str:pk>/update/', views.update_frais, name='update_frais'),
    path('frais/<str:pk>/delete/', views.delete_frais, name='delete_frais'),
    # API pour auto-complétion
    path('api/missions-data/', views.missions_data_api, name='missions_data_api'),

    path('missions/', views.mission_list, name='mission_list'),
    path('missions/create/', views.create_mission, name='create_mission'),
    path('missions/<str:pk>/update/', views.update_mission, name='update_mission'),
    path('missions/<str:pk>/delete/', views.delete_mission, name='delete_mission'),
    path('missions/<str:pk>/terminer/', views.terminer_mission, name='terminer_mission'),
    path('missions/<str:pk>/ajax/terminer/', ajax_views.ajax_terminer_mission_modal_content, name='ajax_terminer_mission_modal'),
    path('missions/<str:pk>/ajax/terminer-execute/', ajax_views.ajax_terminer_mission, name='ajax_terminer_mission'),
    path('missions/<str:pk>/annuler/', views.annuler_mission, name='annuler_mission'),
    path('missions/annulees/', missions_annulees_list, name='missions_annulees_list'),
    # Gestion du stationnement (demurrage)
    path('missions/<str:pk>/bloquer-stationnement/', views.bloquer_stationnement, name='bloquer_stationnement'),
    path('missions/<str:pk>/marquer-dechargement/', views.marquer_dechargement, name='marquer_dechargement'),
    path('missions/<str:pk>/calculer-stationnement/', views.calculer_stationnement, name='calculer_stationnement'),
    path('missions/<str:pk>/preview-frais-stationnement/', views.preview_frais_stationnement, name='preview_frais_stationnement'),
    # AJAX URLs for missions
    path('missions/ajax/create/', ajax_views.ajax_mission_create, name='ajax_mission_create'),
    path('missions/<str:pk>/ajax/update/', ajax_views.ajax_mission_update, name='ajax_mission_update'),
    # Aliases GET pour le chargement du formulaire (utilisés par missions-crud.js)
    path('missions/ajax/create-form/', ajax_views.ajax_mission_create, name='ajax_mission_create_form'),
    path('missions/<str:pk>/ajax/update-form/', ajax_views.ajax_mission_update, name='ajax_mission_update_form'),

    path('mission-conteneurs/', views.mission_conteneur_list, name='mission_conteneur_list'),
    path('mission-conteneurs/create/', views.create_mission_conteneur, name='create_mission_conteneur'),
    path('mission-conteneurs/<str:pk>/update/', views.update_mission_conteneur, name='update_mission_conteneur'),
    path('mission-conteneurs/<str:pk>/delete/', views.delete_mission_conteneur, name='delete_mission_conteneur'),

    path('paiement-missions/', views.paiement_mission_list, name='paiement_mission_list'),
    path('paiement-missions/ajax/filter/', ajax_views.ajax_filter_paiements, name='ajax_filter_paiements'),
    path('paiement-missions/<str:pk>/ajax/validation/', ajax_views.ajax_validation_modal_content, name='ajax_validation_modal'),
    path('paiement-missions/<str:pk>/ajax/validate/', ajax_views.ajax_validate_paiement, name='ajax_validate_paiement'),
    path('clients/ajax/search/', ajax_views.ajax_search_clients, name='ajax_search_clients'),
    path('chauffeurs/ajax/search/', ajax_views.ajax_search_chauffeurs, name='ajax_search_chauffeurs'),
    path('paiement-missions/create/', views.create_paiement_mission, name='create_paiement_mission'),
    path('paiement-missions/<str:pk>/update/', views.update_paiement_mission, name='update_paiement_mission'),
    path('paiement-missions/<str:pk>/delete/', views.delete_paiement_mission, name='delete_paiement_mission'),
    path('paiement-missions/<str:pk>/valider/', views.valider_paiement_mission, name='valider_paiement_mission'),

    # Exports Excel/CSV
    path('missions/export/excel/', export_views.export_missions_excel, name='export_missions_excel'),
    path('missions/export/csv/', export_views.export_missions_csv, name='export_missions_csv'),
    path('paiements/export/excel/', export_views.export_paiements_excel, name='export_paiements_excel'),
    path('paiements/export/csv/', export_views.export_paiements_csv, name='export_paiements_csv'),
    path('utilisateurs/export/excel/', export_views.export_utilisateurs_excel, name='export_utilisateurs_excel'),
    path('audit/export/excel/', export_views.export_audit_excel, name='export_audit_excel'),

    # Rapports PDF avancés
    path('missions/rapport/pdf/', pdf_reports.generate_missions_report_pdf, name='rapport_missions_pdf'),
    path('paiements/rapport/pdf/', pdf_reports.generate_paiements_report_pdf, name='rapport_paiements_pdf'),

    path('mecaniciens/', views.mecanicien_list, name='mecanicien_list'),
    path('mecaniciens/create/', views.create_mecanicien, name='create_mecanicien'),
    path('mecaniciens/<str:pk>/update/', views.update_mecanicien, name='update_mecanicien'),
    path('mecaniciens/<str:pk>/delete/', views.delete_mecanicien, name='delete_mecanicien'),

    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/create/', views.create_fournisseur, name='create_fournisseur'),
    path('fournisseurs/<str:pk>/update/', views.update_fournisseur, name='update_fournisseur'),
    path('fournisseurs/<str:pk>/delete/', views.delete_fournisseur, name='delete_fournisseur'),
    # AJAX URLs for fournisseurs
    path('fournisseurs/ajax/create/', ajax_views.ajax_fournisseur_create, name='ajax_fournisseur_create'),
    path('fournisseurs/<str:pk>/ajax/update/', ajax_views.ajax_fournisseur_update, name='ajax_fournisseur_update'),

    path('reparations/', views.reparation_list, name='reparation_list'),
    path('reparations/create/', views.create_reparation, name='create_reparation'),
    path('reparations/<str:pk>/update/', views.update_reparation, name='update_reparation'),
    path('reparations/<str:pk>/delete/', views.delete_reparation, name='delete_reparation'),

    path('reparation-mecaniciens/', views.reparation_mecanicien_list, name='reparation_mecanicien_list'),
    path('reparation-mecaniciens/create/', views.create_reparation_mecanicien, name='create_reparation_mecanicien'),
    path('reparation-mecaniciens/<str:pk>/update/', views.update_reparation_mecanicien, name='update_reparation_mecanicien'),
    path('reparation-mecaniciens/<str:pk>/delete/', views.delete_reparation_mecanicien, name='delete_reparation_mecanicien'),

    path('pieces-reparees/', views.piece_reparee_list, name='piece_reparee_list'),
    path('pieces-reparees/create/', views.create_piece_reparee, name='create_piece_reparee'),
    path('pieces-reparees/create/<str:reparation_id>/', views.create_piece_reparee, name='create_piece_reparee'),
    path('pieces-reparees/<str:pk>/update/', views.update_piece_reparee, name='update_piece_reparee'),
    path('pieces-reparees/<str:pk>/delete/', views.delete_piece_reparee, name='delete_piece_reparee'),

    path("", views.dashboard, name="dashboard"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/ajax/filter/', ajax_views.ajax_dashboard_filter, name='ajax_dashboard_filter'),

    # Nouveaux dashboards avancés avec KPIs
    path('dashboard/home/', dashboard_views.dashboard_home, name='dashboard_home'),
    path('dashboard/financier/', dashboard_views.dashboard_financier, name='dashboard_financier'),

    # Tableau de bord statistiques (ancien)
    path('statistiques/', views.tableau_bord_statistiques, name='statistiques'),

    # Profil utilisateur et système
    path('profil/', views.user_profile, name='user_profile'),
    path('parametres/', views.user_settings, name='user_settings'),
    path('aide/', views.help_page, name='help_page'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<str:pk>/ajax/mark-read/', ajax_views.ajax_mark_notification_read, name='ajax_mark_notification_read'),
    path('notifications/ajax/mark-all-read/', ajax_views.ajax_mark_all_notifications_read, name='ajax_mark_all_notifications_read'),
    path('notifications/ajax/get/', ajax_views.ajax_get_notifications, name='ajax_get_notifications'),

    # Historique d'audit
    path('audit/', views.audit_log_list, name='audit_log_list'),
    path('audit/cleanup/', views.audit_cleanup, name='audit_cleanup'),
    path('audit/<str:pk>/', views.audit_log_detail, name='audit_log_detail'),

    # Gestion des permissions et rôles
    # Permissions
    path('permissions/', permissions_views.permissions_dashboard, name='permissions_dashboard'),
    path('permissions/users/', permissions_views.user_permissions_list, name='user_permissions_list'),
    path('permissions/users/<str:user_id>/assign/', permissions_views.assign_user_role, name='assign_user_role'),
    path('permissions/groups/<int:group_id>/', permissions_views.group_details, name='group_details'),
    path('permissions/my-permissions/', permissions_views.my_permissions, name='my_permissions'),

    # CRUD Utilisateurs
    path('utilisateurs/', user_crud_views.utilisateur_list, name='utilisateur_list'),
    path('utilisateurs/create/', user_crud_views.utilisateur_create, name='utilisateur_create'),
    path('utilisateurs/<str:pk>/update/', user_crud_views.utilisateur_update, name='utilisateur_update'),
    path('utilisateurs/<str:pk>/delete/', user_crud_views.utilisateur_delete, name='utilisateur_delete'),

    # Gestion des salaires
    path('salaires/', salary_views.salaire_list, name='salaire_list'),
    path('salaires/create/', salary_views.salaire_create, name='salaire_create'),
    path('salaires/<str:pk>/', salary_views.salaire_detail, name='salaire_detail'),
    path('salaires/<str:pk>/update/', salary_views.salaire_update, name='salaire_update'),
    path('salaires/<str:pk>/delete/', salary_views.salaire_delete, name='salaire_delete'),
    path('salaires/<str:pk>/valider/', salary_views.salaire_valider, name='salaire_valider'),
    path('salaires/<str:pk>/payer/', salary_views.salaire_payer, name='salaire_payer'),
    path('salaires/<str:salaire_pk>/primes/add/', salary_views.prime_add, name='prime_add'),
    path('primes/<str:pk>/delete/', salary_views.prime_delete, name='prime_delete'),
    path('salaires/<str:salaire_pk>/deductions/add/', salary_views.deduction_add, name='deduction_add'),
    path('deductions/<str:pk>/delete/', salary_views.deduction_delete, name='deduction_delete'),

    # Gestion des factures
    path('invoices/', invoice_views.invoices_list, name='invoices_list'),
    path('invoices/generate/<str:paiement_id>/', invoice_views.generate_invoice, name='generate_invoice'),
    path('invoices/preview/<str:paiement_id>/', invoice_views.preview_invoice, name='preview_invoice'),
    path('invoices/send/<str:paiement_id>/', invoice_views.send_invoice_email, name='send_invoice_email'),
    path('invoices/bulk-send/', invoice_views.bulk_send_invoices, name='bulk_send_invoices'),

    # Rapports financiers avancés
    path('reports/financial/', reports_views.financial_reports, name='financial_reports'),
    path('reports/financial/export/', reports_views.export_financial_report_excel, name='export_financial_report_excel'),
    path('reports/client/<str:client_id>/', reports_views.client_report, name='client_report'),

    # PWA (Progressive Web App)
    path('manifest.json', pwa_views.manifest, name='manifest'),
    path('sw.js', pwa_views.service_worker, name='service_worker'),
    path('offline/', pwa_views.offline, name='offline'),
    path('clear-cache/', pwa_views.clear_cache, name='clear_cache'),

    path('logout/', views.logout_utilisateur, name='logout'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'transport.views.rediriger_vers_connexion'
handler500 = 'transport.views.rediriger_erreur_serveur'

