"""
Entreprise Views.Py

Vues pour entreprise
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Entreprise)
from ..forms import (EntrepriseForm)
from ..decorators import (can_delete_data)
from ..permissions import role_required


@login_required
@role_required('ADMIN')
def liste_entreprises(request):
    entreprises = Entreprise.objects.all().order_by('-date_creation')
    return render(request, 'transport/entreprise/liste_entreprises.html', {
        'entreprises': entreprises,
        'title': 'Liste des entreprises'
    })

# CREATE

@login_required
@role_required('ADMIN')
def ajouter_entreprise(request):
    form = EntrepriseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Entreprise ajoutée avec succès!")
        return redirect('liste_entreprises')
    return render(request, 'transport/entreprise/ajouter_entreprise.html', {'form': form, 'title': 'Créer une entreprise'})

# UPDATE

@login_required
@role_required('ADMIN')
def modifier_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk_entreprise=pk)
    form = EntrepriseForm(request.POST or None, instance=entreprise)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Entreprise mise à jour avec succès!")
        return redirect('liste_entreprises')

    return render(request, 'transport/entreprise/ajouter_entreprise.html', {
        'form': form,
        'title': 'Modifier une entreprise'
    })

# DELETE

@can_delete_data
def supprimer_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk_entreprise=pk)

    if request.method == 'POST':
        entreprise.delete()
        messages.success(request, "🗑️ Entreprise supprimée avec succès!")
        return redirect('liste_entreprises')

    return render(request, 'transport/entreprise/confirmer_suppression.html', {
        'entreprise': entreprise,
        'title': 'Supprimer une entreprise'
    })

