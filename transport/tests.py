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
            entreprise=self.entreprise,
            destinataire="Test Destinataire",
            montant_total=Decimal('1000000'),
            avance_transport=Decimal('500000'),
            caution=Decimal('50000'),
            date_debut=timezone.now().date(),
            date_limite_retour=timezone.now().date()
        )

        # Récupérer la caution créée automatiquement par le signal
        self.caution = Cautions.objects.filter(contrat=self.contrat).first()

        # Marquer la caution comme remboursée
        self.caution.statut = 'remboursee'
        self.caution.montant_rembourser = Decimal('50000')
        self.caution.save()

        # Récupérer la prestation créée par le signal
        self.prestation = PrestationDeTransports.objects.filter(contrat_transport=self.contrat).first()

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
        caution_statut_avant = self.caution.statut
        caution_montant_rembourser_avant = self.caution.montant_rembourser

        # Vérifier les valeurs avant validation
        self.assertEqual(caution_montant_avant, Decimal('50000'))
        self.assertEqual(caution_statut_avant, 'remboursee')
        self.assertEqual(caution_montant_rembourser_avant, Decimal('50000'))

        # Valider le paiement
        self.paiement.valider_paiement()

        # Recharger la caution depuis la base de données
        self.caution.refresh_from_db()

        # Vérifier que la caution n'a PAS été modifiée
        self.assertEqual(self.caution.montant, caution_montant_avant,
                        "Le montant de la caution a été modifié après validation!")
        self.assertEqual(self.caution.statut, caution_statut_avant,
                        "Le statut a été modifié après validation!")
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

    def test_caution_validation_remboursee_sans_montant(self):
        """Test: Erreur si statut='remboursee' mais montant_rembourser=0"""
        self.caution.statut = 'remboursee'
        self.caution.montant_rembourser = Decimal('0')

        with self.assertRaises(Exception):
            self.caution.full_clean()

    def test_caution_validation_montant_depasse(self):
        """Test: Erreur si montant_rembourser > montant"""
        self.caution.statut = 'remboursee'
        self.caution.montant_rembourser = Decimal('60000')  # > 50000

        with self.assertRaises(Exception):
            self.caution.full_clean()

    def test_caution_validation_montant_sans_statut(self):
        """Test: Erreur si montant_rembourser > 0 mais statut n'est pas remboursee/consommee"""
        self.caution.statut = 'en_attente'
        self.caution.montant_rembourser = Decimal('30000')

        with self.assertRaises(Exception):
            self.caution.full_clean()

    def test_caution_validation_ok(self):
        """Test: Validation réussie pour une caution correcte"""
        self.caution.statut = 'remboursee'
        self.caution.montant_rembourser = Decimal('50000')

        # Ne doit pas lever d'exception
        self.caution.full_clean()
        self.caution.save()

        # Vérifier que les valeurs sont bien sauvegardées
        self.caution.refresh_from_db()
        self.assertEqual(self.caution.statut, 'remboursee')
        self.assertEqual(self.caution.montant_rembourser, Decimal('50000'))


