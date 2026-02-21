"""
URLs de l'API REST pour le système de transport.
Toutes les routes sont préfixées par /api/v1/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    # User & Entreprise
    EntrepriseViewSet, UtilisateurViewSet,
    # Personnel
    ChauffeurViewSet, MecanicienViewSet, AffectationViewSet,
    # Salary
    SalaireViewSet, PrimeViewSet, DeductionViewSet,
    # Vehicles
    CamionViewSet, CompagnieConteneurViewSet, ConteneurViewSet,
    ReparationViewSet, FournisseurViewSet,
    # Commercial
    TransitaireViewSet, ClientViewSet,
    # Contrats
    PrestationDeTransportsViewSet, ContratTransportViewSet,
    # Missions
    MissionViewSet, MissionConteneurViewSet, FraisTrajetViewSet,
    # Finances
    CautionsViewSet, PaiementMissionViewSet,
    # Audit
    NotificationViewSet, AuditLogViewSet,
    # Dashboard
    DashboardAPIView,
    # Login mobile (sans CSRF)
    LoginAPIView,
)

# Configuration du router
router = DefaultRouter()

# Enregistrement des ViewSets
router.register(r'entreprises', EntrepriseViewSet, basename='entreprise')
router.register(r'utilisateurs', UtilisateurViewSet, basename='utilisateur')
router.register(r'chauffeurs', ChauffeurViewSet, basename='chauffeur')
router.register(r'mecaniciens', MecanicienViewSet, basename='mecanicien')
router.register(r'affectations', AffectationViewSet, basename='affectation')
router.register(r'salaires', SalaireViewSet, basename='salaire')
router.register(r'primes', PrimeViewSet, basename='prime')
router.register(r'deductions', DeductionViewSet, basename='deduction')
router.register(r'camions', CamionViewSet, basename='camion')
router.register(r'compagnies-conteneur', CompagnieConteneurViewSet, basename='compagnie-conteneur')
router.register(r'conteneurs', ConteneurViewSet, basename='conteneur')
router.register(r'reparations', ReparationViewSet, basename='reparation')
router.register(r'fournisseurs', FournisseurViewSet, basename='fournisseur')
router.register(r'transitaires', TransitaireViewSet, basename='transitaire')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'prestations', PrestationDeTransportsViewSet, basename='prestation')
router.register(r'contrats', ContratTransportViewSet, basename='contrat')
router.register(r'missions', MissionViewSet, basename='mission')
router.register(r'mission-conteneurs', MissionConteneurViewSet, basename='mission-conteneur')
router.register(r'frais-trajet', FraisTrajetViewSet, basename='frais-trajet')
router.register(r'cautions', CautionsViewSet, basename='caution')
router.register(r'paiements', PaiementMissionViewSet, basename='paiement')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # Authentification JWT
    # Login mobile (sans CSRF, utilise email) - RECOMMANDÉ pour apps mobiles
    path('auth/login/', LoginAPIView, name='api_login'),
    # Login JWT standard (avec CSRF, utilise username)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Dashboard
    path('dashboard/stats/', DashboardAPIView.as_view(), name='dashboard-stats'),

    # Toutes les routes du router
    path('', include(router.urls)),
]
