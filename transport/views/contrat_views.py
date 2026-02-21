"""
Contrat Views.Py

Vues pour contrat
"""

import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.conf import settings

from ..models import (ContratTransport, PrestationDeTransports, Conteneur, AuditLog)
from ..forms import (ContratTransportForm, PrestationDeTransportsForm)
from ..decorators import (can_delete_data)
from utils.generate_contrat_pdf import generate_pdf_contrat

logger = logging.getLogger('transport')



@login_required
def contrat_list(request):
    contrats = ContratTransport.objects.select_related(
        'conteneur', 'client', 'transitaire', 'entreprise', 'camion', 'chauffeur'
    ).order_by('-date_debut')
    return render(request, "transport/contrat/contrat_list.html", {"contrats": contrats, "title": "Liste des contrats"})

# Création d'un contrat

@login_required
def create_contrat(request):
    if request.method == "POST":
        form = ContratTransportForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verrouiller le camion et le chauffeur pour éviter la race condition
                    camion_choisi = form.cleaned_data['camion']
                    chauffeur_choisi = form.cleaned_data['chauffeur']

                    from ..models import Camion, Chauffeur, Mission
                    Camion.objects.select_for_update().get(pk_camion=camion_choisi.pk_camion)
                    Chauffeur.objects.select_for_update().get(pk_chauffeur=chauffeur_choisi.pk_chauffeur)

                    # Re-vérifier la disponibilité après verrouillage
                    if Mission.objects.filter(contrat__camion=camion_choisi, statut='en cours').exists():
                        form.add_error('camion', 'Ce camion vient d\'être affecté à une mission. Veuillez en choisir un autre.')
                        raise ValueError('camion_indisponible')
                    if Mission.objects.filter(contrat__chauffeur=chauffeur_choisi, statut='en cours').exists():
                        form.add_error('chauffeur', 'Ce chauffeur vient d\'être affecté à une mission. Veuillez en choisir un autre.')
                        raise ValueError('chauffeur_indisponible')

                    # 1. Sauvegarde du contrat dans la base
                    contrat = form.save()

                    # 2. Définition du chemin final du PDF
                    folder = os.path.join(settings.MEDIA_ROOT, "contrats")
                    os.makedirs(folder, exist_ok=True)

                    pdf_filename = f"{contrat.pk_contrat}.pdf"
                    pdf_path = os.path.join(folder, pdf_filename)

                    # 3. Génération du PDF
                    generate_pdf_contrat(contrat, pdf_path)

                    # 4. Enregistrement du PDF dans le modèle
                    contrat.pdf_file = f"contrats/{pdf_filename}"
                    contrat.save()

                    # 5. Audit log
                    AuditLog.objects.create(
                        utilisateur=request.user,
                        action='CREATE',
                        model_name='ContratTransport',
                        object_id=contrat.pk_contrat,
                        object_repr=f"Contrat {contrat.numero_bl}",
                        changes={'numero_bl': contrat.numero_bl}
                    )

                logger.info(f"Contrat {contrat.numero_bl} créé par {request.user.email}")
                messages.success(request, "Contrat créé avec succès!")
                return redirect("contrat_list")

            except IntegrityError:
                logger.warning(f"Tentative de création contrat avec BL dupliqué: {form.cleaned_data.get('numero_bl')}")
                messages.error(request, f"Erreur: Le numéro BL '{form.cleaned_data.get('numero_bl')}' existe déjà.")
            except Exception as e:
                logger.error(f"Erreur création contrat: {e}", exc_info=True)
                messages.error(request, f"Erreur lors de la création du contrat: {str(e)}")
        else:
            for _, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

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
                with transaction.atomic():
                    # Verrouiller le camion et le chauffeur pour éviter la race condition
                    camion_choisi = form.cleaned_data['camion']
                    chauffeur_choisi = form.cleaned_data['chauffeur']

                    from ..models import Camion, Chauffeur, Mission
                    Camion.objects.select_for_update().get(pk_camion=camion_choisi.pk_camion)
                    Chauffeur.objects.select_for_update().get(pk_chauffeur=chauffeur_choisi.pk_chauffeur)

                    # Re-vérifier la disponibilité après verrouillage (en excluant le contrat en cours d'édition)
                    if Mission.objects.filter(contrat__camion=camion_choisi, statut='en cours').exclude(contrat=contrat).exists():
                        form.add_error('camion', 'Ce camion vient d\'être affecté à une mission. Veuillez en choisir un autre.')
                        raise ValueError('camion_indisponible')
                    if Mission.objects.filter(contrat__chauffeur=chauffeur_choisi, statut='en cours').exclude(contrat=contrat).exists():
                        form.add_error('chauffeur', 'Ce chauffeur vient d\'être affecté à une mission. Veuillez en choisir un autre.')
                        raise ValueError('chauffeur_indisponible')

                    contrat = form.save()

                    # Audit log
                    AuditLog.objects.create(
                        utilisateur=request.user,
                        action='UPDATE',
                        model_name='ContratTransport',
                        object_id=contrat.pk_contrat,
                        object_repr=f"Contrat {contrat.numero_bl}",
                        changes={}
                    )

                logger.info(f"Contrat {contrat.numero_bl} modifié par {request.user.email}")
                messages.success(request, "Contrat mis à jour avec succès!")
                return redirect('contrat_list')
            except IntegrityError:
                logger.warning(f"Tentative de modification contrat avec BL dupliqué: {form.cleaned_data.get('numero_bl')}")
                messages.error(request, f"Erreur: Le numéro BL '{form.cleaned_data.get('numero_bl')}' existe déjà.")
            except Exception as e:
                logger.error(f"Erreur modification contrat {pk}: {e}", exc_info=True)
                messages.error(request, f"Erreur lors de la modification: {str(e)}")
        else:
            for _, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ContratTransportForm(instance=contrat)
    return render(request, "transport/contrat/contrat_form.html", {"form": form, "title": "Modifier le contrat"})