class AuthenticationTest(TestCase):
    """Tests pour l'authentification et le rate limiting"""

    def setUp(self):
        """Créer un utilisateur de test"""
        from transport.models import Utilisateur
        self.user = Utilisateur.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_login_page_accessible(self):
        """Test: La page de connexion est accessible"""
        response = self.client.get('/connexion/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion')

    def test_login_success(self):
        """Test: Connexion réussie avec les bons identifiants"""
        response = self.client.post('/connexion/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection vers dashboard

    def test_login_failure(self):
        """Test: Connexion échouée avec mauvais mot de passe"""
        response = self.client.post('/connexion/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Reste sur la page
        self.assertContains(response, 'invalide')

    def test_protected_page_requires_login(self):
        """Test: Les pages protégées redirigent vers la connexion"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/connexion/', response.url)


class MissionModelTest(TestCase):
    """Tests pour le modèle Mission"""

    def setUp(self):
        """Créer les données de test"""
        from transport.models import CompagnieConteneur

        self.entreprise = Entreprise.objects.create(
            nom="Test Entreprise",
            secteur_activite="Transport",
            telephone_contact="0123456789"
        )
        self.camion = Camion.objects.create(
            entreprise=self.entreprise,
            immatriculation="TEST-456",
            modele="Test",
            capacite_tonnes=Decimal('20')
        )
        self.chauffeur = Chauffeur.objects.create(
            entreprise=self.entreprise,
            nom="Test",
            prenom="Chauffeur",
            telephone="0123456789"
        )
        self.client_obj = Client.objects.create(
            nom="Client Test",
            type_client="particulier",
            telephone="0123456789"
        )
        self.transitaire = Transitaire.objects.create(
            nom="Transitaire Test",
            telephone="0123456789"
        )
        self.compagnie = CompagnieConteneur.objects.create(nom="Compagnie Test")
        self.conteneur = Conteneur.objects.create(
            numero_conteneur="CONT789",
            type_conteneur="20 pieds",
            compagnie=self.compagnie,
            client=self.client_obj,
            transitaire=self.transitaire
        )

    def test_contrat_creation(self):
        """Test: Création d'un contrat avec toutes les relations"""
        contrat = ContratTransport.objects.create(
            numero_bl="BL-TEST-002",
            client=self.client_obj,
            transitaire=self.transitaire,
            conteneur=self.conteneur,
            camion=self.camion,
            chauffeur=self.chauffeur,
            destinataire="Destinataire Test",
            montant_total=Decimal('1000000'),
            avance_transport=Decimal('500000'),
            caution=Decimal('50000'),
            date_debut=timezone.now().date(),
            entreprise=self.entreprise
        )
        self.assertIsNotNone(contrat.pk_contrat)
        self.assertEqual(contrat.numero_bl, "BL-TEST-002")

    def test_reliquat_calculation(self):
        """Test: Le reliquat est calculé automatiquement"""
        contrat = ContratTransport.objects.create(
            numero_bl="BL-TEST-003",
            client=self.client_obj,
            transitaire=self.transitaire,
            conteneur=self.conteneur,
            camion=self.camion,
            chauffeur=self.chauffeur,
            destinataire="Destinataire Test",
            montant_total=Decimal('1000000'),
            avance_transport=Decimal('400000'),
            caution=Decimal('50000'),
            date_debut=timezone.now().date(),
            entreprise=self.entreprise
        )
        self.assertEqual(contrat.reliquat_transport, Decimal('600000'))


class ViewsSecurityTest(TestCase):
    """Tests de sécurité pour les vues"""

    def setUp(self):
        """Créer un utilisateur de test"""
        from transport.models import Utilisateur
        self.user = Utilisateur.objects.create_user(
            email='viewtest@example.com',
            password='testpass123'
        )

    def test_dashboard_requires_login(self):
        """Test: Le dashboard nécessite une connexion"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/connexion/', response.url)

    def test_dashboard_accessible_when_logged_in(self):
        """Test: Le dashboard est accessible une fois connecté"""
        self.client.login(email='viewtest@example.com', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_camion_list_requires_login(self):
        """Test: La liste des camions nécessite une connexion"""
        response = self.client.get('/camions/')
        self.assertEqual(response.status_code, 302)

    def test_mission_list_requires_login(self):
        """Test: La liste des missions nécessite une connexion"""
        response = self.client.get('/missions/')
        self.assertEqual(response.status_code, 302)

    def test_contrat_list_requires_login(self):
        """Test: La liste des contrats nécessite une connexion"""
        response = self.client.get('/contrats/')
        self.assertEqual(response.status_code, 302)


class RateLimitTest(TestCase):
    """Tests pour le rate limiting"""

    def test_multiple_failed_logins(self):
        """Test: Plusieurs tentatives de connexion échouées"""
        for i in range(3):
            response = self.client.post('/connexion/', {
                'email': 'fake@example.com',
                'password': 'wrongpass'
            })
            self.assertEqual(response.status_code, 200)


class AuditLogTest(TestCase):
    """Tests pour le système d'audit"""

    def setUp(self):
        """Créer un utilisateur de test"""
        from transport.models import Utilisateur
        self.user = Utilisateur.objects.create_user(
            email='audit@example.com',
            password='testpass123'
        )

    def test_audit_log_creation(self):
        """Test: Création d'un log d'audit"""
        from transport.models import AuditLog

        log = AuditLog.objects.create(
            utilisateur=self.user,
            action='CREATE',
            model_name='Test',
            object_id='test-123',
            object_repr='Test object',
            changes={'field': 'value'}
        )
        self.assertIsNotNone(log.pk_audit)
        self.assertEqual(log.action, 'CREATE')

    def test_audit_log_helper_method(self):
        """Test: Méthode helper log_action"""
        from transport.models import AuditLog

        log = AuditLog.log_action(
            utilisateur=self.user,
            action='UPDATE',
            model_name='TestModel',
            object_id='obj-456',
            object_repr='Test representation',
            changes={'old': 'value1', 'new': 'value2'}
        )
        self.assertIsNotNone(log)
        self.assertEqual(log.model_name, 'TestModel')
