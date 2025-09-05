from django.urls import path
from . import views

urlpatterns = [
    path('inscription_utilisateur/', views.inscription_utilisateur, name='inscription_utilisateur'),
    path('connexion/', views.connexion_utilisateur, name='connexion'),
    path('ajouter_entreprise/', views.ajouter_entreprise, name='ajouter_entreprise'),

    path("chauffeurs/", views.chauffeur_list, name="chauffeur_list"),
    path("chauffeurs/create/", views.create_chauffeur, name="chauffeur_create"),
    path("chauffeurs/<str:pk>/update/", views.update_chauffeur, name="chauffeur_update"),
    path("chauffeurs/<str:pk>/delete/", views.delete_chauffeur, name="chauffeur_delete"),

    path('camions/', views.camion_list, name='camion_list'),
    path('camions/create/', views.create_camion, name='create_camion'),
    path('camions/<str:pk>/update/', views.update_camion, name='update_camion'),
    path('camions/<str:pk>/delete/', views.delete_camion, name='delete_camion'),

    path('affectations/', views.affectation_list, name='affectation_list'),
    path('affectations/create/', views.create_affectation, name='create_affectation'),
    path('affectations/<str:pk>/update/', views.update_affectation, name='update_affectation'),
    path('affectations/<str:pk>/delete/', views.delete_affectation, name='delete_affectation'),

    path('transitaires/', views.transitaire_list, name='transitaire_list'),
    path('transitaires/create/', views.create_transitaire, name='create_transitaire'),
    path('transitaires/<str:pk>/update/', views.update_transitaire, name='update_transitaire'),
    path('transitaires/<str:pk>/delete/', views.delete_transitaire, name='delete_transitaire'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.create_client, name='create_client'),
    path('clients/<str:pk>/update/', views.update_client, name='update_client'),
    path('clients/<str:pk>/delete/', views.delete_client, name='delete_client'),

    path('compagnies/', views.compagnie_list, name='compagnie_list'),
    path('compagnies/create/', views.create_compagnie, name='create_compagnie'),
    path('compagnies/<str:pk>/update/', views.update_compagnie, name='update_compagnie'),
    path('compagnies/<str:pk>/delete/', views.delete_compagnie, name='delete_compagnie'),

    path('conteneurs/', views.conteneur_list, name='conteneur_list'),
    path('conteneurs/create/', views.create_conteneur, name='create_conteneur'),
    path('conteneurs/<str:pk>/update/', views.update_conteneur, name='update_conteneur'),
    path('conteneurs/<str:pk>/delete/', views.delete_conteneur, name='delete_conteneur'),

    path('contrats/', views.contrat_list, name='contrat_list'),
    path('contrats/create/', views.create_contrat, name='create_contrat'),
    path('contrats/<str:pk>/update/', views.update_contrat, name='update_contrat'),
    path('contrats/<str:pk>/delete/', views.delete_contrat, name='delete_contrat'),

    path('prestations/', views.presta_transport_list, name='presta_transport_list'),
    path('prestations/create/', views.create_presta_transport, name='create_presta_transport'),
    path('prestations/<str:pk>/update/', views.update_presta_transport, name='update_presta_transport'),
    path('prestations/<str:pk>/delete/', views.delete_presta_transport, name='delete_presta_transport'),

    path('cautions/', views.cautions_list, name='cautions_list'),
    path('cautions/create/', views.create_caution, name='create_caution'),
    path('cautions/<str:pk>/update/', views.update_caution, name='update_caution'),
    path('cautions/<str:pk>/delete/', views.delete_caution, name='delete_caution'),

    path('frais/', views.frais_list, name='frais_list'),
    path('frais/create/', views.create_frais, name='create_frais'),
    path('frais/<str:pk>/update/', views.update_frais, name='update_frais'),
    path('frais/<str:pk>/delete/', views.delete_frais, name='delete_frais'),

    path('missions/', views.mission_list, name='mission_list'),
    path('missions/create/', views.create_mission, name='create_mission'),
    path('missions/<str:pk>/update/', views.update_mission, name='update_mission'),
    path('missions/<str:pk>/delete/', views.delete_mission, name='delete_mission'),

    path('mission-conteneurs/', views.mission_conteneur_list, name='mission_conteneur_list'),
    path('mission-conteneurs/create/', views.create_mission_conteneur, name='create_mission_conteneur'),
    path('mission-conteneurs/<str:pk>/update/', views.update_mission_conteneur, name='update_mission_conteneur'),
    path('mission-conteneurs/<str:pk>/delete/', views.delete_mission_conteneur, name='delete_mission_conteneur'),

    path('paiement-missions/', views.paiement_mission_list, name='paiement_mission_list'),
    path('paiement-missions/create/', views.create_paiement_mission, name='create_paiement_mission'),
    path('paiement-missions/<str:pk>/update/', views.update_paiement_mission, name='update_paiement_mission'),
    path('paiement-missions/<str:pk>/delete/', views.delete_paiement_mission, name='delete_paiement_mission'),

    path('mecaniciens/', views.mecanicien_list, name='mecanicien_list'),
    path('mecaniciens/create/', views.create_mecanicien, name='create_mecanicien'),
    path('mecaniciens/<str:pk>/update/', views.update_mecanicien, name='update_mecanicien'),
    path('mecaniciens/<str:pk>/delete/', views.delete_mecanicien, name='delete_mecanicien'),

    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/create/', views.create_fournisseur, name='create_fournisseur'),
    path('fournisseurs/<str:pk>/update/', views.update_fournisseur, name='update_fournisseur'),
    path('fournisseurs/<str:pk>/delete/', views.delete_fournisseur, name='delete_fournisseur'),

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
    path('pieces-reparees/<str:pk>/update/', views.update_piece_reparee, name='update_piece_reparee'),
    path('pieces-reparees/<str:pk>/delete/', views.delete_piece_reparee, name='delete_piece_reparee'),
]





