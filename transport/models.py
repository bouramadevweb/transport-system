from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.contrib.auth.models import BaseUserManager

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

STATUT_CAUTION_CHOICES = [
    ('bloquée', 'Bloquée'),
    ('débloquée', 'Débloquée'),
]

STATUT_MISSION_CHOICES = [
    ('en cours', 'En cours'),
    ('terminée', 'Terminée'),
    ('annulée', 'Annulée'),
]

# =======================
# Modèles
# =======================

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L’email est obligatoire')
        
        email = self.normalize_email(email)

        # Génération automatique du pk_utilisateur si non fourni
        if not extra_fields.get('pk_utilisateur'):
            base = slugify(email.split('@')[0])
            extra_fields['pk_utilisateur'] = f"{base}-{uuid4().hex[:8]}"

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('actif', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Entreprise(models.Model):
    pk_entreprise = models.CharField(max_length=250, primary_key=True, editable=False)
    nom = models.CharField(max_length=100)
    secteur_activite = models.CharField(max_length=100, blank=True, null=True)
    email_contact = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    telephone_contact = models.CharField(max_length=20, blank=True, null=True)
    date_creation = models.DateField(default=now)
    statut = models.CharField(max_length=10, choices=STATUT_ENTREPRISE_CHOICES, default='active')

    def save(self, *args, **kwargs):
        if not self.pk_entreprise:
           base = f"{self.nom}{self.secteur_activite or ''}{self.email_contact or ''}{self.date_creation}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           self.pk_entreprise = slugify(base)[:250]  # s'assurer que ça tient dans 250 caractères
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('nom', 'secteur_activite', 'email_contact', 'date_creation')

    def __str__(self):
        return (f"{self.pk_entreprise} | "
                f"{self.nom}, {self.secteur_activite or ''}, "
                f"{self.email_contact or ''}, {self.telephone_contact or ''}, "
                f"{self.date_creation}, {self.statut}")


class Utilisateur(AbstractUser):
    pk_utilisateur = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,null=True, blank=True)
    nom_utilisateur = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_UTILISATEUR_CHOICES, default='utilisateur')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    username = None  # Supprimer les champs non utilisés
    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UtilisateurManager()

    class Meta:
        db_table = 'Utilisateur'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.email} ({self.role})"
    

   
class Chauffeur(models.Model):
    pk_chauffeur = models.CharField(max_length=250, primary_key=True, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk_chauffeur:
            base = f"{self.nom}{self.prenom}{self.email or ''}{self.entreprise.pk_entreprise}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_chauffeur = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('nom', 'prenom', 'email', 'entreprise')

    def __str__(self):
        return f"{self.pk_chauffeur}, {self.entreprise}, {self.nom}, {self.prenom}, {self.telephone}, {self.email}"

class Camion(models.Model):
    pk_camion = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=50, blank=True, null=True)
    capacite_tonnes = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.pk_camion:
            base = f"{self.immatriculation}{self.modele}{self.entreprise.pk_entreprise}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_camion = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('immatriculation', 'modele', 'entreprise')

    def __str__(self):
        return f"{self.pk_camion}, {self.entreprise}, {self.immatriculation}, {self.modele}, {self.capacite_tonnes}"

class Affectation(models.Model):
    pk_affectation = models.CharField(max_length=250, primary_key=True, editable=False)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    date_affectation = models.DateField(default=now)
    date_fin_affectation = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk_affectation:
            base = f"{self.chauffeur.pk_chauffeur}_{self.camion.pk_camion}_{self.date_affectation}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_affectation = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('chauffeur', 'camion', 'date_affectation')

    def __str__(self):
        return f"{self.pk_affectation}, {self.chauffeur}, {self.camion}, {self.date_affectation}, {self.date_fin_affectation}"


