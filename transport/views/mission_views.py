"""
Mission Views.Py

Vues pour mission
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Mission, MissionConteneur, Chauffeur, Client, PaiementMission, Cautions, AuditLog)
from ..forms import (MissionForm, MissionConteneurForm)
from ..decorators import (can_delete_data, manager_or_admin_required)
from ..filters import MissionFilter


@login_required
def mission_list(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    # Récupérer les missions de l'entreprise avec relations
    missions = Mission.objects.filter(
        contrat__entreprise=request.user.entreprise
    ).select_related('contrat', 'prestation_transport', 'contrat__chauffeur', 'contrat__client').order_by('-date_depart')

    # Appliquer les filtres
    missions = MissionFilter.apply(missions, request)

    # Séparer par statut (counts uniquement)
    missions_en_cours = missions.filter(statut='en cours')
    missions_terminees = missions.filter(statut='terminée')
    missions_annulees = missions.filter(statut='annulée')

    # Pagination - 20 missions par page
    paginator = Paginator(missions, 20)
    page = request.GET.get('page', 1)

    try:
        missions_page = paginator.page(page)
    except PageNotAnInteger:
        missions_page = paginator.page(1)
    except EmptyPage:
        missions_page = paginator.page(paginator.num_pages)

    # Récupérer les données pour les filtres
    chauffeurs = Chauffeur.objects.filter(entreprise=request.user.entreprise).order_by('nom')
    clients = Client.objects.all().order_by('nom')  # Client n'a pas de FK entreprise

    return render(request, 'transport/missions/mission_list.html', {
        'missions': missions_page,
        'missions_en_cours': missions_en_cours,
        'missions_terminees': missions_terminees,
        'missions_annulees': missions_annulees,
        'chauffeurs': chauffeurs,
        'clients': clients,
        'title': 'Liste des missions',
        # Conserver les valeurs des filtres pour les afficher dans le formulaire
        'filters': request.GET
    })
# Créer une mission

@login_required
def create_mission(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect('mission_list')
    else:
        form = MissionForm()
    return render(request, 'transport/missions/mission_form.html', {'form': form, 'title': 'Créer une mission'})

# Modifier une mission

@login_required
def update_mission(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)
    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            return redirect('mission_list')
    else:
        form = MissionForm(instance=mission)
    return render(request, 'transport/missions/mission_form.html', {'form': form, 'title': 'Modifier une mission'})

# Supprimer une mission

@can_delete_data
def delete_mission(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)
    if request.method == 'POST':
        mission.delete()
        return redirect('mission_list')
    return render(request, 'transport/missions/confirm_delete.html', {'object': mission, 'title': 'Supprimer une mission'})

# Terminer une mission

@login_required
def terminer_mission(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)

    # Vérifier que la mission n'est pas déjà terminée ou annulée
    if mission.statut == 'terminée':
        messages.warning(request, "⚠️ Cette mission est déjà terminée.")
        return redirect('mission_list')

    if mission.statut == 'annulée':
        messages.error(request, "❌ Cette mission est annulée. Impossible de la terminer.")
        return redirect('mission_list')

    # Calculer si en retard
    from django.utils import timezone
    from django.core.exceptions import ValidationError

    # Récupérer la date de retour depuis le formulaire ou utiliser aujourd'hui par défaut
    date_retour_str = request.POST.get('date_retour') if request.method == 'POST' else None

    if date_retour_str:
        try:
            from datetime import datetime
            date_retour = datetime.strptime(date_retour_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_retour = timezone.now().date()
    else:
        date_retour = timezone.now().date()

    # Vérifier que la date de retour n'est pas avant la date de départ
    # Si c'est le cas, ajuster la date de départ automatiquement
    if date_retour < mission.date_depart:
        # Avertissement mais on continue
        date_depart_originale = mission.date_depart
        ajustement_necessaire = True
    else:
        ajustement_necessaire = False
        date_depart_originale = None

    contrat = mission.contrat
    date_limite = contrat.date_limite_retour if contrat else None
    en_retard = bool(date_limite and date_retour > date_limite)
    info_penalite = None

    if en_retard:
        jours_retard = (date_retour - date_limite).days
        penalite = jours_retard * 25000
        info_penalite = {
            'jours_retard': jours_retard,
            'penalite': penalite,
            'date_limite': date_limite
        }

    if request.method == 'POST':
        force = request.POST.get('force') == '1'

        try:
            # Si date de retour < date de départ, ajuster la date de départ
            if ajustement_necessaire:
                mission.date_depart = date_retour
                mission.save()
                messages.info(
                    request,
                    f"ℹ️ La date de départ a été ajustée de {date_depart_originale.strftime('%d/%m/%Y')} "
                    f"à {date_retour.strftime('%d/%m/%Y')} pour correspondre à la date de retour."
                )

            result = mission.terminer_mission(date_retour=date_retour, force=force)

            # Enregistrer l'action dans l'historique d'audit
            AuditLog.log_action(
                utilisateur=request.user,
                action='TERMINER_MISSION',
                model_name='Mission',
                object_id=mission.pk_mission,
                object_repr=f"Mission vers {mission.destination}",
                changes={
                    'statut': {'old': 'en cours', 'new': 'terminée'},
                    'date_retour': str(date_retour),
                    'en_retard': result.get('en_retard', False) if result else False
                },
                request=request
            )

            # Afficher le message approprié
            if result and result.get('en_retard'):
                messages.warning(
                    request,
                    f"⚠️ {result['message']} - Mission terminée malgré le retard."
                )
            else:
                messages.success(
                    request,
                    f"✅ Mission terminée avec succès! Vous pouvez maintenant valider le paiement associé."
                )

            return redirect('mission_list')

        except ValidationError as e:
            # Première tentative - afficher la confirmation
            if not force:
                messages.warning(request, str(e))
                # Récupérer le paiement
                try:
                    paiement = PaiementMission.objects.get(mission=mission)
                except PaiementMission.DoesNotExist:
                    paiement = None

                return render(request, 'transport/missions/terminer_mission.html', {
                    'mission': mission,
                    'paiement': paiement,
                    'en_retard': True,
                    'info_penalite': info_penalite,
                    'confirmation_required': True,
                    'title': 'Terminer la mission'
                })
            else:
                messages.error(request, f"❌ Erreur : {str(e)}")
                return redirect('mission_list')

        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la fin de la mission : {str(e)}")
            return redirect('mission_list')

    # Récupérer le paiement associé s'il existe
    try:
        paiement = PaiementMission.objects.get(mission=mission)
    except PaiementMission.DoesNotExist:
        paiement = None

    return render(request, 'transport/missions/terminer_mission.html', {
        'mission': mission,
        'paiement': paiement,
        'en_retard': en_retard,
        'info_penalite': info_penalite,
        'date_retour': date_retour,
        'title': 'Terminer la mission'
    })

# Annuler une mission

@manager_or_admin_required
def annuler_mission(request, pk):
    """Permet d'annuler une mission en cours"""
    mission = get_object_or_404(Mission, pk_mission=pk)

    # Vérifier que la mission n'est pas déjà terminée
    if mission.statut == 'terminée':
        messages.error(request, "❌ Impossible d'annuler une mission déjà terminée.")
        return redirect('mission_list')

    if mission.statut == 'annulée':
        messages.warning(request, "⚠️ Cette mission est déjà annulée.")
        return redirect('mission_list')

    if request.method == 'POST':
        raison = request.POST.get('raison', '')

        try:
            # Compter les objets qui seront annulés
            nb_cautions = Cautions.objects.filter(contrat=mission.contrat).count()
            nb_paiements = PaiementMission.objects.filter(mission=mission, est_valide=False).count()

            # Annuler la mission et les objets liés
            mission.annuler_mission(raison=raison)

            # Enregistrer l'action dans l'historique d'audit
            AuditLog.log_action(
                utilisateur=request.user,
                action='ANNULER_MISSION',
                model_name='Mission',
                object_id=mission.pk_mission,
                object_repr=f"Mission vers {mission.destination}",
                changes={
                    'statut': {'old': 'en cours', 'new': 'annulée'},
                    'raison': raison or 'Non spécifiée',
                    'nb_cautions_annulees': nb_cautions,
                    'nb_paiements_annules': nb_paiements
                },
                request=request
            )

            # Message détaillé
            details = []
            details.append("✅ Mission annulée")
            if mission.contrat:
                details.append("✅ Contrat de transport annoté")
            if nb_cautions > 0:
                details.append(f"✅ {nb_cautions} caution(s) annulée(s)")
            if nb_paiements > 0:
                details.append(f"✅ {nb_paiements} paiement(s) annoté(s)")

            messages.success(
                request,
                f"🚫 ANNULATION EN CASCADE EFFECTUÉE\n\n" + "\n".join(details) +
                f"\n\nRaison: {raison if raison else 'Non spécifiée'}"
            )
            return redirect('mission_list')

        except Exception as e:
            messages.error(request, f"❌ Erreur lors de l'annulation : {str(e)}")
            return redirect('mission_list')

    return render(request, 'transport/missions/annuler_mission.html', {
        'mission': mission,
        'title': 'Annuler la mission'
    })

