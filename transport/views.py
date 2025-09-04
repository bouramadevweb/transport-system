from django.shortcuts import render, redirect
from .form import EntrepriseForm, InscriptionUtilisateurForm ,ConnexionForm,ChauffeurForm,CamionForm,AffectationForm,TransitaireForm,ClientForm,CompagnieConteneurForm,ConteneurForm,ContratTransportForm,PrestationDeTransportsForm,CautionsForm,FraisTrajetForm,MissionForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from .models import Chauffeur, Entreprise,Camion,Affectation,Transitaire,Client,CompagnieConteneur,Conteneur,ContratTransport,PrestationDeTransports,Cautions,FraisTrajet,Mission

def ajouter_entreprise(request):
    form = EntrepriseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('liste_entreprises')  # ou une autre vue après l'enregistrement
    return render(request, 'transport/ajouter_entreprise.html', {'form': form})

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
    
    return render(request, "transport/chauffeur_form.html", {"form": form, "title": "Ajouter un chauffeur"})

def chauffeur_list(request):
    chauffeurs = Chauffeur.objects.select_related("entreprise").all()
    return render(request, "transport/chauffeur_list.html", {"chauffeurs": chauffeurs})

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

    return render(request, "transport/chauffeur_form.html", {"form": form, "title": "Modifier un chauffeur"})

def delete_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    chauffeur.delete()
    messages.success(request, "🗑️ Chauffeur supprimé avec succès.")
    return redirect("transport/chauffeur_list")

# Liste des camions
def camion_list(request):
    camions = Camion.objects.all()
    return render(request, "transport/camion_list.html", {"camions": camions, "title": "Liste des camions"})

# Ajouter un camion
def create_camion(request):
    if request.method == "POST":
        form = CamionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('camion_list')
    else:
        form = CamionForm()
    return render(request, "transport/camion_form.html", {"form": form, "title": "Ajouter un camion"})

# Modifier un camion
def update_camion(request, pk):
    camion = get_object_or_404(Camion, pk=pk)
    if request.method == "POST":
        form = CamionForm(request.POST, instance=camion)
        if form.is_valid():
            form.save()
            return redirect('camion_list')
    else:
        form = CamionForm(instance=camion)
    return render(request, "transport/camion_form.html", {"form": form, "title": "Modifier le camion"})

# Supprimer un camion
def delete_camion(request, pk):
    camion = get_object_or_404(Camion, pk=pk)
    if request.method == "POST":
        camion.delete()
        return redirect('camion_list')
    return render(request, "transport/camion_confirm_delete.html", {"camion": camion, "title": "Supprimer le camion"})

# Liste des affectations
def affectation_list(request):
    affectations = Affectation.objects.all()
    return render(request, "transport/affectation_list.html", {"affectations": affectations, "title": "Liste des affectations"})

# Ajouter une affectation
def create_affectation(request):
    if request.method == "POST":
        form = AffectationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('affectation_list')
    else:
        form = AffectationForm()
    return render(request, "transport/affectation_form.html", {"form": form, "title": "Ajouter une affectation"})

# Modifier une affectation
def update_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == "POST":
        form = AffectationForm(request.POST, instance=affectation)
        if form.is_valid():
            form.save()
            return redirect('affectation_list')
    else:
        form = AffectationForm(instance=affectation)
    return render(request, "transport/affectation_form.html", {"form": form, "title": "Modifier l'affectation"})

# Supprimer une affectation
def delete_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == "POST":
        affectation.delete()
        return redirect('affectation_list')
    return render(request, "transport/affectation_confirm_delete.html", {"affectation": affectation, "title": "Supprimer l'affectation"})


def transitaire_list(request):
    transitaires = Transitaire.objects.all().order_by('nom')
    return render(request, "transport/transitaire_list.html", {"transitaires": transitaires, "title": "Liste des transitaires"})

