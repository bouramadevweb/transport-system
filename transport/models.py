from django.db import models

# Create your models here.
from django.db import models

# ENUMS
STATUT_ENTREPRISE_CHOICES = [
    ('active', 'Active'),
    ('suspendue', 'Suspendue'),
]

ROLE_UTILISATEUR_CHOICES = [
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('utilisateur', 'Utilisateur'),
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

STATUT_CAUTION_CHOICES = [
    ('bloquée', 'Bloquée'),
    ('débloquée', 'Débloquée'),
]

STATUT_MISSION_CHOICES = [
    ('en cours', 'En cours'),
    ('terminée', 'Terminée'),
    ('annulée', 'Annulée'),
]

class Entreprise(models.Model):
    pk_entreprise = models.CharField(max_length=250,primary_key=True)
    nom = models.CharField(max_length=100)
    secteur_activite = models.CharField(max_length=100, blank=True, null=True)
    email_contact = models.EmailField(max_length=100, blank=True, null=True)
    telephone_contact = models.CharField(max_length=20, blank=True, null=True)
    date_creation = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=STATUT_ENTREPRISE_CHOICES, default='active')

class Utilisateur(models.Model):
    pk_utilisateur = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom_utilisateur = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_UTILISATEUR_CHOICES, default='utilisateur')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

class Chauffeur(models.Model):
    pk_chauffeur = models.CharField(max_length=250,primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

class UtilisateurChauffeur(models.Model):
    pk_utilisateur_chauffeur = models.CharField(max_length=250,primary_key=True)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    mot_de_passe_hash = models.CharField(max_length=255)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

class Camion(models.Model):
    pk_camion = models.CharField(max_length=250,primary_key=True)
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=50, blank=True, null=True)
    capacite_tonnes = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class Mecanicien(models.Model):
    pk_mecanicien = models.CharField(max_length=250,primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

class Fournisseur(models.Model):
    pk_fournisseur = models.CharField(max_length=250,primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    fiabilite = models.CharField(max_length=10, choices=FIABILITE_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

class Transitaire(models.Model):
    pk_transitaire = models.CharField(max_length=250,primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

class Client(models.Model):
    pk_client = models.CharField(max_length=250,primary_key=True)
    nom = models.CharField(max_length=100)
    type_client = models.CharField(max_length=10, choices=TYPE_CLIENT_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

class Conteneur(models.Model):
    pk_conteneur = models.CharField(max_length=250,primary_key=True)
    numero_conteneur = models.CharField(max_length=30, unique=True)
    type_conteneur = models.CharField(max_length=50, blank=True, null=True)
    poids = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.CASCADE)

class ContratTransport(models.Model):
    pk_contrat = models.CharField(max_length=250,primary_key=True)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.SET_NULL, blank=True, null=True)
    id_transporteur = models.IntegerField()  # Remplacer par FK si nécessaire
    date_debut = models.DateField()
    date_limite_retour = models.DateField()
    caution = models.DecimalField(max_digits=10, decimal_places=2)
    statut_caution = models.CharField(max_length=10, choices=STATUT_CAUTION_CHOICES, default='bloquée')
    commentaire = models.TextField(blank=True, null=True)
    signature_chauffeur = models.BooleanField(default=False)
    signature_client = models.BooleanField(default=False)
    signature_transitaire = models.BooleanField(default=False)

class Affectation(models.Model):
    pk_affectation = models.CharField(max_length=250,primary_key=True)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    date_affectation = models.DateField(auto_now_add=True)
    date_fin_affectation = models.DateField(blank=True, null=True)

class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250,primary_key=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_route = models.DecimalField(max_digits=10, decimal_places=2)
    frais_carburant = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('origine', 'destination')

class Mission(models.Model):
    pk_mission = models.CharField(max_length=250,primary_key=True)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    date_depart = models.DateField()
    date_retour = models.DateField(blank=True, null=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    prix_unitaire_par_tonne = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_trajet = models.ForeignKey(FraisTrajet, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_MISSION_CHOICES, default='en cours')

class MissionConteneur(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('mission', 'conteneur')

class Reparation(models.Model):
    pk_reparation = models.CharField(max_length=250,primary_key=True)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.SET_NULL, blank=True, null=True)
    date_reparation = models.DateField()
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

class ReparationMecanicien(models.Model):
    reparation = models.ForeignKey(Reparation, on_delete=models.CASCADE)
    mecanicien = models.ForeignKey(Mecanicien, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('reparation', 'mecanicien')

class PieceReparee(models.Model):
    pk_piece = models.CharField(max_length=250,primary_key=True)
    reparation = models.ForeignKey(Reparation, on_delete=models.CASCADE)
    nom_piece = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField(default=1)
    cout_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)

class PaiementMission(models.Model):
    pk_paiement = models.CharField(max_length=250,primary_key=True)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    montant_avance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_transitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    caution_retiree = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    caution_remboursee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_paiement = models.DateField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=50, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)