# LIST

@login_required
def mission_conteneur_list(request):
    mission_conteneurs = MissionConteneur.objects.all()
    return render(request, 'transport/missions/mission_conteneur_list.html', {
        'title': 'Liste des Missions - Conteneurs',
        'mission_conteneurs': mission_conteneurs
    })

# CREATE

@login_required
def create_mission_conteneur(request):
    if request.method == 'POST':
        form = MissionConteneurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mission_conteneur_list')
    else:
        form = MissionConteneurForm()
    return render(request, 'transport/missions/mission_conteneur_form.html', {
        'title': 'Ajouter un Mission-Conteneur',
        'form': form
    })

# UPDATE

@login_required
def update_mission_conteneur(request, pk):
    mc = get_object_or_404(MissionConteneur, pk=pk)
    if request.method == 'POST':
        form = MissionConteneurForm(request.POST, instance=mc)
        if form.is_valid():
            form.save()
            return redirect('mission_conteneur_list')
    else:
        form = MissionConteneurForm(instance=mc)
    return render(request, 'transport/missions/mission_conteneur_form.html', {
        'title': 'Modifier un Mission-Conteneur',
        'form': form
    })

# DELETE

@can_delete_data
def delete_mission_conteneur(request, pk):
    mc = get_object_or_404(MissionConteneur, pk=pk)
    if request.method == 'POST':
        mc.delete()
        return redirect('mission_conteneur_list')
    return render(request, 'transport/missions/mission_conteneur_confirm_delete.html', {
        'title': 'Supprimer un Mission-Conteneur',
        'mission_conteneur': mc
    })

