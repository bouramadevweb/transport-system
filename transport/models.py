from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.contrib.auth.models import BaseUserManager
from decimal import Decimal

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

    # class Meta:
    #     unique_together = ('nom', 'secteur_activite', 'email_contact', 'date_creation')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'secteur_activite', 'email_contact', 'date_creation'],
                name='unique_entreprise'
            )
        ]    

    def __str__(self):
        return (f"{self.nom}, {self.secteur_activite or ''}")
                


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
    email = models.EmailField(blank=True, null=False)
    est_affecter = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk_chauffeur:
            base = f"{self.nom}{self.prenom}{self.email or ''}{self.entreprise.pk_entreprise}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_chauffeur = slugify(base)[:250]
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'prenom', 'email', 'entreprise'],
                name='unique_chauffeur'
            )
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom}  {self.email}"

class Camion(models.Model):
    pk_camion = models.CharField(max_length=250, primary_key=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=50, blank=True, null=True)
    capacite_tonnes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    est_affecter = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk_camion:
            base = f"{self.immatriculation}{self.modele}{self.entreprise.pk_entreprise}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_camion = slugify(base)[:250]
        super().save(*args, **kwargs)

    # class Meta:
    #     unique_together = ('immatriculation', 'modele', 'entreprise')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['immatriculation', 'modele', 'entreprise'],
                name='unique_camion'
            )
        ]    

    def __str__(self):
        return f"{self.immatriculation}  {self.modele}"

class Affectation(models.Model):
    pk_affectation = models.CharField(max_length=250, primary_key=True, editable=False)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    date_affectation = models.DateField(default=now)
    date_fin_affectation = models.DateField(blank=True, null=True)

    def clean(self):
        """Validation avant sauvegarde"""
        from django.core.exceptions import ValidationError

        # Vérifier si le chauffeur est déjà affecté (affectation active)
        affectations_chauffeur_actives = Affectation.objects.filter(
            chauffeur=self.chauffeur,
            date_fin_affectation__isnull=True
        ).exclude(pk=self.pk_affectation if self.pk_affectation else None)

        if affectations_chauffeur_actives.exists():
            affectation_existante = affectations_chauffeur_actives.first()
            raise ValidationError(
                f"Le chauffeur {self.chauffeur.nom} {self.chauffeur.prenom} est déjà affecté au camion {affectation_existante.camion.immatriculation} "
                f"depuis le {affectation_existante.date_affectation}. "
                f"Veuillez d'abord terminer cette affectation avant d'en créer une nouvelle."
            )

        # Vérifier si le camion est déjà affecté (affectation active)
        affectations_camion_actives = Affectation.objects.filter(
            camion=self.camion,
            date_fin_affectation__isnull=True
        ).exclude(pk=self.pk_affectation if self.pk_affectation else None)

        if affectations_camion_actives.exists():
            affectation_existante = affectations_camion_actives.first()
            raise ValidationError(
                f"Ce camion {self.camion.immatriculation} est déjà affecté au chauffeur {affectation_existante.chauffeur.nom} {affectation_existante.chauffeur.prenom} "
                f"depuis le {affectation_existante.date_affectation}. "
                f"Veuillez d'abord terminer cette affectation avant d'en créer une nouvelle."
            )

    def save(self, *args, **kwargs):
        # Générer la clé primaire
        if not self.pk_affectation:
            base = f"{self.chauffeur.pk_chauffeur}_{self.camion.pk_camion}_{self.date_affectation}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_affectation = slugify(base)[:250]

        # Valider avant de sauvegarder
        self.full_clean()

        # Mettre à jour le statut du chauffeur et du camion
        if self.date_fin_affectation is None:
            # Affectation active - marquer le chauffeur et le camion comme affectés
            self.chauffeur.est_affecter = True
            self.chauffeur.save(update_fields=['est_affecter'])

            self.camion.est_affecter = True
            self.camion.save(update_fields=['est_affecter'])
        else:
            # Affectation terminée - vérifier s'il y a d'autres affectations actives pour le chauffeur
            autres_affectations_chauffeur = Affectation.objects.filter(
                chauffeur=self.chauffeur,
                date_fin_affectation__isnull=True
            ).exclude(pk=self.pk_affectation).exists()

            if not autres_affectations_chauffeur:
                self.chauffeur.est_affecter = False
                self.chauffeur.save(update_fields=['est_affecter'])

            # Vérifier s'il y a d'autres affectations actives pour le camion
            autres_affectations_camion = Affectation.objects.filter(
                camion=self.camion,
                date_fin_affectation__isnull=True
            ).exclude(pk=self.pk_affectation).exists()

            if not autres_affectations_camion:
                self.camion.est_affecter = False
                self.camion.save(update_fields=['est_affecter'])

        super().save(*args, **kwargs)

    def terminer_affectation(self, date_fin=None):
        """Méthode pour terminer proprement une affectation"""
        from django.utils import timezone

        if date_fin is None:
            date_fin = timezone.now().date()

        self.date_fin_affectation = date_fin
        self.save()

    # class Meta:
    #     unique_together = ('chauffeur', 'camion', 'date_affectation')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['chauffeur', 'camion', 'date_affectation'],
                name='unique_affectation'
            )
        ]

    def __str__(self):
        statut = "Active" if self.date_fin_affectation is None else f"Terminée le {self.date_fin_affectation}"
        return f"{self.chauffeur} → {self.camion} ({statut})"


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
    # class Meta:
    #     unique_together = ('nom', 'telephone')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'telephone'],
                name='unique_transitaire'
            )
        ]

    def __str__(self):
        return f"{self.nom}"


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

    # class Meta:
    #       unique_together = ("nom","type_client","telephone") 

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'type_client', 'telephone'],
                name='unique_client'
            )
        ]

    def __str__(self):
        return f"{self.nom}"

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

    # class Meta:   
    #         unique_together = (("nom",),)  

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom'],
                name='unique_compagnie'
            )
        ]

    def __str__(self):
        return f"{self.nom}"

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

    # class Meta:
    #     unique_together = ("numero_conteneur","compagnie","client")  

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['numero_conteneur', 'compagnie', 'client'],
                name='unique_conteneur'
            )
        ]  

    def __str__(self):
        return f"{self.numero_conteneur} | {self.compagnie}"


    
