"""
Frais Views.Py

Vues pour frais
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (FraisTrajet, Mission)
from ..forms import (FraisTrajetForm)
from ..decorators import (can_delete_data)


@login_required
def frais_list(request):
    frais = FraisTrajet.objects.all()
    return render(request, 'transport/frais/frais_list.html', {'frais': frais, 'title': 'Liste des frais de trajet'})

@login_required
def create_frais(request):
    # Récupérer origine et destination depuis GET (pour pré-remplissage)
    origine = request.GET.get('origine', None)
    destination = request.GET.get('destination', None)

    if request.method == 'POST':
        form = FraisTrajetForm(request.POST, origine=origine, destination=destination)
        if form.is_valid():
            frais = form.save()
            messages.success(request, f'Frais de trajet "{frais}" créé avec succès!')

            # Si on vient d'une redirection avec un paramètre de retour, rediriger vers cette page
            next_url = request.GET.get('next', 'frais_list')
            return redirect(next_url)
    else:
        form = FraisTrajetForm(origine=origine, destination=destination)

    context = {
        'form': form,
        'title': 'Ajouter un frais de trajet',
        'origine': origine,
        'destination': destination
    }
    return render(request, 'transport/frais/frais_form.html', context)

@login_required
def update_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)

    if request.method == 'POST':
        form = FraisTrajetForm(request.POST, instance=frais)
        if form.is_valid():
            form.save()
            messages.success(request, f'Frais de trajet "{frais}" modifié avec succès!')
            return redirect('frais_list')
    else:
        form = FraisTrajetForm(instance=frais)

    return render(request, 'transport/frais/frais_form.html', {'form': form, 'title': 'Modifier le frais de trajet'})

@can_delete_data
def delete_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    if request.method == 'POST':
        frais.delete()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_confirm_delete.html', {'frais': frais, 'title': 'Supprimer le frais de trajet'})


@login_required
def missions_data_api(request):
    """API pour récupérer les données des missions (pour auto-complétion du formulaire frais)"""
    missions = Mission.objects.select_related('contrat').all()

    data = {
        'missions': [
            {
                'pk': mission.pk_mission,
                'contrat_pk': mission.contrat.pk_contrat if mission.contrat else None,
                'origine': mission.origine,
                'destination': mission.destination,
                'date_depart': mission.date_depart.isoformat() if mission.date_depart else None,
                'date_retour': mission.date_retour.isoformat() if mission.date_retour else None,
            }
            for mission in missions
        ]
    }

    return JsonResponse(data)


# Liste des missions

