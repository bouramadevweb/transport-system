"""
Vehicle Views.Py

Vues pour vehicle
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction

from ..models import (Camion, Conteneur, Reparation, ReparationMecanicien, PieceReparee, AuditLog)
from ..forms import (CamionForm, ConteneurForm, ReparationForm, ReparationMecanicienForm, PieceRepareeForm)
from ..decorators import can_delete_data

logger = logging.getLogger('transport')

@login_required
def camion_list(request):
    camions = Camion.objects.select_related('entreprise').order_by('-pk_camion')
    return render(request, "transport/camions/camion_list.html", {"camions": camions, "title": "Liste des camions"})

# Ajouter un camion

@login_required
def create_camion(request):
    if request.method == "POST":
        form = CamionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                camion = form.save()
                AuditLog.objects.create(
                    utilisateur=request.user,
                    action='CREATE',
                    model_name='Camion',
                    object_id=camion.pk_camion,
                    object_repr=f"Camion {camion.immatriculation}",
                    changes={}
                )
            logger.info(f"Camion {camion.immatriculation} créé par {request.user.email}")
            messages.success(request, f"Camion {camion.immatriculation} ajouté avec succès!")
            return redirect('camion_list')
    else:
        form = CamionForm()
    return render(request, "transport/camions/camion_form.html", {"form": form, "title": "Ajouter un camion"})

# Modifier un camion

@login_required
def update_camion(request, pk):
    camion = get_object_or_404(Camion, pk=pk)
    if request.method == "POST":
        form = CamionForm(request.POST, instance=camion)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Camion mis à jour avec succès!")
            return redirect('camion_list')
    else:
        form = CamionForm(instance=camion)
    return render(request, "transport/camions/camion_form.html", {"form": form, "title": "Modifier le camion"})

# Supprimer un camion

@can_delete_data
def delete_camion(request, pk):
    camion = get_object_or_404(Camion, pk=pk)
    if request.method == "POST":
        camion.delete()
        messages.success(request, "🗑️ Camion supprimé avec succès!")
        return redirect('camion_list')
    return render(request, "transport/camions/camion_confirm_delete.html", {"camion": camion, "title": "Supprimer le camion"})


# Liste des affectations

@login_required
def conteneur_list(request):
    conteneurs = Conteneur.objects.select_related('compagnie').order_by('numero_conteneur')
    return render(request, "transport/conteneurs/conteneur_list.html", {"conteneurs": conteneurs, "title": "Liste des conteneurs"})

# Création d'un conteneur

@login_required
def create_conteneur(request):
    if request.method == "POST":
        form = ConteneurForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                conteneur = form.save()
                AuditLog.objects.create(
                    utilisateur=request.user,
                    action='CREATE',
                    model_name='Conteneur',
                    object_id=conteneur.pk_conteneur,
                    object_repr=f"Conteneur {conteneur.numero_conteneur}",
                    changes={}
                )
            logger.info(f"Conteneur {conteneur.numero_conteneur} créé par {request.user.email}")
            messages.success(request, f"Conteneur {conteneur.numero_conteneur} ajouté avec succès!")
            return redirect('conteneur_list')
    else:
        form = ConteneurForm()
    return render(request, "transport/conteneurs/conteneur_form.html", {"form": form, "title": "Ajouter un conteneur"})

# Modification d'un conteneur

@login_required
def update_conteneur(request, pk):
    conteneur = get_object_or_404(Conteneur, pk=pk)
    if request.method == "POST":
        form = ConteneurForm(request.POST, instance=conteneur)
        if form.is_valid():
            form.save()
            return redirect('conteneur_list')
    else:
        form = ConteneurForm(instance=conteneur)
    return render(request, "transport/conteneurs/conteneur_form.html", {"form": form, "title": "Modifier le conteneur"})

# Suppression d'un conteneur

@can_delete_data
def delete_conteneur(request, pk):
    conteneur = get_object_or_404(Conteneur, pk=pk)
    if request.method == "POST":
        conteneur.delete()
        return redirect('conteneur_list')
    return render(request, "transport/conteneurs/conteneur_confirm_delete.html", {"conteneur": conteneur, "title": "Supprimer le conteneur"})

# Liste des contrats

@login_required
def reparation_list(request):
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

    # ========== APPLICATION DES FILTRES ==========
    reparations = Reparation.objects.select_related('camion', 'chauffeur').order_by('-date_reparation')

    # Apply date filters if provided
    if date_debut:
        reparations = reparations.filter(date_reparation__gte=date_debut)
    if date_fin:
        reparations = reparations.filter(date_reparation__lte=date_fin)

    return render(request, 'transport/reparations/reparation_list.html', {
        'date_debut': date_debut,
        'date_fin': date_fin,
        'reparations': reparations,
        'title': 'Liste des réparations'
    })

# Création

@login_required
def create_reparation(request):
    if request.method == 'POST':
        form = ReparationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    reparation = form.save()
                    AuditLog.objects.create(
                        utilisateur=request.user,
                        action='CREATE',
                        model_name='Reparation',
                        object_id=reparation.pk_reparation,
                        object_repr=f"Réparation {reparation.camion}",
                        changes={}
                    )
                nb_mecaniciens = reparation.get_mecaniciens().count()
                logger.info(f"Réparation créée par {request.user.email} pour {reparation.camion}")
                messages.success(request, f"Réparation créée avec succès ({nb_mecaniciens} mécanicien(s) assigné(s))")
                messages.info(request, "Vous pouvez maintenant ajouter les pièces utilisées.")
                return redirect('create_piece_reparee', reparation_id=reparation.pk_reparation)
            except Exception as e:
                logger.error(f"Erreur création réparation: {e}", exc_info=True)
                messages.error(request, f"Erreur: {str(e)}")
        else:
            for _, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ReparationForm()
    return render(request, 'transport/reparations/reparation_form.html', {'form': form, 'title': 'Ajouter une réparation'})

# Modification

@login_required
def update_reparation(request, pk):
    reparation = get_object_or_404(Reparation, pk=pk)
    if request.method == 'POST':
        form = ReparationForm(request.POST, instance=reparation)
        if form.is_valid():
            reparation = form.save()
            nb_mecaniciens = reparation.get_mecaniciens().count()
            messages.success(request, f"✅ Réparation mise à jour avec succès ({nb_mecaniciens} mécanicien(s) assigné(s))")
            return redirect('reparation_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        form = ReparationForm(instance=reparation)
    return render(request, 'transport/reparations/reparation_form.html', {'form': form, 'title': 'Modifier une réparation'})

# Suppression

@can_delete_data
def delete_reparation(request, pk):
    reparation = get_object_or_404(Reparation, pk=pk)
    if request.method == 'POST':
        reparation.delete()
        return redirect('reparation_list')
    return render(request, 'transport/reparations/reparation_confirm_delete.html', {
        'reparation': reparation,
        'title': 'Supprimer une réparation'
    })

# Liste

@login_required
def reparation_mecanicien_list(request):
    relations = ReparationMecanicien.objects.select_related('reparation', 'mecanicien')
    return render(request, 'transport/reparations/reparation_mecanicien_list.html', {
        'relations': relations,
        'title': 'Réparations & Mécaniciens'
    })

# Création

@login_required
def create_reparation_mecanicien(request):
    if request.method == 'POST':
        form = ReparationMecanicienForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reparation_mecanicien_list')
    else:
        form = ReparationMecanicienForm()
    return render(request, 'transport/reparations/reparation_mecanicien_form.html', {
        'form': form,
        'title': 'Associer une réparation à un mécanicien'
    })

# Modification

@login_required
def update_reparation_mecanicien(request, pk):
    relation = get_object_or_404(ReparationMecanicien, pk=pk)
    if request.method == 'POST':
        form = ReparationMecanicienForm(request.POST, instance=relation)
        if form.is_valid():
            form.save()
            return redirect('reparation_mecanicien_list')
    else:
        form = ReparationMecanicienForm(instance=relation)
    return render(request, 'transport/reparations/reparation_mecanicien_form.html', {
        'form': form,
        'title': 'Modifier association'
    })

# Suppression

@can_delete_data
def delete_reparation_mecanicien(request, pk):
    relation = get_object_or_404(ReparationMecanicien, pk=pk)
    if request.method == 'POST':
        relation.delete()
        return redirect('reparation_mecanicien_list')
    return render(request, 'transport/reparations/reparation_mecanicien_confirm_delete.html', {
        'relation': relation,
        'title': 'Supprimer association'
    })

# Liste

@login_required
def piece_reparee_list(request):
    pieces = PieceReparee.objects.select_related('reparation', 'fournisseur')
    return render(request, 'transport/reparations/piece_reparee_list.html', {
        'pieces': pieces,
        'title': 'Pièces réparées'
    })

# Création

@login_required
def create_piece_reparee(request, reparation_id=None):
    # Récupérer la réparation si un ID est fourni
    reparation_preselected = None
    if reparation_id:
        reparation_preselected = get_object_or_404(Reparation, pk_reparation=reparation_id)

    if request.method == 'POST':
        form = PieceRepareeForm(request.POST, reparation_id=reparation_id)
        if form.is_valid():
            piece = form.save()
            messages.success(request, f"✅ Pièce '{piece.nom_piece}' ajoutée avec succès!")

            # Rediriger vers la liste des réparations ou des pièces
            if reparation_id:
                return redirect('reparation_list')
            else:
                return redirect('piece_reparee_list')
    else:
        form = PieceRepareeForm(reparation_id=reparation_id)

    context = {
        'form': form,
        'title': 'Ajouter une pièce réparée',
        'reparation_preselected': reparation_preselected
    }
    return render(request, 'transport/reparations/piece_reparee_form.html', context)

# Modification

@login_required
def update_piece_reparee(request, pk):
    piece = get_object_or_404(PieceReparee, pk=pk)
    if request.method == 'POST':
        form = PieceRepareeForm(request.POST, instance=piece)
        if form.is_valid():
            form.save()
            return redirect('piece_reparee_list')
    else:
        form = PieceRepareeForm(instance=piece)
    return render(request, 'transport/reparations/piece_reparee_form.html', {
        'form': form,
        'title': 'Modifier une pièce réparée'
    })

# Suppression

@can_delete_data
def delete_piece_reparee(request, pk):
    piece = get_object_or_404(PieceReparee, pk=pk)
    if request.method == 'POST':
        piece.delete()
        return redirect('piece_reparee_list')
    return render(request, 'transport/reparations/piece_reparee_confirm_delete.html', {
        'piece': piece,
        'title': 'Supprimer une pièce réparée'
    })

# Connexion 
def connexion_utilisateur(request):
    form = ConnexionForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirige vers une page après connexion
            else:
                form.add_error(None, "Email ou mot de passe invalide.")

    return render(request, 'transport/connexion.html', {'form': form})

#tableau de bord

