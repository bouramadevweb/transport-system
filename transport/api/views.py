"""
ViewSets pour l'API REST du système de transport.
Fournit les endpoints CRUD pour React Native.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate

from transport.models import (
    Entreprise, Utilisateur,
    Chauffeur, Mecanicien, Affectation,
    Salaire, Prime, Deduction,
    Camion, CompagnieConteneur, Conteneur, Reparation, Fournisseur,
    Transitaire, Client,
    FraisTrajet, Mission, MissionConteneur,
    ContratTransport, PrestationDeTransports,
    Cautions, PaiementMission,
    Notification, AuditLog,
)

from .serializers import (
    # User & Entreprise
    EntrepriseSerializer, UtilisateurSerializer, UtilisateurCreateSerializer,
    # Personnel
    ChauffeurSerializer, ChauffeurListSerializer, ChauffeurCreateSerializer,
    MecanicienSerializer, MecanicienCreateSerializer, AffectationSerializer,
    # Salary
    SalaireSerializer, SalaireListSerializer, PrimeSerializer, DeductionSerializer,
    # Vehicles
    CamionSerializer, CamionListSerializer, CamionCreateSerializer,
    CompagnieConteneurSerializer, CompagnieConteneurCreateSerializer,
    ConteneurSerializer, ConteneurListSerializer, ConteneurCreateSerializer,
    ReparationSerializer, FournisseurSerializer,
    # Commercial
    TransitaireSerializer, TransitaireListSerializer, TransitaireCreateSerializer,
    ClientSerializer, ClientCreateSerializer, ClientListSerializer,
    # Contrats
    ContratTransportSerializer, ContratTransportCreateSerializer, ContratTransportListSerializer,
    PrestationDeTransportsSerializer,
    # Missions
    MissionSerializer, MissionListSerializer, MissionCreateSerializer,
    MissionConteneurSerializer, FraisTrajetSerializer,
    # Finances
    CautionsSerializer, CautionsListSerializer,
    PaiementMissionSerializer, PaiementMissionListSerializer,
    # Audit
    NotificationSerializer, NotificationListSerializer,
    AuditLogSerializer,
    # Dashboard
    DashboardStatsSerializer,
)


# =============================================================================
# API LOGIN PERSONNALISEE (exemptée de CSRF)
# =============================================================================

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api_view(request):  # noqa: C901
    """API endpoint pour la connexion - exemptée de CSRF pour les apps mobiles"""
    from django.core.cache import cache as _cache
    import logging as _log
    _logger = _log.getLogger(__name__)

    ip = request.META.get('REMOTE_ADDR', 'unknown')
    _logger.info(
        f"LOGIN REQUEST from {ip} - "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')[:50]}"
    )
    # Ne jamais logger email ni password

    # Rate limiting : 5 tentatives par IP sur 15 minutes
    _cache_key = f'login_attempts:{ip}'
    _attempts = _cache.get(_cache_key, 0)
    if _attempts >= 5:
        _logger.warning(f"Brute-force détecté depuis {ip} ({_attempts} tentatives)")
        return Response(
            {'detail': 'Trop de tentatives de connexion. Réessayez dans 15 minutes.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'detail': 'Email et mot de passe requis'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Authentification avec email
    user = authenticate(request, username=email, password=password)

    if user is None:
        # Incrémenter le compteur de tentatives échouées (expire dans 15 min)
        _cache.set(_cache_key, _attempts + 1, 900)
        _logger.warning(f"Échec de connexion depuis {ip} (tentative {_attempts + 1}/5)")
        return Response(
            {'detail': 'Identifiants incorrects'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'detail': 'Compte désactivé'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Connexion réussie : réinitialiser le compteur de tentatives
    _cache.delete(_cache_key)

    # Générer les tokens JWT
    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'pk': user.pk_utilisateur,
            'email': user.email,
            'nom': user.nom_utilisateur,
            'role': user.role,
        }
    })


# Alias pour compatibilité avec urls.py
LoginAPIView = login_api_view


# =============================================================================
# VIEWSETS UTILISATEUR & ENTREPRISE
# =============================================================================

class EntrepriseViewSet(viewsets.ModelViewSet):
    """API endpoint pour les entreprises"""
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email_contact']
    ordering_fields = ['nom', 'date_creation']


class UtilisateurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les utilisateurs"""
    queryset = Utilisateur.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'nom_utilisateur']
    ordering_fields = ['nom_utilisateur', 'date_joined']

    def get_serializer_class(self):
        if self.action == 'create':
            return UtilisateurCreateSerializer
        return UtilisateurSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retourne l'utilisateur connecté"""
        serializer = UtilisateurSerializer(request.user)
        return Response(serializer.data)


