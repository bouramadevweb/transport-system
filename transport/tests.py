from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from decimal import Decimal
from django.utils import timezone
from transport.models import (
    ContratTransport, Cautions, Mission, PaiementMission,
    PrestationDeTransports, Camion, Chauffeur, Client, Transitaire,
    Conteneur, Entreprise, Mecanicien, Reparation, PieceReparee,
    Utilisateur,
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


# ===========================================================================
# NON-REGRESSION : Mécaniciens / Réparations / Pièces réparées
# Bug corrigé : create_mecanicien ne sauvegardait pas l'entreprise du user
# Conséquence : ReparationForm vide → réparations non créables → pièces vides
# ===========================================================================

def _make_request(user, method='GET', data=None):
    """Helper : crée une requête Django de test avec messages support."""
    factory = RequestFactory()
    req = factory.get('/') if method == 'GET' else factory.post('/', data or {})
    req.user = user
    req.session = {}
    req._messages = FallbackStorage(req)
    return req


class MaintenanceSetupMixin:
    """
    Mixin commun : crée deux entreprises, deux users, un camion et
    quelques mécaniciens pour tester l'isolation multi-tenant.
    """

    def setUp(self):
        self.entreprise_a = Entreprise.objects.create(
            nom="Entreprise A",
            secteur_activite="Transport",
            telephone_contact="0000000001",
        )
        self.entreprise_b = Entreprise.objects.create(
            nom="Entreprise B",
            secteur_activite="Transport",
            telephone_contact="0000000002",
        )

        self.user_a = Utilisateur.objects.create_user(
            email="usera@test.com",
            password="pass",
            entreprise=self.entreprise_a,
        )
        self.user_b = Utilisateur.objects.create_user(
            email="userb@test.com",
            password="pass",
            entreprise=self.entreprise_b,
        )

        self.camion_a = Camion.objects.create(
            entreprise=self.entreprise_a,
            immatriculation="NR-TEST-A1",
            modele="TestModel",
            capacite_tonnes=Decimal("10"),
        )
        self.camion_b = Camion.objects.create(
            entreprise=self.entreprise_b,
            immatriculation="NR-TEST-B1",
            modele="TestModel",
            capacite_tonnes=Decimal("10"),
        )

        self.meca_a = Mecanicien.objects.create(
            nom="MecaA",
            telephone="0100000001",
            entreprise=self.entreprise_a,
        )
        self.meca_b = Mecanicien.objects.create(
            nom="MecaB",
            telephone="0100000002",
            entreprise=self.entreprise_b,
        )


# ---------------------------------------------------------------------------
# 1. Tests UNITAIRES — Modèle & Formulaires
# ---------------------------------------------------------------------------

class MecanicienFormTest(MaintenanceSetupMixin, TestCase):
    """Tests unitaires sur MecanicienForm et la sauvegarde de l'entreprise."""

    def test_form_exclut_champ_entreprise(self):
        """Le formulaire ne doit PAS exposer le champ entreprise (injection côté vue)."""
        from transport.forms import MecanicienForm
        form = MecanicienForm(data={"nom": "Test", "telephone": "0123456789"})
        self.assertNotIn("entreprise", form.fields,
                         "entreprise ne doit pas être dans les champs du formulaire")

    def test_form_valide_sans_entreprise(self):
        """Le formulaire est valide même sans entreprise (injected via view)."""
        from transport.forms import MecanicienForm
        form = MecanicienForm(data={"nom": "TestMeca", "telephone": "0123456789"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_commit_false_permet_injection_entreprise(self):
        """commit=False + injection manulle de l'entreprise doit fonctionner."""
        from transport.forms import MecanicienForm
        form = MecanicienForm(data={"nom": "TestInject", "telephone": "0555555555"})
        self.assertTrue(form.is_valid())
        meca = form.save(commit=False)
        meca.entreprise = self.entreprise_a
        meca.save()

        meca.refresh_from_db()
        self.assertEqual(meca.entreprise, self.entreprise_a,
                         "L'entreprise doit être celle du user, pas NULL")

    def test_mecanicien_sans_entreprise_invisible_dans_liste(self):
        """Un mécanicien avec entreprise=NULL ne doit PAS apparaître dans la liste filtrée."""
        orphelin = Mecanicien.objects.create(
            nom="Orphelin",
            telephone="0666000000",
            entreprise=None,
        )
        visibles = Mecanicien.objects.filter(entreprise=self.entreprise_a)
        self.assertNotIn(orphelin, visibles,
                         "Un mécanicien sans entreprise ne doit pas être visible")


class PieceRepareeCoutTotalTest(TestCase):
    """Tests unitaires sur PieceReparee.get_cout_total()."""

    def setUp(self):
        self.entreprise = Entreprise.objects.create(
            nom="EntrepriseTest",
            secteur_activite="Transport",
            telephone_contact="0000000000",
        )
        self.camion = Camion.objects.create(
            entreprise=self.entreprise,
            immatriculation="COUT-TEST-01",
            modele="Model",
            capacite_tonnes=Decimal("5"),
        )
        self.reparation = Reparation.objects.create(
            camion=self.camion,
            date_reparation=timezone.now().date(),
            cout=Decimal("0"),
        )

    def test_cout_total_entier(self):
        piece = PieceReparee.objects.create(
            reparation=self.reparation,
            nom_piece="Filtre huile",
            categorie="moteur",
            quantite=3,
            cout_unitaire=Decimal("5000"),
        )
        self.assertEqual(piece.get_cout_total(), Decimal("15000"))

    def test_cout_total_decimal(self):
        """get_cout_total() doit conserver les centimes — contrairement à widthratio."""
        piece = PieceReparee.objects.create(
            reparation=self.reparation,
            nom_piece="Joint",
            categorie="moteur",
            quantite=2,
            cout_unitaire=Decimal("1500.75"),
        )
        self.assertEqual(piece.get_cout_total(), Decimal("3001.50"),
                         "Les centimes doivent être conservés (widthratio les tronquait)")

    def test_cout_total_quantite_unitaire(self):
        piece = PieceReparee.objects.create(
            reparation=self.reparation,
            nom_piece="Boulon",
            categorie="carrosserie",
            quantite=1,
            cout_unitaire=Decimal("250.00"),
        )
        self.assertEqual(piece.get_cout_total(), Decimal("250.00"))


class ReparationFormMecanicienTest(MaintenanceSetupMixin, TestCase):
    """Tests sur le queryset mécaniciens dans ReparationForm."""

    def test_mecaniciens_filtres_par_entreprise(self):
        """Seuls les mécaniciens de l'entreprise du user doivent apparaître."""
        from transport.forms import ReparationForm
        form = ReparationForm(user=self.user_a)
        qs = form.fields["mecaniciens"].queryset
        self.assertIn(self.meca_a, qs)
        self.assertNotIn(self.meca_b, qs,
                         "Les mécaniciens d'une autre entreprise ne doivent pas apparaître")

    def test_mecaniciens_non_requis(self):
        """Le champ mecaniciens ne doit pas bloquer la soumission si vide."""
        from transport.forms import ReparationForm
        form = ReparationForm(user=self.user_a)
        self.assertFalse(form.fields["mecaniciens"].required,
                         "required=True bloquerait la création quand le queryset est vide")

    def test_fallback_mecaniciens_null_entreprise(self):
        """Si aucun mécanicien avec entreprise, le fallback NULL doit s'activer."""
        from transport.forms import ReparationForm
        # Créer une entreprise sans mécanicien
        entreprise_vide = Entreprise.objects.create(
            nom="EntrepriseVide",
            secteur_activite="Transport",
            telephone_contact="0999999999",
        )
        user_vide = Utilisateur.objects.create_user(
            email="uservide@test.com",
            password="pass",
            entreprise=entreprise_vide,
        )
        meca_null = Mecanicien.objects.create(
            nom="MecaNull",
            telephone="0777000000",
            entreprise=None,
        )
        form = ReparationForm(user=user_vide)
        qs = form.fields["mecaniciens"].queryset
        self.assertIn(meca_null, qs,
                      "Le fallback doit afficher les mécaniciens sans entreprise")


# ---------------------------------------------------------------------------
# 2. Tests d'INTÉGRATION — Vues Django
# ---------------------------------------------------------------------------

class MecanicienListViewTest(MaintenanceSetupMixin, TestCase):
    """Tests d'intégration sur la vue mecanicien_list."""

    def _get_list(self, user):
        from transport.views.personnel_views import mecanicien_list
        req = _make_request(user)
        return mecanicien_list(req)

    def test_liste_charge_http_200(self):
        resp = self._get_list(self.user_a)
        self.assertEqual(resp.status_code, 200)

    def test_liste_affiche_mecaniciens_de_son_entreprise(self):
        resp = self._get_list(self.user_a)
        content = resp.content.decode()
        self.assertIn("MecaA", content,
                      "Le mécanicien de l'entreprise A doit être visible pour user_a")

    def test_liste_cache_mecaniciens_autre_entreprise(self):
        resp = self._get_list(self.user_a)
        content = resp.content.decode()
        self.assertNotIn("MecaB", content,
                         "Le mécanicien de l'entreprise B ne doit PAS être visible pour user_a")

    def test_isolation_inverse(self):
        """User B ne voit que ses mécaniciens."""
        resp = self._get_list(self.user_b)
        content = resp.content.decode()
        self.assertIn("MecaB", content)
        self.assertNotIn("MecaA", content)


class CreateMecanicienViewTest(MaintenanceSetupMixin, TestCase):
    """Tests d'intégration sur la vue create_mecanicien."""

    def test_create_injecte_entreprise_du_user(self):
        """REGRESSION TEST : la vue doit sauvegarder l'entreprise du user connecté."""
        from transport.views.personnel_views import create_mecanicien
        req = _make_request(self.user_a, method='POST', data={
            "nom": "NouveauMeca",
            "telephone": "0888000001",
            "email": "",
        })
        create_mecanicien(req)

        meca = Mecanicien.objects.filter(nom="NouveauMeca").first()
        self.assertIsNotNone(meca, "Le mécanicien doit avoir été créé")
        self.assertEqual(meca.entreprise, self.entreprise_a,
                         "L'entreprise doit être celle de user_a, pas NULL")

    def test_create_ne_laisse_pas_entreprise_null(self):
        """REGRESSION TEST : entreprise ne doit JAMAIS être NULL après création."""
        from transport.views.personnel_views import create_mecanicien
        req = _make_request(self.user_a, method='POST', data={
            "nom": "MecaSansEntreprise",
            "telephone": "0888000002",
        })
        create_mecanicien(req)

        null_mecaniciens = Mecanicien.objects.filter(
            nom="MecaSansEntreprise",
            entreprise__isnull=True,
        )
        self.assertEqual(null_mecaniciens.count(), 0,
                         "Aucun mécanicien ne doit être créé avec entreprise=NULL")

    def test_mecaniciens_deux_entreprises_isoles(self):
        """User A et user B créent chacun un mécanicien : ils ne se voient pas."""
        from transport.views.personnel_views import create_mecanicien
        req_a = _make_request(self.user_a, method='POST', data={"nom": "MecaIsoA", "telephone": "0001"})
        req_b = _make_request(self.user_b, method='POST', data={"nom": "MecaIsoB", "telephone": "0002"})
        create_mecanicien(req_a)
        create_mecanicien(req_b)

        self.assertFalse(Mecanicien.objects.filter(nom="MecaIsoA", entreprise=self.entreprise_b).exists())
        self.assertFalse(Mecanicien.objects.filter(nom="MecaIsoB", entreprise=self.entreprise_a).exists())


class ReparationListViewTest(MaintenanceSetupMixin, TestCase):
    """Tests d'intégration sur la vue reparation_list."""

    def setUp(self):
        super().setUp()
        self.rep_a = Reparation.objects.create(
            camion=self.camion_a,
            date_reparation=timezone.now().date(),
            cout=Decimal("50000"),
            description="Réparation entreprise A",
        )
        self.rep_b = Reparation.objects.create(
            camion=self.camion_b,
            date_reparation=timezone.now().date(),
            cout=Decimal("30000"),
            description="Réparation entreprise B",
        )

    def _get_list(self, user):
        from transport.views.vehicle_views import reparation_list
        req = _make_request(user)
        return reparation_list(req)

    def test_liste_charge_http_200(self):
        self.assertEqual(self._get_list(self.user_a).status_code, 200)

    def test_user_a_voit_sa_reparation(self):
        content = self._get_list(self.user_a).content.decode()
        self.assertIn("Réparation entreprise A", content)

    def test_user_a_ne_voit_pas_reparation_b(self):
        content = self._get_list(self.user_a).content.decode()
        self.assertNotIn("Réparation entreprise B", content,
                         "Une réparation d'une autre entreprise ne doit pas être visible")


class PieceRepareeListViewTest(MaintenanceSetupMixin, TestCase):
    """Tests d'intégration sur la vue piece_reparee_list — filtre entreprise."""

    def setUp(self):
        super().setUp()
        rep_a = Reparation.objects.create(
            camion=self.camion_a,
            date_reparation=timezone.now().date(),
            cout=Decimal("0"),
        )
        rep_b = Reparation.objects.create(
            camion=self.camion_b,
            date_reparation=timezone.now().date(),
            cout=Decimal("0"),
        )
        self.piece_a = PieceReparee.objects.create(
            reparation=rep_a,
            nom_piece="Filtre A",
            categorie="moteur",
            quantite=1,
            cout_unitaire=Decimal("5000"),
        )
        self.piece_b = PieceReparee.objects.create(
            reparation=rep_b,
            nom_piece="Filtre B",
            categorie="moteur",
            quantite=1,
            cout_unitaire=Decimal("3000"),
        )

    def _get_list(self, user):
        from transport.views.vehicle_views import piece_reparee_list
        req = _make_request(user)
        return piece_reparee_list(req)

    def test_liste_charge_http_200(self):
        self.assertEqual(self._get_list(self.user_a).status_code, 200)

    def test_user_a_voit_ses_pieces(self):
        content = self._get_list(self.user_a).content.decode()
        self.assertIn("Filtre A", content)

    def test_user_a_ne_voit_pas_pieces_entreprise_b(self):
        """REGRESSION TEST : le filtre entreprise doit isoler les données."""
        content = self._get_list(self.user_a).content.decode()
        self.assertNotIn("Filtre B", content,
                         "Les pièces d'une autre entreprise ne doivent pas être visibles")

    def test_isolation_inverse(self):
        content = self._get_list(self.user_b).content.decode()
        self.assertIn("Filtre B", content)
        self.assertNotIn("Filtre A", content)
