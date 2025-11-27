#!/usr/bin/env python
"""
Script de test pour vérifier l'automatisation du workflow
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
django.setup()

from transport.models import (
    ContratTransport, Client, Transitaire, Chauffeur, Camion, Conteneur,
    Mission, PaiementMission, PrestationDeTransports, Cautions
)
from datetime import datetime, timedelta

def test_workflow_automatique():
    """Tester la création automatique du workflow"""
    print("=" * 70)
    print("TEST: Automatisation du Workflow")
    print("=" * 70)

    # Compter les objets avant
    nb_contrats_avant = ContratTransport.objects.count()
    nb_missions_avant = Mission.objects.count()
    nb_paiements_avant = PaiementMission.objects.count()
    nb_prestations_avant = PrestationDeTransports.objects.count()
    nb_cautions_avant = Cautions.objects.count()

    print(f"\n📊 État AVANT la création du contrat:")
    print(f"   - Contrats: {nb_contrats_avant}")
    print(f"   - Missions: {nb_missions_avant}")
    print(f"   - Paiements: {nb_paiements_avant}")
    print(f"   - Prestations: {nb_prestations_avant}")
    print(f"   - Cautions: {nb_cautions_avant}")

    # Récupérer les objets nécessaires
    try:
        from transport.models import Entreprise

        client = Client.objects.first()
        transitaire = Transitaire.objects.first()
        chauffeur = Chauffeur.objects.first()
        camion = Camion.objects.first()
        conteneur = Conteneur.objects.first()
        entreprise = Entreprise.objects.first()

        if not all([client, transitaire, chauffeur, camion, conteneur, entreprise]):
            print("\n❌ Erreur: Données manquantes dans la base de données")
            print(f"   Client: {'✓' if client else '✗'}")
            print(f"   Transitaire: {'✓' if transitaire else '✗'}")
            print(f"   Chauffeur: {'✓' if chauffeur else '✗'}")
            print(f"   Camion: {'✓' if camion else '✗'}")
            print(f"   Conteneur: {'✓' if conteneur else '✗'}")
            print(f"   Entreprise: {'✓' if entreprise else '✗'}")
            return False

        # Créer un contrat de test
        print(f"\n🔧 Création d'un contrat de TEST...")
        contrat = ContratTransport.objects.create(
            numero_bl=f"TEST-BL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            client=client,
            transitaire=transitaire,
            chauffeur=chauffeur,
            camion=camion,
            conteneur=conteneur,
            entreprise=entreprise,
            destinataire="Port de Douala - TEST",
            date_debut=datetime.now().date(),
            date_limite_retour=(datetime.now() + timedelta(days=7)).date(),
            montant_total=50000,
            avance_transport=20000,
            caution=5000,
            reliquat_transport=30000,
            commentaire="Contrat de test pour vérifier l'automatisation"
        )

        print(f"✅ Contrat créé: {contrat.numero_bl}")

        # Attendre un peu pour que les signaux se déclenchent
        import time
        time.sleep(1)

        # Compter les objets après
        nb_contrats_apres = ContratTransport.objects.count()
        nb_missions_apres = Mission.objects.count()
        nb_paiements_apres = PaiementMission.objects.count()
        nb_prestations_apres = PrestationDeTransports.objects.count()
        nb_cautions_apres = Cautions.objects.count()

        print(f"\n📊 État APRÈS la création du contrat:")
        print(f"   - Contrats: {nb_contrats_apres} (+{nb_contrats_apres - nb_contrats_avant})")
        print(f"   - Missions: {nb_missions_apres} (+{nb_missions_apres - nb_missions_avant})")
        print(f"   - Paiements: {nb_paiements_apres} (+{nb_paiements_apres - nb_paiements_avant})")
        print(f"   - Prestations: {nb_prestations_apres} (+{nb_prestations_apres - nb_prestations_avant})")
        print(f"   - Cautions: {nb_cautions_apres} (+{nb_cautions_apres - nb_cautions_avant})")

        # Vérifier que tout a été créé
        success = True
        if nb_missions_apres == nb_missions_avant + 1:
            mission = Mission.objects.filter(contrat=contrat).first()
            print(f"\n✅ Mission créée automatiquement: {mission.pk_mission}")
            print(f"   - Statut: {mission.statut}")
            print(f"   - Origine: {mission.origine}")
            print(f"   - Destination: {mission.destination}")
        else:
            print("\n❌ Mission n'a pas été créée automatiquement!")
            success = False

        if nb_paiements_apres == nb_paiements_avant + 1:
            paiement = PaiementMission.objects.filter(mission__contrat=contrat).first()
            print(f"\n✅ Paiement créé automatiquement: {paiement.pk_paiement}")
            print(f"   - Montant total: {paiement.montant_total}€")
            print(f"   - Commission: {paiement.commission_transitaire}€")
            print(f"   - Validé: {'Oui' if paiement.est_valide else 'Non'}")
        else:
            print("\n❌ Paiement n'a pas été créé automatiquement!")
            success = False

        if nb_prestations_apres == nb_prestations_avant + 1:
            prestation = PrestationDeTransports.objects.filter(contrat_transport=contrat).first()
            print(f"\n✅ Prestation créée automatiquement: {prestation.pk_presta_transport}")
        else:
            print("\n❌ Prestation n'a pas été créée automatiquement!")
            success = False

        if nb_cautions_apres == nb_cautions_avant + 1:
            caution = Cautions.objects.filter(contrat=contrat).first()
            print(f"\n✅ Caution créée automatiquement: {caution.pk_caution}")
            print(f"   - Montant: {caution.montant}€")
            print(f"   - Remboursée: {'Oui' if caution.est_rembourser else 'Non'}")
        else:
            print("\n❌ Caution n'a pas été créée automatiquement!")
            success = False

        if success:
            print("\n" + "=" * 70)
            print("🎉 TEST RÉUSSI: Tous les objets ont été créés automatiquement!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ TEST ÉCHOUÉ: Certains objets n'ont pas été créés")
            print("=" * 70)

        return success

    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_workflow_automatique()
