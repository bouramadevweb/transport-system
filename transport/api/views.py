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
from django.db.models import Sum, Count, Q, Exists, OuterRef
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
    serializer_class = EntrepriseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email_contact']
    ordering_fields = ['nom', 'date_creation']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'entreprise') and user.entreprise:
            return Entreprise.objects.filter(pk_entreprise=user.entreprise.pk_entreprise)
        return Entreprise.objects.none()


class UtilisateurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les utilisateurs"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'nom_utilisateur']
    ordering_fields = ['nom_utilisateur', 'date_joined']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'entreprise') and user.entreprise:
            return Utilisateur.objects.filter(entreprise=user.entreprise)
        return Utilisateur.objects.none()

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
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Chauffeur.objects.none()
        # Annotation : en_mission_active = True si le chauffeur a une mission 'en cours'
        en_mission = Mission.objects.filter(
            statut='en cours',
            contrat__chauffeur=OuterRef('pk'),
        )
        queryset = Chauffeur.objects.filter(
            entreprise=user.entreprise
        ).select_related('entreprise').annotate(
            en_mission_active=Exists(en_mission)
        )
        est_affecter = self.request.query_params.get('est_affecter')
        if est_affecter is not None:
            queryset = queryset.filter(en_mission_active=est_affecter.lower() == 'true')
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            queryset = queryset.filter(en_mission_active=False)
        return queryset

    def perform_create(self, serializer):
        serializer.save(entreprise=self.request.user.entreprise)

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
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'telephone']

    def get_serializer_class(self):
        if self.action == 'create':
            return MecanicienCreateSerializer
        return MecanicienSerializer

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Mecanicien.objects.none()
        return Mecanicien.objects.filter(entreprise=user.entreprise)


class AffectationViewSet(viewsets.ModelViewSet):
    """API endpoint pour les affectations chauffeur-camion"""
    serializer_class = AffectationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_affectation', 'date_fin_affectation']

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Affectation.objects.none()
        queryset = Affectation.objects.filter(
            chauffeur__entreprise=user.entreprise
        ).select_related('chauffeur', 'camion')
        actives = self.request.query_params.get('actives')
        if actives and actives.lower() == 'true':
            queryset = queryset.filter(date_fin_affectation__isnull=True)
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

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Camion.objects.none()
        # Annotation : en_mission_active = True si le camion a une mission 'en cours'
        en_mission = Mission.objects.filter(
            statut='en cours',
            contrat__camion=OuterRef('pk'),
        )
        queryset = Camion.objects.filter(
            entreprise=user.entreprise
        ).select_related('entreprise').annotate(
            en_mission_active=Exists(en_mission)
        )
        est_affecter = self.request.query_params.get('est_affecter')
        if est_affecter is not None:
            queryset = queryset.filter(en_mission_active=est_affecter.lower() == 'true')
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            queryset = queryset.filter(en_mission_active=False)
        return queryset

    def perform_create(self, serializer):
        serializer.save(entreprise=self.request.user.entreprise)

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

    def get_queryset(self):
        return CompagnieConteneur.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CompagnieConteneurCreateSerializer
        return CompagnieConteneurSerializer


class ConteneurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les conteneurs"""
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
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Conteneur.objects.none()
        # Conteneur n'a pas de FK entreprise directe — filtrer via ContratTransport
        queryset = Conteneur.objects.filter(
            contrattransport__entreprise=user.entreprise
        ).select_related('compagnie', 'client').distinct()
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            conteneurs_en_mission = Mission.objects.filter(
                statut='en cours'
            ).values_list('contrat__conteneur_id', flat=True)
            queryset = queryset.exclude(pk_conteneur__in=conteneurs_en_mission)
        return queryset


class ReparationViewSet(viewsets.ModelViewSet):
    """API endpoint pour les réparations"""
    serializer_class = ReparationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_reparation']

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Reparation.objects.none()
        return Reparation.objects.filter(
            camion__entreprise=user.entreprise
        ).select_related('camion')


class FournisseurViewSet(viewsets.ModelViewSet):
    """API endpoint pour les fournisseurs"""
    serializer_class = FournisseurSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'telephone']

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Fournisseur.objects.none()
        return Fournisseur.objects.filter(entreprise=user.entreprise)


# =============================================================================
# VIEWSETS COMMERCIAL
# =============================================================================

class TransitaireViewSet(viewsets.ModelViewSet):
    """API endpoint pour les transitaires"""
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

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Transitaire.objects.none()
        return Transitaire.objects.filter(entreprise=user.entreprise)

    def perform_create(self, serializer):
        serializer.save(entreprise=self.request.user.entreprise)


class ClientViewSet(viewsets.ModelViewSet):
    """API endpoint pour les clients"""
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

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Client.objects.none()
        return Client.objects.filter(entreprise=user.entreprise)

    def perform_create(self, serializer):
        serializer.save(entreprise=self.request.user.entreprise)


# =============================================================================
# VIEWSETS CONTRATS
# =============================================================================

class PrestationDeTransportsViewSet(viewsets.ModelViewSet):
    """API endpoint pour les prestations de transport"""
    serializer_class = PrestationDeTransportsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return PrestationDeTransports.objects.none()
        return PrestationDeTransports.objects.filter(
            contrat_transport__entreprise=user.entreprise
        ).select_related('contrat_transport')


class ContratTransportViewSet(viewsets.ModelViewSet):
    """API endpoint pour les contrats de transport"""
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
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return ContratTransport.objects.none()
        queryset = ContratTransport.objects.filter(entreprise=user.entreprise).select_related(
            'client', 'transitaire', 'chauffeur', 'camion', 'entreprise'
        )
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

        from django.utils.html import escape as _esc
        story.append(Paragraph(f"<b>DESTINATAIRE :</b> {_esc(str(contrat.destinataire or ''))}", styles["Normal"]))
        story.append(Paragraph(f"<b>N° BL :</b> {_esc(str(contrat.numero_bl or ''))}", styles["Normal"]))
        story.append(Paragraph(f"<b>N° CONTENEUR(S) :</b> {_esc(contrat.conteneur.numero_conteneur)}", styles["Normal"]))
        story.append(Paragraph(
            f"<b>NOM DU CHAUFFEUR :</b> {_esc(contrat.chauffeur.nom)} {_esc(contrat.chauffeur.prenom)} — Tel {_esc(str(contrat.chauffeur.telephone or ''))}",
            styles["Normal"]
        ))
        story.append(Paragraph(f"<b>NUMÉRO CAMION :</b> {_esc(contrat.camion.immatriculation)}", styles["Normal"]))
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
    queryset = Mission.objects.none()
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
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Mission.objects.none()
        queryset = Mission.objects.filter(
            contrat__entreprise=user.entreprise
        ).select_related('prestation_transport', 'contrat', 'contrat__chauffeur', 'contrat__camion')
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset

    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Termine une mission via la méthode du modèle (cascade + retour conteneur)"""
        mission = self.get_object()
        if mission.statut == 'terminée':
            return Response({'error': 'Cette mission est déjà terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        if mission.statut == 'annulée':
            return Response({'error': 'Impossible de terminer une mission annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            date_retour_str = request.data.get('date_retour')
            date_retour = None
            if date_retour_str:
                from datetime import datetime
                date_retour = datetime.strptime(date_retour_str, '%Y-%m-%d').date()
            force = request.data.get('force', False)
            result = mission.terminer_mission(date_retour=date_retour, force=bool(force))
            return Response({'status': 'Mission terminée', 'details': result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annule une mission via la méthode du modèle (cascade cautions + paiements)"""
        mission = self.get_object()
        if mission.statut == 'annulée':
            return Response({'error': 'Cette mission est déjà annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        if mission.statut == 'terminée':
            return Response({'error': 'Impossible d\'annuler une mission déjà terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            raison = request.data.get('raison', '')
            mission.annuler_mission(raison=raison)
            return Response({'status': 'Mission annulée'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_200_OK)
        return Response({
            'error': f'Impossible de bloquer: statut actuel = {mission.statut_stationnement}'
        }, status=status.HTTP_400_BAD_REQUEST)

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
    serializer_class = MissionConteneurSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return MissionConteneur.objects.none()
        return MissionConteneur.objects.filter(
            mission__contrat__entreprise=user.entreprise
        ).select_related('mission', 'conteneur')


class FraisTrajetViewSet(viewsets.ModelViewSet):
    """API endpoint pour les frais de trajet"""
    serializer_class = FraisTrajetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return FraisTrajet.objects.none()
        return FraisTrajet.objects.filter(
            contrat__entreprise=user.entreprise
        ).select_related('mission', 'contrat')


# =============================================================================
# VIEWSETS FINANCES
# =============================================================================

class CautionsViewSet(viewsets.ModelViewSet):
    """API endpoint pour les cautions"""
    queryset = Cautions.objects.none()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['montant']

    def get_serializer_class(self):
        if self.action == 'list':
            return CautionsListSerializer
        return CautionsSerializer

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Cautions.objects.none()
        queryset = Cautions.objects.filter(
            contrat__entreprise=user.entreprise
        ).select_related('conteneur', 'contrat', 'transitaire', 'client', 'chauffeur', 'camion')
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset


class PaiementMissionViewSet(viewsets.ModelViewSet):
    """API endpoint pour les paiements de mission"""
    queryset = PaiementMission.objects.none()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_paiement', 'montant_total']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaiementMissionListSerializer
        return PaiementMissionSerializer

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return PaiementMission.objects.none()
        queryset = PaiementMission.objects.filter(
            mission__contrat__entreprise=user.entreprise
        ).select_related('mission', 'caution', 'prestation')
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
            return Response({'status': 'Paiement validé'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# VIEWSETS SALAIRES
# =============================================================================

class SalaireViewSet(viewsets.ModelViewSet):
    """API endpoint pour les salaires"""
    queryset = Salaire.objects.none()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['annee', 'mois', 'salaire_net']

    def get_serializer_class(self):
        if self.action == 'list':
            return SalaireListSerializer
        return SalaireSerializer

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Salaire.objects.none()
        queryset = Salaire.objects.filter(
            chauffeur__entreprise=user.entreprise
        ).select_related('chauffeur')
        chauffeur = self.request.query_params.get('chauffeur')
        if chauffeur:
            queryset = queryset.filter(chauffeur__pk_chauffeur=chauffeur)
        annee = self.request.query_params.get('annee')
        if annee:
            queryset = queryset.filter(annee=annee)
        return queryset


class PrimeViewSet(viewsets.ModelViewSet):
    """API endpoint pour les primes"""
    serializer_class = PrimeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Prime.objects.none()
        return Prime.objects.filter(
            salaire__chauffeur__entreprise=user.entreprise
        ).select_related('salaire')


class DeductionViewSet(viewsets.ModelViewSet):
    """API endpoint pour les déductions"""
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Deduction.objects.none()
        return Deduction.objects.filter(
            salaire__chauffeur__entreprise=user.entreprise
        ).select_related('salaire')


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
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action', 'model_name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return AuditLog.objects.none()
        return AuditLog.objects.filter(
            utilisateur__entreprise=user.entreprise
        ).select_related('utilisateur')


# =============================================================================
# API DASHBOARD
# =============================================================================

class DashboardAPIView(APIView):
    """API endpoint pour les statistiques du dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (hasattr(user, 'entreprise') and user.entreprise):
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        entreprise = user.entreprise

        # Missions
        total_missions = Mission.objects.filter(contrat__entreprise=entreprise).count()
        missions_en_cours = Mission.objects.filter(contrat__entreprise=entreprise, statut='en cours').count()
        missions_terminees = Mission.objects.filter(contrat__entreprise=entreprise, statut='terminée').count()

        # Paiements
        paiements = PaiementMission.objects.filter(
            mission__contrat__entreprise=entreprise
        ).aggregate(
            total=Sum('montant_total'),
            en_attente=Count('pk_paiement', filter=Q(est_valide=False))
        )

        # Cautions
        cautions = Cautions.objects.filter(
            contrat__entreprise=entreprise
        ).aggregate(
            total=Sum('montant'),
            bloquees=Count('pk_caution', filter=Q(statut='bloquee'))
        )

        today = timezone.now().date()

        # Missions ce mois
        this_month_start = today.replace(day=1)
        missions_ce_mois = Mission.objects.filter(
            contrat__entreprise=entreprise,
            date_depart__gte=this_month_start,
        ).count()

        # Revenus ce mois (paiements validés)
        revenus_ce_mois = PaiementMission.objects.filter(
            mission__contrat__entreprise=entreprise,
            date_paiement__gte=this_month_start,
            est_valide=True,
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        # Chauffeurs — affectés = ont une mission 'en cours'
        total_chauffeurs = Chauffeur.objects.filter(entreprise=entreprise).count()
        chauffeurs_affectes = Chauffeur.objects.filter(
            entreprise=entreprise,
            contrattransport__mission__statut='en cours',
        ).distinct().count()
        chauffeurs_disponibles = total_chauffeurs - chauffeurs_affectes

        # Camions — affectés = ont une mission 'en cours'
        total_camions = Camion.objects.filter(entreprise=entreprise).count()
        camions_affectes = Camion.objects.filter(
            entreprise=entreprise,
            contrattransport__mission__statut='en cours',
        ).distinct().count()
        camions_disponibles = total_camions - camions_affectes

        # Réparations
        total_reparations = Reparation.objects.filter(camion__entreprise=entreprise).count()
        reparations_en_cours = Reparation.objects.filter(
            camion__entreprise=entreprise,
            date_reparation__gte=this_month_start,
        ).count()

        # Contrats
        total_contrats = ContratTransport.objects.filter(entreprise=entreprise).count()
        contrats_actifs = ContratTransport.objects.filter(entreprise=entreprise, statut='actif').count()

        # Clients
        total_clients = Client.objects.filter(entreprise=entreprise).count()

        # Paiements validés
        paiements_valides = PaiementMission.objects.filter(
            mission__contrat__entreprise=entreprise,
            est_valide=True,
        ).count()

        # Chiffre d'affaires = somme de tous les montants contractuels
        chiffre_affaires = ContratTransport.objects.filter(
            entreprise=entreprise,
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        # Salaires en attente (statut brouillon)
        salaires_en_attente = Salaire.objects.filter(
            chauffeur__entreprise=entreprise,
            statut='brouillon',
        ).count()

        data = {
            'total_missions': total_missions,
            'missions_en_cours': missions_en_cours,
            'missions_terminees': missions_terminees,
            'missions_ce_mois': missions_ce_mois,
            'total_paiements': paiements['total'] or 0,
            'paiements_en_attente': paiements['en_attente'] or 0,
            'paiements_valides': paiements_valides,
            'revenus_ce_mois': revenus_ce_mois,
            'chiffre_affaires': chiffre_affaires,
            'total_cautions': cautions['total'] or 0,
            'cautions_bloquees': cautions['bloquees'] or 0,
            'total_chauffeurs': total_chauffeurs,
            'chauffeurs_affectes': chauffeurs_affectes,
            'chauffeurs_disponibles': chauffeurs_disponibles,
            'total_camions': total_camions,
            'camions_affectes': camions_affectes,
            'camions_disponibles': camions_disponibles,
            'reparations_en_cours': reparations_en_cours,
            'total_reparations': total_reparations,
            'total_contrats': total_contrats,
            'contrats_actifs': contrats_actifs,
            'total_clients': total_clients,
            'salaires_en_attente': salaires_en_attente,
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)
