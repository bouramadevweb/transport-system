"""
Script de Test: Annulation en Cascade
Date: 30 décembre 2024

Ce script teste le comportement actuel d'annulation/suppression
et démontre les problèmes de traçabilité.

ATTENTION: Ce script est en MODE LECTURE SEULE par défaut.
Pour tester réellement la suppression, changez TEST_MODE = False
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_management.settings')
django.setup()

from transport.models import (
    ContratTransport, Mission, Cautions, PaiementMission,
    PrestationDeTransports
)
from django.db import transaction
from decimal import Decimal

# Mode de test (si True, rollback à la fin)
TEST_MODE = True

def print_separator(title):
    """Affiche un séparateur visuel"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def afficher_statistiques(prefix=""):
    """Affiche les statistiques actuelles"""
    print(f"{prefix}Statistiques BDD:")
    print(f"  - Contrats: {ContratTransport.objects.count()}")
    print(f"  - Missions: {Mission.objects.count()}")
    print(f"  - Cautions: {Cautions.objects.count()}")
    print(f"  - Paiements: {PaiementMission.objects.count()}")
    print(f"  - Prestations: {PrestationDeTransports.objects.count()}")

def test_annulation_mission():
    """Test de annuler_mission()"""
    print_separator("TEST 1: Annulation d'une Mission")

    # Trouver une mission en cours
    mission = Mission.objects.filter(statut='en cours').first()

    if not mission:
        print("❌ Aucune mission en cours trouvée")
        return

    print(f"Mission trouvée: {mission.pk_mission}")
    print(f"  - Statut: {mission.statut}")
    print(f"  - Contrat: {mission.contrat.pk_contrat}")

    # Statistiques AVANT
    print("\n📊 AVANT annulation:")
    afficher_statistiques("  ")

    # Vérifier les objets liés
    cautions = Cautions.objects.filter(contrat=mission.contrat)
    paiements = PaiementMission.objects.filter(mission=mission)

    print(f"\n  Objets liés:")
    print(f"  - Cautions liées au contrat: {cautions.count()}")
    for caution in cautions:
        print(f"    • {caution.pk_caution}: {caution.montant} CFA, statut={caution.statut}")

    print(f"  - Paiements liés à la mission: {paiements.count()}")
    for paiement in paiements:
        print(f"    • {paiement.pk_paiement}: {paiement.montant_total} CFA, validé={paiement.est_valide}")

    if not TEST_MODE:
        # Annuler la mission
        print("\n🔄 Annulation de la mission...")
        mission.annuler_mission(raison="Test annulation cascade")

        # Vérifier les changements
        print("\n📊 APRÈS annulation:")
        afficher_statistiques("  ")

        # Re-charger les objets
        mission.refresh_from_db()
        print(f"\n  Mission {mission.pk_mission}:")
        print(f"    Statut: {mission.statut} ✅")

        print(f"\n  Contrat {mission.contrat.pk_contrat}:")
        mission.contrat.refresh_from_db()
        print(f"    Commentaire: {'ANNULÉ trouvé' if 'ANNULÉ' in (mission.contrat.commentaire or '') else 'PAS de mention annulation'} ⚠️")

        print(f"\n  Cautions:")
        for caution in cautions:
            caution.refresh_from_db()
            print(f"    • {caution.pk_caution}: statut={caution.statut} {'✅' if caution.statut == 'annulee' else '❌'}")

        print(f"\n  Paiements:")
        for paiement in paiements:
            paiement.refresh_from_db()
            observation_modifiee = 'ANNULÉ' in (paiement.observation or '')
            print(f"    • {paiement.pk_paiement}: validé={paiement.est_valide}")
            print(f"      Observation modifiée: {observation_modifiee}")
            if paiement.est_valide:
                print(f"      ⚠️  PAIEMENT VALIDÉ NON MODIFIÉ!")

        print("\n✅ Test annulation mission terminé")
    else:
        print("\n⏭️  Mode TEST - Annulation non exécutée")
        print("   Pour tester réellement, changez TEST_MODE = False")