# Suppression d'un contrat

@can_delete_data
def delete_contrat(request, pk):
    from ..models import Mission, Cautions

    contrat = get_object_or_404(ContratTransport, pk=pk)

    if request.method == "POST":
        # Vérifier si le contrat a des missions
        nb_missions = Mission.objects.filter(contrat=contrat).count()

        if nb_missions > 0:
            messages.error(
                request,
                f"❌ Impossible de supprimer ce contrat! "
                f"Il a {nb_missions} mission(s) associée(s). "
                f"Utilisez plutôt l'annulation pour garder la traçabilité. "
                f"(Voir la documentation ANALYSE_ANNULATION_CONTRAT.md)"
            )
            return redirect('contrat_list')

        # Vérifier si le contrat a des cautions
        nb_cautions = Cautions.objects.filter(contrat=contrat).count()

        if nb_cautions > 0:
            messages.error(
                request,
                f"❌ Impossible de supprimer ce contrat! "
                f"Il a {nb_cautions} caution(s) associée(s). "
                f"Utilisez plutôt l'annulation pour garder la traçabilité."
            )
            return redirect('contrat_list')

        # Si aucune donnée associée, autoriser la suppression
        contrat.delete()
        messages.success(request, "✅ Contrat supprimé avec succès (aucune donnée associée)")
        return redirect('contrat_list')

    # Afficher les avertissements lors de l'affichage du formulaire
    nb_missions = Mission.objects.filter(contrat=contrat).count()
    nb_cautions = Cautions.objects.filter(contrat=contrat).count()

    if nb_missions > 0 or nb_cautions > 0:
        messages.warning(
            request,
            f"⚠️ Attention: Ce contrat a {nb_missions} mission(s) et {nb_cautions} caution(s). "
            f"La suppression sera BLOQUÉE. Utilisez l'annulation à la place."
        )

    return render(request, "transport/contrat/contrat_confirm_delete.html", {"contrat": contrat, "title": "Supprimer le contrat"})


# API: Récupérer le chauffeur affecté à un camion

@login_required
def presta_transport_list(request):
    prestations = PrestationDeTransports.objects.select_related(
        'contrat_transport', 'camion', 'client', 'transitaire'
    ).order_by('-date')
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

# API: Récupérer le client et le transitaire d'un conteneur

@login_required
def get_conteneur_info(request, conteneur_id):
    """
    API pour récupérer automatiquement le client et le transitaire
    associés à un conteneur sélectionné
    """
    try:
        conteneur = Conteneur.objects.get(pk_conteneur=conteneur_id)
        return JsonResponse({
            'success': True,
            'client_id': conteneur.client.pk_client if conteneur.client else None,
            'client_nom': conteneur.client.nom if conteneur.client else None,
            'transitaire_id': conteneur.transitaire.pk_transitaire if conteneur.transitaire else None,
            'transitaire_nom': conteneur.transitaire.nom if conteneur.transitaire else None,
        })
    except Conteneur.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Conteneur non trouvé'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Liste des cautions

