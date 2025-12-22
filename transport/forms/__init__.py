"""
Module de formulaires refactorisé pour l'application transport.

Ce module organise les formulaires en sous-modules logiques pour une meilleure maintenabilité.
Tous les formulaires sont ré-exportés ici pour maintenir la compatibilité avec les imports existants.
"""

# Import des formulaires utilisateur
from .user_forms import (
    EntrepriseForm,
    InscriptionUtilisateurForm,
    ConnexionForm,
)

# Import des formulaires personnel
from .personnel_forms import (
    ChauffeurForm,
    AffectationForm,
    MecanicienForm,
)

# Import des formulaires véhicules
from .vehicle_forms import (
    CamionForm,
    ConteneurForm,
    ReparationForm,
    ReparationMecanicienForm,
    PieceRepareeForm,
)

# Import des formulaires commerciaux
from .commercial_forms import (
    TransitaireForm,
    ClientForm,
    CompagnieConteneurForm,
    FournisseurForm,
)

# Import des formulaires missions
from .mission_forms import (
    MissionForm,
    MissionConteneurForm,
    FraisTrajetForm,
)

# Import des formulaires contrats
from .contrat_forms import (
    ContratTransportForm,
    PrestationDeTransportsForm,
)

# Import des formulaires finances
from .finance_forms import (
    CautionsForm,
    PaiementMissionForm,
)

__all__ = [
    # User
    'EntrepriseForm',
    'InscriptionUtilisateurForm',
    'ConnexionForm',

    # Personnel
    'ChauffeurForm',
    'AffectationForm',
    'MecanicienForm',

    # Véhicules
    'CamionForm',
    'ConteneurForm',
    'ReparationForm',
    'ReparationMecanicienForm',
    'PieceRepareeForm',

    # Commercial
    'TransitaireForm',
    'ClientForm',
    'CompagnieConteneurForm',
    'FournisseurForm',

    # Missions
    'MissionForm',
    'MissionConteneurForm',
    'FraisTrajetForm',

    # Contrats
    'ContratTransportForm',
    'PrestationDeTransportsForm',

    # Finances
    'CautionsForm',
    'PaiementMissionForm',
]
