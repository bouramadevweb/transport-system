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

    # === KPIs GLOBAUX ===

    # 1. Missions
    total_missions = Mission.objects.count()
    if period_start:
        missions_periode = Mission.objects.filter(date_depart__gte=period_start)
    else:
        missions_periode = Mission.objects.all()

    missions_en_cours = Mission.objects.filter(statut='en cours').count()
    missions_terminees = Mission.objects.filter(statut='terminée').count()
    missions_annulees = Mission.objects.filter(statut='annulée').count()
    missions_periode_count = missions_periode.count()

    # Taux de réussite
    if total_missions > 0:
        taux_reussite = round((missions_terminees / total_missions) * 100, 1)
        taux_annulation = round((missions_annulees / total_missions) * 100, 1)
    else:
        taux_reussite = 0
        taux_annulation = 0

    # 2. Chiffre d'affaires
    if period_start:
        paiements_valides = PaiementMission.objects.filter(
            est_valide=True,
            date_validation__gte=period_start
        )
    else:
        paiements_valides = PaiementMission.objects.filter(est_valide=True)

    ca_total = paiements_valides.aggregate(total=Sum('montant_total'))['total'] or 0
    commission_total = paiements_valides.aggregate(total=Sum('commission_transitaire'))['total'] or 0
    ca_net = Decimal(ca_total) - Decimal(commission_total)

    # CA en attente (paiements non validés)
    ca_en_attente = PaiementMission.objects.filter(
        est_valide=False
    ).aggregate(total=Sum('montant_total'))['total'] or 0

    # 3. Ressources
    total_conteneurs = Conteneur.objects.count()
    conteneurs_disponibles = Conteneur.objects.filter(statut='au_port').count()
    conteneurs_en_mission = Conteneur.objects.filter(statut='en_mission').count()
    conteneurs_maintenance = Conteneur.objects.filter(statut='en_maintenance').count()

    # Taux d'occupation des conteneurs
    if total_conteneurs > 0:
        taux_occupation_conteneurs = round((conteneurs_en_mission / total_conteneurs) * 100, 1)
    else:
        taux_occupation_conteneurs = 0

    total_camions = Camion.objects.count()
    camions_affectes = Camion.objects.filter(est_affecter=True).count()
    camions_disponibles = total_camions - camions_affectes

    # Taux d'occupation des camions
    if total_camions > 0:
        taux_occupation_camions = round((camions_affectes / total_camions) * 100, 1)
    else:
        taux_occupation_camions = 0

    total_chauffeurs = Chauffeur.objects.count()
    chauffeurs_affectes = Chauffeur.objects.filter(est_affecter=True).count()
    chauffeurs_disponibles = total_chauffeurs - chauffeurs_affectes

    # 4. Clients et Transitaires
    total_clients = Client.objects.count()
    total_transitaires = Transitaire.objects.count()

    # Top 5 clients (par nombre de missions)
    top_clients = Client.objects.annotate(
        nb_missions=Count('contrattransport__mission')
    ).order_by('-nb_missions')[:5]

    # 5. Cautions
    cautions_bloquees = Cautions.objects.filter(statut='en_attente').aggregate(
        total=Sum('montant')
    )['total'] or 0

    cautions_remboursees = Cautions.objects.filter(statut='remboursee').count()
    cautions_consommees = Cautions.objects.filter(statut='consommee').count()

    # 6. Réparations et coûts
    if period_start:
        reparations_periode = Reparation.objects.filter(date_reparation__gte=period_start)
    else:
        reparations_periode = Reparation.objects.all()

    cout_reparations = reparations_periode.aggregate(total=Sum('cout'))['total'] or 0
    nb_reparations = reparations_periode.count()

    # === DONNÉES POUR GRAPHIQUES ===

    # Graphique 1: Évolution des missions par mois (6 derniers mois)
    six_months_ago = today - timedelta(days=180)
    missions_par_mois = Mission.objects.filter(
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
    ca_par_mois = PaiementMission.objects.filter(
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
    missions_retard = Mission.objects.filter(
        statut='en cours',
        date_depart__lte=date_limite_alerte,
        date_retour__isnull=True
    ).select_related('contrat__chauffeur', 'contrat__camion')

    # Conteneurs bloqués en mission depuis longtemps
    conteneurs_bloques = Conteneur.objects.filter(
        statut='en_mission'
    ).select_related('client')

    # Cautions en attente de remboursement
    cautions_en_attente = Cautions.objects.filter(
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
    # Période
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

    # Paiements validés
    if period_start:
        paiements = PaiementMission.objects.filter(
            est_valide=True,
            date_validation__gte=period_start
        )
    else:
        paiements = PaiementMission.objects.filter(est_valide=True)

    # KPIs financiers
    ca_total = paiements.aggregate(total=Sum('montant_total'))['total'] or 0
    commission_total = paiements.aggregate(total=Sum('commission_transitaire'))['total'] or 0
    ca_net = Decimal(ca_total) - Decimal(commission_total)

    # CA moyen par mission
    nb_paiements = paiements.count()
    if nb_paiements > 0:
        ca_moyen = ca_total / nb_paiements
    else:
        ca_moyen = 0

    # Évolution CA par semaine (8 dernières semaines)
    eight_weeks_ago = today - timedelta(weeks=8)
    ca_par_semaine = PaiementMission.objects.filter(
        est_valide=True,
        date_validation__gte=eight_weeks_ago
    ).annotate(
        semaine=TruncWeek('date_validation')
    ).values('semaine').annotate(
        ca=Sum('montant_total')
    ).order_by('semaine')

    labels_semaine = [s['semaine'].strftime('%d/%m') for s in ca_par_semaine]
    data_ca_semaine = [float(s['ca']) for s in ca_par_semaine]

    # Top clients par CA
    top_clients_ca = Client.objects.annotate(
        ca=Sum('contrattransport__mission__paiementmission__montant_total',
               filter=Q(contrattransport__mission__paiementmission__est_valide=True))
    ).order_by('-ca')[:10]

    # Répartition CA par type de client
    ca_entreprises = Client.objects.filter(
        type_client='entreprise'
    ).annotate(
        ca=Sum('contrattransport__mission__paiementmission__montant_total',
               filter=Q(contrattransport__mission__paiementmission__est_valide=True))
    ).aggregate(total=Sum('ca'))['total'] or 0

    ca_particuliers = Client.objects.filter(
        type_client='particulier'
    ).annotate(
        ca=Sum('contrattransport__mission__paiementmission__montant_total',
               filter=Q(contrattransport__mission__paiementmission__est_valide=True))
    ).aggregate(total=Sum('ca'))['total'] or 0

    context = {
        'title': 'Dashboard Financier',
        'filter_period': filter_period,
        'ca_total': ca_total,
        'ca_net': ca_net,
        'commission_total': commission_total,
        'ca_moyen': ca_moyen,
        'nb_paiements': nb_paiements,

        'chart_semaine_labels': labels_semaine,
        'chart_semaine_data': data_ca_semaine,

        'top_clients_ca': top_clients_ca,
        'ca_entreprises': ca_entreprises,
        'ca_particuliers': ca_particuliers,
    }

    return render(request, 'transport/dashboard/financier.html', context)
