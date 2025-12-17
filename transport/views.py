from django.shortcuts import render, redirect
from .form import EntrepriseForm, InscriptionUtilisateurForm ,ConnexionForm,ChauffeurForm,CamionForm,AffectationForm,TransitaireForm,ClientForm,CompagnieConteneurForm,ConteneurForm,ContratTransportForm,PrestationDeTransportsForm,CautionsForm,FraisTrajetForm,MissionForm,MissionConteneurForm,PaiementMissionForm,MecanicienForm,FournisseurForm,ReparationForm,ReparationMecanicienForm,PieceRepareeForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from .models import Chauffeur, Entreprise,Camion,Affectation,Transitaire,Client,CompagnieConteneur,Conteneur,ContratTransport,PrestationDeTransports,Cautions,FraisTrajet,Mission,MissionConteneur,PaiementMission,Mecanicien,Fournisseur,Reparation,ReparationMecanicien,PieceReparee
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect

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
def liste_entreprises(request):
    entreprises = Entreprise.objects.all().order_by('-date_creation')
    return render(request, 'transport/entreprise/liste_entreprises.html', {
        'entreprises': entreprises,
        'title': 'Liste des entreprises'
    })

# CREATE
def ajouter_entreprise(request):
    form = EntrepriseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Entreprise ajoutée avec succès!")
        return redirect('liste_entreprises')
    return render(request, 'transport/entreprise/ajouter_entreprise.html', {'form': form, 'title': 'Créer une entreprise'})

# UPDATE
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



def inscription_utilisateur(request):
    if request.method == 'POST':
        form = InscriptionUtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = InscriptionUtilisateurForm()

    return render(request, 'transport/UserInscription.html', {'form': form})



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

def chauffeur_list(request):
    chauffeurs = Chauffeur.objects.select_related("entreprise").all()
    return render(request, "transport/chauffeurs/chauffeur_list.html", {"chauffeurs": chauffeurs})

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