def create_transitaire(request):
    if request.method == "POST":
        form = TransitaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transitaire_list')
    else:
        form = TransitaireForm()
    return render(request, "transport/transitaire_form.html", {"form": form, "title": "Ajouter un transitaire"})


 #Modification d'un transitaire
def update_transitaire(request, pk):
    transitaire = get_object_or_404(Transitaire, pk=pk)
    if request.method == "POST":
        form = TransitaireForm(request.POST, instance=transitaire)
        if form.is_valid():
            form.save()
            return redirect('transitaire_list')
    else:
        form = TransitaireForm(instance=transitaire)
    return render(request, "transport/transitaire_form.html", {"form": form, "title": "Modifier le transitaire"})

# Suppression d'un transitaire
def delete_transitaire(request, pk):
    transitaire = get_object_or_404(Transitaire, pk=pk)
    if request.method == "POST":
        transitaire.delete()
        return redirect('transitaire_list')
    return render(request, "transport/transitaire_confirm_delete.html", {"transitaire": transitaire, "title": "Supprimer le transitaire"})


# Liste des clients
def client_list(request):
    clients = Client.objects.all().order_by('nom')
    return render(request, "transport/client_list.html", {"clients": clients, "title": "Liste des clients"})

# Création d'un client
def create_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, "transport/client_form.html", {"form": form, "title": "Ajouter un client"})

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
    return render(request, "transport/client_form.html", {"form": form, "title": "Modifier le client"})

# Suppression d'un client
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect('client_list')
    return render(request, "transport/client_confirm_delete.html", {"client": client, "title": "Supprimer le client"})

# Liste des compagnies
def compagnie_list(request):
    compagnies = CompagnieConteneur.objects.all().order_by('nom')
    return render(request, "transport/compagnie_list.html", {"compagnies": compagnies, "title": "Liste des compagnies de conteneurs"})

# Création d'une compagnie
def create_compagnie(request):
    if request.method == "POST":
        form = CompagnieConteneurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compagnie_list')
    else:
        form = CompagnieConteneurForm()
    return render(request, "transport/compagnie_form.html", {"form": form, "title": "Ajouter une compagnie"})

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
    return render(request, "transport/compagnie_form.html", {"form": form, "title": "Modifier la compagnie"})

# Suppression d'une compagnie
def delete_compagnie(request, pk):
    compagnie = get_object_or_404(CompagnieConteneur, pk=pk)
    if request.method == "POST":
        compagnie.delete()
        return redirect('compagnie_list')
    return render(request, "transport/compagnie_confirm_delete.html", {"compagnie": compagnie, "title": "Supprimer la compagnie"})

# Liste des conteneurs
def conteneur_list(request):
    conteneurs = Conteneur.objects.all().order_by('numero_conteneur')
    return render(request, "transport/conteneur_list.html", {"conteneurs": conteneurs, "title": "Liste des conteneurs"})

# Création d'un conteneur
def create_conteneur(request):
    if request.method == "POST":
        form = ConteneurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('conteneur_list')
    else:
        form = ConteneurForm()
    return render(request, "transport/conteneur_form.html", {"form": form, "title": "Ajouter un conteneur"})

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
    return render(request, "transport/conteneur_form.html", {"form": form, "title": "Modifier le conteneur"})

# Suppression d'un conteneur
def delete_conteneur(request, pk):
    conteneur = get_object_or_404(Conteneur, pk=pk)
    if request.method == "POST":
        conteneur.delete()
        return redirect('conteneur_list')
    return render(request, "transport/conteneur_confirm_delete.html", {"conteneur": conteneur, "title": "Supprimer le conteneur"})

# Liste des contrats
def contrat_list(request):
    contrats = ContratTransport.objects.all().order_by('-date_debut')
    return render(request, "transport/contrat_list.html", {"contrats": contrats, "title": "Liste des contrats"})

# Création d'un contrat
def create_contrat(request):
    if request.method == "POST":
        form = ContratTransportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contrat_list')
    else:
        form = ContratTransportForm()
    return render(request, "transport/contrat_form.html", {"form": form, "title": "Ajouter un contrat"})

