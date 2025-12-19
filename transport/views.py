from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import IntegrityError
from django.contrib import messages
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.http import JsonResponse

from .form import (
    EntrepriseForm, InscriptionUtilisateurForm, ConnexionForm, ChauffeurForm,
    CamionForm, AffectationForm, TransitaireForm, ClientForm,
    CompagnieConteneurForm, ConteneurForm, ContratTransportForm,
    PrestationDeTransportsForm, CautionsForm, FraisTrajetForm, MissionForm,
    MissionConteneurForm, PaiementMissionForm, MecanicienForm, FournisseurForm,
    ReparationForm, ReparationMecanicienForm, PieceRepareeForm
)
from .models import (
    Chauffeur, Entreprise, Camion, Affectation, Transitaire, Client,
    CompagnieConteneur, Conteneur, ContratTransport, PrestationDeTransports,
    Cautions, FraisTrajet, Mission, MissionConteneur, PaiementMission,
    Mecanicien, Fournisseur, Reparation, ReparationMecanicien, PieceReparee
)
from .decorators import (
    can_validate_payment, can_delete_data, admin_required,
    manager_or_admin_required
)

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from utils.generate_contrat_pdf import generate_pdf_contrat
from django.conf import settings
import os
from utils.generate_contrat_pdf import generate_pdf_contrat


# def ajouter_entreprise(request):
#     form = EntrepriseForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         form.save()
#         return redirect('liste_entreprises')  # ou une autre vue après l'enregistrement
#     return render(request, 'transport/entreprise/ajouter_entreprise.html', {'form': form})


# LISTE
@login_required
def liste_entreprises(request):
    entreprises = Entreprise.objects.all().order_by('-date_creation')
    return render(request, 'transport/entreprise/liste_entreprises.html', {
        'entreprises': entreprises,
        'title': 'Liste des entreprises'
    })

# CREATE
@login_required
def ajouter_entreprise(request):
    form = EntrepriseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Entreprise ajoutée avec succès!")
        return redirect('liste_entreprises')
    return render(request, 'transport/entreprise/ajouter_entreprise.html', {'form': form, 'title': 'Créer une entreprise'})

# UPDATE
@login_required
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


@login_required
def inscription_utilisateur(request):
    if request.method == 'POST':
        form = InscriptionUtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = InscriptionUtilisateurForm()

    return render(request, 'transport/UserInscription.html', {'form': form})



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
def camion_list(request):
    camions = Camion.objects.all()
    return render(request, "transport/camions/camion_list.html", {"camions": camions, "title": "Liste des camions"})

# Ajouter un camion
@login_required
def create_camion(request):
    if request.method == "POST":
        form = CamionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Camion ajouté avec succès!")
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
def conteneur_list(request):
    conteneurs = Conteneur.objects.all().order_by('numero_conteneur')
    return render(request, "transport/conteneurs/conteneur_list.html", {"conteneurs": conteneurs, "title": "Liste des conteneurs"})

# Création d'un conteneur
@login_required
def create_conteneur(request):
    if request.method == "POST":
        form = ConteneurForm(request.POST)
        if form.is_valid():
            form.save()
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
def contrat_list(request):
    contrats = ContratTransport.objects.all().order_by('-date_debut')
    return render(request, "transport/contrat/contrat_list.html", {"contrats": contrats, "title": "Liste des contrats"})

# Création d'un contrat
@login_required
def create_contrat(request):
    if request.method == "POST":
        form = ContratTransportForm(request.POST)
        if form.is_valid():
            try:
                # 1 Sauvegarde du contrat dans la base
                contrat = form.save()

                # 2 Définition du chemin final du PDF
                folder = os.path.join(settings.MEDIA_ROOT, "contrats")
                os.makedirs(folder, exist_ok=True)

                pdf_filename = f"{contrat.pk_contrat}.pdf"
                pdf_path = os.path.join(folder, pdf_filename)

                # 3 Génération du PDF
                generate_pdf_contrat(contrat, pdf_path)

                # 4 Enregistrement du PDF dans le modèle
                contrat.pdf_file = f"contrats/{pdf_filename}"
                contrat.save()

                # 5 Message de succès et redirection
                messages.success(request, "✅ Contrat créé avec succès!")
                return redirect("contrat_list")

            except IntegrityError:
                messages.error(request, f"❌ Erreur: Le numéro BL '{form.cleaned_data.get('numero_bl')}' existe déjà. Veuillez utiliser un numéro BL unique.")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")

    else:
        form = ContratTransportForm()

    return render(
        request,
        "transport/contrat/contrat_form.html",
        {"form": form, "title": "Ajouter un contrat"}
    )