# =============================================================================
# GESTION DU STATIONNEMENT (DEMURRAGE)
# =============================================================================

@login_required
@manager_or_admin_required
def bloquer_stationnement(request, pk):
    """
    Bloque une mission pour stationnement (demurrage)
    Le camion est arrivé et commence la période de stationnement
    """
    mission = get_object_or_404(Mission, pk_mission=pk)

    # ✅ VÉRIFICATION: Empêcher le double blocage
    if mission.date_arrivee:
        messages.warning(
            request,
            f'⚠️ Cette mission est déjà bloquée pour stationnement depuis le {mission.date_arrivee.strftime("%d/%m/%Y")}. '
            f'Si vous souhaitez modifier la date d\'arrivée, veuillez d\'abord marquer le déchargement ou contacter un administrateur.'
        )
        return redirect('mission_list')

    # ✅ VÉRIFICATION: Mission doit être en cours
    if mission.statut != 'en cours':
        messages.error(
            request,
            f'❌ Impossible de bloquer cette mission. Statut actuel: {mission.get_statut_display()}. '
            f'Seules les missions "en cours" peuvent être bloquées pour stationnement.'
        )
        return redirect('mission_list')

    if request.method == 'POST':
        date_arrivee = request.POST.get('date_arrivee')

        try:
            from datetime import datetime
            from django.utils import timezone

            # Convertir la date si fournie
            if date_arrivee:
                date_arrivee = datetime.strptime(date_arrivee, '%Y-%m-%d').date()
            else:
                date_arrivee = None

            # ✅ VALIDATIONS SERVEUR
            if date_arrivee:
                today = timezone.now().date()

                # Validation 1: Date ne peut pas être dans le futur
                if date_arrivee > today:
                    messages.error(request, '❌ La date d\'arrivée ne peut pas être dans le futur.')
                    return render(request, 'transport/missions/bloquer_stationnement.html', {
                        'title': 'Bloquer pour stationnement',
                        'mission': mission
                    })

                # Validation 2: Date doit être >= date de départ de la mission
                if date_arrivee < mission.date_depart:
                    messages.error(
                        request,
                        f'❌ La date d\'arrivée ({date_arrivee.strftime("%d/%m/%Y")}) ne peut pas être avant '
                        f'la date de départ de la mission ({mission.date_depart.strftime("%d/%m/%Y")}).'
                    )
                    return render(request, 'transport/missions/bloquer_stationnement.html', {
                        'title': 'Bloquer pour stationnement',
                        'mission': mission
                    })

            # Bloquer pour stationnement
            frais_info = mission.bloquer_pour_stationnement(date_arrivee)

            # Enregistrer dans l'audit log
            AuditLog.log_action(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Mission',
                object_id=mission.pk_mission,
                object_repr=f"Mission bloquée pour stationnement - {frais_info['message']}",
                request=request
            )

            messages.success(
                request,
                f"✅ Mission bloquée pour stationnement. {frais_info['message']}. "
                f"Montant actuel: {frais_info['montant']} CFA"
            )

            return redirect('mission_list')

        except Exception as e:
            messages.error(request, f"❌ Erreur: {str(e)}")
            return redirect('mission_list')

    # GET - Afficher le formulaire
    return render(request, 'transport/missions/bloquer_stationnement.html', {
        'title': 'Bloquer pour stationnement',
        'mission': mission
    })