# Modification d'un contrat
def update_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk=pk)
    if request.method == "POST":
        form = ContratTransportForm(request.POST, instance=contrat)
        if form.is_valid():
            form.save()
            return redirect('contrat_list')
    else:
        form = ContratTransportForm(instance=contrat)
    return render(request, "transport/contrat_form.html", {"form": form, "title": "Modifier le contrat"})

# Suppression d'un contrat
def delete_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk=pk)
    if request.method == "POST":
        contrat.delete()
        return redirect('contrat_list')
    return render(request, "transport/contrat_confirm_delete.html", {"contrat": contrat, "title": "Supprimer le contrat"})

# Liste
def presta_transport_list(request):
    prestations = PrestationDeTransports.objects.all()
    return render(request, "transport/prestation_transport_list.html", {"prestations": prestations, "title": "Prestations de transport"})

# Création
def create_presta_transport(request):
    if request.method == 'POST':
        form = PrestationDeTransportsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('presta_transport_list')
    else:
        form = PrestationDeTransportsForm()
    return render(request, "transport/prestation_transport_form.html", {"form": form, "title": "Ajouter une prestation"})

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
    return render(request, "transport/prestation_transport_form.html", {"form": form, "title": "Modifier la prestation"})

# Suppression
def delete_presta_transport(request, pk):
    prestation = get_object_or_404(PrestationDeTransports, pk=pk)
    if request.method == 'POST':
        prestation.delete()
        return redirect('presta_transport_list')
    return render(request, "transport/prestation_transport_confirm_delete.html", {"prestation": prestation})

# Liste des cautions
def cautions_list(request):
    cautions = Cautions.objects.all()
    return render(request, "transport/cautions_list.html", {"cautions": cautions, "title": "Liste des cautions"})

# Création
def create_caution(request):
    if request.method == "POST":
        form = CautionsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cautions_list')
    else:
        form = CautionsForm()
    return render(request, "transport/caution_form.html", {"form": form, "title": "Ajouter une caution"})

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
    return render(request, "transport/caution_form.html", {"form": form, "title": "Modifier une caution"})


# Suppression
def delete_caution(request, pk):
    caution = get_object_or_404(Cautions, pk=pk)
    if request.method == "POST":
        caution.delete()
        return redirect('cautions_list')
    return render(request, "transport/caution_confirm_delete.html", {"caution": caution})



def frais_list(request):
    frais = FraisTrajet.objects.all()
    return render(request, 'transport/frais_list.html', {'frais': frais, 'title': 'Liste des frais de trajet'})


def create_frais(request):
    form = FraisTrajetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('frais_list')
    return render(request, 'transport/frais_form.html', {'form': form, 'title': 'Ajouter un frais de trajet'})

def update_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    form = FraisTrajetForm(request.POST or None, instance=frais)
    if form.is_valid():
        form.save()
        return redirect('frais_list')
    return render(request, 'transport/frais_form.html', {'form': form, 'title': 'Modifier le frais de trajet'})

def delete_frais(request, pk):
    frais = get_object_or_404(FraisTrajet, pk=pk)
    if request.method == 'POST':
        frais.delete()
        return redirect('frais_list')
    return render(request, 'transport/frais_confirm_delete.html', {'frais': frais, 'title': 'Supprimer le frais de trajet'})


# Liste des missions
def mission_list(request):
    missions = Mission.objects.all()
    return render(request, 'transport/mission_list.html', {
        'missions': missions,
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
    return render(request, 'transport/mission_form.html', {'form': form, 'title': 'Créer une mission'})

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
    return render(request, 'transport/mission_form.html', {'form': form, 'title': 'Modifier une mission'})

# Supprimer une mission
def delete_mission(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)
    if request.method == 'POST':
        mission.delete()
        return redirect('mission_list')
    return render(request, 'transport/confirm_delete.html', {'object': mission, 'title': 'Supprimer une mission'})

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