# urlpatterns = [
#     path('inscription_utilisateur/', views.inscription_utilisateur, name='inscription_utilisateur'),
#     path('connexion/', views.connexion_utilisateur, name='connexion'),
#     path('ajouter_entreprise/', views.ajouter_entreprise, name='ajouter_entreprise'),

#     path("chauffeurs/", views.chauffeur_list, name="chauffeur_list"),
#     path("chauffeurs/create/", views.create_chauffeur, name="chauffeur_create"),
#     path("chauffeurs/<str:pk>/update/", views.update_chauffeur, name="chauffeur_update"),
#     path("chauffeurs/<str:pk>/delete/", views.delete_chauffeur, name="chauffeur_delete"),


#     path('camions/', views.camion_list, name='camion_list'),
#     path('camions/create/', views.create_camion, name='create_camion'),
#     path('camions/update/<str:pk>/', views.update_camion, name='update_camion'),
#     path('camions/delete/<str:pk>/', views.delete_camion, name='delete_camion'),


#     path('affectations/', views.affectation_list, name='affectation_list'),
#     path('affectations/create/', views.create_affectation, name='create_affectation'),
#     path('affectations/update/<str:pk>/', views.update_affectation, name='update_affectation'),
#     path('affectations/delete/<str:pk>/', views.delete_affectation, name='delete_affectation'),

#     path('transitaires/', views.transitaire_list, name='transitaire_list'),
#     path('transitaires/create/', views.create_transitaire, name='create_transitaire'),
#     path('transitaires/update/<str:pk>/', views.update_transitaire, name='update_transitaire'),
#     path('transitaires/delete/<str:pk>/', views.delete_transitaire, name='delete_transitaire'),

#     path('clients/', views.client_list, name='client_list'),
#     path('clients/create/', views.create_client, name='create_client'),
#     path('clients/update/<str:pk>/', views.update_client, name='update_client'),
#     path('clients/delete/<str:pk>/', views.delete_client, name='delete_client'),

#     path('compagnies/', views.compagnie_list, name='compagnie_list'),
#     path('compagnies/create/', views.create_compagnie, name='create_compagnie'),
#     path('compagnies/update/<str:pk>/', views.update_compagnie, name='update_compagnie'),
#     path('compagnies/delete/<str:pk>/', views.delete_compagnie, name='delete_compagnie'),

#     path('conteneurs/', views.conteneur_list, name='conteneur_list'),
#     path('conteneurs/create/', views.create_conteneur, name='create_conteneur'),
#     path('conteneurs/update/<str:pk>/', views.update_conteneur, name='update_conteneur'),
#     path('conteneurs/delete/<str:pk>/', views.delete_conteneur, name='delete_conteneur'),


