"""
Mission Views.Py

Vues pour mission
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Mission, MissionConteneur)
from ..forms import (MissionForm, MissionConteneurForm)
from ..decorators import (can_delete_data, manager_or_admin_required)


@login_required
def mission_list(request):
    from .filters import MissionFilter
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    # Récupérer toutes les missions avec relations
    missions = Mission.objects.select_related('contrat', 'prestation_transport', 'contrat__chauffeur', 'contrat__client').order_by('-date_depart')

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
    chauffeurs = Chauffeur.objects.all().order_by('nom')
    clients = Client.objects.all().order_by('nom')

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

    en_retard = date_retour > mission.contrat.date_limite_retour if mission.contrat else False
    info_penalite = None

    if en_retard:
        jours_retard = (date_retour - mission.contrat.date_limite_retour).days
        penalite = jours_retard * 25000
        info_penalite = {
            'jours_retard': jours_retard,
            'penalite': penalite,
            'date_limite': mission.contrat.date_limite_retour
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
            from .models import Cautions, PaiementMission
            nb_cautions = Cautions.objects.filter(contrat=mission.contrat).count()
            nb_paiements = PaiementMission.objects.filter(mission=mission, est_valide=False).count()

            # Annuler la mission et les objets liés
            mission.annuler_mission(raison=raison)

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

# Liste