class ContratTransport(models.Model):
    pk_contrat = models.CharField(max_length=250, primary_key=True, editable=False)

    conteneur = models.ForeignKey("Conteneur", on_delete=models.CASCADE)
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, null=True, blank=True)
    transitaire = models.ForeignKey("Transitaire", on_delete=models.SET_NULL, null=True, blank=True)
    entreprise = models.ForeignKey("Entreprise", on_delete=models.CASCADE)

    camion = models.ForeignKey("Camion", on_delete=models.CASCADE)
    chauffeur = models.ForeignKey("Chauffeur", on_delete=models.CASCADE)

    numero_bl = models.CharField(max_length=100)
    destinataire = models.CharField(max_length=200)

    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    avance_transport = models.DecimalField(max_digits=12, decimal_places=2)
    reliquat_transport = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    caution = models.DecimalField(max_digits=12, decimal_places=2)
    statut_caution = models.CharField(max_length=10, choices=STATUT_CAUTION_CHOICES, default='bloquee')

    date_debut = models.DateField()
    date_limite_retour = models.DateField()

    commentaire = models.TextField(blank=True, null=True)

    signature_chauffeur = models.BooleanField(default=False)
    signature_client = models.BooleanField(default=False)
    signature_transitaire = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='contrats/', null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['conteneur','client','transitaire','entreprise','camion','chauffeur','numero_bl','date_debut'],
                name='unique_contrat_transport'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.pk_contrat:
            base = (
                f"{self.conteneur.pk_conteneur}"
                f"{self.client.pk_client if self.client else ''}"
                f"{self.transitaire.pk_transitaire if self.transitaire else ''}"
                f"{self.camion.immatriculation}"
                f"{self.chauffeur.pk_chauffeur}"
                f"{self.numero_bl}"
                f"{self.date_debut}"
            )
            base = base.replace(" ", "").replace("-", "")
            self.pk_contrat = slugify(base)[:250]

        self.reliquat_transport = Decimal(self.montant_total) - Decimal(self.avance_transport)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contrat {self.pk_contrat} | BL: {self.numero_bl}"
    

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
    
    # class Meta:
    #     unique_together = ("camion","pk_presta_transport","contrat_transport","client","transitaire")
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['camion','pk_presta_transport','contrat_transport','client','transitaire'],
                name='unique_presta_transport'
            )
        ]

    def __str__(self):
        return (f"{self.pk_presta_transport}{self.prix_transport}{self.avance}{self.caution}{self.solde}{self.date}")

class Cautions(models.Model):
    pk_caution = models.CharField(max_length=250, primary_key=True)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.SET_NULL, blank=True, null=True)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.SET_NULL, blank=True, null=True)
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
        return f"{self.pk_caution}, {self.conteneur}, {self.contrat}, {self.transitaire} {self.client}, {self.chauffeur}, {self.camion}, {self.montant}, {self.non_rembourser}, {self.est_rembourser}, {self.montant_rembourser}"

class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250, primary_key=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_route = models.DecimalField(max_digits=10, decimal_places=2)
    frais_carburant = models.DecimalField(max_digits=10, decimal_places=2)

    # class Meta:
    #     unique_together = ('origine', 'destination')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['origine','destination'],
                name='unique_frais_trajet'
            )
        ]    

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

    # class Meta:
    #     unique_together = (
    #         'prestation_transport',
    #         'contrat',
    #         'origine',
    #         'destination',
    #         'date_depart',
    #     )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['prestation_transport','contrat','origine','destination','date_depart'],
                name='unique_mission'
            )
        ]

    def __str__(self):
        return (f"{self.pk_mission}, {self.date_depart}, {self.date_retour}, "
                f"{self.origine}, {self.destination}, {self.frais_trajet}, "
                f"{self.contrat}, {self.statut}")

# ici nest pas encore faite

class MissionConteneur(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.CASCADE)

    class Meta:
        # Supprime l'ID auto
        managed = True
        #unique_together = ('mission', 'conteneur')
        # Ou, en Django 4.1+, tu peux utiliser constraints :
        constraints = [
            models.UniqueConstraint(fields=['mission', 'conteneur'], name='unique_mission_conteneur')
        ]
    
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
         #unique_together = ('mission', 'caution',"prestation") 
         # Simule une clé composite
        constraints = [models.UniqueConstraint(fields=['mission', 'caution','prestation'], name='unique_mission_caution')]  # Alternative

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

    # class Meta:
    #     unique_together = ('reparation', 'mecanicien')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['reparation','mecanicien'],
                name='unique_reparation_mecanicien'
            )
        ]

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

    # class Meta:
    #     unique_together = ("nom_piece", "reparation")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nom_piece','reparation'],
                name='unique_piece_reparee'
            )
        ]

    def __str__(self):
        return f"{self.nom_piece} x{self.quantite} ({self.reparation})"