"""
Contrat Views.Py

Vues pour contrat
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (ContratTransport, PrestationDeTransports, Conteneur, Camion, Chauffeur)
from ..forms import (ContratTransportForm, PrestationDeTransportsForm)
from ..decorators import (can_delete_data)


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

