"""
Serializers pour l'API REST du système de transport.
Convertit les modèles Django en JSON pour React Native.
"""

from rest_framework import serializers

from transport.models import (
    # User & Entreprise
    Entreprise,
    Utilisateur,
    # Personnel
    Chauffeur,
    Mecanicien,
    Affectation,
    # Salary
    Salaire,
    Prime,
    Deduction,
    # Vehicles
    Camion,
    CompagnieConteneur,
    Conteneur,
    Reparation,
    ReparationMecanicien,
    PieceReparee,
    Fournisseur,
    # Commercial
    Transitaire,
    Client,
    # Missions
    FraisTrajet,
    Mission,
    MissionConteneur,
    # Contrats
    ContratTransport,
    PrestationDeTransports,
    # Finances
    Cautions,
    PaiementMission,
    # Audit
    Notification,
    AuditLog,
)


# =============================================================================
# SERIALIZERS UTILISATEUR & ENTREPRISE
# =============================================================================

class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entreprise
        fields = '__all__'


class UtilisateurSerializer(serializers.ModelSerializer):
    entreprise_nom = serializers.CharField(source='entreprise.nom', read_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'pk_utilisateur', 'email', 'nom_utilisateur', 'role',
            'entreprise', 'entreprise_nom', 'is_active', 'date_joined'
        ]
        read_only_fields = ['pk_utilisateur', 'date_joined']


class UtilisateurCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'email', 'nom_utilisateur', 'password', 'password_confirm',
            'role', 'entreprise'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Utilisateur(**validated_data)
        user.set_password(password)
        user.save()
        return user


# =============================================================================
# SERIALIZERS PERSONNEL
# =============================================================================

class ChauffeurSerializer(serializers.ModelSerializer):
    entreprise_nom = serializers.CharField(source='entreprise.nom', read_only=True)
    camion_actuel = serializers.SerializerMethodField()

    class Meta:
        model = Chauffeur
        fields = '__all__'

    def get_camion_actuel(self, obj):
        camion = obj.get_camion_actuel()
        if camion:
            return {
                'pk': camion.pk_camion,
                'immatriculation': camion.immatriculation,
                'modele': camion.modele
            }
        return None


class ChauffeurListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    entreprise_nom = serializers.CharField(source='entreprise.nom', read_only=True, default=None)

    class Meta:
        model = Chauffeur
        fields = ['pk_chauffeur', 'nom', 'prenom', 'telephone', 'email', 'est_affecter', 'entreprise_nom']


class ChauffeurCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de chauffeur avec valeurs par défaut"""
    est_affecter = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Chauffeur
        fields = ['nom', 'prenom', 'telephone', 'email', 'entreprise', 'est_affecter']
        extra_kwargs = {
            'telephone': {'required': False, 'allow_blank': True, 'allow_null': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class MecanicienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mecanicien
        fields = '__all__'


class MecanicienCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de mécanicien"""
    class Meta:
        model = Mecanicien
        fields = ['nom', 'telephone', 'email']
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class AffectationSerializer(serializers.ModelSerializer):
    chauffeur_nom = serializers.CharField(source='chauffeur.__str__', read_only=True)
    camion_immat = serializers.CharField(source='camion.immatriculation', read_only=True)

    class Meta:
        model = Affectation
        fields = '__all__'


# =============================================================================
# SERIALIZERS VEHICULES
# =============================================================================

class CamionSerializer(serializers.ModelSerializer):
    entreprise_nom = serializers.CharField(source='entreprise.nom', read_only=True)

    class Meta:
        model = Camion
        fields = '__all__'


class CamionListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    class Meta:
        model = Camion
        fields = ['pk_camion', 'immatriculation', 'modele', 'capacite_tonnes', 'est_affecter']


class CamionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de camion avec valeurs par défaut"""
    est_affecter = serializers.BooleanField(default=False, required=False)
    capacite_tonnes = serializers.DecimalField(max_digits=5, decimal_places=2, default=0, required=False)

    class Meta:
        model = Camion
        fields = ['immatriculation', 'modele', 'capacite_tonnes', 'entreprise', 'est_affecter']
        extra_kwargs = {
            'modele': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class CompagnieConteneurSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompagnieConteneur
        fields = '__all__'


class CompagnieConteneurCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de compagnie conteneur"""
    class Meta:
        model = CompagnieConteneur
        fields = ['nom']


