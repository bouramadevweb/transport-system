"""
Ajax Views.Py

Vues pour ajax
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import (Chauffeur, Camion, Affectation)


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

