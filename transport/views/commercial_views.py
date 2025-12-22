"""
Commercial Views.Py

Vues pour commercial
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Transitaire, Client, CompagnieConteneur, Fournisseur)
from ..forms import (TransitaireForm, ClientForm, CompagnieConteneurForm, FournisseurForm)
from ..decorators import (can_delete_data)


@login_required
def transitaire_list(request):
    transitaires = Transitaire.objects.all().order_by('nom')
    return render(request, "transport/transitaires/transitaire_list.html", {"transitaires": transitaires, "title": "Liste des transitaires"})

@login_required
def create_transitaire(request):
    if request.method == "POST":
        form = TransitaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Transitaire ajouté avec succès!")
            return redirect('transitaire_list')
    else:
        form = TransitaireForm()
    return render(request, "transport/transitaires/transitaire_form.html", {"form": form, "title": "Ajouter un transitaire"})


 #Modification d'un transitaire

@login_required
def update_transitaire(request, pk):
    transitaire = get_object_or_404(Transitaire, pk=pk)
    if request.method == "POST":
        form = TransitaireForm(request.POST, instance=transitaire)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Transitaire mis à jour avec succès!")
            return redirect('transitaire_list')
    else:
        form = TransitaireForm(instance=transitaire)
    return render(request, "transport/transitaires/transitaire_form.html", {"form": form, "title": "Modifier le transitaire"})

# Suppression d'un transitaire

@can_delete_data
def delete_transitaire(request, pk):
    transitaire = get_object_or_404(Transitaire, pk=pk)
    if request.method == "POST":
        transitaire.delete()
        messages.success(request, "🗑️ Transitaire supprimé avec succès!")
        return redirect('transitaire_list')
    return render(request, "transport/transitaires/transitaire_confirm_delete.html", {"transitaire": transitaire, "title": "Supprimer le transitaire"})


# Liste des clients

@login_required
def client_list(request):
    clients = Client.objects.all().order_by('nom')
    return render(request, "transport/clients/client_list.html", {"clients": clients, "title": "Liste des clients"})

# Création d'un client

@login_required
def create_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, "transport/clients/client_form.html", {"form": form, "title": "Ajouter un client"})

# Modification d'un client

@login_required
def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, "transport/clients/client_form.html", {"form": form, "title": "Modifier le client"})

# Suppression d'un client

@can_delete_data
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect('client_list')
    return render(request, "transport/clients/client_confirm_delete.html", {"client": client, "title": "Supprimer le client"})

# Liste des compagnies

@login_required
def compagnie_list(request):
    compagnies = CompagnieConteneur.objects.all().order_by('nom')
    return render(request, "transport/compagnies/compagnie_list.html", {"compagnies": compagnies, "title": "Liste des compagnies de conteneurs"})

# Création d'une compagnie

@login_required
def create_compagnie(request):
    if request.method == "POST":
        form = CompagnieConteneurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compagnie_list')
    else:
        form = CompagnieConteneurForm()
    return render(request, "transport/compagnies/compagnie_form.html", {"form": form, "title": "Ajouter une compagnie"})

# Modification d'une compagnie

@login_required
def update_compagnie(request, pk):
    compagnie = get_object_or_404(CompagnieConteneur, pk=pk)
    if request.method == "POST":
        form = CompagnieConteneurForm(request.POST, instance=compagnie)
        if form.is_valid():
            form.save()
            return redirect('compagnie_list')
    else:
        form = CompagnieConteneurForm(instance=compagnie)
    return render(request, "transport/compagnies/compagnie_form.html", {"form": form, "title": "Modifier la compagnie"})

# Suppression d'une compagnie

@can_delete_data
def delete_compagnie(request, pk):
    compagnie = get_object_or_404(CompagnieConteneur, pk=pk)
    if request.method == "POST":
        compagnie.delete()
        return redirect('compagnie_list')
    return render(request, "transport/compagnies/compagnie_confirm_delete.html", {"compagnie": compagnie, "title": "Supprimer la compagnie"})

# Liste des conteneurs

@login_required
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all().order_by('-created_at')
    return render(request, 'transport/fournisseurs/fournisseur_list.html', {
        'fournisseurs': fournisseurs,
        'title': 'Liste des fournisseurs'
    })

# Création

@login_required
def create_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'transport/fournisseurs/fournisseur_form.html', {'form': form, 'title': 'Ajouter un fournisseur'})

# Mise à jour

@login_required
def update_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'transport/fournisseurs/fournisseur_form.html', {'form': form, 'title': 'Modifier un fournisseur'})

# Suppression

@can_delete_data
def delete_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        return redirect('fournisseur_list')
    return render(request, 'transport/fournisseurs/fournisseur_confirm_delete.html', {
        'fournisseur': fournisseur,
        'title': 'Supprimer un fournisseur'
    })


# Liste