def test_suppression_contrat():
    """Test de suppression d'un contrat"""
    print_separator("TEST 2: Suppression d'un Contrat")

    # Trouver un contrat avec des données
    contrat = ContratTransport.objects.annotate(
        nb_missions=models.Count('mission')
    ).filter(nb_missions__gt=0).first()

    if not contrat:
        print("❌ Aucun contrat avec missions trouvé")
        return

    print(f"Contrat trouvé: {contrat.pk_contrat}")
    print(f"  - BL: {contrat.numero_bl}")

    # Compter les objets liés
    from django.db.models import Count
    missions = Mission.objects.filter(contrat=contrat)
    cautions = Cautions.objects.filter(contrat=contrat)
    paiements = PaiementMission.objects.filter(mission__contrat=contrat)
    prestations = PrestationDeTransports.objects.filter(contrat_transport=contrat)

    nb_missions = missions.count()
    nb_cautions = cautions.count()
    nb_paiements = paiements.count()
    nb_prestations = prestations.count()

    print(f"\n📊 AVANT suppression:")
    print(f"  - Missions: {nb_missions}")
    print(f"  - Cautions: {nb_cautions}")
    print(f"  - Paiements: {nb_paiements}")
    print(f"  - Prestations: {nb_prestations}")

    # Sauvegarder les IDs pour vérification
    mission_ids = list(missions.values_list('pk_mission', flat=True))
    caution_ids = list(cautions.values_list('pk_caution', flat=True))
    paiement_ids = list(paiements.values_list('pk_paiement', flat=True))

    print(f"\n  IDs sauvegardés:")
    print(f"    Missions: {mission_ids[:3]}{'...' if len(mission_ids) > 3 else ''}")
    print(f"    Cautions: {caution_ids[:3]}{'...' if len(caution_ids) > 3 else ''}")
    print(f"    Paiements: {paiement_ids[:3]}{'...' if len(paiement_ids) > 3 else ''}")

    if not TEST_MODE:
        print("\n⚠️  ATTENTION: SUPPRESSION RÉELLE!")
        print("   Cette opération est IRRÉVERSIBLE!")

        # Demander confirmation
        confirmation = input("\n   Confirmer la suppression? (tapez 'OUI'): ")
        if confirmation != 'OUI':
            print("   ❌ Suppression annulée")
            return

        # Supprimer le contrat
        print("\n🔄 Suppression du contrat...")
        contrat.delete()

        print("\n📊 APRÈS suppression:")
        afficher_statistiques("  ")

        # Vérifier ce qui reste
        print(f"\n  Vérification des IDs:")

        missions_restantes = Mission.objects.filter(pk_mission__in=mission_ids)
        print(f"    Missions: {missions_restantes.count()}/{nb_missions} {'❌ TOUTES SUPPRIMÉES' if missions_restantes.count() == 0 else ''}")

        paiements_restants = PaiementMission.objects.filter(pk_paiement__in=paiement_ids)
        print(f"    Paiements: {paiements_restants.count()}/{nb_paiements} {'❌ TOUS SUPPRIMÉS' if paiements_restants.count() == 0 else ''}")

        cautions_restantes = Cautions.objects.filter(pk_caution__in=caution_ids)
        print(f"    Cautions: {cautions_restantes.count()}/{nb_cautions}")

        if cautions_restantes.exists():
            print(f"\n    Détail cautions orphelines:")
            for caution in cautions_restantes:
                print(f"      • {caution.pk_caution}: contrat_id={caution.contrat_id} ⚠️ (NULL)")
                print(f"        statut={caution.statut} {'❌ PAS annulée' if caution.statut != 'annulee' else ''}")

        print("\n❌ PROBLÈME: Perte totale de traçabilité!")
        print("   - Missions: SUPPRIMÉES")
        print("   - Paiements: SUPPRIMÉS")
        print("   - Cautions: ORPHELINES")
        print("   - Historique: PERDU")

    else:
        print("\n⏭️  Mode TEST - Suppression non exécutée")
        print("   Pour tester réellement, changez TEST_MODE = False")
        print("\n⚠️  Si cette suppression était réelle:")
        print(f"   ❌ {nb_missions} missions SUPPRIMÉES")
        print(f"   ❌ {nb_paiements} paiements SUPPRIMÉS")
        print(f"   ⚠️  {nb_cautions} cautions ORPHELINES")
        print(f"   ❌ Historique financier PERDU")

