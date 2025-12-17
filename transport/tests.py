from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from transport.models import (
    ContratTransport, Cautions, Mission, PaiementMission,
    PrestationDeTransports, Camion, Chauffeur, Client, Transitaire,
    Conteneur, Entreprise
)


class CautionPreservationTest(TestCase):
    """Tests pour vérifier que la caution n'est PAS modifiée après validation du paiement"""

    def setUp(self):
        """Créer des données de test"""
        # Créer une entreprise
        self.entreprise = Entreprise.objects.create(
            nom="Entreprise Test",
            secteur_activite="Transport",
            telephone_contact="0123456789"
        )

        # Créer un camion
        self.camion = Camion.objects.create(
            entreprise=self.entreprise,
            immatriculation="TEST-123",
            modele="Test Model",
            capacite_tonnes=Decimal('20')
        )

        # Créer un chauffeur
        self.chauffeur = Chauffeur.objects.create(
            entreprise=self.entreprise,
            nom="Test",
            prenom="Driver",
            telephone="0123456789"
        )

        # Créer un client
        self.client = Client.objects.create(
            nom="Test Client",
            type_client="particulier",
            telephone="0123456789"
        )

        # Créer un transitaire
        self.transitaire = Transitaire.objects.create(
            nom="Test Transitaire",
            telephone="0123456789"
        )

        # Créer une compagnie de conteneur
        from transport.models import CompagnieConteneur
        self.compagnie = CompagnieConteneur.objects.create(
            nom="Compagnie Test"
        )

        # Créer un conteneur
        self.conteneur = Conteneur.objects.create(
            numero_conteneur="CONT123",
            type_conteneur="20 pieds",
            compagnie=self.compagnie,
            client=self.client,
            transitaire=self.transitaire
        )

        # Créer un contrat
        self.contrat = ContratTransport.objects.create(
            numero_bl="BL-TEST-001",
            client=self.client,
            transitaire=self.transitaire,
            conteneur=self.conteneur,
            camion=self.camion,
            chauffeur=self.chauffeur,
            destinataire="Test Destinataire",
            marchandise="Test Marchandise",
            montant_total=Decimal('1000000'),
            avance_transport=Decimal('500000'),
            caution=Decimal('50000'),
            date_debut=timezone.now().date()
        )

        # Récupérer la caution créée automatiquement par le signal
        self.caution = Cautions.objects.filter(contrat=self.contrat).first()

        # Marquer la caution comme remboursée
        self.caution.est_rembourser = True
        self.caution.montant_rembourser = Decimal('50000')
        self.caution.save()

        # Récupérer la prestation créée par le signal
        self.prestation = PrestationDeTransports.objects.filter(contrat=self.contrat).first()

        # Récupérer la mission créée par le signal
        self.mission = Mission.objects.filter(contrat=self.contrat).first()

        # Terminer la mission
        self.mission.statut = 'terminée'
        self.mission.date_retour = timezone.now().date()
        self.mission.save()

        # Récupérer le paiement créé par le signal
        self.paiement = PaiementMission.objects.filter(mission=self.mission).first()

    def test_caution_not_modified_after_payment_validation(self):
        """Test: La caution ne doit PAS être modifiée après validation du paiement"""

        # Sauvegarder les valeurs originales de la caution
        caution_montant_avant = self.caution.montant
        caution_est_rembourser_avant = self.caution.est_rembourser
        caution_montant_rembourser_avant = self.caution.montant_rembourser

        # Vérifier les valeurs avant validation
        self.assertEqual(caution_montant_avant, Decimal('50000'))
        self.assertTrue(caution_est_rembourser_avant)
        self.assertEqual(caution_montant_rembourser_avant, Decimal('50000'))

        # Valider le paiement
        self.paiement.valider_paiement()

        # Recharger la caution depuis la base de données
        self.caution.refresh_from_db()

        # Vérifier que la caution n'a PAS été modifiée
        self.assertEqual(self.caution.montant, caution_montant_avant,
                        "Le montant de la caution a été modifié après validation!")
        self.assertEqual(self.caution.est_rembourser, caution_est_rembourser_avant,
                        "Le statut est_rembourser a été modifié après validation!")
        self.assertEqual(self.caution.montant_rembourser, caution_montant_rembourser_avant,
                        "Le montant_rembourser a été modifié après validation!")

    def test_payment_validated_correctly(self):
        """Test: Le paiement doit être correctement validé"""

        # Valider le paiement
        self.paiement.valider_paiement()

        # Recharger le paiement depuis la base de données
        self.paiement.refresh_from_db()

        # Vérifier que le paiement est validé
        self.assertTrue(self.paiement.est_valide,
                       "Le paiement n'a pas été marqué comme validé!")
        self.assertIsNotNone(self.paiement.date_validation,
                            "La date de validation n'a pas été enregistrée!")
        self.assertTrue(self.paiement.caution_est_retiree,
                       "Le champ caution_est_retiree n'a pas été coché!")

    def test_caution_audit_trail_in_observation(self):
        """Test: L'état de la caution doit être enregistré dans l'observation"""

        # Valider le paiement
        self.paiement.valider_paiement()

        # Recharger le paiement
        self.paiement.refresh_from_db()

        # Vérifier que l'observation contient les informations de la caution
        self.assertIn("État de la caution au moment de la validation", self.paiement.observation)
        self.assertIn("50000", self.paiement.observation)  # Montant
        self.assertIn("Remboursée", self.paiement.observation)


