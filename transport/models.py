from django.db import models

# Create your models here.
from django.db import models

# =======================
# ENUMS – Constantes pour les choix
# =======================

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
    ('bloque', 'Bloqué'),
]

TYPE_CLIENT_CHOICES = [
    ('entreprise', 'Entreprise'),
    ('particulier', 'Particulier'),
]

STATUT_CAUTION_CHOICES = [
    ('bloquee', 'Bloquée'),
    ('debloquee', 'Débloquée'),
]

STATUT_MISSION_CHOICES = [
    ('en_cours', 'En cours'),
    ('terminee', 'Terminée'),
    ('annulee', 'Annulée'),
]

# =======================
# Modèles
# =======================

class Entreprise(models.Model):
    pk_entreprise = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    secteur_activite = models.CharField(max_length=100, blank=True, null=True)
    email_contact = models.EmailField(max_length=100, blank=True, null=True)
    telephone_contact = models.CharField(max_length=20, blank=True, null=True)
    date_creation = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=STATUT_ENTREPRISE_CHOICES, default='active')

    def __str__(self):
        return self.pk_entreprise,  self.nom, self.secteur_activite, self.email_contact, self.telephone_contact, self.date_creation, self.statut


class Utilisateur(models.Model):
    pk_utilisateur = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom_utilisateur = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=15, choices=ROLE_UTILISATEUR_CHOICES, default='utilisateur')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk_utilisateur}, {self.entreprise}, {self.nom_utilisateur}, {self.email}, {self.email}, {self.mot_de_passe_hash}, {self.role}, {self.actif}, {self.date_creation}"


class Chauffeur(models.Model):
    pk_chauffeur = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk_chauffeur}, {self.entreprise},{self.nom}, {self.prenom}, {self.telephone}, {self.email}"


class UtilisateurChauffeur(models.Model):
    pk_utilisateur_chauffeur = models.CharField(max_length=250, primary_key=True)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    mot_de_passe_hash = models.CharField(max_length=255)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk_utilisateur_chauffeur},{self.chauffeur}, {self.email}, {self.mot_de_passe_hash}, {self.actif} ,{self.date_creation}"


class Camion(models.Model):
    pk_camion = models.CharField(max_length=250, primary_key=True)
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=50, blank=True, null=True)
    capacite_tonnes = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.pk_camion},{self.immatriculation},{self.modele}, {self.capacite_tonnes}"


class Mecanicien(models.Model):
    pk_mecanicien = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk_mecanicien}, {self.nom}, {self.telephone}, {self.email}"


class Fournisseur(models.Model):
    pk_fournisseur = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    fiabilite = models.CharField(max_length=10, choices=FIABILITE_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return  f"{self.pk_fournisseur}, {self.telephone}, {self.email}, {self.adresse}, {self.fiabilite}, {self.commentaire},  {self.nom}"


class Transitaire(models.Model):
    pk_transitaire = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Client(models.Model):
    pk_client = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    type_client = models.CharField(max_length=15, choices=TYPE_CLIENT_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Conteneur(models.Model):
    pk_conteneur = models.CharField(max_length=250, primary_key=True)
    numero_conteneur = models.CharField(max_length=30, unique=True)
    type_conteneur = models.CharField(max_length=50, blank=True, null=True)
    poids = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.CASCADE)

    def __str__(self):
        return self.numero_conteneur


class ContratTransport(models.Model):
    pk_contrat = models.CharField(max_length=250, primary_key=True)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.SET_NULL, blank=True, null=True)
    id_transporteur = models.IntegerField()
    date_debut = models.DateField()
    date_limite_retour = models.DateField()
    caution = models.DecimalField(max_digits=10, decimal_places=2)
    statut_caution = models.CharField(max_length=15, choices=STATUT_CAUTION_CHOICES, default='bloquee')
    commentaire = models.TextField(blank=True, null=True)
    signature_chauffeur = models.BooleanField(default=False)
    signature_client = models.BooleanField(default=False)
    signature_transitaire = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk_contrat} ,{self.conteneur}, {self.client}, {self.transitaire}"


class Affectation(models.Model):
    pk_affectation = models.CharField(max_length=250, primary_key=True)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    date_affectation = models.DateField(auto_now_add=True)
    date_fin_affectation = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.chauffeur} - {self.camion}"


class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250, primary_key=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_route = models.DecimalField(max_digits=10, decimal_places=2)
    frais_carburant = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('origine', 'destination')

    def __str__(self):
        return f"{self.origine} - {self.destination}"


class Mission(models.Model):
    pk_mission = models.CharField(max_length=250, primary_key=True)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    date_depart = models.DateField()
    date_retour = models.DateField(blank=True, null=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    prix_unitaire_par_tonne = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_trajet = models.ForeignKey(FraisTrajet, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.CASCADE)
    statut = models.CharField(max_length=15, choices=STATUT_MISSION_CHOICES, default='en_cours')

    def __str__(self):
        return self.pk_mission