def chauffeur_delete(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    if request.method == "POST":
       chauffeur.delete()
       messages.success(request, "🗑️ Chauffeur supprimé avec succès.")
       return redirect("chauffeur_list")
    return render(request, "transport/chauffeurs/chauffeur_confirm_delete.html", {"chauffeur": chauffeur})

# Liste des camions
def camion_list(request):
    camions = Camion.objects.all()
    return render(request, "transport/camions/camion_list.html", {"camions": camions, "title": "Liste des camions"})

# Ajouter un camion
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
def delete_camion(request, pk):
    camion = get_object_or_404(Camion, pk=pk)
    if request.method == "POST":
        camion.delete()
        messages.success(request, "🗑️ Camion supprimé avec succès!")
        return redirect('camion_list')
    return render(request, "transport/camions/camion_confirm_delete.html", {"camion": camion, "title": "Supprimer le camion"})


# Liste des affectations
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
def delete_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == "POST":
        affectation.delete()
        messages.success(request, "🗑️ Affectation supprimée avec succès!")
        return redirect('affectation_list')
    return render(request, "transport/affectations/affectation_confirm_delete.html", {"affectation": affectation, "title": "Supprimer l'affectation"})


def transitaire_list(request):
    transitaires = Transitaire.objects.all().order_by('nom')
    return render(request, "transport/transitaires/transitaire_list.html", {"transitaires": transitaires, "title": "Liste des transitaires"})

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
def delete_transitaire(request, pk):
    transitaire = get_object_or_404(Transitaire, pk=pk)
    if request.method == "POST":
        transitaire.delete()
        messages.success(request, "🗑️ Transitaire supprimé avec succès!")
        return redirect('transitaire_list')
    return render(request, "transport/transitaires/transitaire_confirm_delete.html", {"transitaire": transitaire, "title": "Supprimer le transitaire"})


# Liste des clients
def client_list(request):
    clients = Client.objects.all().order_by('nom')
    return render(request, "transport/clients/client_list.html", {"clients": clients, "title": "Liste des clients"})

# Création d'un client
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
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect('client_list')
    return render(request, "transport/clients/client_confirm_delete.html", {"client": client, "title": "Supprimer le client"})

# Liste des compagnies
def compagnie_list(request):
    compagnies = CompagnieConteneur.objects.all().order_by('nom')
    return render(request, "transport/compagnies/compagnie_list.html", {"compagnies": compagnies, "title": "Liste des compagnies de conteneurs"})

# Création d'une compagnie
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
def delete_compagnie(request, pk):
    compagnie = get_object_or_404(CompagnieConteneur, pk=pk)
    if request.method == "POST":
        compagnie.delete()
        return redirect('compagnie_list')
    return render(request, "transport/compagnies/compagnie_confirm_delete.html", {"compagnie": compagnie, "title": "Supprimer la compagnie"})

# Liste des conteneurs
def conteneur_list(request):
    conteneurs = Conteneur.objects.all().order_by('numero_conteneur')
    return render(request, "transport/conteneurs/conteneur_list.html", {"conteneurs": conteneurs, "title": "Liste des conteneurs"})

# Création d'un conteneur
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
def delete_conteneur(request, pk):
    conteneur = get_object_or_404(Conteneur, pk=pk)
    if request.method == "POST":
        conteneur.delete()
        return redirect('conteneur_list')
    return render(request, "transport/conteneurs/conteneur_confirm_delete.html", {"conteneur": conteneur, "title": "Supprimer le conteneur"})

# Liste des contrats
def contrat_list(request):
    contrats = ContratTransport.objects.all().order_by('-date_debut')
    return render(request, "transport/contrat/contrat_list.html", {"contrats": contrats, "title": "Liste des contrats"})

# Création d'un contrat
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
def delete_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk=pk)
    if request.method == "POST":
        contrat.delete()
        return redirect('contrat_list')
    return render(request, "transport/contrat/contrat_confirm_delete.html", {"contrat": contrat, "title": "Supprimer le contrat"})


# API: Récupérer le chauffeur affecté à un camion
def get_chauffeur_from_camion(request, pk_camion):
    """
    Retourne le chauffeur actuellement affecté au camion spécifié
    """
    from django.http import JsonResponse

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


# Liste
def presta_transport_list(request):
    prestations = PrestationDeTransports.objects.all()
    return render(request, "transport/prestations/prestation_transport_list.html", {"prestations": prestations, "title": "Prestations de transport"})

# Création
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
def delete_presta_transport(request, pk):
    prestation = get_object_or_404(PrestationDeTransports, pk=pk)
    if request.method == 'POST':
        prestation.delete()
        return redirect('presta_transport_list')
    return render(request, "transport/prestations/prestation_transport_confirm_delete.html", {"prestation": prestation})

# Liste des cautions
def cautions_list(request):
    cautions = Cautions.objects.all()
    return render(request, "transport/cautions/cautions_list.html", {"cautions": cautions, "title": "Liste des cautions"})

# Création
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
def delete_caution(request, pk):
    caution = get_object_or_404(Cautions, pk=pk)
    if request.method == "POST":
        caution.delete()
        return redirect('cautions_list')
    return render(request, "transport/cautions/caution_confirm_delete.html", {"caution": caution})



def frais_list(request):
    frais = FraisTrajet.objects.all()
    return render(request, 'transport/frais/frais_list.html', {'frais': frais, 'title': 'Liste des frais de trajet'})


def create_frais(request):
    form = FraisTrajetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_form.html', {'form': form, 'title': 'Ajouter un frais de trajet'})

def update_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    form = FraisTrajetForm(request.POST or None, instance=frais)
    if form.is_valid():
        form.save()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_form.html', {'form': form, 'title': 'Modifier le frais de trajet'})

def delete_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    if request.method == 'POST':
        frais.delete()
        return redirect('frais_list')
    return render(request, 'transport/frais/frais_confirm_delete.html', {'frais': frais, 'title': 'Supprimer le frais de trajet'})