class CautionValidationTest(TestCase):
    """Tests pour la validation de la caution"""

    def setUp(self):
        """Créer des données de test minimales"""
        # Créer les objets nécessaires (simplifié)
        self.client = Client.objects.create(
            nom="Test Client", type_client="particulier", telephone="0123456789"
        )
        self.transitaire = Transitaire.objects.create(
            nom="Transitaire Test", telephone="0123456789"
        )
        from transport.models import CompagnieConteneur
        self.compagnie = CompagnieConteneur.objects.create(
            nom="Compagnie Test"
        )
        self.conteneur = Conteneur.objects.create(
            numero_conteneur="CONT456",
            type_conteneur="20 pieds",
            compagnie=self.compagnie,
            client=self.client,
            transitaire=self.transitaire
        )

        self.caution = Cautions.objects.create(
            conteneur=self.conteneur,
            transitaire=self.transitaire,
            client=self.client,
            montant=Decimal('50000')
        )

    def test_caution_validation_rembourser_sans_montant(self):
        """Test: Erreur si est_rembourser=True mais montant_rembourser=0"""

        self.caution.est_rembourser = True
        self.caution.montant_rembourser = Decimal('0')

        with self.assertRaises(Exception):
            self.caution.full_clean()

    def test_caution_validation_montant_depasse(self):
        """Test: Erreur si montant_rembourser > montant"""

        self.caution.est_rembourser = True
        self.caution.montant_rembourser = Decimal('60000')  # > 50000

        with self.assertRaises(Exception):
            self.caution.full_clean()

    def test_caution_validation_montant_sans_checkbox(self):
        """Test: Erreur si montant_rembourser > 0 mais est_rembourser=False"""

        self.caution.est_rembourser = False
        self.caution.montant_rembourser = Decimal('30000')

        with self.assertRaises(Exception):
            self.caution.full_clean()

    def test_caution_validation_ok(self):
        """Test: Validation réussie pour une caution correcte"""

        self.caution.est_rembourser = True
        self.caution.montant_rembourser = Decimal('50000')

        # Ne doit pas lever d'exception
        self.caution.full_clean()
        self.caution.save()

        # Vérifier que les valeurs sont bien sauvegardées
        self.caution.refresh_from_db()
        self.assertTrue(self.caution.est_rembourser)
        self.assertEqual(self.caution.montant_rembourser, Decimal('50000'))