# Modification d'un contrat
@login_required
def update_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk=pk)
    if request.method == "POST":
        form = ContratTransportForm(request.POST, instance=contrat)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Contrat mis à jour avec succès!")
                return redirect('contrat_list')
            except IntegrityError:
                messages.error(request, f"❌ Erreur: Le numéro BL '{form.cleaned_data.get('numero_bl')}' existe déjà. Veuillez utiliser un numéro BL unique.")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        form = ContratTransportForm(instance=contrat)
    return render(request, "transport/contrat/contrat_form.html", {"form": form, "title": "Modifier le contrat"})

# Suppression d'un contrat
@can_delete_data
def delete_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk=pk)
    if request.method == "POST":
        contrat.delete()
        return redirect('contrat_list')
    return render(request, "transport/contrat/contrat_confirm_delete.html", {"contrat": contrat, "title": "Supprimer le contrat"})


# API: Récupérer le chauffeur affecté à un camion
@login_required
def get_chauffeur_from_camion(request, pk_camion):
    """
    Retourne le chauffeur actuellement affecté au camion spécifié
    """

    try:
        camion = Camion.objects.get(pk_camion=pk_camion)

        # Chercher l'affectation active (sans date_fin_affectation)
        affectation = Affectation.objects.filter(
            camion=camion,
            date_fin_affectation__isnull=True
        ).first()

        if affectation and affectation.chauffeur:
            return JsonResponse({
                'success': True,
                'chauffeur_id': affectation.chauffeur.pk_chauffeur,
                'chauffeur_nom': f"{affectation.chauffeur.nom} {affectation.chauffeur.prenom}"
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Aucun chauffeur affecté à ce camion'
            })
    except Camion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Camion non trouvé'
        }, status=404)


# API: Récupérer le camion affecté à un chauffeur
@login_required
def get_camion_from_chauffeur(request, pk_chauffeur):
    """
    Retourne le camion actuellement affecté au chauffeur spécifié
    """

    try:
        chauffeur = Chauffeur.objects.get(pk_chauffeur=pk_chauffeur)

        # Chercher l'affectation active (sans date_fin_affectation)
        affectation = Affectation.objects.filter(
            chauffeur=chauffeur,
            date_fin_affectation__isnull=True
        ).first()

        if affectation and affectation.camion:
            return JsonResponse({
                'success': True,
                'camion_id': affectation.camion.pk_camion,
                'camion_immatriculation': affectation.camion.immatriculation
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Aucun camion affecté à ce chauffeur'
            })
    except Chauffeur.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Chauffeur non trouvé'
        }, status=404)


# Liste
@login_required
def presta_transport_list(request):
    prestations = PrestationDeTransports.objects.all()
    return render(request, "transport/prestations/prestation_transport_list.html", {"prestations": prestations, "title": "Prestations de transport"})

# Création
@login_required
def create_presta_transport(request):
    if request.method == 'POST':
        form = PrestationDeTransportsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('presta_transport_list')
    else:
        form = PrestationDeTransportsForm()
    return render(request, "transport/prestations/prestation_transport_form.html", {"form": form, "title": "Ajouter une prestation"})

# Modification
@login_required
def update_presta_transport(request, pk):
    prestation = get_object_or_404(PrestationDeTransports, pk=pk)
    if request.method == 'POST':
        form = PrestationDeTransportsForm(request.POST, instance=prestation)
        if form.is_valid():
            form.save()
            return redirect('presta_transport_list')
    else:
        form = PrestationDeTransportsForm(instance=prestation)
    return render(request, "transport/prestations/prestation_transport_form.html", {"form": form, "title": "Modifier la prestation"})