@login_required
@manager_or_admin_required
def marquer_dechargement(request, pk):
    """
    Marque le déchargement effectif et calcule les frais finaux
    """
    mission = get_object_or_404(Mission, pk_mission=pk)

    # ✅ VÉRIFICATION: La mission doit d'abord être bloquée
    if not mission.date_arrivee:
        messages.error(
            request,
            '❌ Cette mission n\'a pas été bloquée pour stationnement. '
            'Veuillez d\'abord bloquer la mission en enregistrant la date d\'arrivée du camion.'
        )
        return redirect('bloquer_stationnement', pk=mission.pk_mission)

    # ✅ VÉRIFICATION: Empêcher le double déchargement
    if mission.date_dechargement:
        messages.warning(
            request,
            f'⚠️ Cette mission a déjà été marquée comme déchargée le {mission.date_dechargement.strftime("%d/%m/%Y")}. '
            f'Frais de stationnement calculés: {mission.montant_stationnement} CFA.'
        )
        return redirect('mission_list')

    # ✅ VÉRIFICATION: Mission doit être en cours
    if mission.statut != 'en cours':
        messages.error(
            request,
            f'❌ Impossible de marquer le déchargement. Statut actuel: {mission.get_statut_display()}. '
            f'Seules les missions "en cours" peuvent être déchargées.'
        )
        return redirect('mission_list')

    if request.method == 'POST':
        date_dechargement = request.POST.get('date_dechargement')

        try:
            from datetime import datetime
            from django.utils import timezone

            # Convertir la date si fournie
            if date_dechargement:
                date_dechargement = datetime.strptime(date_dechargement, '%Y-%m-%d').date()
            else:
                date_dechargement = None

            # ✅ VALIDATIONS SERVEUR
            if date_dechargement:
                today = timezone.now().date()

                # Validation 1: Date ne peut pas être dans le futur
                if date_dechargement > today:
                    messages.error(request, '❌ La date de déchargement ne peut pas être dans le futur.')
                    return render(request, 'transport/missions/marquer_dechargement.html', {
                        'title': 'Marquer le déchargement',
                        'mission': mission
                    })

                # Validation 2: Date doit être >= date d'arrivée
                if date_dechargement < mission.date_arrivee:
                    messages.error(
                        request,
                        f'❌ La date de déchargement ({date_dechargement.strftime("%d/%m/%Y")}) ne peut pas être avant '
                        f'la date d\'arrivée ({mission.date_arrivee.strftime("%d/%m/%Y")}).'
                    )
                    return render(request, 'transport/missions/marquer_dechargement.html', {
                        'title': 'Marquer le déchargement',
                        'mission': mission
                    })

            # Marquer le déchargement
            frais_info = mission.marquer_dechargement(date_dechargement)

            # Enregistrer dans l'audit log
            AuditLog.log_action(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Mission',
                object_id=mission.pk_mission,
                object_repr=f"Déchargement effectué - Frais: {frais_info['montant']} CFA ({frais_info['jours_facturables']} jours)",
                request=request
            )

            if frais_info['jours_facturables'] > 0:
                messages.success(
                    request,
                    f"✅ Déchargement effectué. {frais_info['message']}. "
                    f"💰 FRAIS DE STATIONNEMENT: {frais_info['montant']} CFA"
                )
            else:
                messages.success(
                    request,
                    f"✅ Déchargement effectué dans les délais (3 jours gratuits). Aucun frais supplémentaire."
                )

            return redirect('mission_list')

        except Exception as e:
            messages.error(request, f"❌ Erreur: {str(e)}")
            return redirect('mission_list')

    # GET - Afficher le formulaire
    return render(request, 'transport/missions/marquer_dechargement.html', {
        'title': 'Marquer le déchargement',
        'mission': mission
    })


