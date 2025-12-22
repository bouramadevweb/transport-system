"""
Constantes et choix pour les modèles

Ce module contient toutes les constantes CHOICES utilisées dans les modèles.
"""

STATUT_ENTREPRISE_CHOICES = [
    ('active', 'Active'),
    ('suspendue', 'Suspendue'),
]

ROLE_UTILISATEUR_CHOICES = [
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('utilisateur', 'Utilisateur'),
    ('chauffeur', 'Chauffeur')
]

FIABILITE_CHOICES = [
    ('bon', 'Bon'),
    ('moyen', 'Moyen'),
    ('mauvais', 'Mauvais'),
]

ETAT_PAIEMENT_CHOICES = [
    ('bon', 'Bon'),
    ('moyen', 'Moyen'),
    ('mauvais', 'Mauvais'),
    ('bloqué', 'Bloqué'),
]

TYPE_CLIENT_CHOICES = [
    ('entreprise', 'Entreprise'),
    ('particulier', 'Particulier'),
]

STATUT_CONTENEUR_CHOICES = [
    ('au_port', 'Au port (disponible)'),
    ('en_mission', 'En mission'),
    ('en_maintenance', 'En maintenance'),
]

STATUT_CAUTION_CONTRAT_CHOICES = [
    ('bloquée', 'Bloquée'),
    ('débloquée', 'Débloquée'),
]

STATUT_MISSION_CHOICES = [
    ('en cours', 'En cours'),
    ('terminée', 'Terminée'),
    ('annulée', 'Annulée'),
]

STATUT_CAUTION_CHOICES = [
    ('en_attente', 'En attente'),
    ('remboursee', 'Remboursée'),
    ('non_remboursee', 'Non remboursée'),
    ('consommee', 'Consommée'),
    ('annulee', 'Annulée'),
]

MOIS_CHOICES = [
    (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
    (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
    (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
]

STATUT_SALAIRE_CHOICES = [
    ('brouillon', 'Brouillon'),
    ('valide', 'Validé'),
    ('paye', 'Payé'),
]

MODE_PAIEMENT_SALAIRE_CHOICES = [
    ('especes', 'Espèces'),
    ('virement', 'Virement'),
    ('cheque', 'Chèque'),
    ('mobile', 'Paiement Mobile'),
]

