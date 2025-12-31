#!/usr/bin/env python
"""
Script de test pour vérifier la méthode get_camion_actuel() du modèle Chauffeur

Teste que le camion est correctement récupéré via l'affectation active
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
sys.path.append('/home/bracoul/Documents/Document/Dossier_location_Andie/transport-system')
django.setup()

from transport.models import Chauffeur, Camion, Affectation


def test_get_camion_actuel():
    """Teste la méthode get_camion_actuel"""

    print("=" * 80)
    print("TEST DE LA MÉTHODE get_camion_actuel()")
    print("=" * 80)
    print()

    # Récupérer quelques chauffeurs
    chauffeurs = Chauffeur.objects.all()[:5]

    if not chauffeurs.exists():
        print("❌ Aucun chauffeur trouvé dans la base de données")
        return

    print(f"✅ {chauffeurs.count()} chauffeur(s) trouvé(s)\n")

    for chauffeur in chauffeurs:
        print("-" * 80)
        print(f"Chauffeur: {chauffeur.nom} {chauffeur.prenom}")
        print(f"Téléphone: {chauffeur.telephone or 'N/A'}")
        print(f"Est affecté: {'Oui' if chauffeur.est_affecter else 'Non'}")

        # Récupérer le camion actuel
        camion = chauffeur.get_camion_actuel()

        if camion:
            print(f"✅ Camion affecté: {camion.immatriculation}")
            print(f"   Modèle: {camion.modele or 'N/A'}")
            print(f"   Capacité: {camion.capacite_tonnes} tonnes")

            # Récupérer l'affectation active
            affectation = Affectation.objects.filter(
                chauffeur=chauffeur,
                date_fin_affectation__isnull=True
            ).first()

            if affectation:
                print(f"   Date affectation: {affectation.date_affectation.strftime('%d/%m/%Y')}")
        else:
            print("❌ Aucun camion affecté actuellement")

            # Vérifier s'il y a des affectations terminées
            affectations_terminees = Affectation.objects.filter(
                chauffeur=chauffeur,
                date_fin_affectation__isnull=False
            ).order_by('-date_fin_affectation')[:1]

            if affectations_terminees.exists():
                derniere = affectations_terminees.first()
                print(f"   Dernière affectation terminée: {derniere.camion.immatriculation}")
                print(f"   Terminée le: {derniere.date_fin_affectation.strftime('%d/%m/%Y')}")

        print()

    print("=" * 80)
    print("✅ Test terminé!")
    print("=" * 80)


if __name__ == '__main__':
    test_get_camion_actuel()
