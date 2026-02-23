"""
Annulation Views.py

Vues pour gérer l'annulation des contrats et missions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from ..models import ContratTransport, Mission
from ..decorators import manager_or_admin_required


@login_required
@manager_or_admin_required
def annuler_contrat_view(request, pk):
    """Vue pour annuler un contrat avec confirmation

    Cette vue affiche un formulaire de confirmation avant d'annuler le contrat.
    L'annulation est en cascade: contrat → missions → cautions → paiements
    """
    contrat = get_object_or_404(ContratTransport, pk=pk, entreprise=request.user.entreprise)

    # Vérifier que le contrat n'est pas déjà annulé
    if contrat.statut == 'annule':
        messages.warning(request, "⚠️ Ce contrat est déjà annulé.")
        return redirect('contrat_list')

    # Compter les objets liés pour information
    from ..models import Mission, Cautions, PaiementMission
    nb_missions = Mission.objects.filter(contrat=contrat).count()
    nb_cautions = Cautions.objects.filter(contrat=contrat).count()
    nb_paiements = PaiementMission.objects.filter(mission__contrat=contrat).count()

    if request.method == 'POST':
        raison = request.POST.get('raison', '').strip()

        if not raison:
            messages.error(request, "❌ La raison de l'annulation est obligatoire.")
            return render(request, 'transport/contrat/annuler_confirm.html', {
                'contrat': contrat,
                'nb_missions': nb_missions,
                'nb_cautions': nb_cautions,
                'nb_paiements': nb_paiements,
                'title': 'Annuler le contrat',
            })

        try:
            # Annuler le contrat
            result = contrat.annuler_contrat(raison=raison)

            # Message de succès détaillé
            messages.success(
                request,
                f"✅ Contrat {contrat.numero_bl} annulé avec succès! "
                f"• {result['missions_annulees']} mission(s) annulée(s) "
                f"• {result['cautions_annulees']} caution(s) annulée(s) "
                f"• {result['prestations']} prestation(s) affectée(s) "
                f"• Traçabilité complète conservée"
            )

            return redirect('contrat_list')

        except ValidationError as e:
            messages.error(request, f"❌ Erreur: {e}")
        except Exception as e:
            messages.error(request, f"❌ Erreur inattendue: {e}")

    return render(request, 'transport/contrat/annuler_confirm.html', {
        'contrat': contrat,
        'nb_missions': nb_missions,
        'nb_cautions': nb_cautions,
        'nb_paiements': nb_paiements,
        'title': 'Annuler le contrat',
    })


@login_required
@manager_or_admin_required
def annuler_mission_view(request, pk):
    """Vue pour annuler une mission avec confirmation

    Cette vue affiche un formulaire de confirmation avant d'annuler la mission.
    L'annulation affecte: mission → cautions → paiements
    """
    mission = get_object_or_404(Mission, pk=pk, contrat__entreprise=request.user.entreprise)

    # Vérifier que la mission n'est pas déjà annulée
    if mission.statut == 'annulée':
        messages.warning(request, "⚠️ Cette mission est déjà annulée.")
        return redirect('mission_list')

    # Compter les objets liés pour information
    from ..models import Cautions, PaiementMission
    nb_cautions = Cautions.objects.filter(contrat=mission.contrat).count()
    nb_paiements = PaiementMission.objects.filter(mission=mission).count()

    if request.method == 'POST':
        raison = request.POST.get('raison', '').strip()

        if not raison:
            messages.error(request, "❌ La raison de l'annulation est obligatoire.")
            return render(request, 'transport/missions/annuler_confirm.html', {
                'mission': mission,
                'nb_cautions': nb_cautions,
                'nb_paiements': nb_paiements,
                'title': 'Annuler la mission',
            })

        try:
            # Annuler la mission
            mission.annuler_mission(raison=raison)

            # Message de succès
            messages.success(
                request,
                f"✅ Mission annulée avec succès! "
                f"• Cautions: annulées "
                f"• Paiements: annulés "
                f"• Traçabilité complète conservée"
            )

            return redirect('mission_list')

        except ValidationError as e:
            messages.error(request, f"❌ Erreur: {e}")
        except Exception as e:
            messages.error(request, f"❌ Erreur inattendue: {e}")

    return render(request, 'transport/missions/annuler_confirm.html', {
        'mission': mission,
        'nb_cautions': nb_cautions,
        'nb_paiements': nb_paiements,
        'title': 'Annuler la mission',
    })


@login_required
@manager_or_admin_required
def contrats_annules_list(request):
    """Liste tous les contrats annulés pour consultation et audit"""
    from django.db.models import Count

    contrats = ContratTransport.objects.filter(statut='annule', entreprise=request.user.entreprise).annotate(
        nb_missions=Count('mission')
    ).order_by('-date_debut')

    return render(request, 'transport/contrat/contrats_annules_list.html', {
        'contrats': contrats,
        'title': 'Contrats annulés'
    })


@login_required
@manager_or_admin_required
def missions_annulees_list(request):
    """Liste toutes les missions annulées pour consultation et audit"""
    missions = Mission.objects.filter(statut='annulée', contrat__entreprise=request.user.entreprise).select_related(
        'contrat', 'prestation_transport'
    ).order_by('-date_depart')

    return render(request, 'transport/missions/missions_annulees_list.html', {
        'missions': missions,
        'title': 'Missions annulées'
    })
