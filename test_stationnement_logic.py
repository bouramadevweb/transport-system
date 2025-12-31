#!/usr/bin/env python
"""
Script de test pour la logique de calcul du stationnement (demurrage)

Teste les nouvelles règles:
- 3 premiers jours ouvrables gratuits (lun-ven)
- Si arrivée le weekend, les 3 jours gratuits commencent le lundi suivant
- Après le 4ème jour ouvrable: TOUS les jours comptent (y compris sam/dim)
- Tarif: 25 000 CFA par jour
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
sys.path.append('/home/bracoul/Documents/Document/Dossier_location_Andie/transport-system')
django.setup()

from transport.models import Mission


def test_stationnement_calculation():
    """Teste différents scénarios de calcul de stationnement"""

    print("=" * 80)
    print("TEST DE LA LOGIQUE DE STATIONNEMENT (DEMURRAGE)")
    print("=" * 80)
    print()

    # Créer une mission fictive pour les tests
    class MissionTest:
        """Classe de test simulant une Mission"""
        def __init__(self):
            self.date_arrivee = None
            self.date_dechargement = None

        # Copier la méthode calculer_frais_stationnement depuis Mission
        def calculer_frais_stationnement(self):
            if not self.date_arrivee:
                return {
                    'jours_total': 0,
                    'jours_gratuits': 0,
                    'jours_facturables': 0,
                    'montant': Decimal('0.00'),
                    'message': 'Date d\'arrivée non renseignée'
                }

            from datetime import timedelta

            date_fin = self.date_dechargement
            JOURS_GRATUITS = 3
            TARIF_JOUR = Decimal('25000.00')

            # Étape 1: Trouver le début de la période gratuite
            date_debut_gratuit = self.date_arrivee
            while date_debut_gratuit.weekday() >= 5:
                date_debut_gratuit += timedelta(days=1)

            # Étape 2: Compter 3 jours ouvrables à partir de là
            jours_ouvrables_comptes = 0
            current_date = date_debut_gratuit
            date_fin_gratuit = None

            while jours_ouvrables_comptes < JOURS_GRATUITS:
                if current_date.weekday() < 5:
                    jours_ouvrables_comptes += 1
                    if jours_ouvrables_comptes == JOURS_GRATUITS:
                        date_fin_gratuit = current_date
                        break
                current_date += timedelta(days=1)

            # Étape 3: Compter tous les jours après la période gratuite
            if date_fin <= date_fin_gratuit:
                jours_facturables = 0
            else:
                jours_facturables = (date_fin - date_fin_gratuit).days

            montant = jours_facturables * TARIF_JOUR
            jours_total = (date_fin - self.date_arrivee).days + 1

            return {
                'jours_total': jours_total,
                'jours_gratuits': JOURS_GRATUITS,
                'jours_facturables': jours_facturables,
                'montant': montant,
                'date_debut_gratuit': date_debut_gratuit,
                'date_fin_gratuit': date_fin_gratuit,
            }

    # Test 1: Arrivée lundi, déchargement lundi suivant
    print("Test 1: Arrivée lundi, déchargement lundi suivant (7 jours)")
    print("-" * 80)
    mission1 = MissionTest()
    mission1.date_arrivee = date(2025, 1, 6)  # Lundi 6 janvier 2025
    mission1.date_dechargement = date(2025, 1, 13)  # Lundi 13 janvier 2025
    result1 = mission1.calculer_frais_stationnement()
    print(f"Date arrivée: {mission1.date_arrivee.strftime('%A %d/%m/%Y')}")
    print(f"Date déchargement: {mission1.date_dechargement.strftime('%A %d/%m/%Y')}")
    print(f"Date début gratuit: {result1['date_debut_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Date fin gratuit (3ème jour): {result1['date_fin_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Jours total: {result1['jours_total']}")
    print(f"Jours gratuits: {result1['jours_gratuits']}")
    print(f"Jours facturables: {result1['jours_facturables']}")
    print(f"Montant: {result1['montant']:,.0f} CFA")
    print(f"Attendu: Gratuit lun-mer (3 jours), facturable jeu-lun (5 jours = 125 000 CFA)")
    print()

    # Test 2: Arrivée samedi, déchargement vendredi suivant
    print("Test 2: Arrivée samedi, déchargement vendredi suivant")
    print("-" * 80)
    mission2 = MissionTest()
    mission2.date_arrivee = date(2025, 1, 4)  # Samedi 4 janvier 2025
    mission2.date_dechargement = date(2025, 1, 10)  # Vendredi 10 janvier 2025
    result2 = mission2.calculer_frais_stationnement()
    print(f"Date arrivée: {mission2.date_arrivee.strftime('%A %d/%m/%Y')}")
    print(f"Date déchargement: {mission2.date_dechargement.strftime('%A %d/%m/%Y')}")
    print(f"Date début gratuit: {result2['date_debut_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Date fin gratuit (3ème jour): {result2['date_fin_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Jours total: {result2['jours_total']}")
    print(f"Jours gratuits: {result2['jours_gratuits']}")
    print(f"Jours facturables: {result2['jours_facturables']}")
    print(f"Montant: {result2['montant']:,.0f} CFA")
    print(f"Attendu: Gratuit lun-mer (3 jours), facturable jeu-ven (2 jours = 50 000 CFA)")
    print()

    # Test 3: Arrivée vendredi, déchargement mardi suivant (pendant période gratuite)
    print("Test 3: Arrivée vendredi, déchargement mardi suivant (période gratuite)")
    print("-" * 80)
    mission3 = MissionTest()
    mission3.date_arrivee = date(2025, 1, 3)  # Vendredi 3 janvier 2025
    mission3.date_dechargement = date(2025, 1, 7)  # Mardi 7 janvier 2025
    result3 = mission3.calculer_frais_stationnement()
    print(f"Date arrivée: {mission3.date_arrivee.strftime('%A %d/%m/%Y')}")
    print(f"Date déchargement: {mission3.date_dechargement.strftime('%A %d/%m/%Y')}")
    print(f"Date début gratuit: {result3['date_debut_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Date fin gratuit (3ème jour): {result3['date_fin_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Jours total: {result3['jours_total']}")
    print(f"Jours gratuits: {result3['jours_gratuits']}")
    print(f"Jours facturables: {result3['jours_facturables']}")
    print(f"Montant: {result3['montant']:,.0f} CFA")
    print(f"Attendu: Gratuit ven-mar (3 jours ouvrables), aucun frais (0 CFA)")
    print()

    # Test 4: Arrivée mercredi, déchargement lundi suivant (avec weekend facturé)
    print("Test 4: Arrivée mercredi, déchargement lundi suivant (weekend facturé)")
    print("-" * 80)
    mission4 = MissionTest()
    mission4.date_arrivee = date(2025, 1, 1)  # Mercredi 1er janvier 2025
    mission4.date_dechargement = date(2025, 1, 13)  # Lundi 13 janvier 2025
    result4 = mission4.calculer_frais_stationnement()
    print(f"Date arrivée: {mission4.date_arrivee.strftime('%A %d/%m/%Y')}")
    print(f"Date déchargement: {mission4.date_dechargement.strftime('%A %d/%m/%Y')}")
    print(f"Date début gratuit: {result4['date_debut_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Date fin gratuit (3ème jour): {result4['date_fin_gratuit'].strftime('%A %d/%m/%Y')}")
    print(f"Jours total: {result4['jours_total']}")
    print(f"Jours gratuits: {result4['jours_gratuits']}")
    print(f"Jours facturables: {result4['jours_facturables']}")
    print(f"Montant: {result4['montant']:,.0f} CFA")
    print(f"Attendu: Gratuit mer-ven (3 jours), facturable sam-lun (9 jours incluant weekend = 225 000 CFA)")
    print()

    print("=" * 80)
    print("✅ Tests terminés!")
    print("=" * 80)


if __name__ == '__main__':
    test_stationnement_calculation()
