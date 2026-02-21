"""
Dashboard Views.Py

Vues pour dashboard
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse

from ..models import (
    Chauffeur, Camion, Mission, Reparation, PaiementMission, Affectation,
    Client, Notification, AuditLog, Entreprise, ContratTransport,
    PieceReparee, Utilisateur
)
from ..decorators import manager_or_admin_required

logger = logging.getLogger('transport')


@login_required
def dashboard(request):
    from datetime import timedelta, datetime
    from django.utils import timezone

    # ========== RÉCUPÉRATION DES FILTRES DE DATE ==========
    date_debut_str = request.GET.get('date_debut', '')
    date_fin_str = request.GET.get('date_fin', '')

    date_debut = None
    date_fin = None

    if date_debut_str:
        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if date_fin_str:
        try:
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # ========== APPLICATION DES FILTRES ==========
    # Missions queryset with filters
    missions_qs = Mission.objects.all()
    if date_debut:
        missions_qs = missions_qs.filter(date_depart__gte=date_debut)
    if date_fin:
        missions_qs = missions_qs.filter(date_depart__lte=date_fin)

    # Paiements queryset with filters
    paiements_qs = PaiementMission.objects.all()
    if date_debut:
        paiements_qs = paiements_qs.filter(date_paiement__gte=date_debut)
    if date_fin:
        paiements_qs = paiements_qs.filter(date_paiement__lte=date_fin)

    # Réparations queryset with filters
    reparations_qs = Reparation.objects.all()
    if date_debut:
        reparations_qs = reparations_qs.filter(date_reparation__gte=date_debut)
    if date_fin:
        reparations_qs = reparations_qs.filter(date_reparation__lte=date_fin)

    # Statistiques générales
    stats = {
        "chauffeurs": Chauffeur.objects.count(),
        "camions": Camion.objects.count(),
        "missions": missions_qs.count(),
        "missions_en_cours": missions_qs.filter(statut="en cours").count(),
        "missions_terminees": missions_qs.filter(statut="terminée").count(),
        "reparations": reparations_qs.count(),
        "paiements": paiements_qs.aggregate(total=Sum("montant_total"))["total"] or 0,
        "clients": Client.objects.count(),
        "affectations": Affectation.objects.count(),
    }

    # Missions par statut pour le graphique
    mission_par_statut = missions_qs.values("statut").annotate(total=Count("statut"))

    # Paiements mensuels
    paiements_mensuels = (
        paiements_qs
        .annotate(mois=TruncMonth("date_paiement"))
        .values("mois")
        .annotate(total=Sum("montant_total"))
        .order_by("mois")
    )

    mois_labels = [p["mois"].strftime("%b %Y") for p in paiements_mensuels]
    montant_values = [float(p["total"]) for p in paiements_mensuels]

    # Dernières missions (5 plus récentes)
    dernieres_missions = missions_qs.select_related(
        'prestation_transport', 'contrat'
    ).order_by('-date_depart')[:5]

    # Derniers paiements (5 plus récents)
    derniers_paiements = paiements_qs.select_related(
        'mission'
    ).order_by('-date_paiement')[:5]

    # Missions en cours
    missions_actives = missions_qs.filter(
        statut="en cours"
    ).select_related('prestation_transport', 'contrat')[:5]

    # Alertes - Missions qui devraient être terminées (date retour passée)
    today = timezone.now().date()
    missions_en_retard = missions_qs.filter(
        statut="en cours",
        date_retour__lt=today
    ).count() if missions_qs.filter(statut="en cours").exists() else 0

    # Réparations récentes
    reparations_recentes = reparations_qs.select_related(
        'camion'
    ).order_by('-date_reparation')[:5]

    # Statistiques par entreprise
    entreprises_stats = []
    entreprises = Entreprise.objects.all()
    for entreprise in entreprises:
        entreprises_stats.append({
            'nom': entreprise.nom,
            'chauffeurs': Chauffeur.objects.filter(entreprise=entreprise).count(),
            'camions': Camion.objects.filter(entreprise=entreprise).count(),
        })

    # Calcul des revenus du mois en cours (ou période filtrée)
    if date_debut and date_fin:
        revenus_mois_actuel = paiements_qs.aggregate(total=Sum("montant_total"))["total"] or 0
    else:
        current_month = timezone.now().month
        current_year = timezone.now().year
        revenus_mois_actuel = PaiementMission.objects.filter(
            date_paiement__month=current_month,
            date_paiement__year=current_year
        ).aggregate(total=Sum("montant_total"))["total"] or 0

    return render(request, "transport/dashboard.html", {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "stats": stats,
        "mission_par_statut": list(mission_par_statut),
        "paiements_mois_labels": mois_labels,
        "paiements_mois_values": montant_values,
        "dernieres_missions": dernieres_missions,
        "derniers_paiements": derniers_paiements,
        "missions_actives": missions_actives,
        "missions_en_retard": missions_en_retard,
        "reparations_recentes": reparations_recentes,
        "entreprises_stats": entreprises_stats,
        "revenus_mois_actuel": revenus_mois_actuel,
    })

# gestion url redirection si pas bon url vers la connexion
# def rediriger_vers_connexion(request, exception=None):
#     return redirect('connexion')

# handler404 = rediriger_vers_connexion
# # gestion probleme server si la connexion n'est pas bon 
# def rediriger_erreur_serveur(request):
#     return redirect('connexion')

# handler500 = rediriger_erreur_serveur

# ============================================================================
# PROFIL UTILISATEUR ET SYSTÈME
# ============================================================================

@login_required
def help_page(request):
    """
    Affiche la page d'aide et documentation
    """
    return render(request, 'transport/user/help.html', {
        'title': 'Aide'
    })

@login_required
def notifications_list(request):
    """
    Affiche la liste des notifications de l'utilisateur
    """
    # Récupérer toutes les notifications de l'utilisateur
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-created_at')

    # Séparer les notifications lues et non lues
    notifications_non_lues = notifications.filter(is_read=False)
    notifications_lues = notifications.filter(is_read=True)[:10]  # Limiter les notifications lues

    # Marquer comme lue une notification spécifique si demandé
    notification_id = request.GET.get('mark_read')
    if notification_id:
        try:
            notification = Notification.objects.get(pk_notification=notification_id, utilisateur=request.user)
            notification.is_read = True
            notification.save()
            messages.success(request, "✅ Notification marquée comme lue.")
            return redirect('notifications_list')
        except Notification.DoesNotExist:
            pass

    return render(request, 'transport/user/notifications.html', {
        'title': 'Notifications',
        'notifications': notifications,
        'notifications_non_lues': notifications_non_lues,
        'notifications_lues': notifications_lues,
        'total_non_lues': notifications_non_lues.count(),
    })

@login_required
def mark_all_notifications_read(request):
    """
    Marque toutes les notifications comme lues
    """
    if request.method == 'POST':
        # Marquer toutes les notifications de l'utilisateur comme lues
        count = Notification.objects.filter(
            utilisateur=request.user,
            is_read=False
        ).update(is_read=True)

        if count > 0:
            messages.success(request, f"✅ {count} notification(s) marquée(s) comme lue(s).")
        else:
            messages.info(request, "ℹ️ Aucune notification non lue.")

        return redirect('notifications_list')

    return redirect('notifications_list')

# ============================================================================
# GESTIONNAIRES D'ERREURS
# ============================================================================

@login_required
def tableau_bord_statistiques(request):
    """
    Affiche le tableau de bord avec toutes les statistiques avancées :
    - Statistiques par camion/chauffeur
    - Évolution temporelle (par mois/année)
    - Top et bottom performers
    """
    from datetime import datetime

    # ========== RÉCUPÉRATION DES FILTRES DE DATE ==========
    date_debut_str = request.GET.get('date_debut', '')
    date_fin_str = request.GET.get('date_fin', '')

    date_debut = None
    date_fin = None

    if date_debut_str:
        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if date_fin_str:
        try:
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # ========== STATISTIQUES GLOBALES ==========
    # Apply date filters to missions
    missions_qs = Mission.objects.all()
    if date_debut:
        missions_qs = missions_qs.filter(date_depart__gte=date_debut)
    if date_fin:
        missions_qs = missions_qs.filter(date_depart__lte=date_fin)

    # Apply date filters to contracts
    contrats_qs = ContratTransport.objects.all()
    if date_debut:
        contrats_qs = contrats_qs.filter(date_debut__gte=date_debut)
    if date_fin:
        contrats_qs = contrats_qs.filter(date_debut__lte=date_fin)

    # Apply date filters to reparations
    reparations_qs = Reparation.objects.all()
    if date_debut:
        reparations_qs = reparations_qs.filter(date_reparation__gte=date_debut)
    if date_fin:
        reparations_qs = reparations_qs.filter(date_reparation__lte=date_fin)

    # Apply date filters to pieces
    pieces_qs = PieceReparee.objects.all()
    if date_debut:
        pieces_qs = pieces_qs.filter(reparation__date_reparation__gte=date_debut)
    if date_fin:
        pieces_qs = pieces_qs.filter(reparation__date_reparation__lte=date_fin)

    total_missions = missions_qs.count()
    total_camions = Camion.objects.count()
    total_chauffeurs = Chauffeur.objects.count()
    total_reparations = reparations_qs.count()
    total_pieces = pieces_qs.count()
    ca_total = contrats_qs.aggregate(total=Sum('montant_total'))['total'] or 0
    cout_reparations_total = reparations_qs.aggregate(total=Sum('cout'))['total'] or 0
    cout_pieces_total = pieces_qs.aggregate(total=Sum(F('quantite') * F('cout_unitaire')))['total'] or 0

    # ========== TOP PERFORMERS ==========

    # Camion avec le plus de missions
    top_camion_missions = missions_qs.values(
        'contrat__camion__immatriculation',
        'contrat__camion__modele'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions').first()

    # Chauffeur avec le plus de missions
    top_chauffeur_missions = missions_qs.values(
        'contrat__chauffeur__nom',
        'contrat__chauffeur__prenom'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions').first()

    # Camion qui a généré le plus d'argent
    top_camion_ca = contrats_qs.values(
        'camion__immatriculation',
        'camion__modele'
    ).annotate(ca_total=Sum('montant_total')).order_by('-ca_total').first()

    # Camion avec le moins de réparations (qui a au moins une réparation)
    bottom_camion_reparations = reparations_qs.values(
        'camion__immatriculation',
        'camion__modele'
    ).annotate(nb_reparations=Count('pk_reparation')).order_by('nb_reparations').first()

    # ========== STATISTIQUES PAR CAMION ==========

    # 1. Missions par camion
    missions_par_camion = missions_qs.values(
        'contrat__camion__pk_camion',
        'contrat__camion__immatriculation',
        'contrat__camion__modele'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions')

    # 2. Missions par chauffeur
    missions_par_chauffeur = missions_qs.values(
        'contrat__chauffeur__pk_chauffeur',
        'contrat__chauffeur__nom',
        'contrat__chauffeur__prenom'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions')

    # 3. CA par camion
    ca_par_camion = contrats_qs.values(
        'camion__pk_camion',
        'camion__immatriculation',
        'camion__modele'
    ).annotate(ca_total=Sum('montant_total')).order_by('-ca_total')

    # 4. Réparations par camion
    reparations_par_camion = reparations_qs.values(
        'camion__pk_camion',
        'camion__immatriculation',
        'camion__modele'
    ).annotate(
        nb_reparations=Count('pk_reparation'),
        cout_total=Sum('cout')
    ).order_by('-nb_reparations')

    # ========== ÉVOLUTION TEMPORELLE (PAR MOIS) ==========

    # Missions par mois et par camion
    missions_par_mois_camion = missions_qs.annotate(
        mois=TruncMonth('date_depart')
    ).values(
        'mois',
        'contrat__camion__immatriculation'
    ).annotate(
        nb_missions=Count('pk_mission')
    ).order_by('-mois', 'contrat__camion__immatriculation')

    # CA par mois et par camion
    ca_par_mois_camion = contrats_qs.annotate(
        mois=TruncMonth('date_debut')
    ).values(
        'mois',
        'camion__immatriculation'
    ).annotate(
        ca=Sum('montant_total')
    ).order_by('-mois', 'camion__immatriculation')

    # Réparations par mois et par camion
    reparations_par_mois_camion = reparations_qs.annotate(
        mois=TruncMonth('date_reparation')
    ).values(
        'mois',
        'camion__immatriculation'
    ).annotate(
        nb_reparations=Count('pk_reparation'),
        cout_total=Sum('cout')
    ).order_by('-mois', 'camion__immatriculation')

    # Pièces réparées par mois et par camion
    pieces_par_mois_camion = pieces_qs.annotate(
        mois=TruncMonth('reparation__date_reparation')
    ).values(
        'mois',
        'reparation__camion__immatriculation'
    ).annotate(
        nb_pieces=Count('pk_piece'),
        cout_total=Sum(F('quantite') * F('cout_unitaire'))
    ).order_by('-mois', 'reparation__camion__immatriculation')

    # ========== ÉVOLUTION TEMPORELLE (PAR ANNÉE) ==========

    # Missions par année
    missions_par_annee = missions_qs.annotate(
        annee=TruncYear('date_depart')
    ).values('annee').annotate(
        nb_missions=Count('pk_mission')
    ).order_by('-annee')

    # CA par année
    ca_par_annee = contrats_qs.annotate(
        annee=TruncYear('date_debut')
    ).values('annee').annotate(
        ca=Sum('montant_total')
    ).order_by('-annee')

    # Réparations par année
    reparations_par_annee = reparations_qs.annotate(
        annee=TruncYear('date_reparation')
    ).values('annee').annotate(
        nb_reparations=Count('pk_reparation'),
        cout_total=Sum('cout')
    ).order_by('-annee')

    # ========== PIÈCES ==========

    # Pièces réparées détaillées
    pieces_reparees = pieces_qs.select_related(
        'reparation__camion', 'fournisseur'
    ).annotate(
        cout_total_piece=F('quantite') * F('cout_unitaire')
    ).order_by('-cout_total_piece')

    # Statistiques des pièces par catégorie
    pieces_par_categorie = pieces_qs.values(
        'categorie'
    ).annotate(
        nb_pieces=Count('pk_piece'),
        cout_total=Sum(F('quantite') * F('cout_unitaire'))
    ).order_by('-cout_total')

    # Ajouter le nom de la catégorie
    for item in pieces_par_categorie:
        item['categorie_display'] = dict(
            PieceReparee._meta.get_field('categorie').choices
        ).get(item['categorie'], item['categorie'])

    context = {
        'title': 'Tableau de bord - Statistiques',

        # Filtres de date
        'date_debut': date_debut,
        'date_fin': date_fin,

        # Globales
        'total_missions': total_missions,
        'total_camions': total_camions,
        'total_chauffeurs': total_chauffeurs,
        'total_reparations': total_reparations,
        'total_pieces': total_pieces,
        'ca_total': ca_total,
        'cout_reparations_total': cout_reparations_total,
        'cout_pieces_total': cout_pieces_total,

        # Top performers
        'top_camion_missions': top_camion_missions,
        'top_chauffeur_missions': top_chauffeur_missions,
        'top_camion_ca': top_camion_ca,
        'bottom_camion_reparations': bottom_camion_reparations,

        # Par camion/chauffeur
        'missions_par_camion': missions_par_camion,
        'missions_par_chauffeur': missions_par_chauffeur,
        'ca_par_camion': ca_par_camion,
        'reparations_par_camion': reparations_par_camion,

        # Évolution temporelle (mois)
        'missions_par_mois_camion': missions_par_mois_camion,
        'ca_par_mois_camion': ca_par_mois_camion,
        'reparations_par_mois_camion': reparations_par_mois_camion,
        'pieces_par_mois_camion': pieces_par_mois_camion,

        # Évolution temporelle (année)
        'missions_par_annee': missions_par_annee,
        'ca_par_annee': ca_par_annee,
        'reparations_par_annee': reparations_par_annee,

        # Pièces
        'pieces_reparees': pieces_reparees,
        'pieces_par_categorie': pieces_par_categorie,
    }

    return render(request, 'transport/statistiques/tableau_bord.html', context)


# ============================================================================
# AUDIT LOG / HISTORIQUE
# ============================================================================

@manager_or_admin_required
def audit_log_list(request):
    """
    Affiche l'historique complet des actions effectuées dans le système
    Accessible uniquement aux managers et admins
    """
    from django.db.models import Count

    # Récupérer tous les logs
    all_logs = AuditLog.objects.select_related('utilisateur').order_by('-timestamp')
    logs = all_logs

    # Filtrage
    action_filter = request.GET.get('action')
    if action_filter and action_filter != 'tous':
        logs = logs.filter(action=action_filter)

    model_filter = request.GET.get('model')
    if model_filter:
        logs = logs.filter(model_name__icontains=model_filter)

    user_filter = request.GET.get('utilisateur')
    if user_filter:
        logs = logs.filter(utilisateur__pk_utilisateur=user_filter)

    date_debut = request.GET.get('date_debut')
    if date_debut:
        try:
            logs = logs.filter(timestamp__date__gte=date_debut)
        except ValueError:
            pass

    date_fin = request.GET.get('date_fin')
    if date_fin:
        try:
            logs = logs.filter(timestamp__date__lte=date_fin)
        except ValueError:
            pass

    # Pagination: limiter à 100 derniers logs par défaut, max 1000
    try:
        limit = min(int(request.GET.get('limit', 100)), 1000)
    except (ValueError, TypeError):
        limit = 100
    logs_limited = logs[:limit]

    # Calculer des statistiques sur TOUS les logs (pas seulement les filtrés)
    stats = {
        'total': all_logs.count(),
        'creates': all_logs.filter(action='CREATE').count(),
        'updates': all_logs.filter(action='UPDATE').count(),
        'deletes': all_logs.filter(action='DELETE').count(),
        'validations': all_logs.filter(action__in=['VALIDER_PAIEMENT', 'TERMINER_MISSION']).count(),
    }

    # Top 5 utilisateurs les plus actifs
    top_users = all_logs.values('utilisateur__email').annotate(
        count=Count('pk_audit')
    ).order_by('-count')[:5]

    # Récupérer les utilisateurs pour le filtre
    utilisateurs = Utilisateur.objects.all().order_by('email')

    # Types d'actions disponibles
    action_choices = AuditLog.ACTION_CHOICES

    return render(request, 'transport/audit/audit_log_list.html', {
        'logs': logs_limited,
        'utilisateurs': utilisateurs,
        'action_choices': action_choices,
        'filters': request.GET,
        'stats': stats,
        'top_users': top_users,
        'title': "Historique d'audit"
    })

@manager_or_admin_required
def audit_log_detail(request, pk):
    """
    Affiche le détail d'un log d'audit spécifique
    """
    log = get_object_or_404(AuditLog, pk_audit=pk)

    return render(request, 'transport/audit/audit_log_detail.html', {
        'log': log,
        'title': "Détail de l'audit"
    })


@manager_or_admin_required
def audit_cleanup(request):
    """
    Nettoyer les anciens logs d'audit
    Accessible uniquement aux administrateurs
    """
    from datetime import datetime, timedelta
    from django.db.models import Count

    if request.method == 'POST':
        months = int(request.POST.get('months', 6))

        # Calculer la date limite
        date_limite = datetime.now() - timedelta(days=months * 30)

        # Récupérer les logs à supprimer
        logs_to_delete = AuditLog.objects.filter(timestamp__lt=date_limite)
        count = logs_to_delete.count()

        # Supprimer
        logs_to_delete.delete()

        messages.success(request, f"✅ {count} enregistrement(s) d'audit supprimé(s) (plus de {months} mois)")
        return redirect('audit_log_list')

    # GET: Afficher la page de confirmation
    # Calculer les statistiques par période
    stats_by_period = []
    for months in [3, 6, 12, 24]:
        date_limite = datetime.now() - timedelta(days=months * 30)
        count = AuditLog.objects.filter(timestamp__lt=date_limite).count()
        stats_by_period.append({
            'months': months,
            'count': count,
            'date_limite': date_limite
        })

    total_logs = AuditLog.objects.count()

    return render(request, 'transport/audit/audit_cleanup.html', {
        'stats_by_period': stats_by_period,
        'total_logs': total_logs,
        'title': "Nettoyage de l'audit"
    })