# Suppression
@can_delete_data
def delete_presta_transport(request, pk):
    prestation = get_object_or_404(PrestationDeTransports, pk=pk)
    if request.method == 'POST':
        prestation.delete()
        return redirect('presta_transport_list')
    return render(request, "transport/prestations/prestation_transport_confirm_delete.html", {"prestation": prestation})

# Liste des cautions
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
@login_required
def mission_list(request):
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
    missions = Mission.objects.select_related('contrat', 'prestation_transport').order_by('-date_depart')

    # Apply date filters if provided
    if date_debut:
        missions = missions.filter(date_depart__gte=date_debut)
    if date_fin:
        missions = missions.filter(date_depart__lte=date_fin)

    # Séparer par statut
    missions_en_cours = missions.filter(statut='en cours')
    missions_terminees = missions.filter(statut='terminée')
    missions_annulees = missions.filter(statut='annulée')

    return render(request, 'transport/missions/mission_list.html', {
        'date_debut': date_debut,
        'date_fin': date_fin,
        'missions': missions,
        'missions_en_cours': missions_en_cours,
        'missions_terminees': missions_terminees,
        'missions_annulees': missions_annulees,
        'title': 'Liste des missions'
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
@login_required
def paiement_mission_list(request):
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
    paiements = PaiementMission.objects.select_related('mission', 'caution', 'prestation').order_by('-date_paiement')

    # Apply date filters if provided
    if date_debut:
        paiements = paiements.filter(date_paiement__gte=date_debut)
    if date_fin:
        paiements = paiements.filter(date_paiement__lte=date_fin)

    # Séparer validés et en attente
    paiements_valides = paiements.filter(est_valide=True)
    paiements_attente = paiements.filter(est_valide=False)

    return render(request, 'transport/paiements-mission/paiement_mission_list.html', {
        'date_debut': date_debut,
        'date_fin': date_fin,
        'paiements': paiements,
        'paiements_valides': paiements_valides,
        'paiements_attente': paiements_attente,
        'title': 'Liste des paiements'
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
            paiement.valider_paiement()
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
            reparation = form.save()
            nb_mecaniciens = reparation.get_mecaniciens().count()
            messages.success(request, f"✅ Réparation créée avec succès ({nb_mecaniciens} mécanicien(s) assigné(s))")
            messages.info(request, f"🔧 Vous pouvez maintenant ajouter les pièces utilisées pour cette réparation.")
            # Rediriger vers l'ajout de pièces avec la réparation pré-remplie
            return redirect('create_piece_reparee', reparation_id=reparation.pk_reparation)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
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

@login_required
def dashboard(request):
    from .models import Chauffeur, Camion, Mission, Reparation, PaiementMission, Affectation, Client
    from datetime import timedelta, datetime
    from django.utils import timezone

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
    # Missions queryset with filters
    missions_qs = Mission.objects.all()
    if date_debut:
        missions_qs = missions_qs.filter(date_depart__gte=date_debut)
    if date_fin:
        missions_qs = missions_qs.filter(date_depart__lte=date_fin)

    # Paiements queryset with filters
    paiements_qs = PaiementMission.objects.all()
    if date_debut:
        paiements_qs = paiements_qs.filter(date_paiement__gte=date_debut)
    if date_fin:
        paiements_qs = paiements_qs.filter(date_paiement__lte=date_fin)

    # Réparations queryset with filters
    reparations_qs = Reparation.objects.all()
    if date_debut:
        reparations_qs = reparations_qs.filter(date_reparation__gte=date_debut)
    if date_fin:
        reparations_qs = reparations_qs.filter(date_reparation__lte=date_fin)

    # Statistiques générales
    stats = {
        "chauffeurs": Chauffeur.objects.count(),
        "camions": Camion.objects.count(),
        "missions": missions_qs.count(),
        "missions_en_cours": missions_qs.filter(statut="En cours").count(),
        "missions_terminees": missions_qs.filter(statut__in=["Terminée", "Terminee"]).count(),
        "reparations": reparations_qs.count(),
        "paiements": paiements_qs.aggregate(total=Sum("montant_total"))["total"] or 0,
        "clients": Client.objects.count(),
        "affectations": Affectation.objects.count(),
    }

    # Missions par statut pour le graphique
    mission_par_statut = missions_qs.values("statut").annotate(total=Count("statut"))

    # Paiements mensuels
    paiements_mensuels = (
        paiements_qs
        .annotate(mois=TruncMonth("date_paiement"))
        .values("mois")
        .annotate(total=Sum("montant_total"))
        .order_by("mois")
    )

    mois_labels = [p["mois"].strftime("%b %Y") for p in paiements_mensuels]
    montant_values = [float(p["total"]) for p in paiements_mensuels]

    # Dernières missions (5 plus récentes)
    dernieres_missions = missions_qs.select_related(
        'prestation_transport', 'contrat'
    ).order_by('-date_depart')[:5]

    # Derniers paiements (5 plus récents)
    derniers_paiements = paiements_qs.select_related(
        'mission'
    ).order_by('-date_paiement')[:5]

    # Missions en cours
    missions_actives = missions_qs.filter(
        statut="En cours"
    ).select_related('prestation_transport', 'contrat')[:5]

    # Alertes - Missions qui devraient être terminées (date retour passée)
    today = timezone.now().date()
    missions_en_retard = missions_qs.filter(
        statut="En cours",
        date_retour__lt=today
    ).count() if missions_qs.filter(statut="En cours").exists() else 0

    # Réparations récentes
    reparations_recentes = reparations_qs.select_related(
        'camion'
    ).order_by('-date_reparation')[:5]

    # Statistiques par entreprise
    entreprises_stats = []
    from .models import Entreprise
    entreprises = Entreprise.objects.all()
    for entreprise in entreprises:
        entreprises_stats.append({
            'nom': entreprise.nom,
            'chauffeurs': Chauffeur.objects.filter(entreprise=entreprise).count(),
            'camions': Camion.objects.filter(entreprise=entreprise).count(),
        })

    # Calcul des revenus du mois en cours (ou période filtrée)
    if date_debut and date_fin:
        revenus_mois_actuel = paiements_qs.aggregate(total=Sum("montant_total"))["total"] or 0
    else:
        current_month = timezone.now().month
        current_year = timezone.now().year
        revenus_mois_actuel = PaiementMission.objects.filter(
            date_paiement__month=current_month,
            date_paiement__year=current_year
        ).aggregate(total=Sum("montant_total"))["total"] or 0

    return render(request, "transport/dashboard.html", {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "stats": stats,
        "mission_par_statut": list(mission_par_statut),
        "paiements_mois_labels": mois_labels,
        "paiements_mois_values": montant_values,
        "dernieres_missions": dernieres_missions,
        "derniers_paiements": derniers_paiements,
        "missions_actives": missions_actives,
        "missions_en_retard": missions_en_retard,
        "reparations_recentes": reparations_recentes,
        "entreprises_stats": entreprises_stats,
        "revenus_mois_actuel": revenus_mois_actuel,
    })

# gestion url redirection si pas bon url vers la connexion
# def rediriger_vers_connexion(request, exception=None):
#     return redirect('connexion')

# handler404 = rediriger_vers_connexion
# # gestion probleme server si la connexion n'est pas bon 
# def rediriger_erreur_serveur(request):
#     return redirect('connexion')

# handler500 = rediriger_erreur_serveur

# ============================================================================
# PROFIL UTILISATEUR ET SYSTÈME
# ============================================================================

@login_required
def user_profile(request):
    """
    Affiche le profil de l'utilisateur connecté
    """
    return render(request, 'transport/user/profile.html', {
        'title': 'Mon Profil',
        'user': request.user
    })

@login_required
def user_settings(request):
    """
    Affiche les paramètres du compte utilisateur et gère le changement de mot de passe
    """
    password_form = None

    if request.method == 'POST':
        if 'change_password' in request.POST:
            # Changement de mot de passe
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur
                messages.success(request, '✅ Votre mot de passe a été changé avec succès!')
                return redirect('user_settings')
            else:
                messages.error(request, '❌ Erreur lors du changement de mot de passe. Veuillez vérifier les informations.')

        elif 'update_email' in request.POST:
            # Mise à jour de l'email
            new_email = request.POST.get('email')
            if new_email and new_email != request.user.email:
                request.user.email = new_email
                request.user.save()
                messages.success(request, '✅ Votre email a été mis à jour avec succès!')
                return redirect('user_settings')

    # Créer le formulaire de changement de mot de passe si pas déjà créé
    if not password_form:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'transport/user/settings.html', {
        'title': 'Paramètres',
        'user': request.user,
        'password_form': password_form
    })

@login_required
def help_page(request):
    """
    Affiche la page d'aide et documentation
    """
    return render(request, 'transport/user/help.html', {
        'title': 'Aide'
    })

@login_required
def notifications_list(request):
    """
    Affiche la liste des notifications de l'utilisateur
    """
    from .models import Notification

    # Récupérer toutes les notifications de l'utilisateur
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-created_at')

    # Séparer les notifications lues et non lues
    notifications_non_lues = notifications.filter(is_read=False)
    notifications_lues = notifications.filter(is_read=True)[:10]  # Limiter les notifications lues

    # Marquer comme lue une notification spécifique si demandé
    notification_id = request.GET.get('mark_read')
    if notification_id:
        try:
            notification = Notification.objects.get(pk_notification=notification_id, utilisateur=request.user)
            notification.is_read = True
            notification.save()
            messages.success(request, "✅ Notification marquée comme lue.")
            return redirect('notifications_list')
        except Notification.DoesNotExist:
            pass

    return render(request, 'transport/user/notifications.html', {
        'title': 'Notifications',
        'notifications': notifications,
        'notifications_non_lues': notifications_non_lues,
        'notifications_lues': notifications_lues,
        'total_non_lues': notifications_non_lues.count(),
    })

@login_required
def mark_all_notifications_read(request):
    """
    Marque toutes les notifications comme lues
    """
    from .models import Notification

    if request.method == 'POST':
        # Marquer toutes les notifications de l'utilisateur comme lues
        count = Notification.objects.filter(
            utilisateur=request.user,
            is_read=False
        ).update(is_read=True)

        if count > 0:
            messages.success(request, f"✅ {count} notification(s) marquée(s) comme lue(s).")
        else:
            messages.info(request, "ℹ️ Aucune notification non lue.")

        return redirect('notifications_list')

    return redirect('notifications_list')

# ============================================================================
# GESTIONNAIRES D'ERREURS
# ============================================================================

def rediriger_vers_connexion(request, exception=None):
    return redirect('connexion')

def rediriger_erreur_serveur(request):
    return redirect('connexion')

# deconnexion 
@login_required
def logout_utilisateur(request):
    logout(request)
    return redirect('connexion')


@login_required
def pdf_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk_contrat=pk)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", alignment=1, fontSize=16, spaceAfter=12))
    styles.add(ParagraphStyle(name="NormalBold", fontSize=12))
    styles.add(ParagraphStyle(name="NormalJustify", alignment=4, leading=14))

    story = []

    # === TITRE ===
    story.append(Paragraph("<b>FEUILLE DE ROUTE</b>", styles["TitleCenter"]))
    story.append(Paragraph(f"{contrat.entreprise.nom}", styles["TitleCenter"]))
    story.append(Spacer(1, 10))

    # === DETAIL DESTINATAIRE ===
    story.append(Paragraph(f"<b>DESTINATAIRE :</b> {contrat.destinataire}", styles["Normal"]))
    story.append(Paragraph(f"<b>N° BL :</b> {contrat.numero_bl}", styles["Normal"]))
    story.append(Paragraph(f"<b>N° CONTENEUR(S) :</b> {contrat.conteneur.numero_conteneur}", styles["Normal"]))
    story.append(Paragraph(
        f"<b>NOM DU CHAUFFEUR :</b> {contrat.chauffeur.nom} {contrat.chauffeur.prenom} — Tel {contrat.chauffeur.telephone}",
        styles["Normal"]
    ))
    story.append(Paragraph(f"<b>NUMÉRO CAMION :</b> {contrat.camion.immatriculation}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # === Tableau des montants ===
    data = [
        ["DÉSIGNATION", "MONTANT"],
        ["Montant total", f"{contrat.montant_total} FCFA"],
        ["Avance transport", f"{contrat.avance_transport} FCFA"],
        ["Reliquat transport", f"{contrat.reliquat_transport} FCFA"],
        ["Caution", f"{contrat.caution} FCFA"],
    ]

    table = Table(data, colWidths=[250, 150])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    # === INFORMATIONS ===
    story.append(Paragraph(f"<b>Nature de la marchandise :</b> Produits divers", styles["Normal"]))
    story.append(Paragraph(f"<b>Transitaire :</b> {contrat.transitaire.nom} — {contrat.transitaire.telephone}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # === CLAUSES ===
    text = """
    <b>NB : Clause de responsabilité et pénalité</b><br/><br/>
    • Le transporteur est responsable uniquement en cas de perte, vol ou avarie causée par négligence.<br/>
    • La responsabilité est proportionnelle à la part non couverte par l’assurance.<br/>
    • Pas de responsabilité en cas de force majeure, douane, port, ou tiers intervenants.<br/><br/>
    • Le transporteur dispose de <b>23 jours</b> pour ramener les conteneurs vides à Dakar.<br/>
    • Retard dû au destinataire → <b>25 000 FCFA/jour</b> à facturer.<br/>
    • Retard dû au transporteur → <b>25 000 FCFA/jour</b> de pénalité.<br/><br/>
    • Une fois à Bamako, le destinataire dispose de <b>3 jours</b> pour décharger. Après : <b>25 000 FCFA/jour</b>.
    """
    story.append(Paragraph(text, styles["NormalJustify"]))
    story.append(Spacer(1, 20))

    # === Dates et signatures ===
    story.append(Paragraph(f"<b>Date de chargement :</b> {contrat.date_debut}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date de sortie :</b> {contrat.date_limite_retour}", styles["Normal"]))
    story.append(Spacer(1, 12))

    sign_table = Table(
        [["Signature transporteur", "Signature agent transit"],
         ["(signature)", "(signature)"]],
        colWidths=[250, 250]
    )
    sign_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEBELOW", (0, 1), (-1, 1), 0.8, colors.black),
    ]))

    story.append(sign_table)

    # Génération finale
    doc.build(story)

    buffer.seek(0)
    return HttpResponse(
        buffer,
        content_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"Feuille_de_Route_{pk}.pdf\"'}
    )


# ============================================================================
# TABLEAU DE BORD STATISTIQUES
# ============================================================================

@login_required
def tableau_bord_statistiques(request):
    """
    Affiche le tableau de bord avec toutes les statistiques avancées :
    - Statistiques par camion/chauffeur
    - Évolution temporelle (par mois/année)
    - Top et bottom performers
    """
    from django.db.models import Count, Sum, F, Max, Min, Q
    from django.db.models.functions import TruncMonth, TruncYear
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

    # ========== STATISTIQUES GLOBALES ==========
    # Apply date filters to missions
    missions_qs = Mission.objects.all()
    if date_debut:
        missions_qs = missions_qs.filter(date_depart__gte=date_debut)
    if date_fin:
        missions_qs = missions_qs.filter(date_depart__lte=date_fin)

    # Apply date filters to contracts
    contrats_qs = ContratTransport.objects.all()
    if date_debut:
        contrats_qs = contrats_qs.filter(date_debut__gte=date_debut)
    if date_fin:
        contrats_qs = contrats_qs.filter(date_debut__lte=date_fin)

    # Apply date filters to reparations
    reparations_qs = Reparation.objects.all()
    if date_debut:
        reparations_qs = reparations_qs.filter(date_reparation__gte=date_debut)
    if date_fin:
        reparations_qs = reparations_qs.filter(date_reparation__lte=date_fin)

    # Apply date filters to pieces
    pieces_qs = PieceReparee.objects.all()
    if date_debut:
        pieces_qs = pieces_qs.filter(reparation__date_reparation__gte=date_debut)
    if date_fin:
        pieces_qs = pieces_qs.filter(reparation__date_reparation__lte=date_fin)

    total_missions = missions_qs.count()
    total_camions = Camion.objects.count()
    total_chauffeurs = Chauffeur.objects.count()
    total_reparations = reparations_qs.count()
    total_pieces = pieces_qs.count()
    ca_total = contrats_qs.aggregate(total=Sum('montant_total'))['total'] or 0
    cout_reparations_total = reparations_qs.aggregate(total=Sum('cout'))['total'] or 0
    cout_pieces_total = pieces_qs.aggregate(total=Sum(F('quantite') * F('cout_unitaire')))['total'] or 0

    # ========== TOP PERFORMERS ==========

    # Camion avec le plus de missions
    top_camion_missions = missions_qs.values(
        'contrat__camion__immatriculation',
        'contrat__camion__modele'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions').first()

    # Chauffeur avec le plus de missions
    top_chauffeur_missions = missions_qs.values(
        'contrat__chauffeur__nom',
        'contrat__chauffeur__prenom'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions').first()

    # Camion qui a généré le plus d'argent
    top_camion_ca = contrats_qs.values(
        'camion__immatriculation',
        'camion__modele'
    ).annotate(ca_total=Sum('montant_total')).order_by('-ca_total').first()

    # Camion avec le moins de réparations (qui a au moins une réparation)
    bottom_camion_reparations = reparations_qs.values(
        'camion__immatriculation',
        'camion__modele'
    ).annotate(nb_reparations=Count('pk_reparation')).order_by('nb_reparations').first()

    # ========== STATISTIQUES PAR CAMION ==========

    # 1. Missions par camion
    missions_par_camion = missions_qs.values(
        'contrat__camion__pk_camion',
        'contrat__camion__immatriculation',
        'contrat__camion__modele'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions')

    # 2. Missions par chauffeur
    missions_par_chauffeur = missions_qs.values(
        'contrat__chauffeur__pk_chauffeur',
        'contrat__chauffeur__nom',
        'contrat__chauffeur__prenom'
    ).annotate(nb_missions=Count('pk_mission')).order_by('-nb_missions')

    # 3. CA par camion
    ca_par_camion = contrats_qs.values(
        'camion__pk_camion',
        'camion__immatriculation',
        'camion__modele'
    ).annotate(ca_total=Sum('montant_total')).order_by('-ca_total')

    # 4. Réparations par camion
    reparations_par_camion = reparations_qs.values(
        'camion__pk_camion',
        'camion__immatriculation',
        'camion__modele'
    ).annotate(
        nb_reparations=Count('pk_reparation'),
        cout_total=Sum('cout')
    ).order_by('-nb_reparations')

    # ========== ÉVOLUTION TEMPORELLE (PAR MOIS) ==========

    # Missions par mois et par camion
    missions_par_mois_camion = missions_qs.annotate(
        mois=TruncMonth('date_depart')
    ).values(
        'mois',
        'contrat__camion__immatriculation'
    ).annotate(
        nb_missions=Count('pk_mission')
    ).order_by('-mois', 'contrat__camion__immatriculation')

    # CA par mois et par camion
    ca_par_mois_camion = contrats_qs.annotate(
        mois=TruncMonth('date_debut')
    ).values(
        'mois',
        'camion__immatriculation'
    ).annotate(
        ca=Sum('montant_total')
    ).order_by('-mois', 'camion__immatriculation')

    # Réparations par mois et par camion
    reparations_par_mois_camion = reparations_qs.annotate(
        mois=TruncMonth('date_reparation')
    ).values(
        'mois',
        'camion__immatriculation'
    ).annotate(
        nb_reparations=Count('pk_reparation'),
        cout_total=Sum('cout')
    ).order_by('-mois', 'camion__immatriculation')

    # Pièces réparées par mois et par camion
    pieces_par_mois_camion = pieces_qs.annotate(
        mois=TruncMonth('reparation__date_reparation')
    ).values(
        'mois',
        'reparation__camion__immatriculation'
    ).annotate(
        nb_pieces=Count('pk_piece'),
        cout_total=Sum(F('quantite') * F('cout_unitaire'))
    ).order_by('-mois', 'reparation__camion__immatriculation')

    # ========== ÉVOLUTION TEMPORELLE (PAR ANNÉE) ==========

    # Missions par année
    missions_par_annee = missions_qs.annotate(
        annee=TruncYear('date_depart')
    ).values('annee').annotate(
        nb_missions=Count('pk_mission')
    ).order_by('-annee')

    # CA par année
    ca_par_annee = contrats_qs.annotate(
        annee=TruncYear('date_debut')
    ).values('annee').annotate(
        ca=Sum('montant_total')
    ).order_by('-annee')

    # Réparations par année
    reparations_par_annee = reparations_qs.annotate(
        annee=TruncYear('date_reparation')
    ).values('annee').annotate(
        nb_reparations=Count('pk_reparation'),
        cout_total=Sum('cout')
    ).order_by('-annee')

    # ========== PIÈCES ==========

    # Pièces réparées détaillées
    pieces_reparees = pieces_qs.select_related(
        'reparation__camion', 'fournisseur'
    ).annotate(
        cout_total_piece=F('quantite') * F('cout_unitaire')
    ).order_by('-cout_total_piece')

    # Statistiques des pièces par catégorie
    pieces_par_categorie = pieces_qs.values(
        'categorie'
    ).annotate(
        nb_pieces=Count('pk_piece'),
        cout_total=Sum(F('quantite') * F('cout_unitaire'))
    ).order_by('-cout_total')

    # Ajouter le nom de la catégorie
    for item in pieces_par_categorie:
        item['categorie_display'] = dict(
            PieceReparee._meta.get_field('categorie').choices
        ).get(item['categorie'], item['categorie'])

    context = {
        'title': 'Tableau de bord - Statistiques',

        # Filtres de date
        'date_debut': date_debut,
        'date_fin': date_fin,

        # Globales
        'total_missions': total_missions,
        'total_camions': total_camions,
        'total_chauffeurs': total_chauffeurs,
        'total_reparations': total_reparations,
        'total_pieces': total_pieces,
        'ca_total': ca_total,
        'cout_reparations_total': cout_reparations_total,
        'cout_pieces_total': cout_pieces_total,

        # Top performers
        'top_camion_missions': top_camion_missions,
        'top_chauffeur_missions': top_chauffeur_missions,
        'top_camion_ca': top_camion_ca,
        'bottom_camion_reparations': bottom_camion_reparations,

        # Par camion/chauffeur
        'missions_par_camion': missions_par_camion,
        'missions_par_chauffeur': missions_par_chauffeur,
        'ca_par_camion': ca_par_camion,
        'reparations_par_camion': reparations_par_camion,

        # Évolution temporelle (mois)
        'missions_par_mois_camion': missions_par_mois_camion,
        'ca_par_mois_camion': ca_par_mois_camion,
        'reparations_par_mois_camion': reparations_par_mois_camion,
        'pieces_par_mois_camion': pieces_par_mois_camion,

        # Évolution temporelle (année)
        'missions_par_annee': missions_par_annee,
        'ca_par_annee': ca_par_annee,
        'reparations_par_annee': reparations_par_annee,

        # Pièces
        'pieces_reparees': pieces_reparees,
        'pieces_par_categorie': pieces_par_categorie,
    }

    return render(request, 'transport/statistiques/tableau_bord.html', context)

