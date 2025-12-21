"""
Filtres avancés pour les listes de données
==========================================

Ce module fournit des fonctions et classes pour filtrer les données
dans les différentes vues de liste de l'application.
"""

from datetime import datetime
from django.db.models import Q


class MissionFilter:
    """Filtre pour la liste des missions"""

    @staticmethod
    def apply(queryset, request):
        """
        Applique les filtres à partir des paramètres GET

        Filtres disponibles:
        - statut: en cours, terminée, annulée
        - chauffeur: pk_chauffeur
        - date_debut: date de début (YYYY-MM-DD)
        - date_fin: date de fin (YYYY-MM-DD)
        - search: recherche par origine ou destination
        """
        # Filtre par statut
        statut = request.GET.get('statut')
        if statut and statut != 'tous':
            queryset = queryset.filter(statut=statut)

        # Filtre par chauffeur
        chauffeur = request.GET.get('chauffeur')
        if chauffeur:
            queryset = queryset.filter(contrat__chauffeur__pk_chauffeur=chauffeur)

        # Filtre par client
        client = request.GET.get('client')
        if client:
            queryset = queryset.filter(contrat__client__pk_client=client)

        # Filtre par plage de dates (date de départ)
        date_debut = request.GET.get('date_debut')
        if date_debut:
            try:
                queryset = queryset.filter(date_depart__gte=date_debut)
            except ValueError:
                pass

        date_fin = request.GET.get('date_fin')
        if date_fin:
            try:
                queryset = queryset.filter(date_depart__lte=date_fin)
            except ValueError:
                pass

        # Recherche textuelle
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(origine__icontains=search) |
                Q(destination__icontains=search) |
                Q(pk_mission__icontains=search)
            )

        return queryset


class PaiementMissionFilter:
    """Filtre pour la liste des paiements de mission"""

    @staticmethod
    def apply(queryset, request):
        """
        Applique les filtres à partir des paramètres GET

        Filtres disponibles:
        - est_valide: oui, non
        - montant_min: montant minimum
        - montant_max: montant maximum
        - date_debut: date de début
        - date_fin: date de fin
        - chauffeur: pk_chauffeur
        - search: recherche par pk_paiement
        """
        # Filtre par validation
        est_valide = request.GET.get('est_valide')
        if est_valide == 'oui':
            queryset = queryset.filter(est_valide=True)
        elif est_valide == 'non':
            queryset = queryset.filter(est_valide=False)

        # Filtre par montant
        montant_min = request.GET.get('montant_min')
        if montant_min:
            try:
                queryset = queryset.filter(montant_total__gte=float(montant_min))
            except ValueError:
                pass

        montant_max = request.GET.get('montant_max')
        if montant_max:
            try:
                queryset = queryset.filter(montant_total__lte=float(montant_max))
            except ValueError:
                pass

        # Filtre par date de validation
        date_debut = request.GET.get('date_debut')
        if date_debut:
            try:
                queryset = queryset.filter(date_validation__gte=date_debut)
            except ValueError:
                pass

        date_fin = request.GET.get('date_fin')
        if date_fin:
            try:
                queryset = queryset.filter(date_validation__lte=date_fin)
            except ValueError:
                pass

        # Filtre par chauffeur
        chauffeur = request.GET.get('chauffeur')
        if chauffeur:
            queryset = queryset.filter(mission__contrat__chauffeur__pk_chauffeur=chauffeur)

        # Recherche textuelle
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(pk_paiement__icontains=search) |
                Q(mission__pk_mission__icontains=search)
            )

        return queryset


