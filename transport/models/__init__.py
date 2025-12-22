"""
Module de modèles refactorisé pour l'application transport.

Ce module organise les modèles en sous-modules logiques pour une meilleure maintenabilité.
Tous les modèles sont ré-exportés ici pour maintenir la compatibilité avec les imports existants.
"""

# Import des constantes et choix
from .choices import (
    STATUT_ENTREPRISE_CHOICES,
    ROLE_UTILISATEUR_CHOICES,
    FIABILITE_CHOICES,
    ETAT_PAIEMENT_CHOICES,
    TYPE_CLIENT_CHOICES,
    STATUT_CONTENEUR_CHOICES,
    STATUT_CAUTION_CONTRAT_CHOICES,
    STATUT_MISSION_CHOICES,
    STATUT_CAUTION_CHOICES,
    MOIS_CHOICES,
    STATUT_SALAIRE_CHOICES,
    MODE_PAIEMENT_SALAIRE_CHOICES,
)

# Import des modèles utilisateur
from .user import (
    UtilisateurManager,
    Entreprise,
    Utilisateur,
)

# Import des modèles personnel
from .personnel import (
    Chauffeur,
    Mecanicien,
    Affectation,
)

# Import des modèles salaire
from .salary import (
    Salaire,
    Prime,
    Deduction,
)

# Import des modèles véhicules
from .vehicle import (
    Camion,
    CompagnieConteneur,
    Conteneur,
    Reparation,
    ReparationMecanicien,
    PieceReparee,
    Fournisseur,
)

# Import des modèles commerciaux
from .commercial import (
    Transitaire,
    Client,
)

# Import des modèles missions
from .mission import (
    FraisTrajet,
    Mission,
    MissionConteneur,
)

# Import des modèles contrats
from .contrat import (
    ContratTransport,
    PrestationDeTransports,
)

# Import des modèles finances
from .finance import (
    Cautions,
    PaiementMission,
)

# Import des modèles audit
from .audit import (
    Notification,
    AuditLog,
)

__all__ = [
    # Choices
    'STATUT_ENTREPRISE_CHOICES',
    'ROLE_UTILISATEUR_CHOICES',
    'FIABILITE_CHOICES',
    'ETAT_PAIEMENT_CHOICES',
    'TYPE_CLIENT_CHOICES',
    'STATUT_CONTENEUR_CHOICES',
    'STATUT_CAUTION_CONTRAT_CHOICES',
    'STATUT_MISSION_CHOICES',
    'STATUT_CAUTION_CHOICES',
    'MOIS_CHOICES',
    'STATUT_SALAIRE_CHOICES',
    'MODE_PAIEMENT_SALAIRE_CHOICES',

    # User
    'UtilisateurManager',
    'Entreprise',
    'Utilisateur',

    # Personnel
    'Chauffeur',
    'Mecanicien',
    'Affectation',

    # Salary
    'Salaire',
    'Prime',
    'Deduction',

    # Véhicules
    'Camion',
    'CompagnieConteneur',
    'Conteneur',
    'Reparation',
    'ReparationMecanicien',
    'PieceReparee',
    'Fournisseur',

    # Commercial
    'Transitaire',
    'Client',

    # Missions
    'FraisTrajet',
    'Mission',
    'MissionConteneur',

    # Contrats
    'ContratTransport',
    'PrestationDeTransports',

    # Finances
    'Cautions',
    'PaiementMission',

    # Audit
    'Notification',
    'AuditLog',
]
