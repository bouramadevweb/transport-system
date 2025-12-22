"""
Frais Views.Py

Vues pour frais
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (FraisTrajet)
from ..forms import (FraisTrajetForm)
from ..decorators import (can_delete_data)


@login_required
def frais_list(request):
    frais = FraisTrajet.objects.all()
    return render(request, 'transport/frais/frais_list.html', {'frais': frais, 'title': 'Liste des frais de trajet'})

@login_required
def create_frais(request):
    form = FraisTrajetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_form.html', {'form': form, 'title': 'Ajouter un frais de trajet'})

@login_required
def update_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    form = FraisTrajetForm(request.POST or None, instance=frais)
    if form.is_valid():
        form.save()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_form.html', {'form': form, 'title': 'Modifier le frais de trajet'})

@can_delete_data
def delete_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    if request.method == 'POST':
        frais.delete()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_confirm_delete.html', {'frais': frais, 'title': 'Supprimer le frais de trajet'})


# Liste des missions