class Transitaire(models.Model):
    pk_transitaire = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk_transitaire:
            base = f"{self.nom}{self.telephone}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_transitaire = slugify(base)[:250]
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('nom', 'telephone')
    def __str__(self):
        return f"{self.pk_transitaire}, {self.nom}, {self.telephone}, {self.email}, {self.score_fidelite}, {self.etat_paiement}, {self.commentaire}"


class Client(models.Model):
    pk_client = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    type_client = models.CharField(max_length=50, choices=TYPE_CLIENT_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    score_fidelite = models.IntegerField(default=100)
    etat_paiement = models.CharField(max_length=10, choices=ETAT_PAIEMENT_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)

    def save(self,*args, **kwargs):
        if not self.pk_client:
            base = f"{self.nom}{self.type_client}{self.telephone}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_client =slugify(base)[:250]
        super().save(*args, **kwargs) 

    class Meta:
          unique_together = ("nom","type_client","telephone") 

    def __str__(self):
        return f"{self.pk_client}, {self.nom}, {self.type_client}, {self.telephone}, {self.email}, {self.score_fidelite}, {self.commentaire}"

class CompagnieConteneur(models.Model):
    """
    les compagnies de contneur """
    pk_compagnie = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=250, blank=True, null=True )
    def save(self,*args, **kwargs):
        """
        creation de clée composite"""
        if not self.pk_compagnie:
            base = f"{self.nom}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_compagnie = slugify(base)[:250]
        super().save(*args, **kwargs)   

    class Meta:   
            unique_together = (("nom",),)    
    def __str__(self):
        return f"{self.pk_compagnie}, {self.nom}"

class Conteneur(models.Model):
    pk_conteneur = models.CharField(max_length=250, primary_key=True)
    numero_conteneur = models.CharField(max_length=30, unique=True)
    compagnie = models.ForeignKey(CompagnieConteneur, on_delete=models.CASCADE)
    type_conteneur = models.CharField(max_length=50, blank=True, null=True)
    poids = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk_conteneur:
            base = f"{self.numero_conteneur}{self.compagnie.nom}{self.compagnie.pk_compagnie}{self.client.nom}{self.client.pk_client}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_conteneur = slugify(base)[:250]
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ("numero_conteneur","compagnie","client")    

    def __str__(self):
        return f"{self.pk_conteneur}, {self.numero_conteneur}, {self.compagnie}, {self.type_conteneur}, {self.poids}, {self.client}, {self.transitaire}"


    
class ContratTransport(models.Model):
    """
    contrat de transport et la signature """
    pk_contrat = models.CharField(max_length=250, primary_key=True)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.SET_NULL, blank=True, null=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_limite_retour = models.DateField()
    caution = models.DecimalField(max_digits=10, decimal_places=2)
    statut_caution = models.CharField(max_length=10, choices=STATUT_CAUTION_CHOICES, default='bloquée')
    commentaire = models.TextField(blank=True, null=True)
    signature_chauffeur = models.BooleanField(default=False)
    signature_client = models.BooleanField(default=False)
    signature_transitaire = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        """
        pour le pk composite """
        if not self.pk_contrat:
            base = (f"{self.conteneur.pk_conteneur}{self.client.pk_client}{self.transitaire.pk_transitaire}"
                   f"{self.entreprise.pk_entreprise}{self.camion.immatriculation}{self.chauffeur.pk_chauffeur}"
                   f"{self.date_debut}{self.date_limite_retour}")
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_contrat = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
          unique_together = ("conteneur","client","transitaire","entreprise","camion","chauffeur","date_debut","date_limite_retour")

    def __str__(self):
        return (
            f"Contrat {self.pk_contrat} | "
            f"Conteneur: {self.conteneur.numero_conteneur} | "
            f"Client: {self.client.nom if self.client else 'N/A'} | "
            f"Transitaire: {self.transitaire.nom if self.transitaire else 'N/A'} | "
            f"Entreprise: {self.entreprise.nom} | "
            f"Camion: {self.camion.immatriculation} | "
            f"Chauffeur: {self.chauffeur.nom} {self.chauffeur.prenom} | "
            f"Début: {self.date_debut} | "
            f"Retour limite: {self.date_limite_retour} | "
            f"Caution: {self.caution} ({self.statut_caution}) | "
            f"Signatures - Chauffeur: {'✔' if self.signature_chauffeur else '✘'}, "
            f"Client: {'✔' if self.signature_client else '✘'}, "
            f"Transitaire: {'✔' if self.signature_transitaire else '✘'}"
        )