# Liste des missions
def mission_list(request):
    missions = Mission.objects.select_related('contrat', 'prestation_transport').order_by('-date_depart')

    # Séparer par statut
    missions_en_cours = missions.filter(statut='en cours')
    missions_terminees = missions.filter(statut='terminée')
    missions_annulees = missions.filter(statut='annulée')

    return render(request, 'transport/missions/mission_list.html', {
        'missions': missions,
        'missions_en_cours': missions_en_cours,
        'missions_terminees': missions_terminees,
        'missions_annulees': missions_annulees,
        'title': 'Liste des missions'
    })
# Créer une mission
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
def delete_mission(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)
    if request.method == 'POST':
        mission.delete()
        return redirect('mission_list')
    return render(request, 'transport/missions/confirm_delete.html', {'object': mission, 'title': 'Supprimer une mission'})

# Terminer une mission
def terminer_mission(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)

    # Vérifier que la mission n'est pas déjà terminée
    if mission.statut == 'terminée':
        messages.warning(request, "⚠️ Cette mission est déjà terminée.")
        return redirect('mission_list')

    if request.method == 'POST':
        try:
            mission.terminer_mission()
            messages.success(request, f"✅ Mission terminée avec succès! Vous pouvez maintenant valider le paiement associé.")
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
        'title': 'Terminer la mission'
    })

# LIST
def mission_conteneur_list(request):
    mission_conteneurs = MissionConteneur.objects.all()
    return render(request, 'transport/missions/mission_conteneur_list.html', {
        'title': 'Liste des Missions - Conteneurs',
        'mission_conteneurs': mission_conteneurs
    })

# CREATE
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
def paiement_mission_list(request):
    paiements = PaiementMission.objects.select_related('mission', 'caution', 'prestation').order_by('-date_paiement')

    # Séparer validés et en attente
    paiements_valides = paiements.filter(est_valide=True)
    paiements_attente = paiements.filter(est_valide=False)

    return render(request, 'transport/paiements-mission/paiement_mission_list.html', {
        'paiements': paiements,
        'paiements_valides': paiements_valides,
        'paiements_attente': paiements_attente,
        'title': 'Liste des paiements'
    })

# Création
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
def delete_paiement_mission(request, pk):
    paiement = get_object_or_404(PaiementMission, pk=pk)
    if request.method == 'POST':
        paiement.delete()
        return redirect('paiement_mission_list')
    return render(request, 'transport/paiements-mission/paiement_mission_confirm_delete.html', {'paiement': paiement, 'title': 'Supprimer un paiement'})

# Valider un paiement
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
def mecanicien_list(request):
    mecaniciens = Mecanicien.objects.all().order_by('-created_at')
    return render(request, 'transport/mecaniciens/mecanicien_list.html', {
        'mecaniciens': mecaniciens,
        'title': 'Liste des mécaniciens'
    })

# Création
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
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all().order_by('-created_at')
    return render(request, 'transport/fournisseurs/fournisseur_list.html', {
        'fournisseurs': fournisseurs,
        'title': 'Liste des fournisseurs'
    })

# Création
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
def reparation_list(request):
    reparations = Reparation.objects.select_related('camion', 'chauffeur').order_by('-date_reparation')
    return render(request, 'transport/reparations/reparation_list.html', {
        'reparations': reparations,
        'title': 'Liste des réparations'
    })

# Création
def create_reparation(request):
    if request.method == 'POST':
        form = ReparationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reparation_list')
    else:
        form = ReparationForm()
    return render(request, 'transport/reparations/reparation_form.html', {'form': form, 'title': 'Ajouter une réparation'})

# Modification
def update_reparation(request, pk):
    reparation = get_object_or_404(Reparation, pk=pk)
    if request.method == 'POST':
        form = ReparationForm(request.POST, instance=reparation)
        if form.is_valid():
            form.save()
            return redirect('reparation_list')
    else:
        form = ReparationForm(instance=reparation)
    return render(request, 'transport/reparations/reparation_form.html', {'form': form, 'title': 'Modifier une réparation'})

