"""
Ajax Views.Py

Vues AJAX complètes pour tous les modules
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Sum, F
from django.http import JsonResponse, QueryDict
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.urls import reverse

logger = logging.getLogger('transport')

from ..models import (
    Chauffeur, Camion, Affectation, Client, Conteneur, ContratTransport,
    PrestationDeTransports, Entreprise, AuditLog, Mission, PaiementMission,
    Notification, Reparation, Transitaire, CompagnieConteneur, Fournisseur
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_request_data(request):
    """
    Helper pour extraire les données POST d'une requête AJAX.
    Supporte à la fois application/json et application/x-www-form-urlencoded
    Convertit les données JSON en QueryDict pour compatibilité Django Forms
    """
    content_type = request.content_type or ''

    logger.debug(f"get_request_data - Content-Type: {content_type}")

    # Vérifier si c'est du JSON
    if 'application/json' in content_type:
        # On ne log la taille du body que pour JSON (pour multipart, request.body
        # lèverait RawPostDataException si request.POST a déjà été accédé par le
        # middleware CSRF)
        logger.debug(f"get_request_data - Body length: {len(request.body) if request.body else 0}")
        try:
            # Tenter de parser le body en JSON
            if request.body:
                json_data = json.loads(request.body)
                logger.debug(f"get_request_data - JSON data keys: {list(json_data.keys())}")

                # Convertir en QueryDict pour compatibilité Django Forms
                query_dict = QueryDict('', mutable=True)
                for key, value in json_data.items():
                    # Ignorer le token CSRF (géré par header)
                    if key == 'csrfmiddlewaretoken':
                        continue
                    # Convertir les valeurs en string pour Django Forms
                    if value is None:
                        query_dict[key] = ''
                    elif isinstance(value, bool):
                        # Les checkboxes HTML n'envoient rien quand non cochées.
                        # Django BooleanField attend 'on' pour True, absence pour False.
                        if value:
                            query_dict[key] = 'on'
                        # Pour False : ne pas ajouter la clé (comportement HTML natif)
                    elif isinstance(value, (list, tuple)):
                        # Pour les champs multi-valeurs
                        for v in value:
                            query_dict.appendlist(key, str(v) if v is not None else '')
                    else:
                        query_dict[key] = str(value)

                logger.debug(f"get_request_data - QueryDict: {dict(query_dict)}")
                return query_dict
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Erreur parsing JSON: {e}")
            pass

    # Sinon retourner request.POST
    logger.debug(f"get_request_data - Using request.POST: {dict(request.POST)}")
    return request.POST


def get_form_errors_json(form):
    """
    Convertit les erreurs de formulaire Django en format JSON sérialisable.
    """
    errors = {}
    for field, error_list in form.errors.items():
        errors[field] = [str(e) for e in error_list]
    return errors


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
        form = ConteneurForm(get_request_data(request))
        if form.is_valid():
            conteneur = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Conteneur',
                object_id=conteneur.pk_conteneur,
                object_repr=str(conteneur),
                changes={}
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
                'errors': get_form_errors_json(form)
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
        form = ConteneurForm(get_request_data(request), instance=conteneur)
        if form.is_valid():
            conteneur = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Conteneur',
                object_id=conteneur.pk_conteneur,
                object_repr=str(conteneur),
                changes={}
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
                'errors': get_form_errors_json(form)
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
        data = get_request_data(request)
        form = ContratTransportForm(data)

        if form.is_valid():
            with transaction.atomic():
                contrat = form.save()

                # Log
                AuditLog.objects.create(
                    utilisateur=request.user,
                    action='CREATE',
                    model_name='ContratTransport',
                    object_id=contrat.pk_contrat,
                    object_repr=str(contrat),
                    changes={}
                )

            logger.info(f"Contrat {contrat.numero_bl} créé par {request.user.email}")
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
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        logger.error(f"Erreur création contrat: {e}", exc_info=True)
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
        form = ContratTransportForm(get_request_data(request), instance=contrat)
        if form.is_valid():
            contrat = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='ContratTransport',
                object_id=contrat.pk_contrat,
                object_repr=str(contrat),
                changes={}
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
                'errors': get_form_errors_json(form)
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
        form = PrestationDeTransportsForm(get_request_data(request))
        if form.is_valid():
            prestation = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='PrestationDeTransports',
                object_id=prestation.pk_prestation,
                object_repr=str(prestation),
                changes={}
            )

            # Redirection vers la page de modification du contrat
            redirect_url = reverse('update_contrat', kwargs={'pk': prestation.contrat_transport.pk_contrat})

            return JsonResponse({
                'success': True,
                'message': f'Prestation créée avec succès',
                'redirect_url': redirect_url
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
                'errors': get_form_errors_json(form)
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
        form = PrestationDeTransportsForm(get_request_data(request), instance=prestation)
        if form.is_valid():
            prestation = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='PrestationDeTransports',
                object_id=prestation.pk_prestation,
                object_repr=str(prestation),
                changes={}
            )

            # Redirection vers la page de modification du contrat
            redirect_url = reverse('update_contrat', kwargs={'pk': prestation.contrat_transport.pk_contrat})

            return JsonResponse({
                'success': True,
                'message': f'Prestation modifiée avec succès',
                'redirect_url': redirect_url
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
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }, status=500)


# ============================================================================
# CLIENTS - AJAX CRUD OPERATIONS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_client_create(request):
    """Créer un client via AJAX"""
    from ..forms.commercial_forms import ClientForm

    logger.info(f"ajax_client_create - Method: {request.method}")

    if request.method == 'GET':
        form = ClientForm()
        html = render_to_string(
            'transport/clients/partials/client_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        request_data = get_request_data(request)
        logger.info(f"ajax_client_create - Request data: {dict(request_data)}")

        form = ClientForm(request_data)
        logger.info(f"ajax_client_create - Form valid: {form.is_valid()}")

        if form.is_valid():
            client = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Client',
                object_id=client.pk_client,
                object_repr=str(client),
                changes={}
            )

            logger.info(f"ajax_client_create - Client created: {client.pk_client}")
            return JsonResponse({
                'success': True,
                'message': f'Client "{client.nom}" créé avec succès'
            })
        else:
            logger.warning(f"ajax_client_create - Form errors: {form.errors}")
            html = render_to_string(
                'transport/clients/partials/client_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        logger.error(f"ajax_client_create - Exception: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_client_update(request, pk):
    """Modifier un client via AJAX"""
    from ..forms.commercial_forms import ClientForm

    try:
        client = get_object_or_404(Client, pk_client=pk)

        if request.method == 'GET':
            form = ClientForm(instance=client)
            html = render_to_string(
                'transport/clients/partials/client_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'client': client
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = ClientForm(get_request_data(request), instance=client)
        if form.is_valid():
            client = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Client',
                object_id=client.pk_client,
                object_repr=str(client),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Client "{client.nom}" modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/clients/partials/client_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'client': client
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }, status=500)


@login_required
def ajax_search_clients(request):
    """Recherche AJAX pour les clients"""
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    clients = Client.objects.filter(
        Q(nom__icontains=query) | Q(telephone__icontains=query)
    )[:10]

    results = [{'id': c.pk_client, 'text': f"{c.nom} - {c.telephone}"} for c in clients]
    return JsonResponse({'results': results})

# ============================================================================
# CHAUFFEURS - AJAX CRUD OPERATIONS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_chauffeur_create(request):
    """Créer un chauffeur via AJAX"""
    from ..forms.personnel_forms import ChauffeurForm

    if request.method == 'GET':
        form = ChauffeurForm()
        html = render_to_string(
            'transport/chauffeurs/partials/chauffeur_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = ChauffeurForm(get_request_data(request))
        if form.is_valid():
            chauffeur = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Chauffeur',
                object_id=chauffeur.pk_chauffeur,
                object_repr=str(chauffeur),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Chauffeur "{chauffeur.nom} {chauffeur.prenom}" créé avec succès'
            })
        else:
            html = render_to_string(
                'transport/chauffeurs/partials/chauffeur_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_chauffeur_update(request, pk):
    """Modifier un chauffeur via AJAX"""
    from ..forms.personnel_forms import ChauffeurForm

    try:
        chauffeur = get_object_or_404(Chauffeur, pk_chauffeur=pk)

        if request.method == 'GET':
            form = ChauffeurForm(instance=chauffeur)
            html = render_to_string(
                'transport/chauffeurs/partials/chauffeur_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'chauffeur': chauffeur
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = ChauffeurForm(get_request_data(request), instance=chauffeur)
        if form.is_valid():
            chauffeur = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Chauffeur',
                object_id=chauffeur.pk_chauffeur,
                object_repr=str(chauffeur),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Chauffeur "{chauffeur.nom} {chauffeur.prenom}" modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/chauffeurs/partials/chauffeur_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'chauffeur': chauffeur
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs du formulaire',
                'html': html,
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }, status=500)


@login_required
def ajax_search_chauffeurs(request):
    """Recherche AJAX pour les chauffeurs"""
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    chauffeurs = Chauffeur.objects.filter(
        Q(nom__icontains=query) | Q(prenom__icontains=query)
    )[:10]

    results = [{'id': c.pk_chauffeur, 'text': f"{c.nom} {c.prenom}"} for c in chauffeurs]
    return JsonResponse({'results': results})

@login_required
@require_http_methods(["GET", "POST"])
def ajax_camion_create(request):
    """Créer un camion via AJAX"""
    from ..forms.vehicle_forms import CamionForm

    if request.method == 'GET':
        form = CamionForm()
        html = render_to_string(
            'transport/camions/partials/camion_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = CamionForm(get_request_data(request))
        if form.is_valid():
            camion = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Camion',
                object_id=camion.pk_camion,
                object_repr=str(camion),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Camion "{camion.immatriculation}" créé avec succès'
            })
        else:
            html = render_to_string(
                'transport/camions/partials/camion_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_camion_update(request, pk):
    """Modifier un camion via AJAX"""
    from ..forms.vehicle_forms import CamionForm

    try:
        camion = get_object_or_404(Camion, pk_camion=pk)

        if request.method == 'GET':
            form = CamionForm(instance=camion)
            html = render_to_string(
                'transport/camions/partials/camion_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'camion': camion
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = CamionForm(get_request_data(request), instance=camion)
        if form.is_valid():
            camion = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Camion',
                object_id=camion.pk_camion,
                object_repr=str(camion),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Camion "{camion.immatriculation}" modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/camions/partials/camion_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'camion': camion
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_mission_create(request):
    """Créer une mission via AJAX"""
    from ..forms.mission_forms import MissionForm

    if request.method == 'GET':
        form = MissionForm()
        html = render_to_string(
            'transport/missions/partials/mission_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = MissionForm(get_request_data(request))
        if form.is_valid():
            with transaction.atomic():
                mission = form.save()
                AuditLog.objects.create(
                    utilisateur=request.user,
                    action='CREATE',
                    model_name='Mission',
                    object_id=mission.pk_mission,
                    object_repr=str(mission),
                    changes={}
                )

            # Redirection vers la page de modification du contrat
            redirect_url = reverse('update_contrat', kwargs={'pk': mission.contrat.pk_contrat})

            logger.info(f"Mission {mission.pk_mission} créée par {request.user.email}")
            return JsonResponse({
                'success': True,
                'message': 'Mission créée avec succès',
                'redirect_url': redirect_url
            })
        else:
            html = render_to_string(
                'transport/missions/partials/mission_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        logger.error(f"Erreur création mission: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_mission_update(request, pk):
    """Modifier une mission via AJAX"""
    from ..forms.mission_forms import MissionForm

    try:
        mission = get_object_or_404(Mission, pk_mission=pk)

        if request.method == 'GET':
            form = MissionForm(instance=mission)
            html = render_to_string(
                'transport/missions/partials/mission_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'mission': mission
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = MissionForm(get_request_data(request), instance=mission)
        if form.is_valid():
            mission = form.save()

            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Mission',
                object_id=mission.pk_mission,
                object_repr=str(mission),
                changes={}
            )

            # Redirection vers la page de modification du contrat
            redirect_url = reverse('update_contrat', kwargs={'pk': mission.contrat.pk_contrat})

            return JsonResponse({
                'success': True,
                'message': 'Mission modifiée avec succès',
                'redirect_url': redirect_url
            })
        else:
            html = render_to_string(
                'transport/missions/partials/mission_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'mission': mission
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def ajax_terminer_mission_modal_content(request, pk):
    """Contenu du modal pour terminer une mission via AJAX"""
    from django.utils import timezone
    try:
        mission = get_object_or_404(Mission, pk_mission=pk)

        # Date de retour par défaut = aujourd'hui
        date_retour = timezone.now().date()

        # Calculer si en retard
        en_retard = False
        info_penalite = None
        date_limite = None

        if mission.contrat and mission.contrat.date_limite_retour:
            date_limite = mission.contrat.date_limite_retour
            if date_retour > date_limite:
                en_retard = True
                jours_retard = (date_retour - date_limite).days
                penalite = jours_retard * 25000
                info_penalite = {
                    'jours_retard': jours_retard,
                    'penalite': penalite,
                    'date_limite': date_limite
                }

        # Récupérer le paiement associé
        paiement = mission.paiement_mission.first() if hasattr(mission, 'paiement_mission') else None

        html = render_to_string(
            'transport/missions/partials/terminer_mission_modal_content.html',
            {
                'mission': mission,
                'en_retard': en_retard,
                'info_penalite': info_penalite,
                'paiement': paiement,
                'date_retour': date_retour.strftime('%Y-%m-%d'),
                'date_limite': date_limite.strftime('%Y-%m-%d') if date_limite else None
            },
            request=request
        )
        return JsonResponse({'success': True, 'html': html})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def ajax_terminer_mission(request, pk):
    """Terminer une mission via AJAX"""
    from django.utils import timezone
    from datetime import datetime

    try:
        mission = get_object_or_404(Mission, pk_mission=pk)

        # Vérifier que la mission n'est pas déjà terminée ou annulée
        if mission.statut == 'terminée':
            return JsonResponse({
                'success': False,
                'message': 'Cette mission est déjà terminée.'
            })

        if mission.statut == 'annulée':
            return JsonResponse({
                'success': False,
                'message': 'Cette mission est annulée. Impossible de la terminer.'
            })

        # Récupérer les données
        data = get_request_data(request)

        # Récupérer la date de retour
        date_retour_str = data.get('date_retour')
        if date_retour_str:
            try:
                date_retour = datetime.strptime(date_retour_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                date_retour = timezone.now().date()
        else:
            date_retour = timezone.now().date()

        # Récupérer le flag force
        force = data.get('force') == '1'

        with transaction.atomic():
            # Ajuster la date de départ si nécessaire
            if date_retour < mission.date_depart:
                mission.date_depart = date_retour
                mission.save()

            # Terminer la mission
            result = mission.terminer_mission(date_retour=date_retour, force=force)

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='TERMINER_MISSION',
                model_name='Mission',
                object_id=mission.pk_mission,
                object_repr=str(mission),
                changes={'date_retour': str(date_retour), 'force': force}
            )

        logger.info(f"Mission {mission.pk_mission} terminée par {request.user.email}")
        return JsonResponse({
            'success': True,
            'message': 'Mission terminée avec succès',
            'result': result
        })

    except Exception as e:
        logger.error(f"Erreur terminaison mission {pk}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def ajax_filter_paiements(request):
    """Filtrer les paiements via AJAX"""
    from ..filters import PaiementMissionFilter
    try:
        # Récupérer tous les paiements avec relations
        paiements = PaiementMission.objects.select_related(
            'mission', 'caution', 'prestation',
            'mission__contrat__chauffeur', 'mission__contrat__client'
        ).order_by('-date_paiement')

        # Appliquer les filtres
        paiements = PaiementMissionFilter.apply(paiements, request)

        # Render le template partial avec les lignes de paiements
        html = render_to_string(
            'transport/paiements-mission/partials/paiement_rows.html',
            {'paiements': paiements},
            request=request
        )

        # Compter les paiements validés et en attente
        paiements_valides = paiements.filter(est_valide=True).count()
        paiements_attente = paiements.filter(est_valide=False).count()

        return JsonResponse({
            'success': True,
            'html': html,
            'count': paiements.count(),
            'paiements_valides': paiements_valides,
            'paiements_attente': paiements_attente
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def ajax_validation_modal_content(request, pk):
    """Contenu du modal de validation de paiement via AJAX"""
    try:
        paiement = get_object_or_404(PaiementMission, pk_paiement=pk)

        # Vérifier le statut de la mission
        mission_terminee = paiement.mission.statut == 'terminée'

        # Vérifier l'état de la caution
        caution = paiement.caution
        caution_ok = True  # Par défaut OK si pas de caution

        if caution:
            # Caution OK si remboursée ou consommée
            caution_ok = caution.statut in ['remboursee', 'consommee']

        # Peut valider seulement si mission terminée ET caution ok
        can_validate = mission_terminee and caution_ok

        html = render_to_string(
            'transport/paiements-mission/partials/validation_modal_content.html',
            {
                'paiement': paiement,
                'mission_terminee': mission_terminee,
                'caution': caution,
                'caution_ok': caution_ok,
                'can_validate': can_validate
            },
            request=request
        )
        return JsonResponse({'success': True, 'html': html})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def ajax_validate_paiement(request, pk):
    """Valider un paiement via AJAX"""
    try:
        paiement = get_object_or_404(PaiementMission, pk_paiement=pk)

        # Vérifier que le paiement n'est pas déjà validé
        if paiement.est_valide:
            return JsonResponse({
                'success': False,
                'message': 'Ce paiement a déjà été validé.'
            })

        # Vérifier le statut de la mission
        if paiement.mission.statut != 'terminée':
            return JsonResponse({
                'success': False,
                'message': f"Impossible de valider! La mission est '{paiement.mission.statut}'. Terminez d'abord la mission."
            })

        # Vérifier l'état de la caution
        if paiement.caution:
            if paiement.caution.statut not in ['remboursee', 'consommee']:
                return JsonResponse({
                    'success': False,
                    'message': f"Impossible de valider! La caution de {paiement.caution.montant} FCFA n'a pas été remboursée."
                })

        with transaction.atomic():
            # Valider le paiement
            paiement.valider_paiement()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='VALIDER_PAIEMENT',
                model_name='PaiementMission',
                object_id=paiement.pk_paiement,
                object_repr=str(paiement),
                changes={'montant_total': str(paiement.montant_total)}
            )

        logger.info(f"Paiement {paiement.pk_paiement} validé par {request.user.email}")
        return JsonResponse({
            'success': True,
            'message': f'Paiement de {paiement.montant_total} FCFA validé avec succès'
        })

    except Exception as e:
        logger.error(f"Erreur validation paiement {pk}: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def ajax_dashboard_filter(request):
    """Filtrer le dashboard via AJAX"""
    from datetime import datetime
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncMonth
    from django.utils import timezone

    try:
        # Récupération des filtres de date
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

        # Application des filtres
        missions_qs = Mission.objects.all()
        if date_debut:
            missions_qs = missions_qs.filter(date_depart__gte=date_debut)
        if date_fin:
            missions_qs = missions_qs.filter(date_depart__lte=date_fin)

        paiements_qs = PaiementMission.objects.all()
        if date_debut:
            paiements_qs = paiements_qs.filter(date_paiement__gte=date_debut)
        if date_fin:
            paiements_qs = paiements_qs.filter(date_paiement__lte=date_fin)

        reparations_qs = Reparation.objects.all()
        if date_debut:
            reparations_qs = reparations_qs.filter(date_reparation__gte=date_debut)
        if date_fin:
            reparations_qs = reparations_qs.filter(date_reparation__lte=date_fin)

        # Statistiques
        stats = {
            "chauffeurs": Chauffeur.objects.count(),
            "camions": Camion.objects.count(),
            "missions": missions_qs.count(),
            "missions_en_cours": missions_qs.filter(statut="en cours").count(),
            "missions_terminees": missions_qs.filter(statut="terminée").count(),
            "reparations": reparations_qs.count(),
            "paiements": paiements_qs.aggregate(total=Sum("montant_total"))["total"] or 0,
            "clients": Client.objects.count(),
            "affectations": Affectation.objects.count(),
        }

        # Missions par statut
        mission_par_statut = list(missions_qs.values("statut").annotate(total=Count("statut")))

        # Paiements mensuels
        paiements_mensuels = list(
            paiements_qs
            .annotate(mois=TruncMonth("date_paiement"))
            .values("mois")
            .annotate(total=Sum("montant_total"))
            .order_by("mois")
        )

        # Calcul des revenus
        if date_debut and date_fin:
            revenus_mois_actuel = paiements_qs.aggregate(total=Sum("montant_total"))["total"] or 0
        else:
            current_month = timezone.now().month
            current_year = timezone.now().year
            revenus_mois_actuel = PaiementMission.objects.filter(
                date_paiement__month=current_month,
                date_paiement__year=current_year
            ).aggregate(total=Sum("montant_total"))["total"] or 0

        # Missions en retard
        today = timezone.now().date()
        missions_en_retard = missions_qs.filter(
            statut="en cours",
            date_retour__lt=today
        ).count() if missions_qs.filter(statut="en cours").exists() else 0

        return JsonResponse({
            'success': True,
            'stats': stats,
            'mission_par_statut': mission_par_statut,
            'paiements_mensuels': paiements_mensuels,
            'revenus_mois_actuel': float(revenus_mois_actuel),
            'missions_en_retard': missions_en_retard
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def ajax_mark_notification_read(request, pk):
    """Marquer une notification comme lue via AJAX"""
    try:
        notification = get_object_or_404(Notification, pk_notification=pk, utilisateur=request.user)
        notification.is_read = True
        notification.save()

        # Log
        AuditLog.objects.create(
            utilisateur=request.user,
            action='UPDATE',
            model_name='Notification',
            object_id=notification.pk_notification,
            object_repr=str(notification),
            changes={'lue': True}
        )

        # Compter les notifications non lues restantes
        unread_count = Notification.objects.filter(utilisateur=request.user, is_read=False).count()

        return JsonResponse({
            'success': True,
            'message': 'Notification marquée comme lue',
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def ajax_mark_all_notifications_read(request):
    """Marquer toutes les notifications comme lues via AJAX"""
    try:
        # Marquer toutes les notifications de l'utilisateur comme lues
        count = Notification.objects.filter(
            utilisateur=request.user,
            is_read=False
        ).update(is_read=True)

        # Log
        if count > 0:
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Notification',
                object_id='bulk',
                object_repr=f'{count} notifications',
                changes={'count': count, 'lue': True}
            )

        return JsonResponse({
            'success': True,
            'message': f'{count} notification(s) marquée(s) comme lue(s)' if count > 0 else 'Aucune notification non lue',
            'count': count,
            'unread_count': 0
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def ajax_get_notifications(request):
    """Récupérer les notifications via AJAX"""
    try:
        # Récupérer les notifications de l'utilisateur (max 100)
        try:
            limit = min(int(request.GET.get('limit', 10)), 100)
        except (ValueError, TypeError):
            limit = 10
        only_unread = request.GET.get('only_unread', 'false').lower() == 'true'

        notifications_qs = Notification.objects.filter(utilisateur=request.user).order_by('-created_at')

        if only_unread:
            notifications_qs = notifications_qs.filter(is_read=False)

        notifications_qs = notifications_qs[:limit]

        # Convertir en liste de dictionnaires
        from django.utils.timesince import timesince
        notifications_list = []
        for notif in notifications_qs:
            notifications_list.append({
                'pk_notification': notif.pk_notification,
                'title': notif.title,
                'message': notif.message,
                'type': notif.type_notification,
                'icon': notif.icon,
                'color': notif.color,
                'is_read': notif.is_read,
                'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'timesince': timesince(notif.created_at),
            })

        # Compter les notifications non lues
        unread_count = Notification.objects.filter(utilisateur=request.user, is_read=False).count()

        return JsonResponse({
            'success': True,
            'notifications': notifications_list,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_affectation_create(request):
    """Créer une affectation via AJAX"""
    from ..forms.personnel_forms import AffectationForm

    if request.method == 'GET':
        form = AffectationForm()
        html = render_to_string(
            'transport/affectations/partials/affectation_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = AffectationForm(get_request_data(request))
        if form.is_valid():
            affectation = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Affectation',
                object_id=affectation.pk_affectation,
                object_repr=str(affectation),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': 'Affectation créée avec succès'
            })
        else:
            html = render_to_string(
                'transport/affectations/partials/affectation_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_affectation_update(request, pk):
    """Modifier une affectation via AJAX"""
    from ..forms.personnel_forms import AffectationForm

    try:
        affectation = get_object_or_404(Affectation, pk_affectation=pk)

        if request.method == 'GET':
            form = AffectationForm(instance=affectation)
            html = render_to_string(
                'transport/affectations/partials/affectation_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'affectation': affectation
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = AffectationForm(get_request_data(request), instance=affectation)
        if form.is_valid():
            affectation = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Affectation',
                object_id=affectation.pk_affectation,
                object_repr=str(affectation),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': 'Affectation modifiée avec succès'
            })
        else:
            html = render_to_string(
                'transport/affectations/partials/affectation_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'affectation': affectation
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_entreprise_create(request):
    """Créer une entreprise via AJAX"""
    from ..forms.user_forms import EntrepriseForm

    if request.method == 'GET':
        form = EntrepriseForm()
        html = render_to_string(
            'transport/entreprise/partials/entreprise_form_modal.html',
            {'form': form, 'mode': 'create'},
            request=request
        )
        return JsonResponse({'success': True, 'html': html})

    # POST
    try:
        form = EntrepriseForm(get_request_data(request))
        if form.is_valid():
            entreprise = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Entreprise',
                object_id=entreprise.pk_entreprise,
                object_repr=str(entreprise),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Entreprise "{entreprise.nom}" créée avec succès'
            })
        else:
            html = render_to_string(
                'transport/entreprise/partials/entreprise_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_entreprise_update(request, pk):
    """Modifier une entreprise via AJAX"""
    from ..forms.user_forms import EntrepriseForm

    try:
        entreprise = get_object_or_404(Entreprise, pk_entreprise=pk)

        if request.method == 'GET':
            form = EntrepriseForm(instance=entreprise)
            html = render_to_string(
                'transport/entreprise/partials/entreprise_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'entreprise': entreprise
                },
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = EntrepriseForm(get_request_data(request), instance=entreprise)
        if form.is_valid():
            entreprise = form.save()

            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Entreprise',
                object_id=entreprise.pk_entreprise,
                object_repr=str(entreprise),
                changes={}
            )

            return JsonResponse({
                'success': True,
                'message': f'Entreprise "{entreprise.nom}" modifiée avec succès'
            })
        else:
            html = render_to_string(
                'transport/entreprise/partials/entreprise_form_modal.html',
                {
                    'form': form,
                    'mode': 'update',
                    'entreprise': entreprise
                },
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# ============================================================================
# TRANSITAIRE AJAX VIEWS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_transitaire_create(request):
    """Créer un transitaire via AJAX"""
    from ..forms.commercial_forms import TransitaireForm
    try:
        if request.method == 'GET':
            form = TransitaireForm()
            html = render_to_string(
                'transport/transitaires/partials/transitaire_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = TransitaireForm(get_request_data(request))
        if form.is_valid():
            transitaire = form.save()
            
            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Transitaire',
                object_id=transitaire.pk_transitaire,
                object_repr=str(transitaire),
                changes={}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Transitaire {transitaire.nom} créé avec succès'
            })
        else:
            html = render_to_string(
                'transport/transitaires/partials/transitaire_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_transitaire_update(request, pk):
    """Modifier un transitaire via AJAX"""
    from ..forms.commercial_forms import TransitaireForm
    try:
        transitaire = get_object_or_404(Transitaire, pk_transitaire=pk)
        
        if request.method == 'GET':
            form = TransitaireForm(instance=transitaire)
            html = render_to_string(
                'transport/transitaires/partials/transitaire_form_modal.html',
                {'form': form, 'mode': 'update', 'transitaire': transitaire},
                request=request
            )
            return JsonResponse({'success': True, 'html': html})
        
        # POST
        form = TransitaireForm(get_request_data(request), instance=transitaire)
        if form.is_valid():
            transitaire = form.save()
            
            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Transitaire',
                object_id=transitaire.pk_transitaire,
                object_repr=str(transitaire),
                changes={}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Transitaire {transitaire.nom} modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/transitaires/partials/transitaire_form_modal.html',
                {'form': form, 'mode': 'update', 'transitaire': transitaire},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# ============================================================================
# COMPAGNIE AJAX VIEWS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_compagnie_create(request):
    """Créer une compagnie via AJAX"""
    from ..forms.commercial_forms import CompagnieConteneurForm
    try:
        if request.method == 'GET':
            form = CompagnieConteneurForm()
            html = render_to_string(
                'transport/compagnies/partials/compagnie_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = CompagnieConteneurForm(get_request_data(request))
        if form.is_valid():
            compagnie = form.save()
            
            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='CompagnieConteneur',
                object_id=compagnie.pk_compagnie,
                object_repr=str(compagnie),
                changes={}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Compagnie {compagnie.nom} créée avec succès'
            })
        else:
            html = render_to_string(
                'transport/compagnies/partials/compagnie_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_compagnie_update(request, pk):
    """Modifier une compagnie via AJAX"""
    from ..forms.commercial_forms import CompagnieConteneurForm
    try:
        compagnie = get_object_or_404(CompagnieConteneur, pk_compagnie=pk)
        
        if request.method == 'GET':
            form = CompagnieConteneurForm(instance=compagnie)
            html = render_to_string(
                'transport/compagnies/partials/compagnie_form_modal.html',
                {'form': form, 'mode': 'update', 'compagnie': compagnie},
                request=request
            )
            return JsonResponse({'success': True, 'html': html})
        
        # POST
        form = CompagnieConteneurForm(get_request_data(request), instance=compagnie)
        if form.is_valid():
            compagnie = form.save()
            
            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='CompagnieConteneur',
                object_id=compagnie.pk_compagnie,
                object_repr=str(compagnie),
                changes={}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Compagnie {compagnie.nom} modifiée avec succès'
            })
        else:
            html = render_to_string(
                'transport/compagnies/partials/compagnie_form_modal.html',
                {'form': form, 'mode': 'update', 'compagnie': compagnie},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# ============================================================================
# FOURNISSEUR AJAX VIEWS
# ============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def ajax_fournisseur_create(request):
    """Créer un fournisseur via AJAX"""
    from ..forms.commercial_forms import FournisseurForm
    try:
        if request.method == 'GET':
            form = FournisseurForm()
            html = render_to_string(
                'transport/fournisseurs/partials/fournisseur_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({'success': True, 'html': html})

        # POST
        form = FournisseurForm(get_request_data(request))
        if form.is_valid():
            fournisseur = form.save()
            
            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='CREATE',
                model_name='Fournisseur',
                object_id=fournisseur.pk_fournisseur,
                object_repr=str(fournisseur),
                changes={}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Fournisseur {fournisseur.nom} créé avec succès'
            })
        else:
            html = render_to_string(
                'transport/fournisseurs/partials/fournisseur_form_modal.html',
                {'form': form, 'mode': 'create'},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def ajax_fournisseur_update(request, pk):
    """Modifier un fournisseur via AJAX"""
    from ..forms.commercial_forms import FournisseurForm
    try:
        fournisseur = get_object_or_404(Fournisseur, pk_fournisseur=pk)
        
        if request.method == 'GET':
            form = FournisseurForm(instance=fournisseur)
            html = render_to_string(
                'transport/fournisseurs/partials/fournisseur_form_modal.html',
                {'form': form, 'mode': 'update', 'fournisseur': fournisseur},
                request=request
            )
            return JsonResponse({'success': True, 'html': html})
        
        # POST
        form = FournisseurForm(get_request_data(request), instance=fournisseur)
        if form.is_valid():
            fournisseur = form.save()
            
            # Log
            AuditLog.objects.create(
                utilisateur=request.user,
                action='UPDATE',
                model_name='Fournisseur',
                object_id=fournisseur.pk_fournisseur,
                object_repr=str(fournisseur),
                changes={}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Fournisseur {fournisseur.nom} modifié avec succès'
            })
        else:
            html = render_to_string(
                'transport/fournisseurs/partials/fournisseur_form_modal.html',
                {'form': form, 'mode': 'update', 'fournisseur': fournisseur},
                request=request
            )
            return JsonResponse({
                'success': False,
                'message': 'Veuillez corriger les erreurs',
                'html': html,
                'errors': get_form_errors_json(form)
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