class ContratTransportFilter:
    """Filtre pour la liste des contrats"""

    @staticmethod
    def apply(queryset, request):
        """
        Applique les filtres à partir des paramètres GET

        Filtres disponibles:
        - chauffeur: pk_chauffeur
        - client: pk_client
        - transitaire: pk_transitaire
        - camion: pk_camion
        - statut_caution: bloquée, débloquée
        - date_debut: date de début
        - date_fin: date de fin
        - search: recherche par numero_bl ou pk_contrat
        """
        # Filtre par chauffeur
        chauffeur = request.GET.get('chauffeur')
        if chauffeur:
            queryset = queryset.filter(chauffeur__pk_chauffeur=chauffeur)

        # Filtre par client
        client = request.GET.get('client')
        if client:
            queryset = queryset.filter(client__pk_client=client)

        # Filtre par transitaire
        transitaire = request.GET.get('transitaire')
        if transitaire:
            queryset = queryset.filter(transitaire__pk_transitaire=transitaire)

        # Filtre par camion
        camion = request.GET.get('camion')
        if camion:
            queryset = queryset.filter(camion__pk_camion=camion)

        # Filtre par statut caution
        statut_caution = request.GET.get('statut_caution')
        if statut_caution and statut_caution != 'tous':
            queryset = queryset.filter(statut_caution=statut_caution)

        # Filtre par plage de dates
        date_debut = request.GET.get('date_debut')
        if date_debut:
            try:
                queryset = queryset.filter(date_debut__gte=date_debut)
            except ValueError:
                pass

        date_fin = request.GET.get('date_fin')
        if date_fin:
            try:
                queryset = queryset.filter(date_debut__lte=date_fin)
            except ValueError:
                pass

        # Recherche textuelle
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero_bl__icontains=search) |
                Q(pk_contrat__icontains=search) |
                Q(destinataire__icontains=search)
            )

        return queryset


class ReparationFilter:
    """Filtre pour la liste des réparations"""

    @staticmethod
    def apply(queryset, request):
        """
        Applique les filtres à partir des paramètres GET

        Filtres disponibles:
        - camion: pk_camion
        - cout_min: coût minimum
        - cout_max: coût maximum
        - date_debut: date de début
        - date_fin: date de fin
        - search: recherche par description ou pk_reparation
        """
        # Filtre par camion
        camion = request.GET.get('camion')
        if camion:
            queryset = queryset.filter(camion__pk_camion=camion)

        # Filtre par coût
        cout_min = request.GET.get('cout_min')
        if cout_min:
            try:
                queryset = queryset.filter(cout__gte=float(cout_min))
            except ValueError:
                pass

        cout_max = request.GET.get('cout_max')
        if cout_max:
            try:
                queryset = queryset.filter(cout__lte=float(cout_max))
            except ValueError:
                pass

        # Filtre par plage de dates
        date_debut = request.GET.get('date_debut')
        if date_debut:
            try:
                queryset = queryset.filter(date_reparation__gte=date_debut)
            except ValueError:
                pass

        date_fin = request.GET.get('date_fin')
        if date_fin:
            try:
                queryset = queryset.filter(date_reparation__lte=date_fin)
            except ValueError:
                pass

        # Recherche textuelle
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(pk_reparation__icontains=search)
            )

        return queryset


class CautionFilter:
    """Filtre pour la liste des cautions"""

    @staticmethod
    def apply(queryset, request):
        """
        Applique les filtres à partir des paramètres GET

        Filtres disponibles:
        - statut: en_attente, remboursee, non_remboursee, consommee, annulee
        - chauffeur: pk_chauffeur
        - client: pk_client
        - montant_min: montant minimum
        - montant_max: montant maximum
        - search: recherche par pk_caution
        """
        # Filtre par statut
        statut = request.GET.get('statut')
        if statut and statut != 'tous':
            queryset = queryset.filter(statut=statut)

        # Filtre par chauffeur
        chauffeur = request.GET.get('chauffeur')
        if chauffeur:
            queryset = queryset.filter(chauffeur__pk_chauffeur=chauffeur)

        # Filtre par client
        client = request.GET.get('client')
        if client:
            queryset = queryset.filter(client__pk_client=client)

        # Filtre par montant
        montant_min = request.GET.get('montant_min')
        if montant_min:
            try:
                queryset = queryset.filter(montant__gte=float(montant_min))
            except ValueError:
                pass

        montant_max = request.GET.get('montant_max')
        if montant_max:
            try:
                queryset = queryset.filter(montant__lte=float(montant_max))
            except ValueError:
                pass

        # Recherche textuelle
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(pk_caution__icontains=search)
            )

        return queryset