@login_required
@manager_or_admin_required
def calculer_stationnement(request, pk):
    """
    Recalcule les frais de stationnement en temps réel (AJAX ou page)
    """
    mission = get_object_or_404(Mission, pk_mission=pk)

    if not mission.date_arrivee:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Date d\'arrivée non renseignée'
            })
        else:
            messages.error(request, "❌ La date d'arrivée doit être renseignée")
            return redirect('mission_list')

    # Calculer les frais actuels
    frais_info = mission.calculer_frais_stationnement()

    # Mettre à jour la mission
    mission.jours_stationnement_facturables = frais_info['jours_facturables']
    mission.montant_stationnement = frais_info['montant']
    mission.statut_stationnement = frais_info['statut']
    mission.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'jours_total': frais_info['jours_total'],
            'jours_gratuits': frais_info['jours_gratuits'],
            'jours_facturables': frais_info['jours_facturables'],
            'montant': str(frais_info['montant']),
            'message': frais_info['message'],
            'statut': frais_info['statut']
        })
    else:
        messages.info(request, f"📊 {frais_info['message']}. Montant: {frais_info['montant']} CFA")
        return redirect('mission_list')


@login_required
@manager_or_admin_required
def preview_frais_stationnement(request, pk):
    """
    Calcule un aperçu des frais de stationnement pour une date de déchargement donnée
    Cette vue est utilisée pour l'aperçu en temps réel via AJAX

    Paramètres GET:
        - date_dechargement: Date de déchargement à tester (format YYYY-MM-DD)

    Retourne un JSON avec:
        - success: True/False
        - jours_total: Nombre total de jours calendaires
        - jours_gratuits: Nombre de jours gratuits utilisés
        - jours_facturables: Nombre de jours facturables
        - montant: Montant total des frais
        - debut_gratuit: Date de début de la période gratuite
        - fin_gratuit: Date de fin de la période gratuite
        - debut_facturation: Date de début de facturation
        - message: Message descriptif
    """
    from datetime import datetime, timedelta
    from decimal import Decimal

    mission = get_object_or_404(Mission, pk_mission=pk)

    # Vérifier que la mission est bloquée
    if not mission.date_arrivee:
        return JsonResponse({
            'success': False,
            'message': 'La mission n\'a pas été bloquée pour stationnement'
        }, status=400)

    # Récupérer la date de déchargement depuis les paramètres GET
    date_dechargement_str = request.GET.get('date_dechargement')

    if not date_dechargement_str:
        return JsonResponse({
            'success': False,
            'message': 'Paramètre date_dechargement manquant'
        }, status=400)

    try:
        # Parser la date de déchargement
        date_dechargement = datetime.strptime(date_dechargement_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Format de date invalide (attendu: YYYY-MM-DD)'
        }, status=400)

    # Validation: date_dechargement >= date_arrivee
    if date_dechargement < mission.date_arrivee:
        return JsonResponse({
            'success': False,
            'message': f'La date de déchargement ne peut pas être avant la date d\'arrivée ({mission.date_arrivee.strftime("%d/%m/%Y")})'
        }, status=400)

    # Calculer les frais pour cette date hypothétique
    # On utilise la même logique que dans Mission.calculer_frais_stationnement()
    # mais avec la date de déchargement fournie

    TARIF_JOURNALIER = Decimal('25000.00')
    date_arrivee = mission.date_arrivee

    # Fonction helper pour vérifier si c'est un weekend
    def est_weekend(date):
        return date.weekday() >= 5  # 5=samedi, 6=dimanche

    # Étape 1: Trouver le début de la période gratuite
    debut_gratuit = date_arrivee
    while est_weekend(debut_gratuit):
        debut_gratuit += timedelta(days=1)

    # Étape 2: Calculer la fin de la période gratuite (3 jours ouvrables)
    jours_gratuits_comptes = 0
    current_date = debut_gratuit
    fin_gratuit = None

    while jours_gratuits_comptes < 3:
        if not est_weekend(current_date):
            jours_gratuits_comptes += 1
            if jours_gratuits_comptes == 3:
                fin_gratuit = current_date
                break
        current_date += timedelta(days=1)

    # Étape 3: Date de début de facturation (jour après la fin de la période gratuite)
    debut_facturation = fin_gratuit + timedelta(days=1)

    # Étape 4: Calculer les jours facturables
    if date_dechargement >= debut_facturation:
        # TOUS les jours comptent après la période gratuite (y compris weekends)
        jours_facturables = (date_dechargement - debut_facturation).days + 1
    else:
        jours_facturables = 0

    # Calculer le montant
    montant_total = jours_facturables * TARIF_JOURNALIER

    # Statistiques supplémentaires
    jours_total = (date_dechargement - date_arrivee).days + 1

    # Compter les jours ouvrables utilisés
    jours_ouvrables_utilises = 0
    current = date_arrivee
    while current <= date_dechargement:
        if not est_weekend(current):
            jours_ouvrables_utilises += 1
        current += timedelta(days=1)

    jours_gratuits_utilises = min(3, jours_ouvrables_utilises)

    # Message descriptif
    if jours_facturables == 0:
        message = "Aucun frais - Déchargement dans la période gratuite"
        statut = "gratuit"
    else:
        message = f"{jours_facturables} jour(s) facturable(s) × {TARIF_JOURNALIER:,.0f} CFA = {montant_total:,.0f} CFA"
        statut = "payant"

    return JsonResponse({
        'success': True,
        'jours_total': jours_total,
        'jours_gratuits': jours_gratuits_utilises,
        'jours_facturables': jours_facturables,
        'montant': str(montant_total),
        'montant_formatted': f'{montant_total:,.0f}'.replace(',', ' '),
        'debut_gratuit': debut_gratuit.strftime('%Y-%m-%d'),
        'fin_gratuit': fin_gratuit.strftime('%Y-%m-%d'),
        'debut_facturation': debut_facturation.strftime('%Y-%m-%d'),
        'date_arrivee': date_arrivee.strftime('%Y-%m-%d'),
        'date_dechargement': date_dechargement.strftime('%Y-%m-%d'),
        'message': message,
        'statut': statut,
        'tarif_journalier': str(TARIF_JOURNALIER)
    })

# Liste

