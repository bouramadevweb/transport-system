"""
Vues pour le Dashboard avec Statistiques et KPIs
=================================================

Ce module contient les vues pour afficher un tableau de bord complet
avec des statistiques, KPIs et graphiques.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from .models import (
    Mission, PaiementMission, Conteneur, Camion, Chauffeur,
    ContratTransport, Reparation, Client, Transitaire, Cautions
)


@login_required
def dashboard_home(request):
    """
    Dashboard principal avec vue d'ensemble et KPIs
    """
    # Période par défaut : 30 derniers jours
    today = timezone.now().date()
    period_start = today - timedelta(days=30)

    # Filtres personnalisables
    filter_period = request.GET.get('period', '30')  # 7, 30, 90, 365, all

    if filter_period == '7':
        period_start = today - timedelta(days=7)
    elif filter_period == '30':
        period_start = today - timedelta(days=30)
    elif filter_period == '90':
        period_start = today - timedelta(days=90)
    elif filter_period == '365':
        period_start = today - timedelta(days=365)
    elif filter_period == 'all':
        period_start = None

    # Entreprise de l'utilisateur courant (isolation multi-tenant)
    entreprise = getattr(request.user, 'entreprise', None)

    # === KPIs PAR ENTREPRISE ===

    # 1. Missions
    missions_qs = Mission.objects.filter(contrat__entreprise=entreprise)
    total_missions = missions_qs.count()
    if period_start:
        missions_periode = missions_qs.filter(date_depart__gte=period_start)
    else:
        missions_periode = missions_qs

    missions_en_cours = missions_qs.filter(statut='en cours').count()
    missions_terminees = missions_qs.filter(statut='terminée').count()
    missions_annulees = missions_qs.filter(statut='annulée').count()
    missions_periode_count = missions_periode.count()

    # Taux de réussite
    if total_missions > 0:
        taux_reussite = round((missions_terminees / total_missions) * 100, 1)
        taux_annulation = round((missions_annulees / total_missions) * 100, 1)
    else:
        taux_reussite = 0
        taux_annulation = 0

    # 2. Chiffre d'affaires
    paiements_qs = PaiementMission.objects.filter(mission__contrat__entreprise=entreprise)
    if period_start:
        paiements_valides = paiements_qs.filter(
            est_valide=True,
            date_validation__gte=period_start
        )
    else:
        paiements_valides = paiements_qs.filter(est_valide=True)

    ca_total = paiements_valides.aggregate(total=Sum('montant_total'))['total'] or 0
    commission_total = paiements_valides.aggregate(total=Sum('commission_transitaire'))['total'] or 0
    ca_net = Decimal(ca_total) - Decimal(commission_total)

    # CA en attente (paiements non validés)
    ca_en_attente = paiements_qs.filter(
        est_valide=False
    ).aggregate(total=Sum('montant_total'))['total'] or 0

    # 3. Ressources
    # Conteneurs liés à l'entreprise via les contrats (Client.entreprise peut être null)
    conteneurs_qs = Conteneur.objects.filter(contrattransport__entreprise=entreprise).distinct()
    total_conteneurs = conteneurs_qs.count()
    conteneurs_disponibles = conteneurs_qs.filter(statut='au_port').count()
    conteneurs_en_mission = conteneurs_qs.filter(statut='en_mission').count()
    conteneurs_maintenance = conteneurs_qs.filter(statut='en_maintenance').count()

    # Taux d'occupation des conteneurs
    if total_conteneurs > 0:
        taux_occupation_conteneurs = round((conteneurs_en_mission / total_conteneurs) * 100, 1)
    else:
        taux_occupation_conteneurs = 0

    camions_qs = Camion.objects.filter(entreprise=entreprise)
    total_camions = camions_qs.count()
    camions_affectes = camions_qs.filter(est_affecter=True).count()
    camions_disponibles = total_camions - camions_affectes

    # Taux d'occupation des camions
    if total_camions > 0:
        taux_occupation_camions = round((camions_affectes / total_camions) * 100, 1)
    else:
        taux_occupation_camions = 0

    chauffeurs_qs = Chauffeur.objects.filter(entreprise=entreprise)
    total_chauffeurs = chauffeurs_qs.count()
    chauffeurs_affectes = chauffeurs_qs.filter(est_affecter=True).count()
    chauffeurs_disponibles = total_chauffeurs - chauffeurs_affectes

    # 4. Clients et Transitaires (via les contrats de l'entreprise)
    total_clients = Client.objects.filter(
        contrattransport__entreprise=entreprise
    ).distinct().count()
    total_transitaires = Transitaire.objects.filter(
        contrattransport__entreprise=entreprise
    ).distinct().count()

    # Top 5 clients (par nombre de missions)
    top_clients = Client.objects.filter(
        contrattransport__entreprise=entreprise
    ).annotate(
        nb_missions=Count('contrattransport__mission')
    ).order_by('-nb_missions').distinct()[:5]

    # 5. Cautions
    cautions_qs = Cautions.objects.filter(contrat__entreprise=entreprise)
    cautions_bloquees = cautions_qs.filter(statut='en_attente').aggregate(
        total=Sum('montant')
    )['total'] or 0

    cautions_remboursees = cautions_qs.filter(statut='remboursee').count()
    cautions_consommees = cautions_qs.filter(statut='consommee').count()

    # 6. Réparations et coûts
    reparations_qs = Reparation.objects.filter(camion__entreprise=entreprise)
    if period_start:
        reparations_periode = reparations_qs.filter(date_reparation__gte=period_start)
    else:
        reparations_periode = reparations_qs

    cout_reparations = reparations_periode.aggregate(total=Sum('cout'))['total'] or 0
    nb_reparations = reparations_periode.count()

    # === DONNÉES POUR GRAPHIQUES ===

    # Graphique 1: Évolution des missions par mois (6 derniers mois)
    six_months_ago = today - timedelta(days=180)
    missions_par_mois = missions_qs.filter(
        date_depart__gte=six_months_ago
    ).annotate(
        mois=TruncMonth('date_depart')
    ).values('mois').annotate(
        total=Count('pk_mission'),
        en_cours=Count('pk_mission', filter=Q(statut='en cours')),
        terminees=Count('pk_mission', filter=Q(statut='terminée')),
        annulees=Count('pk_mission', filter=Q(statut='annulée'))
    ).order_by('mois')

    # Formater pour Chart.js
    labels_mois = [m['mois'].strftime('%b %Y') for m in missions_par_mois]
    data_total = [m['total'] for m in missions_par_mois]
    data_terminees = [m['terminees'] for m in missions_par_mois]
    data_annulees = [m['annulees'] for m in missions_par_mois]

    # Graphique 2: CA par mois (6 derniers mois)
    ca_par_mois = paiements_qs.filter(
        est_valide=True,
        date_validation__gte=six_months_ago
    ).annotate(
        mois=TruncMonth('date_validation')
    ).values('mois').annotate(
        ca=Sum('montant_total'),
        commission=Sum('commission_transitaire')
    ).order_by('mois')

    labels_ca_mois = [c['mois'].strftime('%b %Y') for c in ca_par_mois]
    data_ca = [float(c['ca']) for c in ca_par_mois]
    data_commission = [float(c['commission']) for c in ca_par_mois]

    # Graphique 3: Statut des missions (pie chart)
    missions_statut = {
        'en_cours': missions_en_cours,
        'terminees': missions_terminees,
        'annulees': missions_annulees
    }

    # Graphique 4: Taux d'occupation des ressources
    occupation_data = {
        'conteneurs': {
            'disponibles': conteneurs_disponibles,
            'en_mission': conteneurs_en_mission,
            'maintenance': conteneurs_maintenance
        },
        'camions': {
            'disponibles': camions_disponibles,
            'affectes': camions_affectes
        },
        'chauffeurs': {
            'disponibles': chauffeurs_disponibles,
            'affectes': chauffeurs_affectes
        }
    }

    # === ALERTES ET NOTIFICATIONS ===

    # Missions en retard (date_depart > 23 jours et pas de retour)
    date_limite_alerte = today - timedelta(days=23)
    missions_retard = missions_qs.filter(
        statut='en cours',
        date_depart__lte=date_limite_alerte,
        date_retour__isnull=True
    ).select_related('contrat__chauffeur', 'contrat__camion')

    # Conteneurs bloqués en mission depuis longtemps
    conteneurs_bloques = conteneurs_qs.filter(
        statut='en_mission'
    ).select_related('client')

    # Cautions en attente de remboursement
    cautions_en_attente = cautions_qs.filter(
        statut='en_attente'
    ).count()

    # Contexte pour le template
    context = {
        'title': 'Dashboard - Vue d\'ensemble',
        'filter_period': filter_period,
        'period_start': period_start,

        # KPIs Missions
        'total_missions': total_missions,
        'missions_periode_count': missions_periode_count,
        'missions_en_cours': missions_en_cours,
        'missions_terminees': missions_terminees,
        'missions_annulees': missions_annulees,
        'taux_reussite': taux_reussite,
        'taux_annulation': taux_annulation,

        # KPIs Financiers
        'ca_total': ca_total,
        'ca_net': ca_net,
        'commission_total': commission_total,
        'ca_en_attente': ca_en_attente,
        'cautions_bloquees': cautions_bloquees,

        # KPIs Ressources
        'total_conteneurs': total_conteneurs,
        'conteneurs_disponibles': conteneurs_disponibles,
        'conteneurs_en_mission': conteneurs_en_mission,
        'conteneurs_maintenance': conteneurs_maintenance,
        'taux_occupation_conteneurs': taux_occupation_conteneurs,

        'total_camions': total_camions,
        'camions_affectes': camions_affectes,
        'camions_disponibles': camions_disponibles,
        'taux_occupation_camions': taux_occupation_camions,

        'total_chauffeurs': total_chauffeurs,
        'chauffeurs_affectes': chauffeurs_affectes,
        'chauffeurs_disponibles': chauffeurs_disponibles,

        # Clients
        'total_clients': total_clients,
        'total_transitaires': total_transitaires,
        'top_clients': top_clients,

        # Réparations
        'cout_reparations': cout_reparations,
        'nb_reparations': nb_reparations,

        # Cautions
        'cautions_remboursees': cautions_remboursees,
        'cautions_consommees': cautions_consommees,
        'cautions_en_attente': cautions_en_attente,

        # Données pour graphiques
        'chart_missions_labels': labels_mois,
        'chart_missions_total': data_total,
        'chart_missions_terminees': data_terminees,
        'chart_missions_annulees': data_annulees,

        'chart_ca_labels': labels_ca_mois,
        'chart_ca_data': data_ca,
        'chart_commission_data': data_commission,

        'missions_statut': missions_statut,
        'occupation_data': occupation_data,

        # Alertes
        'missions_retard': missions_retard,
        'nb_missions_retard': missions_retard.count(),
        'conteneurs_bloques': conteneurs_bloques,
    }

    return render(request, 'transport/dashboard/home.html', context)


@login_required
def dashboard_financier(request):
    """
    Dashboard financier détaillé
    """
    today = timezone.now().date()
    filter_period = request.GET.get('period', '30')

    if filter_period == '7':
        period_start = today - timedelta(days=7)
    elif filter_period == '30':
        period_start = today - timedelta(days=30)
    elif filter_period == '90':
        period_start = today - timedelta(days=90)
    elif filter_period == '365':
        period_start = today - timedelta(days=365)
    else:
        period_start = None

    # Entreprise de l'utilisateur courant
    entreprise = getattr(request.user, 'entreprise', None)

    # Tous les paiements de l'entreprise (validés + en attente)
    paiements_qs_base = PaiementMission.objects.filter(
        mission__contrat__entreprise=entreprise
    )
    if period_start:
        paiements_qs_base = paiements_qs_base.filter(date_paiement__gte=period_start)

    # Paiements validés uniquement
    paiements_valides = paiements_qs_base.filter(est_valide=True)
    # Paiements en attente
    paiements_attente = paiements_qs_base.filter(est_valide=False)

    # === KPIs ===
    ca_valide = paiements_valides.aggregate(total=Sum('montant_total'))['total'] or 0
    ca_en_attente = paiements_attente.aggregate(total=Sum('montant_total'))['total'] or 0
    ca_total = Decimal(ca_valide) + Decimal(ca_en_attente)

    commission_total = paiements_valides.aggregate(total=Sum('commission_transitaire'))['total'] or 0
    ca_net = Decimal(ca_valide) - Decimal(commission_total)

    nb_paiements_valides = paiements_valides.count()
    nb_paiements_attente = paiements_attente.count()
    nb_paiements = paiements_qs_base.count()

    ca_moyen = (ca_valide / nb_paiements_valides) if nb_paiements_valides > 0 else 0

    # === Évolution CA par semaine (8 dernières semaines) — tous paiements ===
    eight_weeks_ago = today - timedelta(weeks=8)
    ca_par_semaine = PaiementMission.objects.filter(
        mission__contrat__entreprise=entreprise,
        date_paiement__gte=eight_weeks_ago
    ).annotate(
        semaine=TruncWeek('date_paiement')
    ).values('semaine').annotate(
        ca=Sum('montant_total'),
        ca_valide=Sum('montant_total', filter=Q(est_valide=True)),
        ca_attente=Sum('montant_total', filter=Q(est_valide=False)),
    ).order_by('semaine')

    labels_semaine = [s['semaine'].strftime('%d/%m') for s in ca_par_semaine]
    data_ca_semaine = [float(s['ca'] or 0) for s in ca_par_semaine]
    data_ca_valide_semaine = [float(s['ca_valide'] or 0) for s in ca_par_semaine]
    data_ca_attente_semaine = [float(s['ca_attente'] or 0) for s in ca_par_semaine]

    # === Top clients par CA total (tous paiements) ===
    top_clients_ca = Client.objects.filter(
        contrattransport__entreprise=entreprise
    ).annotate(
        ca=Sum('contrattransport__mission__paiementmission__montant_total'),
        ca_valide=Sum('contrattransport__mission__paiementmission__montant_total',
                      filter=Q(contrattransport__mission__paiementmission__est_valide=True)),
    ).order_by('-ca').distinct()[:10]

    # === Répartition CA par type de client ===
    ca_entreprises = Client.objects.filter(
        contrattransport__entreprise=entreprise,
        type_client='entreprise'
    ).annotate(
        ca=Sum('contrattransport__mission__paiementmission__montant_total')
    ).aggregate(total=Sum('ca'))['total'] or 0

    ca_particuliers = Client.objects.filter(
        contrattransport__entreprise=entreprise,
        type_client='particulier'
    ).annotate(
        ca=Sum('contrattransport__mission__paiementmission__montant_total')
    ).aggregate(total=Sum('ca'))['total'] or 0

    context = {
        'title': 'Dashboard Financier',
        'filter_period': filter_period,

        'ca_total': ca_total,
        'ca_valide': ca_valide,
        'ca_en_attente': ca_en_attente,
        'ca_net': ca_net,
        'commission_total': commission_total,
        'ca_moyen': ca_moyen,

        'nb_paiements': nb_paiements,
        'nb_paiements_valides': nb_paiements_valides,
        'nb_paiements_attente': nb_paiements_attente,

        'chart_semaine_labels': labels_semaine,
        'chart_semaine_data': data_ca_semaine,
        'chart_semaine_valide': data_ca_valide_semaine,
        'chart_semaine_attente': data_ca_attente_semaine,

        'top_clients_ca': top_clients_ca,
        'ca_entreprises': ca_entreprises,
        'ca_particuliers': ca_particuliers,
    }

    return render(request, 'transport/dashboard/financier.html', context)