def test_propositions():
    """Affiche les propositions d'amélioration"""
    print_separator("PROPOSITIONS D'AMÉLIORATION")

    print("🔧 Recommandation 1: Ajouter un champ 'statut' au ContratTransport")
    print("   Code proposé:")
    print("""
    class ContratTransport(models.Model):
        statut = models.CharField(
            max_length=10,
            choices=[
                ('actif', 'Actif'),
                ('termine', 'Terminé'),
                ('annule', 'Annulé'),
            ],
            default='actif'
        )
    """)

    print("\n🔧 Recommandation 2: Créer une méthode annuler_contrat()")
    print("   Code proposé:")
    print("""
    def annuler_contrat(self, raison=''):
        # 1. Annuler le contrat
        self.statut = 'annule'
        self.commentaire += f'ANNULÉ: {raison}'
        self.save()

        # 2. Annuler toutes les missions
        for mission in Mission.objects.filter(contrat=self):
            mission.annuler_mission(raison)

        # 3. Annuler toutes les cautions
        for caution in Cautions.objects.filter(contrat=self):
            caution.statut = 'annulee'
            caution.save()

        # RÉSULTAT: Tout annulé mais CONSERVÉ en BDD ✅
    """)

    print("\n🔧 Recommandation 3: Changer CASCADE → PROTECT")
    print("   Code proposé:")
    print("""
    class Mission(models.Model):
        contrat = models.ForeignKey(
            "ContratTransport",
            on_delete=models.PROTECT  # ← Bloque la suppression
        )
    """)

    print("\n🔧 Recommandation 4: Modifier delete_contrat() avec protection")
    print("   Code proposé:")
    print("""
    def delete_contrat(request, pk):
        contrat = get_object_or_404(ContratTransport, pk=pk)

        # Vérifier s'il y a des données
        if Mission.objects.filter(contrat=contrat).exists():
            messages.error(
                request,
                "❌ Impossible! Utilisez l'annulation pour "
                "garder la traçabilité."
            )
            return redirect('contrat_list')

        # Suppression autorisée seulement si vide
        contrat.delete()
    """)

def main():
    """Fonction principale"""
    print_separator("SCRIPT DE TEST: ANNULATION EN CASCADE")

    if TEST_MODE:
        print("⚠️  MODE TEST ACTIVÉ")
        print("   Les modifications seront annulées à la fin")
        print("   Pour tester réellement, changez TEST_MODE = False dans le script")
    else:
        print("⚠️  MODE RÉEL ACTIVÉ")
        print("   ATTENTION: Les modifications seront PERMANENTES!")

    # Statistiques initiales
    print_separator("Statistiques Initiales")
    afficher_statistiques()

    # Tests
    try:
        if TEST_MODE:
            with transaction.atomic():
                test_annulation_mission()
                test_suppression_contrat()
                # Rollback automatique à la fin du bloc
                raise Exception("Rollback test")
        else:
            test_annulation_mission()
            print("\n" + "="*70)
            input("Appuyez sur Entrée pour continuer avec le test de suppression...")
            test_suppression_contrat()
    except Exception as e:
        if TEST_MODE and "Rollback test" in str(e):
            print("\n✅ Tests terminés - Rollback effectué")
        else:
            print(f"\n❌ Erreur: {e}")

    # Propositions
    test_propositions()

    # Statistiques finales
    print_separator("Statistiques Finales")
    afficher_statistiques()

    print_separator("CONCLUSION")
    print("📋 Pour voir l'analyse complète:")
    print("   - ANALYSE_ANNULATION_CONTRAT.md")
    print("   - DIAGRAMME_CASCADE_ANNULATION.md")
    print("\n⚠️  RAPPEL:")
    print("   - Éviter la suppression de contrats")
    print("   - Utiliser uniquement l'annulation")
    print("   - Implémenter les recommandations pour sécuriser le système")

if __name__ == "__main__":
    main()