class PrestationDeTransports(models.Model):
    pk_presta_transport = models.CharField(max_length=250, primary_key=True)
    contrat_transport = models.ForeignKey(ContratTransport, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.CASCADE)

    prix_transport = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    avance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    caution = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    solde = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    date = models.DateTimeField()

    def save(self,*args, **kwargs):
        if not self.pk_presta_transport:
           base = f"{self.camion.immatriculation}{self.contrat_transport.pk_contrat}{self.client.pk_client}{self.transitaire.pk_transitaire}{self.date}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           self.pk_presta_transport = slugify(base)[:250]
        super().save(*args,**kwargs)
    
    class Meta:
        unique_together = ("camion","pk_presta_transport","contrat_transport","client","transitaire")

    def __str__(self):
        return (f"{self.pk_presta_transport}{self.prix_transport}{self.avance}{self.caution}{self.solde}{self.date}")

class Cautions(models.Model):
    pk_caution = models.CharField(max_length=250, primary_key=True)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.SET_NULL, blank=True, null=True)
    transiteur = models.ForeignKey(Transitaire, on_delete=models.SET_NULL, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.SET_NULL, blank=True, null=True)
    camion = models.ForeignKey(Camion, on_delete=models.SET_NULL, blank=True, null=True)
    montant =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    non_rembourser = models.BooleanField(default=False)
    est_rembourser = models.BooleanField(default=True)
    montant_rembourser = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.pk_caution:
           base = f"{self.conteneur.pk_conteneur if self.conteneur else ''}{self.contrat.pk_contrat if self.contrat else ''}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           self.pk_caution = slugify(base)[:250]
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.pk_caution}, {self.conteneur}, {self.contrat}, {self.transiteur} {self.client}, {self.chauffeur}, {self.camion}, {self.montant}, {self.non_rembourser}, {self.est_rembourser}, {self.montant_rembourser}"


class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250, primary_key=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_route = models.DecimalField(max_digits=10, decimal_places=2)
    frais_carburant = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('origine', 'destination')

    def __str__(self):
        return f"{self.pk_frais}, {self.origine}, {self.destination}, {self.frais_route}, {self.frais_carburant}"


class Mission(models.Model):
    pk_mission = models.CharField(max_length=250, primary_key=True, editable=False)
    prestation_transport = models.ForeignKey(PrestationDeTransports, on_delete=models.CASCADE)
    date_depart = models.DateField()
    date_retour = models.DateField(blank=True, null=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_trajet = models.ForeignKey(FraisTrajet, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_MISSION_CHOICES, default='en cours')

    def save(self, *args, **kwargs):
        if not self.pk_mission:
            base = (
                f"{self.prestation_transport.pk_presta_transport}_"
                f"{self.contrat.pk_contrat}_"
                f"{self.origine}_{self.destination}_"
                f"{self.date_depart}"
            )
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_mission = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            'prestation_transport',
            'contrat',
            'origine',
            'destination',
            'date_depart',
        )

    def __str__(self):
        return (f"{self.pk_mission}, {self.date_depart}, {self.date_retour}, "
                f"{self.origine}, {self.destination}, {self.frais_trajet}, "
                f"{self.contrat}, {self.statut}")


class MissionConteneur(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)

    class Meta:
        # Supprime l'ID auto
        managed = True
        unique_together = ('mission', 'conteneur')
        # Ou, en Django 4.1+, tu peux utiliser constraints :
        # constraints = [
        #     models.UniqueConstraint(fields=['mission', 'conteneur'], name='unique_mission_conteneur')
        # ]

    def __str__(self):
        return f"{self.mission}, {self.conteneur}"
    