# =============================================================================
# VIEWSETS PERSONNEL
# =============================================================================

class ChauffeurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les chauffeurs"""
    queryset = Chauffeur.objects.select_related('entreprise').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'prenom', 'telephone']
    ordering_fields = ['nom', 'prenom']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChauffeurListSerializer
        if self.action == 'create':
            return ChauffeurCreateSerializer
        return ChauffeurSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrer par statut d'affectation
        est_affecter = self.request.query_params.get('est_affecter')
        if est_affecter is not None:
            queryset = queryset.filter(est_affecter=est_affecter.lower() == 'true')
        # Filtrer les chauffeurs disponibles (pas en mission active)
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            chauffeurs_en_mission = Mission.objects.filter(
                statut='en cours'
            ).values_list('contrat__chauffeur_id', flat=True)
            queryset = queryset.exclude(pk_chauffeur__in=chauffeurs_en_mission)
        return queryset

    @action(detail=True, methods=['get'])
    def camion_actuel(self, request, pk=None):
        """Retourne le camion actuellement affecté au chauffeur"""
        chauffeur = self.get_object()
        camion = chauffeur.get_camion_actuel()
        if camion:
            return Response(CamionListSerializer(camion).data)
        return Response({'detail': 'Aucun camion affecté'}, status=404)


class MecanicienViewSet(viewsets.ModelViewSet):
    """API endpoint pour les mécaniciens"""
    queryset = Mecanicien.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'telephone']

    def get_serializer_class(self):
        if self.action == 'create':
            return MecanicienCreateSerializer
        return MecanicienSerializer


class AffectationViewSet(viewsets.ModelViewSet):
    """API endpoint pour les affectations chauffeur-camion"""
    queryset = Affectation.objects.select_related('chauffeur', 'camion').all()
    serializer_class = AffectationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_debut', 'date_fin']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrer les affectations actives
        actives = self.request.query_params.get('actives')
        if actives and actives.lower() == 'true':
            queryset = queryset.filter(date_fin__isnull=True)
        return queryset

    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Termine une affectation"""
        affectation = self.get_object()
        affectation.terminer_affectation()
        return Response({'status': 'Affectation terminée'})


# =============================================================================
# VIEWSETS VEHICULES
# =============================================================================

class CamionViewSet(viewsets.ModelViewSet):
    """API endpoint pour les camions"""
    queryset = Camion.objects.select_related('entreprise').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['immatriculation', 'modele']
    ordering_fields = ['immatriculation', 'capacite_tonnes']

    def get_serializer_class(self):
        if self.action == 'list':
            return CamionListSerializer
        if self.action == 'create':
            return CamionCreateSerializer
        return CamionSerializer

    def partial_update(self, request, *args, **kwargs):
        print(f"📥 PATCH data received: {request.data}")
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        est_affecter = self.request.query_params.get('est_affecter')
        if est_affecter is not None:
            queryset = queryset.filter(est_affecter=est_affecter.lower() == 'true')
        # Filtrer les camions disponibles (pas en mission active)
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            camions_en_mission = Mission.objects.filter(
                statut='en cours'
            ).values_list('contrat__camion_id', flat=True)
            queryset = queryset.exclude(pk_camion__in=camions_en_mission)
        return queryset

    @action(detail=True, methods=['get'])
    def chauffeur_actuel(self, request, pk=None):
        """Retourne le chauffeur actuellement affecté au camion"""
        camion = self.get_object()
        affectation = Affectation.objects.filter(
            camion=camion,
            date_fin_affectation__isnull=True
        ).first()
        if affectation:
            return Response(ChauffeurListSerializer(affectation.chauffeur).data)
        return Response({'detail': 'Aucun chauffeur affecté'}, status=404)


class CompagnieConteneurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les compagnies de conteneurs"""
    queryset = CompagnieConteneur.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom']

    def get_serializer_class(self):
        if self.action == 'create':
            return CompagnieConteneurCreateSerializer
        return CompagnieConteneurSerializer


class ConteneurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les conteneurs"""
    queryset = Conteneur.objects.select_related('compagnie', 'client').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_conteneur']
    ordering_fields = ['numero_conteneur', 'poids']

    def get_serializer_class(self):
        if self.action == 'list':
            return ConteneurListSerializer
        if self.action == 'create':
            return ConteneurCreateSerializer
        return ConteneurSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrer les conteneurs disponibles (pas en mission active)
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            conteneurs_en_mission = Mission.objects.filter(
                statut='en cours'
            ).values_list('contrat__conteneur_id', flat=True)
            queryset = queryset.exclude(pk_conteneur__in=conteneurs_en_mission)
        return queryset


class ReparationViewSet(viewsets.ModelViewSet):
    """API endpoint pour les réparations"""
    queryset = Reparation.objects.select_related('camion').all()
    serializer_class = ReparationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_debut', 'date_fin']


class FournisseurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les fournisseurs"""
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'telephone']


# =============================================================================
# VIEWSETS COMMERCIAL
# =============================================================================

class TransitaireViewSet(viewsets.ModelViewSet):
    """API endpoint pour les transitaires"""
    queryset = Transitaire.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'telephone', 'email']
    ordering_fields = ['nom']

    def get_serializer_class(self):
        if self.action == 'list':
            return TransitaireListSerializer
        if self.action == 'create':
            return TransitaireCreateSerializer
        return TransitaireSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """API endpoint pour les clients"""
    queryset = Client.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'telephone']
    ordering_fields = ['nom', 'type_client']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        if self.action == 'create':
            return ClientCreateSerializer
        return ClientSerializer


# =============================================================================
# VIEWSETS CONTRATS
# =============================================================================

class PrestationDeTransportsViewSet(viewsets.ModelViewSet):
    """API endpoint pour les prestations de transport"""
    queryset = PrestationDeTransports.objects.select_related('contrat').all()
    serializer_class = PrestationDeTransportsSerializer
    permission_classes = [IsAuthenticated]


class ContratTransportViewSet(viewsets.ModelViewSet):
    """API endpoint pour les contrats de transport"""
    queryset = ContratTransport.objects.select_related(
        'client', 'transitaire', 'chauffeur', 'camion', 'entreprise'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_bl', 'client__nom']
    ordering_fields = ['date_debut', 'montant_total']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContratTransportListSerializer
        if self.action == 'create':
            return ContratTransportCreateSerializer
        return ContratTransportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def pdf(self, request, pk=None):
        """Génère et retourne le PDF du contrat (Feuille de Route)"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors as rl_colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from io import BytesIO
        from django.http import HttpResponse

        contrat = self.get_object()
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=30)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="TitleCenter", alignment=1, fontSize=16, spaceAfter=12))
        styles.add(ParagraphStyle(name="NormalBold", fontSize=12))
        styles.add(ParagraphStyle(name="NormalJustify", alignment=4, leading=14))

        story = []
        story.append(Paragraph("<b>FEUILLE DE ROUTE</b>", styles["TitleCenter"]))
        story.append(Paragraph(f"{contrat.entreprise.nom}", styles["TitleCenter"]))
        story.append(Spacer(1, 10))

        story.append(Paragraph(f"<b>DESTINATAIRE :</b> {contrat.destinataire}", styles["Normal"]))
        story.append(Paragraph(f"<b>N° BL :</b> {contrat.numero_bl}", styles["Normal"]))
        story.append(Paragraph(f"<b>N° CONTENEUR(S) :</b> {contrat.conteneur.numero_conteneur}", styles["Normal"]))
        story.append(Paragraph(
            f"<b>NOM DU CHAUFFEUR :</b> {contrat.chauffeur.nom} {contrat.chauffeur.prenom} — Tel {contrat.chauffeur.telephone}",
            styles["Normal"]
        ))
        story.append(Paragraph(f"<b>NUMÉRO CAMION :</b> {contrat.camion.immatriculation}", styles["Normal"]))
        story.append(Spacer(1, 12))

        data = [
            ["DÉSIGNATION", "MONTANT"],
            ["Montant total", f"{contrat.montant_total} FCFA"],
            ["Avance transport", f"{contrat.avance_transport} FCFA"],
            ["Reliquat transport", f"{contrat.reliquat_transport} FCFA"],
            ["Caution", f"{contrat.caution} FCFA"],
        ]
        table = Table(data, colWidths=[250, 150])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.8, rl_colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), rl_colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(table)
        story.append(Spacer(1, 14))

        story.append(Paragraph(f"<b>Nature de la marchandise :</b> Produits divers", styles["Normal"]))
        _trans_nom = contrat.transitaire.nom if contrat.transitaire else "Non spécifié"
        _trans_tel = contrat.transitaire.telephone if contrat.transitaire else "N/A"
        story.append(Paragraph(f"<b>Transitaire :</b> {_trans_nom} — {_trans_tel}", styles["Normal"]))
        story.append(Spacer(1, 12))

        text = """
        <b>NB : Clause de responsabilité et pénalité</b><br/><br/>
        • Le transporteur est responsable uniquement en cas de perte, vol ou avarie causée par négligence.<br/>
        • La responsabilité est proportionnelle à la part non couverte par l'assurance.<br/>
        • Pas de responsabilité en cas de force majeure, douane, port, ou tiers intervenants.<br/><br/>
        • Le transporteur dispose de <b>23 jours</b> pour ramener les conteneurs vides à Dakar.<br/>
        • Retard dû au destinataire → <b>25 000 FCFA/jour</b> à facturer.<br/>
        • Retard dû au transporteur → <b>25 000 FCFA/jour</b> de pénalité.<br/><br/>
        • Une fois à Bamako, le destinataire dispose de <b>3 jours</b> pour décharger. Après : <b>25 000 FCFA/jour</b>.
        """
        story.append(Paragraph(text, styles["NormalJustify"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"<b>Date de chargement :</b> {contrat.date_debut}", styles["Normal"]))
        story.append(Paragraph(f"<b>Date de sortie :</b> {contrat.date_limite_retour}", styles["Normal"]))
        story.append(Spacer(1, 12))

        sign_table = Table(
            [["Signature transporteur", "Signature agent transit"],
             ["(signature)", "(signature)"]],
            colWidths=[250, 250]
        )
        sign_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LINEBELOW", (0, 1), (-1, 1), 0.8, rl_colors.black),
        ]))
        story.append(sign_table)

        doc.build(story)
        buffer.seek(0)
        return HttpResponse(
            buffer,
            content_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="Feuille_de_Route_{contrat.numero_bl}.pdf"'}
        )

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annule un contrat et tous les objets liés en cascade"""
        contrat = self.get_object()
        raison = request.data.get('raison', '')
        try:
            result = contrat.annuler_contrat(raison=raison)
            return Response({
                'status': 'Contrat annulé',
                'details': result,
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=400)


# =============================================================================
# VIEWSETS MISSIONS
# =============================================================================

class MissionViewSet(viewsets.ModelViewSet):
    """API endpoint pour les missions"""
    queryset = Mission.objects.select_related(
        'prestation_transport',
        'contrat',
        'contrat__chauffeur',
        'contrat__camion'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['pk_mission']
    ordering_fields = ['date_depart', 'date_retour', 'statut']
    ordering = ['-date_depart']

    def get_serializer_class(self):
        if self.action == 'list':
            return MissionListSerializer
        if self.action == 'create':
            return MissionCreateSerializer
        return MissionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset

    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Termine une mission"""
        mission = self.get_object()
        mission.statut = 'terminee'
        mission.date_arrivee = timezone.now().date()
        mission.save()
        return Response({'status': 'Mission terminée'})

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annule une mission"""
        mission = self.get_object()
        mission.statut = 'annulee'
        mission.save()
        return Response({'status': 'Mission annulée'})

    @action(detail=True, methods=['get'])
    def calculer_stationnement(self, request, pk=None):
        """Calcule les frais de stationnement"""
        mission = self.get_object()
        return Response({
            'jours_facturables': mission.jours_stationnement_facturables,
            'montant': float(mission.montant_stationnement) if mission.montant_stationnement else 0
        })

    @action(detail=True, methods=['post'])
    def bloquer_stationnement(self, request, pk=None):
        """Bloque le stationnement d'une mission (statut -> en_stationnement)"""
        mission = self.get_object()
        if mission.statut_stationnement == 'attente':
            mission.statut_stationnement = 'en_stationnement'
            if not mission.date_arrivee:
                mission.date_arrivee = timezone.now().date()
            mission.save()
            return Response({
                'status': 'Stationnement bloqué',
                'statut_stationnement': mission.statut_stationnement,
                'date_arrivee': str(mission.date_arrivee)
            })
        return Response({
            'error': f'Impossible de bloquer: statut actuel = {mission.statut_stationnement}'
        }, status=400)

    @action(detail=True, methods=['post'])
    def marquer_dechargement(self, request, pk=None):
        """Marque le déchargement d'une mission (arrête les frais de stationnement)"""
        mission = self.get_object()
        if mission.statut_stationnement in ['attente', 'en_stationnement']:
            # Appeler la méthode du modèle si elle existe
            if hasattr(mission, 'marquer_dechargement'):
                mission.marquer_dechargement()
            else:
                mission.statut_stationnement = 'decharge'
                mission.date_dechargement = timezone.now().date()
                mission.save()
            return Response({
                'status': 'Déchargement marqué',
                'statut_stationnement': mission.statut_stationnement,
                'date_dechargement': str(mission.date_dechargement),
                'jours_facturables': mission.jours_stationnement_facturables if hasattr(mission, 'jours_stationnement_facturables') else 0,
                'montant_stationnement': float(mission.montant_stationnement) if mission.montant_stationnement else 0
            })
        return Response({
            'error': f'Déjà déchargé ou statut invalide: {mission.statut_stationnement}'
        }, status=400)


class MissionConteneurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les conteneurs de mission"""
    queryset = MissionConteneur.objects.select_related('mission', 'conteneur').all()
    serializer_class = MissionConteneurSerializer
    permission_classes = [IsAuthenticated]


class FraisTrajetViewSet(viewsets.ModelViewSet):
    """API endpoint pour les frais de trajet"""
    queryset = FraisTrajet.objects.select_related('mission', 'contrat').all()
    serializer_class = FraisTrajetSerializer
    permission_classes = [IsAuthenticated]


# =============================================================================
# VIEWSETS FINANCES
# =============================================================================

class CautionsViewSet(viewsets.ModelViewSet):
    """API endpoint pour les cautions"""
    queryset = Cautions.objects.select_related(
        'conteneur', 'contrat', 'transitaire', 'client', 'chauffeur', 'camion'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_creation', 'montant']

    def get_serializer_class(self):
        if self.action == 'list':
            return CautionsListSerializer
        return CautionsSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset


class PaiementMissionViewSet(viewsets.ModelViewSet):
    """API endpoint pour les paiements de mission"""
    queryset = PaiementMission.objects.select_related('mission', 'caution', 'prestation').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_paiement', 'montant_total']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaiementMissionListSerializer
        return PaiementMissionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        est_valide = self.request.query_params.get('est_valide')
        if est_valide is not None:
            queryset = queryset.filter(est_valide=est_valide.lower() == 'true')
        return queryset

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Valide un paiement"""
        paiement = self.get_object()
        try:
            paiement.valider_paiement()
            return Response({'status': 'Paiement validé'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


# =============================================================================
# VIEWSETS SALAIRES
# =============================================================================

class SalaireViewSet(viewsets.ModelViewSet):
    """API endpoint pour les salaires"""
    queryset = Salaire.objects.select_related('chauffeur').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['annee', 'mois', 'salaire_net']

    def get_serializer_class(self):
        if self.action == 'list':
            return SalaireListSerializer
        return SalaireSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        chauffeur = self.request.query_params.get('chauffeur')
        if chauffeur:
            queryset = queryset.filter(chauffeur__pk_chauffeur=chauffeur)
        annee = self.request.query_params.get('annee')
        if annee:
            queryset = queryset.filter(annee=annee)
        return queryset


class PrimeViewSet(viewsets.ModelViewSet):
    """API endpoint pour les primes"""
    queryset = Prime.objects.select_related('salaire').all()
    serializer_class = PrimeSerializer
    permission_classes = [IsAuthenticated]


class DeductionViewSet(viewsets.ModelViewSet):
    """API endpoint pour les déductions"""
    queryset = Deduction.objects.select_related('salaire').all()
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]


# =============================================================================
# VIEWSETS AUDIT & NOTIFICATIONS
# =============================================================================

class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint pour les notifications"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    def get_queryset(self):
        # Retourner uniquement les notifications de l'utilisateur connecté
        return Notification.objects.filter(utilisateur=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marque toutes les notifications comme lues"""
        Notification.objects.filter(
            utilisateur=request.user, is_read=False
        ).update(is_read=True)
        return Response({'status': 'Toutes les notifications marquées comme lues'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marque une notification comme lue"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marquée comme lue'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Retourne le nombre de notifications non lues"""
        count = Notification.objects.filter(
            utilisateur=request.user, is_read=False
        ).count()
        return Response({'count': count})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint pour les logs d'audit (lecture seule)"""
    queryset = AuditLog.objects.select_related('utilisateur').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action', 'model_name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


# =============================================================================
# API DASHBOARD
# =============================================================================

class DashboardAPIView(APIView):
    """API endpoint pour les statistiques du dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Missions
        total_missions = Mission.objects.count()
        missions_en_cours = Mission.objects.filter(statut='en_cours').count()
        missions_terminees = Mission.objects.filter(statut='terminee').count()

        # Paiements
        paiements = PaiementMission.objects.aggregate(
            total=Sum('montant_total'),
            en_attente=Count('pk_paiement', filter=Q(est_valide=False))
        )

        # Cautions
        cautions = Cautions.objects.aggregate(
            total=Sum('montant'),
            bloquees=Count('pk_caution', filter=Q(statut='bloquee'))
        )

        # Chauffeurs
        total_chauffeurs = Chauffeur.objects.count()
        chauffeurs_affectes = Chauffeur.objects.filter(est_affecter=True).count()

        # Camions
        total_camions = Camion.objects.count()
        camions_affectes = Camion.objects.filter(est_affecter=True).count()

        data = {
            'total_missions': total_missions,
            'missions_en_cours': missions_en_cours,
            'missions_terminees': missions_terminees,
            'total_paiements': paiements['total'] or 0,
            'paiements_en_attente': paiements['en_attente'] or 0,
            'total_cautions': cautions['total'] or 0,
            'cautions_bloquees': cautions['bloquees'] or 0,
            'total_chauffeurs': total_chauffeurs,
            'chauffeurs_affectes': chauffeurs_affectes,
            'total_camions': total_camions,
            'camions_affectes': camions_affectes,
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)
