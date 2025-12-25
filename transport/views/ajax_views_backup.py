"""
Ajax Views.Py

Vues AJAX complètes pour tous les modules
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from ..models import (
    Chauffeur, Camion, Affectation, Client, Conteneur, ContratTransport,
    PrestationDeTransports, Entreprise, AuditLog
)


# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

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


# ============================================================================
# CONTENEURS - AJAX CRUD OPERATIONS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_conteneur_create(request):
    """Créer un conteneur via AJAX"""
    from ..forms.vehicle_forms import ConteneurForm

    if request.method == 'GET':
        form = ConteneurForm()
        html = render_to_string(
            'transport/conteneurs/partials/conteneur_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = ConteneurForm(request.POST)
        if form.is_valid():
            conteneur = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action=f"Création conteneur AJAX",
                details=f"Conteneur: {conteneur.numero_conteneur}"
            )

            return JsonResponse({
                'success': True,
                'message': f'Conteneur "{conteneur.numero_conteneur}" créé avec succès'
            })
        else:
            html = render_to_string(
                'transport/conteneurs/partials/conteneur_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_conteneur_update(request, pk):
    """Modifier un conteneur via AJAX"""
    from ..forms.vehicle_forms import ConteneurForm

    try:
        conteneur = get_object_or_404(Conteneur, pk_conteneur=pk)

        if request.method == 'GET':
            form = ConteneurForm(instance=conteneur)
            html = render_to_string(
                'transport/conteneurs/partials/conteneur_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'conteneur': conteneur
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = ConteneurForm(request.POST, instance=conteneur)
        if form.is_valid():
            conteneur = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action=f"Modification conteneur AJAX",
                details=f"Conteneur: {conteneur.numero_conteneur}"
            )

            return JsonResponse({
                'success': True,
                'message': f'Conteneur "{conteneur.numero_conteneur}" modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/conteneurs/partials/conteneur_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'conteneur': conteneur
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': form.errors
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }, status=500)


# ============================================================================
# CONTRATS - AJAX CRUD OPERATIONS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_contrat_create(request):
    """Créer un contrat de transport via AJAX"""
    from ..forms.contrat_forms import ContratTransportForm

    if request.method == 'GET':
        form = ContratTransportForm()
        html = render_to_string(
            'transport/contrat/partials/contrat_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = ContratTransportForm(request.POST)
        if form.is_valid():
            contrat = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action=f"Création contrat AJAX",
                details=f"Contrat: {contrat.numero_bl}"
            )

            return JsonResponse({
                'success': True,
                'message': f'Contrat "{contrat.numero_bl}" créé avec succès'
            })
        else:
            html = render_to_string(
                'transport/contrat/partials/contrat_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_contrat_update(request, pk):
    """Modifier un contrat de transport via AJAX"""
    from ..forms.contrat_forms import ContratTransportForm

    try:
        contrat = get_object_or_404(ContratTransport, pk_contrat=pk)

        if request.method == 'GET':
            form = ContratTransportForm(instance=contrat)
            html = render_to_string(
                'transport/contrat/partials/contrat_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'contrat': contrat
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = ContratTransportForm(request.POST, instance=contrat)
        if form.is_valid():
            contrat = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action=f"Modification contrat AJAX",
                details=f"Contrat: {contrat.numero_bl}"
            )

            return JsonResponse({
                'success': True,
                'message': f'Contrat "{contrat.numero_bl}" modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/contrat/partials/contrat_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'contrat': contrat
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': form.errors
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }, status=500)


# ============================================================================
# PRESTATIONS - AJAX CRUD OPERATIONS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_prestation_create(request):
    """Créer une prestation de transport via AJAX"""
    from ..forms.contrat_forms import PrestationDeTransportsForm

    if request.method == 'GET':
        form = PrestationDeTransportsForm()
        html = render_to_string(
            'transport/prestations/partials/prestation_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = PrestationDeTransportsForm(request.POST)
        if form.is_valid():
            prestation = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action=f"Création prestation AJAX",
                details=f"Prestation pour {prestation.client.nom}"
            )

            return JsonResponse({
                'success': True,
                'message': f'Prestation créée avec succès'
            })
        else:
            html = render_to_string(
                'transport/prestations/partials/prestation_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_prestation_update(request, pk):
    """Modifier une prestation de transport via AJAX"""
    from ..forms.contrat_forms import PrestationDeTransportsForm

    try:
        prestation = get_object_or_404(PrestationDeTransports, pk_presta_transport=pk)

        if request.method == 'GET':
            form = PrestationDeTransportsForm(instance=prestation)
            html = render_to_string(
                'transport/prestations/partials/prestation_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'prestation': prestation
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = PrestationDeTransportsForm(request.POST, instance=prestation)
        if form.is_valid():
            prestation = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action=f"Modification prestation AJAX",
                details=f"Prestation pour {prestation.client.nom}"
            )

            return JsonResponse({
                'success': True,
                'message': f'Prestation modifiée avec succès'
            })
        else:
            html = render_to_string(
                'transport/prestations/partials/prestation_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'prestation': prestation
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': form.errors
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }, status=500)