class PaiementMission(models.Model):
    pk_paiement = models.CharField(max_length=250,primary_key=True)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    caution = models.ForeignKey(Cautions, on_delete=models.CASCADE)
    prestation = models.ForeignKey(PrestationDeTransports, on_delete=models.CASCADE)
     
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    commission_transitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    caution_est_retiree = models.BooleanField(default=False)

    date_paiement = models.DateField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=50, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk_paiement:
            base = f"{self.mission}{self.caution}{self.prestation}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')

            self.pk_paiement = slugify(base)[:250]
        super().save(*args, **kwargs)


    class Meta:
        unique_together = ('mission', 'caution',"prestation")  # Simule une clé composite
        # constraints = [models.UniqueConstraint(fields=['mission', 'caution'], name='unique_mission_caution')]  # Alternative

    def __str__(self):
        return (
            f"{self.mission}, {self.caution}, {self.montant_total}, "
            f"{self.commission_transitaire} "
            f"{self.date_paiement}, {self.mode_paiement}, {self.observation}"
        )


class Mecanicien(models.Model):
    pk_mecanicien = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_mecanicien:
            base = f"{self.nom}{self.telephone}".replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            slug = slugify(base)[:240]
            self.pk_mecanicien = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.telephone}"


class Fournisseur(models.Model):
    pk_fournisseur = models.CharField(max_length=250, primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    fiabilite = models.CharField(max_length=10, choices=FIABILITE_CHOICES, default='bon')
    commentaire = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_fournisseur:
            base = f"{self.nom}{self.telephone or ''}".replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            slug = slugify(base)[:240]
            self.pk_fournisseur = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.telephone or 'N/A'}"


class Reparation(models.Model):
    pk_reparation = models.CharField(max_length=250, primary_key=True)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.SET_NULL, blank=True, null=True)
    date_reparation = models.DateField()
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_reparation:
            base = f"{self.camion_id or ''}{self.chauffeur_id or ''}{self.date_reparation}".replace('-', '')
            slug = slugify(base)[:240]
            self.pk_reparation = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Réparation {self.pk_reparation} - {self.camion}"


class ReparationMecanicien(models.Model):
    reparation = models.ForeignKey(Reparation, on_delete=models.CASCADE)
    mecanicien = models.ForeignKey(Mecanicien, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('reparation', 'mecanicien')

    def __str__(self):
        return f"{self.reparation} - {self.mecanicien}"


class PieceReparee(models.Model):

    CATEGORIES = [
        ('moteur', 'Moteur'),
        ('transmission', 'Transmission'),
        ('suspension', 'Suspension & Direction'),
        ('freinage', 'Freinage'),
        ('electrique', 'Éléments électriques'),
        ('eclairage', 'Éclairage & Signalisation'),
        ('auxiliaire', 'Systèmes auxiliaires'),
        ('carrosserie', 'Carrosserie & Structure'),
        ('pneumatique', 'Pneumatiques & Roues'),
        ('alimentation', "Système d'alimentation"),
    ]
    pk_piece = models.CharField(max_length=250, primary_key=True)
    reparation = models.ForeignKey(Reparation, on_delete=models.CASCADE)
    nom_piece = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    reference = models.CharField(max_length=50, blank=True, null=True, help_text="Référence fabricant")
    quantite = models.PositiveIntegerField(default=1)
    cout_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk_piece:
            base = f"{self.nom_piece}{self.reparation.pk_reparation}{self.fournisseur or ''}".replace('-', '')
            slug = slugify(base)[:240]
            self.pk_piece = f"{slug}{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("nom_piece", "reparation")

    def __str__(self):
        return f"{self.nom_piece} x{self.quantite} ({self.reparation})"