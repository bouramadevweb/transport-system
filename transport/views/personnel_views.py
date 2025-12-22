"""
Personnel Views.Py

Vues pour personnel
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Chauffeur, Affectation, Mecanicien)
from ..forms import (ChauffeurForm, AffectationForm, MecanicienForm)
from ..decorators import (can_delete_data)


@login_required
def create_chauffeur(request):
    if request.method == "POST":
        form = ChauffeurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Chauffeur ajouté avec succès.")
            return redirect("chauffeur_list")
    else:
        form = ChauffeurForm()
    
    return render(request, "transport/chauffeurs/chauffeur_form.html", {"form": form, "title": "Ajouter un chauffeur"})

@login_required
def chauffeur_list(request):
    chauffeurs = Chauffeur.objects.select_related("entreprise").all()
    return render(request, "transport/chauffeurs/chauffeur_list.html", {"chauffeurs": chauffeurs})

@login_required
def update_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)

    if request.method == "POST":
        form = ChauffeurForm(request.POST, instance=chauffeur)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Chauffeur mis à jour avec succès.")
            return redirect("chauffeur_list")
    else:
        form = ChauffeurForm(instance=chauffeur)

    return render(request, "transport/chauffeurs/chauffeur_form.html", {"form": form, "title": "Modifier un chauffeur"})

@can_delete_data
def chauffeur_delete(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    if request.method == "POST":
       chauffeur.delete()
       messages.success(request, "🗑️ Chauffeur supprimé avec succès.")
       return redirect("chauffeur_list")
    return render(request, "transport/chauffeurs/chauffeur_confirm_delete.html", {"chauffeur": chauffeur})

# Liste des camions

@login_required
def affectation_list(request):
    affectations = Affectation.objects.select_related('chauffeur', 'camion').order_by('-date_affectation')

    # Séparer les affectations actives et terminées
    affectations_actives = affectations.filter(date_fin_affectation__isnull=True)
    affectations_terminees = affectations.filter(date_fin_affectation__isnull=False)

    return render(request, "transport/affectations/affectation_list.html", {
        "affectations": affectations,
        "affectations_actives": affectations_actives,
        "affectations_terminees": affectations_terminees,
        "title": "Liste des affectations"
    })

# Ajouter une affectation

@login_required
def create_affectation(request):
    if request.method == "POST":
        form = AffectationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Affectation ajoutée avec succès!")
                return redirect('affectation_list')
            except Exception as e:
                messages.error(request, f"❌ Erreur lors de l'affectation : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        form = AffectationForm()
    return render(request, "transport/affectations/affectation_form.html", {"form": form, "title": "Ajouter une affectation"})

# Modifier une affectation

@login_required
def update_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == "POST":
        form = AffectationForm(request.POST, instance=affectation)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Affectation mise à jour avec succès!")
                return redirect('affectation_list')
            except Exception as e:
                messages.error(request, f"❌ Erreur lors de la mise à jour : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        form = AffectationForm(instance=affectation)
    return render(request, "transport/affectations/affectation_form.html", {"form": form, "title": "Modifier l'affectation"})

# Terminer une affectation

@login_required
def terminer_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)

    # Vérifier que l'affectation est active
    if affectation.date_fin_affectation is not None:
        messages.warning(request, "⚠️ Cette affectation est déjà terminée.")
        return redirect('affectation_list')

    if request.method == "POST":
        try:
            affectation.terminer_affectation()
            messages.success(request, f"✅ Affectation terminée avec succès! Le camion {affectation.camion.immatriculation} est maintenant disponible.")
            return redirect('affectation_list')
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la fin de l'affectation : {str(e)}")
            return redirect('affectation_list')

    return render(request, "transport/affectations/terminer_affectation.html", {
        "affectation": affectation,
        "title": "Terminer l'affectation"
    })

# Supprimer une affectation

@can_delete_data
def delete_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == "POST":
        affectation.delete()
        messages.success(request, "🗑️ Affectation supprimée avec succès!")
        return redirect('affectation_list')
    return render(request, "transport/affectations/affectation_confirm_delete.html", {"affectation": affectation, "title": "Supprimer l'affectation"})

@login_required
def mecanicien_list(request):
    mecaniciens = Mecanicien.objects.all().order_by('-created_at')
    return render(request, 'transport/mecaniciens/mecanicien_list.html', {
        'mecaniciens': mecaniciens,
        'title': 'Liste des mécaniciens'
    })

# Création

@login_required
def create_mecanicien(request):
    if request.method == 'POST':
        form = MecanicienForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mecanicien_list')
    else:
        form = MecanicienForm()
    return render(request, 'transport/mecaniciens/mecanicien_form.html', {'form': form, 'title': 'Ajouter un mécanicien'})

# Mise à jour

@login_required
def update_mecanicien(request, pk):
    mecanicien = get_object_or_404(Mecanicien, pk=pk)
    if request.method == 'POST':
        form = MecanicienForm(request.POST, instance=mecanicien)
        if form.is_valid():
            form.save()
            return redirect('mecanicien_list')
    else:
        form = MecanicienForm(instance=mecanicien)
    return render(request, 'transport/mecaniciens/mecanicien_form.html', {'form': form, 'title': 'Modifier un mécanicien'})

# Suppression

@can_delete_data
def delete_mecanicien(request, pk):
    mecanicien = get_object_or_404(Mecanicien, pk=pk)
    if request.method == 'POST':
        mecanicien.delete()
        return redirect('mecanicien_list')
    return render(request, 'transport/mecaniciens/mecanicien_confirm_delete.html', {
        'mecanicien': mecanicien,
        'title': 'Supprimer un mécanicien'
    })

# Liste

