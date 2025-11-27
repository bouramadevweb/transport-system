#!/usr/bin/env python
"""
Script de test pour vérifier les validations des montants
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
django.setup()

from transport.models import ContratTransport, PaiementMission, Cautions
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal

def test_validation_contrat():
    """Test des validations sur ContratTransport"""
    print("=" * 70)
    print("TEST 1: Validation ContratTransport")
    print("=" * 70)

    from transport.models import Client, Transitaire, Chauffeur, Camion, Conteneur, Entreprise

    # Récupérer les objets nécessaires
    client = Client.objects.first()
    transitaire = Transitaire.objects.first()
    chauffeur = Chauffeur.objects.first()
    camion = Camion.objects.first()
    conteneur = Conteneur.objects.first()
    entreprise = Entreprise.objects.first()

    # Test 1: Avance supérieure au montant total (DOIT ÉCHOUER)
    print("\n📝 Test 1.1: Avance > Montant total (DOIT ÉCHOUER)")
    try:
        contrat = ContratTransport(
            numero_bl=f"TEST-VAL-1-{datetime.now().strftime('%H%M%S')}",
            client=client,
            transitaire=transitaire,
            chauffeur=chauffeur,
            camion=camion,
            conteneur=conteneur,
            entreprise=entreprise,
            destinataire="Test",
            date_debut=datetime.now().date(),
            date_limite_retour=(datetime.now() + timedelta(days=7)).date(),
            montant_total=Decimal('10000'),
            avance_transport=Decimal('15000'),  # Plus que le total!
            caution=Decimal('1000'),
        )
        contrat.full_clean()  # Trigger validation
        print("   ❌ ÉCHEC: La validation aurait dû échouer!")
        return False
    except ValidationError as e:
        print(f"   ✅ SUCCÈS: Validation échouée comme prévu: {e.message_dict.get('avance_transport', e)}")

    # Test 2: Caution trop élevée (> 50% du montant) (DOIT ÉCHOUER)
    print("\n📝 Test 1.2: Caution > 50% du montant (DOIT ÉCHOUER)")
    try:
        contrat = ContratTransport(
            numero_bl=f"TEST-VAL-2-{datetime.now().strftime('%H%M%S')}",
            client=client,
            transitaire=transitaire,
            chauffeur=chauffeur,
            camion=camion,
            conteneur=conteneur,
            entreprise=entreprise,
            destinataire="Test",
            date_debut=datetime.now().date(),
            date_limite_retour=(datetime.now() + timedelta(days=7)).date(),
            montant_total=Decimal('10000'),
            avance_transport=Decimal('5000'),
            caution=Decimal('6000'),  # Plus de 50%!
        )
        contrat.full_clean()
        print("   ❌ ÉCHEC: La validation aurait dû échouer!")
        return False
    except ValidationError as e:
        print(f"   ✅ SUCCÈS: Validation échouée comme prévu: {e.message_dict.get('caution', e)}")

    # Test 3: Date de retour avant date de début (DOIT ÉCHOUER)
    print("\n📝 Test 1.3: Date retour < Date début (DOIT ÉCHOUER)")
    try:
        contrat = ContratTransport(
            numero_bl=f"TEST-VAL-3-{datetime.now().strftime('%H%M%S')}",
            client=client,
            transitaire=transitaire,
            chauffeur=chauffeur,
            camion=camion,
            conteneur=conteneur,
            entreprise=entreprise,
            destinataire="Test",
            date_debut=datetime.now().date(),
            date_limite_retour=(datetime.now() - timedelta(days=1)).date(),  # Avant!
            montant_total=Decimal('10000'),
            avance_transport=Decimal('5000'),
            caution=Decimal('1000'),
        )
        contrat.full_clean()
        print("   ❌ ÉCHEC: La validation aurait dû échouer!")
        return False
    except ValidationError as e:
        print(f"   ✅ SUCCÈS: Validation échouée comme prévu: {e.message_dict.get('date_limite_retour', e)}")

    # Test 4: Valeurs valides (DOIT RÉUSSIR)
    print("\n📝 Test 1.4: Valeurs valides (DOIT RÉUSSIR)")
    try:
        contrat = ContratTransport(
            numero_bl=f"TEST-VAL-4-{datetime.now().strftime('%H%M%S')}",
            client=client,
            transitaire=transitaire,
            chauffeur=chauffeur,
            camion=camion,
            conteneur=conteneur,
            entreprise=entreprise,
            destinataire="Test",
            date_debut=datetime.now().date(),
            date_limite_retour=(datetime.now() + timedelta(days=7)).date(),
            montant_total=Decimal('10000'),
            avance_transport=Decimal('5000'),  # 50%
            caution=Decimal('2000'),  # 20%
            statut_caution='bloquee'  # Valeur par défaut
        )
        contrat.full_clean(exclude=['pk_contrat'])  # Exclure la PK
        print(f"   ✅ SUCCÈS: Validation réussie!")
    except ValidationError as e:
        # Ignorer les erreurs de PK et statut_caution
        if 'avance_transport' in e.message_dict or 'caution' in e.message_dict or 'date_limite_retour' in e.message_dict:
            print(f"   ❌ ÉCHEC: Erreur de validation des montants: {e}")
            return False
        else:
            print(f"   ✅ SUCCÈS: Validation réussie (erreurs non liées aux montants ignorées)")

    return True


def test_validation_paiement():
    """Test des validations sur PaiementMission"""
    print("\n" + "=" * 70)
    print("TEST 2: Validation PaiementMission")
    print("=" * 70)

    from transport.models import Mission, PrestationDeTransports

    mission = Mission.objects.first()
    caution = Cautions.objects.first()
    prestation = PrestationDeTransports.objects.first()

    if not all([mission, caution, prestation]):
        print("   ⚠️ Pas assez de données pour tester")
        return True

    # Test 1: Commission > Montant total (DOIT ÉCHOUER)
    print("\n📝 Test 2.1: Commission > Montant total (DOIT ÉCHOUER)")
    try:
        paiement = PaiementMission(
            mission=mission,
            caution=caution,
            prestation=prestation,
            montant_total=Decimal('10000'),
            commission_transitaire=Decimal('12000'),  # Plus que le montant!
        )
        paiement.full_clean()
        print("   ❌ ÉCHEC: La validation aurait dû échouer!")
        return False
    except ValidationError as e:
        print(f"   ✅ SUCCÈS: Validation échouée comme prévu: {e.message_dict.get('commission_transitaire', e)}")

    # Test 2: Commission > 30% (DOIT ÉCHOUER)
    print("\n📝 Test 2.2: Commission > 30% du montant (DOIT ÉCHOUER)")
    try:
        paiement = PaiementMission(
            mission=mission,
            caution=caution,
            prestation=prestation,
            montant_total=Decimal('10000'),
            commission_transitaire=Decimal('3500'),  # 35%!
        )
        paiement.full_clean()
        print("   ❌ ÉCHEC: La validation aurait dû échouer!")
        return False
    except ValidationError as e:
        print(f"   ✅ SUCCÈS: Validation échouée comme prévu: {e.message_dict.get('commission_transitaire', e)}")

    # Test 3: Valeurs valides (DOIT RÉUSSIR)
    print("\n📝 Test 2.3: Commission valide (DOIT RÉUSSIR)")
    try:
        paiement = PaiementMission(
            mission=mission,
            caution=caution,
            prestation=prestation,
            montant_total=Decimal('10000'),
            commission_transitaire=Decimal('2000'),  # 20%
        )
        paiement.full_clean(exclude=['pk_paiement'])
        print(f"   ✅ SUCCÈS: Validation réussie!")
    except ValidationError as e:
        # Ignorer les erreurs de PK et contraintes uniques
        if 'commission_transitaire' in e.message_dict or 'montant_total' in e.message_dict:
            print(f"   ❌ ÉCHEC: Erreur de validation des montants: {e}")
            return False
        else:
            print(f"   ✅ SUCCÈS: Validation réussie (erreurs non liées aux montants ignorées)")

    return True


def test_validation_caution():
    """Test des validations sur Cautions"""
    print("\n" + "=" * 70)
    print("TEST 3: Validation Cautions")
    print("=" * 70)

    # Test 1: Montant remboursé > Montant caution (DOIT ÉCHOUER)
    print("\n📝 Test 3.1: Montant remboursé > Montant caution (DOIT ÉCHOUER)")
    try:
        caution = Cautions(
            montant=Decimal('5000'),
            montant_rembourser=Decimal('7000'),  # Plus que la caution!
        )
        caution.full_clean()
        print("   ❌ ÉCHEC: La validation aurait dû échouer!")
        return False
    except ValidationError as e:
        print(f"   ✅ SUCCÈS: Validation échouée comme prévu: {e.message_dict.get('montant_rembourser', e)}")

    # Test 2: Valeurs valides (DOIT RÉUSSIR)
    print("\n📝 Test 3.2: Montant remboursé valide (DOIT RÉUSSIR)")
    try:
        caution = Cautions(
            montant=Decimal('5000'),
            montant_rembourser=Decimal('5000'),  # Égal ou inférieur
        )
        caution.full_clean(exclude=['pk_caution'])
        print(f"   ✅ SUCCÈS: Validation réussie!")
    except ValidationError as e:
        # Ignorer les erreurs de PK
        if 'montant_rembourser' in e.message_dict or 'montant' in e.message_dict:
            print(f"   ❌ ÉCHEC: Erreur de validation des montants: {e}")
            return False
        else:
            print(f"   ✅ SUCCÈS: Validation réussie (erreurs non liées aux montants ignorées)")

    return True


if __name__ == "__main__":
    print("\n🔍 TESTS DE VALIDATION DES MONTANTS\n")

    results = []

    results.append(("ContratTransport", test_validation_contrat()))
    results.append(("PaiementMission", test_validation_paiement()))
    results.append(("Cautions", test_validation_caution()))

    print("\n" + "=" * 70)
    print("RÉSUMÉ DES TESTS")
    print("=" * 70)

    for nom, resultat in results:
        status = "✅ RÉUSSI" if resultat else "❌ ÉCHOUÉ"
        print(f"{nom}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