# Suppression
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
def reparation_mecanicien_list(request):
    relations = ReparationMecanicien.objects.select_related('reparation', 'mecanicien')
    return render(request, 'transport/reparations/reparation_mecanicien_list.html', {
        'relations': relations,
        'title': 'Réparations & Mécaniciens'
    })

# Création
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
def piece_reparee_list(request):
    pieces = PieceReparee.objects.select_related('reparation', 'fournisseur')
    return render(request, 'transport/reparations/piece_reparee_list.html', {
        'pieces': pieces,
        'title': 'Pièces réparées'
    })

# Création
def create_piece_reparee(request):
    if request.method == 'POST':
        form = PieceRepareeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('piece_reparee_list')
    else:
        form = PieceRepareeForm()
    return render(request, 'transport/reparations/piece_reparee_form.html', {
        'form': form,
        'title': 'Ajouter une pièce réparée'
    })

# Modification
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

def dashboard(request):
    from .models import Chauffeur, Camion, Mission, Reparation, PaiementMission, Affectation, Client
    from datetime import timedelta
    from django.utils import timezone

    # Statistiques générales
    stats = {
        "chauffeurs": Chauffeur.objects.count(),
        "camions": Camion.objects.count(),
        "missions": Mission.objects.count(),
        "missions_en_cours": Mission.objects.filter(statut="En cours").count(),
        "missions_terminees": Mission.objects.filter(statut__in=["Terminée", "Terminee"]).count(),
        "reparations": Reparation.objects.count(),
        "paiements": PaiementMission.objects.aggregate(total=Sum("montant_total"))["total"] or 0,
        "clients": Client.objects.count(),
        "affectations": Affectation.objects.count(),
    }

    # Missions par statut pour le graphique
    mission_par_statut = Mission.objects.values("statut").annotate(total=Count("statut"))

    # Paiements mensuels
    paiements_mensuels = (
        PaiementMission.objects
        .annotate(mois=TruncMonth("date_paiement"))
        .values("mois")
        .annotate(total=Sum("montant_total"))
        .order_by("mois")
    )

    mois_labels = [p["mois"].strftime("%b %Y") for p in paiements_mensuels]
    montant_values = [float(p["total"]) for p in paiements_mensuels]

    # Dernières missions (5 plus récentes)
    dernieres_missions = Mission.objects.select_related(
        'prestation_transport', 'contrat'
    ).order_by('-date_depart')[:5]

    # Derniers paiements (5 plus récents)
    derniers_paiements = PaiementMission.objects.select_related(
        'mission'
    ).order_by('-date_paiement')[:5]

    # Missions en cours
    missions_actives = Mission.objects.filter(
        statut="En cours"
    ).select_related('prestation_transport', 'contrat')[:5]

    # Alertes - Missions qui devraient être terminées (date retour passée)
    today = timezone.now().date()
    missions_en_retard = Mission.objects.filter(
        statut="En cours",
        date_retour__lt=today
    ).count() if Mission.objects.filter(statut="En cours").exists() else 0

    # Réparations récentes
    reparations_recentes = Reparation.objects.select_related(
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

    # Calcul des revenus du mois en cours
    current_month = timezone.now().month
    current_year = timezone.now().year
    revenus_mois_actuel = PaiementMission.objects.filter(
        date_paiement__month=current_month,
        date_paiement__year=current_year
    ).aggregate(total=Sum("montant_total"))["total"] or 0

    return render(request, "transport/dashboard.html", {
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

def rediriger_vers_connexion(request, exception=None):
    return redirect('connexion')

def rediriger_erreur_serveur(request):
    return redirect('connexion')

# deconnexion 
def logout_utilisateur(request):
    logout(request)
    return redirect('connexion')


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

