"""
Ajax Views - Complete AJAX views for all modules
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F, Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from ..models import (
    Chauffeur, Camion, Affectation, Client, Conteneur, ContratTransport,
    PrestationDeTransports, Entreprise, AuditLog, Mission, PaiementMission,
    Notification
)


# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

@login_required
def get_chauffeur_from_camion(request, pk_camion):
    """Retourne le chauffeur actuellement affecté au camion spécifié"""
    try:
        camion = Camion.objects.get(pk_camion=pk_camion)
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
    """Retourne le camion actuellement affecté au chauffeur spécifié"""
    try:
        chauffeur = Chauffeur.objects.get(pk_chauffeur=pk_chauffeur)
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


# Search endpoints
@login_required
def ajax_search_clients(request):
    """Recherche AJAX pour les clients"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    clients = Client.objects.filter(
        Q(nom__icontains=query) | Q(telephone__icontains=query)
    )[:10]
    
    results = [{'id': c.pk_client, 'text': f"{c.nom} - {c.telephone}"} for c in clients]
    return JsonResponse({'results': results})


@login_required
def ajax_search_chauffeurs(request):
    """Recherche AJAX pour les chauffeurs"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    chauffeurs = Chauffeur.objects.filter(
        Q(nom__icontains=query) | Q(prenom__icontains=query)
    )[:10]
    
    results = [{'id': c.pk_chauffeur, 'text': f"{c.nom} {c.prenom}"} for c in chauffeurs]
    return JsonResponse({'results': results})


