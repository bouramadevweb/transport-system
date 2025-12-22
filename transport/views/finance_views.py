"""
Finance Views.Py

Vues pour finance
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Cautions, PaiementMission, Chauffeur, AuditLog)
from ..forms import (CautionsForm, PaiementMissionForm)
from ..decorators import (can_delete_data, can_validate_payment)
from ..filters import PaiementMissionFilter


@login_required
def cautions_list(request):
    cautions = Cautions.objects.all()
    return render(request, "transport/cautions/cautions_list.html", {"cautions": cautions, "title": "Liste des cautions"})

# Création

@login_required
def create_caution(request):
    if request.method == "POST":
        form = CautionsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cautions_list')
    else:
        form = CautionsForm()
    return render(request, "transport/cautions/caution_form.html", {"form": form, "title": "Ajouter une caution"})

# Modification

@login_required
def update_caution(request, pk):
    caution = get_object_or_404(Cautions, pk=pk)
    if request.method == "POST":
        form = CautionsForm(request.POST, instance=caution)
        if form.is_valid():
            form.save()
            return redirect('cautions_list')
    else:
        form = CautionsForm(instance=caution)
    return render(request, "transport/cautions/caution_form.html", {"form": form, "title": "Modifier une caution"})


# Suppression

@can_delete_data
def delete_caution(request, pk):
    caution = get_object_or_404(Cautions, pk=pk)
    if request.method == "POST":
        caution.delete()
        return redirect('cautions_list')
    return render(request, "transport/cautions/caution_confirm_delete.html", {"caution": caution})

@login_required
def paiement_mission_list(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    # Récupérer tous les paiements avec relations
    paiements = PaiementMission.objects.select_related(
        'mission', 'caution', 'prestation',
        'mission__contrat__chauffeur', 'mission__contrat__client'
    ).order_by('-date_paiement')

    # Appliquer les filtres
    paiements = PaiementMissionFilter.apply(paiements, request)

    # Séparer validés et en attente (counts uniquement)
    paiements_valides = paiements.filter(est_valide=True)
    paiements_attente = paiements.filter(est_valide=False)

    # Pagination - 20 paiements par page
    paginator = Paginator(paiements, 20)
    page = request.GET.get('page', 1)

    try:
        paiements_page = paginator.page(page)
    except PageNotAnInteger:
        paiements_page = paginator.page(1)
    except EmptyPage:
        paiements_page = paginator.page(paginator.num_pages)

    # Récupérer les données pour les filtres
    chauffeurs = Chauffeur.objects.all().order_by('nom')

    return render(request, 'transport/paiements-mission/paiement_mission_list.html', {
        'paiements': paiements_page,
        'paiements_valides': paiements_valides,
        'paiements_attente': paiements_attente,
        'chauffeurs': chauffeurs,
        'title': 'Liste des paiements',
        # Conserver les valeurs des filtres pour les afficher dans le formulaire
        'filters': request.GET
    })

# Création

@login_required
def create_paiement_mission(request):
    if request.method == 'POST':
        form = PaiementMissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paiement_mission_list')
    else:
        form = PaiementMissionForm()
    return render(request, 'transport/paiements-mission/paiement_mission_form.html', {'form': form, 'title': 'Créer un paiement'})

# Mise à jour

@login_required
def update_paiement_mission(request, pk):
    paiement = get_object_or_404(PaiementMission, pk=pk)
    if request.method == 'POST':
        form = PaiementMissionForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            return redirect('paiement_mission_list')
    else:
        form = PaiementMissionForm(instance=paiement)
    return render(request, 'transport/paiements-mission/paiement_mission_form.html', {'form': form, 'title': 'Modifier un paiement'})

# Suppression

@can_delete_data
def delete_paiement_mission(request, pk):
    paiement = get_object_or_404(PaiementMission, pk=pk)
    if request.method == 'POST':
        paiement.delete()
        return redirect('paiement_mission_list')
    return render(request, 'transport/paiements-mission/paiement_mission_confirm_delete.html', {'paiement': paiement, 'title': 'Supprimer un paiement'})

# Valider un paiement

@can_validate_payment
def valider_paiement_mission(request, pk):
    paiement = get_object_or_404(PaiementMission, pk=pk)

    # Vérifier que le paiement n'est pas déjà validé
    if paiement.est_valide:
        messages.warning(request, "⚠️ Ce paiement a déjà été validé.")
        return redirect('paiement_mission_list')

    # Vérifier le statut de la mission
    mission_terminee = paiement.mission.statut == 'terminée'

    # Vérifier l'état de la caution
    caution = paiement.caution
    caution_ok = False
    caution_message = ""

    if caution:
        if caution.statut in ['remboursee', 'consommee']:
            caution_ok = True
            statut_label = caution.get_statut_display()
            caution_message = f"✅ Caution {statut_label.lower()} ({caution.montant_rembourser} FCFA sur {caution.montant} FCFA)"
        else:
            caution_ok = False
            statut_label = caution.get_statut_display()
            caution_message = f"❌ Caution {statut_label.lower()} ({caution.montant} FCFA)"

    if request.method == 'POST':
        if not mission_terminee:
            messages.error(request, f"❌ Impossible de valider! La mission est '{paiement.mission.statut}'. Terminez d'abord la mission.")
            return redirect('paiement_mission_list')

        if not caution_ok:
            messages.error(request, f"❌ Impossible de valider! La caution de {caution.montant} FCFA n'a pas été remboursée. Veuillez rembourser la caution avant de valider le paiement.")
            return redirect('paiement_mission_list')

        try:
            # Valider le paiement
            paiement.valider_paiement()

            # Enregistrer l'action dans l'historique d'audit
            AuditLog.log_action(
                utilisateur=request.user,
                action='VALIDER_PAIEMENT',
                model_name='PaiementMission',
                object_id=paiement.pk_paiement,
                object_repr=f"Paiement de {paiement.montant_total} FCFA pour mission {paiement.mission.destination}",
                changes={
                    'est_valide': {'old': False, 'new': True},
                    'montant_total': paiement.montant_total
                },
                request=request
            )

            messages.success(request, f"✅ Paiement validé avec succès! Montant: {paiement.montant_total} FCFA")
            return redirect('paiement_mission_list')
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la validation : {str(e)}")
            return redirect('paiement_mission_list')

    return render(request, 'transport/paiements-mission/valider_paiement.html', {
        'paiement': paiement,
        'mission_terminee': mission_terminee,
        'caution': caution,
        'caution_ok': caution_ok,
        'caution_message': caution_message,
        'title': 'Valider le paiement'
    })

# Liste