#     path('contrats/', views.contrat_list, name='contrat_list'),
#     path('contrats/create/', views.create_contrat, name='create_contrat'),
#     path('contrats/update/<str:pk>/', views.update_contrat, name='update_contrat'),
#     path('contrats/delete/<str:pk>/', views.delete_contrat, name='delete_contrat'),

    
#     path('prestations/', views.presta_transport_list, name='presta_transport_list'),
#     path('prestations/create/', views.create_presta_transport, name='create_presta_transport'),
#     path('prestations/update/<str:pk>/', views.update_presta_transport, name='update_presta_transport'),
#     path('prestations/delete/<str:pk>/', views.delete_presta_transport, name='delete_presta_transport'),

#     path('cautions/', views.cautions_list, name='cautions_list'),
#     path('cautions/create/', views.create_caution, name='create_caution'),
#     path('cautions/update/<str:pk>/', views.update_caution, name='update_caution'),
#     path('cautions/delete/<str:pk>/', views.delete_caution, name='delete_caution'),

#     path('frais/', views.frais_list, name='frais_list'),
#     path('frais/create/', views.create_frais, name='create_frais'),
#     path('frais/update/<str:pk>/', views.update_frais, name='update_frais'),
#     path('frais/delete/<str:pk>/', views.delete_frais, name='delete_frais'),

#     path('missions/', views.mission_list, name='mission_list'),
#     path('missions/create/', views.create_mission, name='create_mission'),
#     path('missions/update/<str:pk>/', views.update_mission, name='update_mission'),
#     path('missions/delete/<str:pk>/', views.delete_mission, name='delete_mission'),

#     path('mission-conteneurs/', views.mission_conteneur_list, name='mission_conteneur_list'),
#     path('mission-conteneurs/create/', views.create_mission_conteneur, name='create_mission_conteneur'),
#     path('mission-conteneurs/<int:pk>/update/', views.update_mission_conteneur, name='update_mission_conteneur'),
#     path('mission-conteneurs/<int:pk>/delete/', views.delete_mission_conteneur, name='delete_mission_conteneur'),

#     path('paiement-missions/', views.paiement_mission_list, name='paiement_mission_list'),
#     path('paiement-missions/create/', views.create_paiement_mission, name='create_paiement_mission'),
#     path('paiement-missions/<str:pk>/update/', views.update_paiement_mission, name='update_paiement_mission'),
#     path('paiement-missions/<str:pk>/delete/', views.delete_paiement_mission, name='delete_paiement_mission'),

#     path('mecaniciens/', views.mecanicien_list, name='mecanicien_list'),
#     path('mecaniciens/create/', views.create_mecanicien, name='create_mecanicien'),
#     path('mecaniciens/<str:pk>/update/', views.update_mecanicien, name='update_mecanicien'),
#     path('mecaniciens/<str:pk>/delete/', views.delete_mecanicien, name='delete_mecanicien'),

#     path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
#     path('fournisseurs/create/', views.create_fournisseur, name='create_fournisseur'),
#     path('fournisseurs/<str:pk>/update/', views.update_fournisseur, name='update_fournisseur'),
#     path('fournisseurs/<str:pk>/delete/', views.delete_fournisseur, name='delete_fournisseur'),

#     path('reparations/', views.reparation_list, name='reparation_list'),
#     path('reparations/create/', views.create_reparation, name='create_reparation'),
#     path('reparations/<str:pk>/update/', views.update_reparation, name='update_reparation'),
#     path('reparations/<str:pk>/delete/', views.delete_reparation, name='delete_reparation'),

#     path('reparation-mecaniciens/', views.reparation_mecanicien_list, name='reparation_mecanicien_list'),
#     path('reparation-mecaniciens/create/', views.create_reparation_mecanicien, name='create_reparation_mecanicien'),
#     path('reparation-mecaniciens/<int:pk>/update/', views.update_reparation_mecanicien, name='update_reparation_mecanicien'),
#     path('reparation-mecaniciens/<int:pk>/delete/', views.delete_reparation_mecanicien, name='delete_reparation_mecanicien'),

#     path('pieces-reparees/', views.piece_reparee_list, name='piece_reparee_list'),
#     path('pieces-reparees/create/', views.create_piece_reparee, name='create_piece_reparee'),
#     path('pieces-reparees/<str:pk>/update/', views.update_piece_reparee, name='update_piece_reparee'),
#     path('pieces-reparees/<str:pk>/delete/', views.delete_piece_reparee, name='delete_piece_reparee'),



  




# ]