class ConteneurSerializer(serializers.ModelSerializer):
    compagnie_nom = serializers.CharField(source='compagnie.nom', read_only=True)
    client_nom = serializers.CharField(source='client.nom', read_only=True)

    class Meta:
        model = Conteneur
        fields = '__all__'


class ConteneurListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    compagnie_nom = serializers.CharField(source='compagnie.nom', read_only=True)
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    transitaire_nom = serializers.CharField(source='transitaire.nom', read_only=True)

    class Meta:
        model = Conteneur
        fields = ['pk_conteneur', 'numero_conteneur', 'type_conteneur', 'poids', 'compagnie_nom', 'client', 'client_nom', 'transitaire', 'transitaire_nom', 'statut']


class ConteneurCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de conteneur"""
    poids = serializers.DecimalField(max_digits=6, decimal_places=2, default=0, required=False)

    class Meta:
        model = Conteneur
        fields = ['numero_conteneur', 'compagnie', 'type_conteneur', 'poids', 'client', 'transitaire']
        extra_kwargs = {
            'type_conteneur': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'


class PieceRepareeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceReparee
        fields = '__all__'


class ReparationMecanicienSerializer(serializers.ModelSerializer):
    mecanicien_nom = serializers.CharField(source='mecanicien.__str__', read_only=True)

    class Meta:
        model = ReparationMecanicien
        fields = '__all__'


class ReparationSerializer(serializers.ModelSerializer):
    camion_immat = serializers.CharField(source='camion.immatriculation', read_only=True)
    pieces = PieceRepareeSerializer(many=True, read_only=True, source='piecereparee_set')
    mecaniciens = ReparationMecanicienSerializer(many=True, read_only=True, source='reparationmecanicien_set')

    class Meta:
        model = Reparation
        fields = '__all__'


# =============================================================================
# SERIALIZERS COMMERCIAL
# =============================================================================

class TransitaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transitaire
        fields = '__all__'


class TransitaireListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    class Meta:
        model = Transitaire
        fields = ['pk_transitaire', 'nom', 'telephone', 'email']


class TransitaireCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de transitaire"""
    score_fidelite = serializers.IntegerField(default=100, required=False)
    etat_paiement = serializers.CharField(default='bon', required=False)

    class Meta:
        model = Transitaire
        fields = ['nom', 'telephone', 'email', 'score_fidelite', 'etat_paiement', 'commentaire']
        extra_kwargs = {
            'telephone': {'required': False, 'allow_blank': True, 'allow_null': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
            'commentaire': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de client avec valeurs par défaut"""
    score_fidelite = serializers.IntegerField(default=100, required=False)
    etat_paiement = serializers.CharField(default='bon', required=False)

    class Meta:
        model = Client
        fields = ['nom', 'type_client', 'telephone', 'email', 'score_fidelite', 'etat_paiement', 'commentaire']
        extra_kwargs = {
            'telephone': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
            'commentaire': {'required': False, 'allow_blank': True},
        }


class ClientListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    class Meta:
        model = Client
        fields = ['pk_client', 'nom', 'type_client', 'telephone']


# =============================================================================
# SERIALIZERS CONTRATS & PRESTATIONS
# =============================================================================

class PrestationDeTransportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrestationDeTransports
        fields = '__all__'


class ContratTransportSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    transitaire_nom = serializers.CharField(source='transitaire.nom', read_only=True)
    chauffeur_nom = serializers.CharField(source='chauffeur.__str__', read_only=True)
    camion_immat = serializers.CharField(source='camion.immatriculation', read_only=True)
    conteneur_numero = serializers.CharField(source='conteneur.numero_conteneur', read_only=True)

    class Meta:
        model = ContratTransport
        fields = '__all__'


class ContratTransportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de contrat"""
    avance_transport = serializers.DecimalField(max_digits=12, decimal_places=2, default=0, required=False)
    caution = serializers.DecimalField(max_digits=12, decimal_places=2, default=0, required=False)
    reliquat_transport = serializers.DecimalField(max_digits=12, decimal_places=2, default=0, required=False)
    lieu_chargement = serializers.CharField(default='Bamako', required=False)
    date_limite_retour = serializers.DateField(required=False, allow_null=True)
    statut_caution = serializers.CharField(default='bloquee', required=False)
    commentaire = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ContratTransport
        fields = [
            'numero_bl', 'lieu_chargement', 'destinataire',
            'conteneur', 'client', 'transitaire', 'entreprise', 'camion', 'chauffeur',
            'montant_total', 'avance_transport', 'reliquat_transport', 'caution',
            'statut_caution', 'date_debut', 'date_limite_retour', 'commentaire',
        ]


class ContratTransportListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    transitaire_nom = serializers.CharField(source='transitaire.nom', read_only=True, default=None)

    class Meta:
        model = ContratTransport
        fields = [
            'pk_contrat', 'numero_bl', 'date_debut', 'date_limite_retour',
            'montant_total', 'statut', 'statut_caution', 'client_nom', 'transitaire_nom',
            'lieu_chargement', 'destinataire',
        ]


# =============================================================================
# SERIALIZERS MISSIONS
# =============================================================================

class FraisTrajetSerializer(serializers.ModelSerializer):
    camion_immat = serializers.CharField(source='contrat.camion.immatriculation', read_only=True, default=None)
    chauffeur_nom = serializers.SerializerMethodField()
    mission_pk_short = serializers.SerializerMethodField()
    total_frais = serializers.SerializerMethodField()

    class Meta:
        model = FraisTrajet
        fields = '__all__'

    def get_chauffeur_nom(self, obj):
        try:
            if obj.contrat and obj.contrat.chauffeur:
                c = obj.contrat.chauffeur
                return f"{c.nom} {c.prenom}"
        except Exception:
            pass
        return None

    def get_mission_pk_short(self, obj):
        try:
            if obj.mission:
                return str(obj.mission.pk_mission)[:20]
        except Exception:
            pass
        return None

    def get_total_frais(self, obj):
        try:
            return float((obj.frais_route or 0) + (obj.frais_carburant or 0))
        except Exception:
            return 0


class MissionConteneurSerializer(serializers.ModelSerializer):
    conteneur_numero = serializers.CharField(source='conteneur.numero_conteneur', read_only=True)

    class Meta:
        model = MissionConteneur
        fields = '__all__'


class MissionSerializer(serializers.ModelSerializer):
    prestation_info = PrestationDeTransportsSerializer(source='prestation_transport', read_only=True)
    conteneurs = MissionConteneurSerializer(many=True, read_only=True, source='missionconteneur_set')
    frais = FraisTrajetSerializer(many=True, read_only=True, source='fraistrajet_set')
    chauffeur_nom = serializers.SerializerMethodField()
    camion_immat = serializers.SerializerMethodField()
    contrat_numero_bl = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = '__all__'

    def get_chauffeur_nom(self, obj):
        try:
            if obj.contrat and obj.contrat.chauffeur:
                return str(obj.contrat.chauffeur)
        except Exception:
            pass
        return None

    def get_camion_immat(self, obj):
        try:
            if obj.contrat and obj.contrat.camion:
                return obj.contrat.camion.immatriculation
        except Exception:
            pass
        return None

    def get_contrat_numero_bl(self, obj):
        try:
            if obj.contrat:
                return obj.contrat.numero_bl
        except Exception:
            pass
        return None


class MissionListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    chauffeur_nom = serializers.SerializerMethodField()
    camion_immat = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    origine = serializers.CharField(read_only=True)
    destination = serializers.CharField(read_only=True)
    statut_stationnement = serializers.CharField(read_only=True)

    class Meta:
        model = Mission
        fields = [
            'pk_mission', 'date_depart', 'date_retour', 'date_arrivee',
            'statut', 'statut_display', 'chauffeur_nom', 'camion_immat',
            'origine', 'destination', 'statut_stationnement',
            'jours_stationnement_facturables', 'montant_stationnement'
        ]

    def get_chauffeur_nom(self, obj):
        try:
            if obj.contrat and obj.contrat.chauffeur:
                return str(obj.contrat.chauffeur)
        except Exception:
            pass
        return None

    def get_camion_immat(self, obj):
        try:
            if obj.contrat and obj.contrat.camion:
                return obj.contrat.camion.immatriculation
        except Exception:
            pass
        return None


class MissionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de mission"""
    class Meta:
        model = Mission
        fields = ['prestation', 'date_depart', 'date_retour']


# =============================================================================
# SERIALIZERS FINANCES
# =============================================================================

class CautionsSerializer(serializers.ModelSerializer):
    conteneur_numero = serializers.CharField(source='conteneur.numero_conteneur', read_only=True)
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    transitaire_nom = serializers.CharField(source='transitaire.nom', read_only=True)

    class Meta:
        model = Cautions
        fields = '__all__'


class CautionsListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    conteneur_numero = serializers.CharField(source='conteneur.numero_conteneur', read_only=True)

    class Meta:
        model = Cautions
        fields = ['pk_caution', 'montant', 'statut', 'montant_rembourser', 'client_nom', 'conteneur_numero']


class PaiementMissionSerializer(serializers.ModelSerializer):
    mission_info = MissionListSerializer(source='mission', read_only=True)
    caution_info = CautionsListSerializer(source='caution', read_only=True)

    class Meta:
        model = PaiementMission
        fields = '__all__'


class PaiementMissionListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    mission_pk = serializers.CharField(source='mission.pk_mission', read_only=True)
    mission_origine = serializers.CharField(source='mission.origine', read_only=True, default=None)
    mission_destination = serializers.CharField(source='mission.destination', read_only=True, default=None)
    chauffeur_nom = serializers.SerializerMethodField()

    class Meta:
        model = PaiementMission
        fields = [
            'pk_paiement', 'mission_pk', 'mission_origine', 'mission_destination',
            'chauffeur_nom', 'montant_total', 'frais_stationnement',
            'commission_transitaire', 'est_valide', 'statut_paiement', 'date_paiement'
        ]

    def get_chauffeur_nom(self, obj):
        try:
            if obj.mission and obj.mission.contrat and obj.mission.contrat.chauffeur:
                c = obj.mission.contrat.chauffeur
                return f"{c.nom} {c.prenom}"
        except Exception:
            pass
        return None


# =============================================================================
# SERIALIZERS SALAIRES
# =============================================================================

class PrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prime
        fields = '__all__'


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'


class SalaireSerializer(serializers.ModelSerializer):
    chauffeur_nom = serializers.CharField(source='chauffeur.__str__', read_only=True)
    primes = PrimeSerializer(many=True, read_only=True, source='prime_set')
    deductions = DeductionSerializer(many=True, read_only=True, source='deduction_set')

    class Meta:
        model = Salaire
        fields = '__all__'


class SalaireListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    chauffeur_nom = serializers.CharField(source='chauffeur.__str__', read_only=True)

    class Meta:
        model = Salaire
        fields = [
            'pk_salaire', 'chauffeur_nom', 'mois', 'annee',
            'salaire_base', 'salaire_net', 'statut'
        ]


# =============================================================================
# SERIALIZERS AUDIT & NOTIFICATIONS
# =============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    class Meta:
        model = Notification
        fields = ['id', 'message', 'type_notification', 'is_read', 'icon', 'color', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_utilisateur', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'utilisateur', 'utilisateur_nom',
            'action', 'model_name', 'object_id',
            'timestamp', 'ip_address',
        ]
        read_only_fields = fields


# =============================================================================
# SERIALIZERS DASHBOARD / STATISTIQUES
# =============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques du dashboard"""
    total_missions = serializers.IntegerField()
    missions_en_cours = serializers.IntegerField()
    missions_terminees = serializers.IntegerField()
    total_paiements = serializers.DecimalField(max_digits=15, decimal_places=2)
    paiements_en_attente = serializers.IntegerField()
    total_cautions = serializers.DecimalField(max_digits=15, decimal_places=2)
    cautions_bloquees = serializers.IntegerField()
    total_chauffeurs = serializers.IntegerField()
    chauffeurs_affectes = serializers.IntegerField()
    total_camions = serializers.IntegerField()
    camions_affectes = serializers.IntegerField()
