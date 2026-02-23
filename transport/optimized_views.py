"""
Vues optimisées avec pagination et requêtes efficaces
======================================================

Ce module contient des vues optimisées pour remplacer les vues existantes.
Utilise pagination, select_related, prefetch_related pour de meilleures performances.

Usage:
    Dans urls.py, remplacez les vues par défaut par ces vues optimisées:

    # Au lieu de:
    path('missions/', views.mission_list, name='mission_list'),

    # Utilisez:
    path('missions/', optimized_views.mission_list_optimized, name='mission_list'),
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from .models import (
    Mission, PaiementMission, Conteneur, ContratTransport,
    Camion, Chauffeur, Client, Transitaire, Reparation,
    Affectation, Cautions
)
from .filters import (
    MissionFilter, PaiementMissionFilter, ContratTransportFilter,
    ReparationFilter, CautionFilter
)


def get_paginated_queryset(queryset, request, per_page=20):
    """
    Fonction utilitaire pour paginer un queryset

    Args:
        queryset: QuerySet à paginer
        request: Requête HTTP
        per_page: Nombre d'éléments par page (défaut: 20)

    Returns:
        Objet Page paginé
    """
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, per_page)

    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        # Si page n'est pas un entier, retourner la première page
        paginated = paginator.page(1)
    except EmptyPage:
        # Si page est hors limites, retourner la dernière page
        paginated = paginator.page(paginator.num_pages)

    return paginated


@login_required
def mission_list_optimized(request):
    """
    Liste des missions avec pagination et requêtes optimisées

    Optimisations:
    - select_related pour contrat, chauffeur, client, camion, conteneur
    - Pagination (20 par page)
    - Filtres avancés
    """
    entreprise = request.user.entreprise

    # Requête optimisée avec select_related pour éviter les requêtes N+1
    missions = Mission.objects.filter(contrat__entreprise=entreprise).select_related(
        'contrat',
        'contrat__chauffeur',
        'contrat__client',
        'contrat__transitaire',
        'contrat__camion',
        'contrat__conteneur',
        'contrat__conteneur__compagnie',
        'prestation_transport'
    ).prefetch_related(
        'frais_trajets'  # Charger tous les frais de trajet (aller + retour)
    ).order_by('-date_depart')

    # Appliquer les filtres
    missions = MissionFilter.apply(missions, request)

    # Pagination
    missions_paginated = get_paginated_queryset(missions, request, per_page=20)

    # Compter les missions par statut pour les filtres
    total_missions = Mission.objects.filter(contrat__entreprise=entreprise).count()
    missions_en_cours = Mission.objects.filter(statut='en cours', contrat__entreprise=entreprise).count()
    missions_terminees = Mission.objects.filter(statut='terminée', contrat__entreprise=entreprise).count()
    missions_annulees = Mission.objects.filter(statut='annulée', contrat__entreprise=entreprise).count()

    # 🆕 Compter les missions par type de transport
    from django.db.models import Q, Exists, OuterRef
    from .models import FraisTrajet

    # Missions avec aller ET retour
    missions_aller_retour = Mission.objects.filter(
        contrat__entreprise=entreprise
    ).filter(
        Exists(FraisTrajet.objects.filter(mission=OuterRef('pk'), type_trajet='aller')),
        Exists(FraisTrajet.objects.filter(mission=OuterRef('pk'), type_trajet='retour'))
    ).count()

    # Missions avec aller seulement
    missions_aller_simple = Mission.objects.filter(
        contrat__entreprise=entreprise
    ).filter(
        Exists(FraisTrajet.objects.filter(mission=OuterRef('pk'), type_trajet='aller'))
    ).exclude(
        Exists(FraisTrajet.objects.filter(mission=OuterRef('pk'), type_trajet='retour'))
    ).count()

    # Missions sans trajets
    missions_sans_trajet = Mission.objects.filter(
        contrat__entreprise=entreprise
    ).exclude(
        Exists(FraisTrajet.objects.filter(mission=OuterRef('pk')))
    ).count()

    context = {
        'missions': missions_paginated,
        'title': 'Liste des missions',
        'total_missions': total_missions,
        'missions_en_cours': missions_en_cours,
        'missions_terminees': missions_terminees,
        'missions_annulees': missions_annulees,

        # 🆕 Statistiques par type de transport
        'missions_aller_retour': missions_aller_retour,
        'missions_aller_simple': missions_aller_simple,
        'missions_sans_trajet': missions_sans_trajet,

        # Pour le formulaire de filtre
        'filter_statut': request.GET.get('statut', ''),
        'filter_chauffeur': request.GET.get('chauffeur', ''),
        'filter_client': request.GET.get('client', ''),
        'filter_search': request.GET.get('search', ''),

        # Listes pour les filtres
        'chauffeurs': Chauffeur.objects.filter(entreprise=entreprise).order_by('nom'),
        'clients': Client.objects.filter(entreprise=entreprise).order_by('nom'),
    }

    return render(request, 'transport/missions/mission_list.html', context)


@login_required
def paiement_mission_list_optimized(request):
    """
    Liste des paiements avec pagination et requêtes optimisées
    """
    entreprise = request.user.entreprise

    paiements = PaiementMission.objects.filter(
        mission__contrat__entreprise=entreprise
    ).select_related(
        'mission',
        'mission__contrat',
        'mission__contrat__chauffeur',
        'mission__contrat__client',
        'mission__contrat__transitaire',
        'caution',
        'prestation'
    ).order_by('-date_paiement')

    # Appliquer les filtres
    paiements = PaiementMissionFilter.apply(paiements, request)

    # Pagination
    paiements_paginated = get_paginated_queryset(paiements, request, per_page=20)

    # Statistiques
    total_paiements = PaiementMission.objects.filter(mission__contrat__entreprise=entreprise).count()
    paiements_valides = PaiementMission.objects.filter(est_valide=True, mission__contrat__entreprise=entreprise).count()
    paiements_en_attente = total_paiements - paiements_valides

    context = {
        'paiements': paiements_paginated,
        'title': 'Liste des paiements de mission',
        'total_paiements': total_paiements,
        'paiements_valides': paiements_valides,
        'paiements_en_attente': paiements_en_attente,

        # Filtres
        'filter_est_valide': request.GET.get('est_valide', ''),
        'filter_search': request.GET.get('search', ''),

        'chauffeurs': Chauffeur.objects.filter(entreprise=entreprise).order_by('nom'),
    }

    return render(request, 'transport/paiements-mission/paiement_mission_list.html', context)


@login_required
def conteneur_list_optimized(request):
    """
    Liste des conteneurs avec pagination et informations sur les missions
    """
    conteneurs = Conteneur.objects.select_related(
        'compagnie',
        'client',
        'transitaire'
    ).order_by('numero_conteneur')

    # Filtres
    statut = request.GET.get('statut')
    if statut and statut != 'tous':
        conteneurs = conteneurs.filter(statut=statut)

    search = request.GET.get('search')
    if search:
        conteneurs = conteneurs.filter(
            Q(numero_conteneur__icontains=search) |
            Q(compagnie__nom__icontains=search) |
            Q(client__nom__icontains=search)
        )

    # Pagination
    conteneurs_paginated = get_paginated_queryset(conteneurs, request, per_page=25)

    # Statistiques
    total_conteneurs = Conteneur.objects.count()
    conteneurs_disponibles = Conteneur.objects.filter(statut='au_port').count()
    conteneurs_en_mission = Conteneur.objects.filter(statut='en_mission').count()
    conteneurs_maintenance = Conteneur.objects.filter(statut='en_maintenance').count()

    context = {
        'conteneurs': conteneurs_paginated,
        'title': 'Liste des conteneurs',
        'total_conteneurs': total_conteneurs,
        'conteneurs_disponibles': conteneurs_disponibles,
        'conteneurs_en_mission': conteneurs_en_mission,
        'conteneurs_maintenance': conteneurs_maintenance,

        'filter_statut': statut or '',
        'filter_search': search or '',
    }

    return render(request, 'transport/conteneurs/conteneur_list.html', context)


@login_required
def contrat_list_optimized(request):
    """
    Liste des contrats avec pagination et requêtes optimisées
    """
    contrats = ContratTransport.objects.filter(
        entreprise=request.user.entreprise
    ).select_related(
        'conteneur',
        'conteneur__compagnie',
        'client',
        'transitaire',
        'entreprise',
        'camion',
        'chauffeur'
    ).order_by('-date_debut')

    # Appliquer les filtres
    contrats = ContratTransportFilter.apply(contrats, request)

    # Pagination
    contrats_paginated = get_paginated_queryset(contrats, request, per_page=20)

    context = {
        'contrats': contrats_paginated,
        'title': 'Liste des contrats de transport',

        # Filtres
        'filter_statut_caution': request.GET.get('statut_caution', ''),
        'filter_search': request.GET.get('search', ''),

        'chauffeurs': Chauffeur.objects.filter(entreprise=request.user.entreprise).order_by('nom'),
        'clients': Client.objects.filter(entreprise=request.user.entreprise).order_by('nom'),
        'transitaires': Transitaire.objects.filter(entreprise=request.user.entreprise).order_by('nom'),
    }

    return render(request, 'transport/contrat/contrat_list.html', context)


@login_required
def chauffeur_list_optimized(request):
    """
    Liste des chauffeurs avec informations sur leurs affectations
    """
    chauffeurs = Chauffeur.objects.filter(entreprise=request.user.entreprise).select_related('entreprise').prefetch_related(
        Prefetch(
            'affectation_set',
            queryset=Affectation.objects.filter(date_fin_affectation__isnull=True).select_related('camion'),
            to_attr='affectations_actives'
        )
    ).order_by('nom', 'prenom')

    # Filtres
    search = request.GET.get('search')
    if search:
        chauffeurs = chauffeurs.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )

    disponible = request.GET.get('disponible')
    if disponible == 'oui':
        chauffeurs = chauffeurs.filter(est_affecter=False)
    elif disponible == 'non':
        chauffeurs = chauffeurs.filter(est_affecter=True)

    # Pagination
    chauffeurs_paginated = get_paginated_queryset(chauffeurs, request, per_page=25)

    # Statistiques
    total_chauffeurs = Chauffeur.objects.filter(entreprise=request.user.entreprise).count()
    chauffeurs_disponibles = Chauffeur.objects.filter(entreprise=request.user.entreprise, est_affecter=False).count()
    chauffeurs_affectes = total_chauffeurs - chauffeurs_disponibles

    context = {
        'chauffeurs': chauffeurs_paginated,
        'title': 'Liste des chauffeurs',
        'total_chauffeurs': total_chauffeurs,
        'chauffeurs_disponibles': chauffeurs_disponibles,
        'chauffeurs_affectes': chauffeurs_affectes,

        'filter_search': search or '',
        'filter_disponible': disponible or '',
    }

    return render(request, 'transport/chauffeurs/chauffeur_list.html', context)


@login_required
def camion_list_optimized(request):
    """
    Liste des camions avec informations sur leurs affectations
    """
    camions = Camion.objects.filter(entreprise=request.user.entreprise).select_related('entreprise').prefetch_related(
        Prefetch(
            'affectation_set',
            queryset=Affectation.objects.filter(date_fin_affectation__isnull=True).select_related('chauffeur'),
            to_attr='affectations_actives'
        )
    ).order_by('immatriculation')

    # Filtres
    search = request.GET.get('search')
    if search:
        camions = camions.filter(
            Q(immatriculation__icontains=search) |
            Q(modele__icontains=search)
        )

    disponible = request.GET.get('disponible')
    if disponible == 'oui':
        camions = camions.filter(est_affecter=False)
    elif disponible == 'non':
        camions = camions.filter(est_affecter=True)

    # Pagination
    camions_paginated = get_paginated_queryset(camions, request, per_page=25)

    # Statistiques
    total_camions = Camion.objects.filter(entreprise=request.user.entreprise).count()
    camions_disponibles = Camion.objects.filter(entreprise=request.user.entreprise, est_affecter=False).count()
    camions_affectes = total_camions - camions_disponibles

    context = {
        'camions': camions_paginated,
        'title': 'Liste des camions',
        'total_camions': total_camions,
        'camions_disponibles': camions_disponibles,
        'camions_affectes': camions_affectes,

        'filter_search': search or '',
        'filter_disponible': disponible or '',
    }

    return render(request, 'transport/camions/camion_list.html', context)


@login_required
def reparation_list_optimized(request):
    """
    Liste des réparations avec pagination et requêtes optimisées
    """
    reparations = Reparation.objects.filter(
        camion__entreprise=request.user.entreprise
    ).select_related(
        'camion',
        'camion__entreprise',
        'chauffeur'
    ).prefetch_related(
        Prefetch(
            'reparationmecanicien_set',
            queryset=ReparationMecanicien.objects.select_related('mecanicien'),
            to_attr='mecaniciens_list'
        ),
        Prefetch(
            'piecereparee_set',
            to_attr='pieces_list'
        )
    ).order_by('-date_reparation')

    # Appliquer les filtres
    reparations = ReparationFilter.apply(reparations, request)

    # Pagination
    reparations_paginated = get_paginated_queryset(reparations, request, per_page=20)

    context = {
        'reparations': reparations_paginated,
        'title': 'Liste des réparations',

        'filter_search': request.GET.get('search', ''),
        'camions': Camion.objects.filter(entreprise=request.user.entreprise).order_by('immatriculation'),
    }

    return render(request, 'transport/reparations/reparation_list.html', context)


@login_required
def caution_list_optimized(request):
    """
    Liste des cautions avec pagination et requêtes optimisées
    """
    cautions = Cautions.objects.filter(
        contrat__entreprise=request.user.entreprise
    ).select_related(
        'conteneur',
        'contrat',
        'transitaire',
        'client',
        'chauffeur',
        'camion'
    ).order_by('-pk_caution')

    # Appliquer les filtres
    cautions = CautionFilter.apply(cautions, request)

    # Pagination
    cautions_paginated = get_paginated_queryset(cautions, request, per_page=20)

    # Statistiques
    from django.db.models import Sum
    cautions_qs_stats = Cautions.objects.filter(contrat__entreprise=request.user.entreprise)
    total_cautions = cautions_qs_stats.count()
    cautions_en_attente = cautions_qs_stats.filter(statut='en_attente').count()
    cautions_remboursees = cautions_qs_stats.filter(statut='remboursee').count()
    montant_bloque = cautions_qs_stats.filter(statut='en_attente').aggregate(
        total=Sum('montant')
    )['total'] or 0

    context = {
        'cautions': cautions_paginated,
        'title': 'Liste des cautions',
        'total_cautions': total_cautions,
        'cautions_en_attente': cautions_en_attente,
        'cautions_remboursees': cautions_remboursees,
        'montant_bloque': montant_bloque,

        'filter_statut': request.GET.get('statut', ''),
        'filter_search': request.GET.get('search', ''),

        'chauffeurs': Chauffeur.objects.filter(entreprise=request.user.entreprise).order_by('nom'),
        'clients': Client.objects.filter(entreprise=request.user.entreprise).order_by('nom'),
    }

    return render(request, 'transport/cautions/cautions_list.html', context)
