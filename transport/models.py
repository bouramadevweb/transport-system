from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.contrib.auth.models import BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
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
    email = models.EmailField(blank=True, null=True)
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
        return f"{self.compagnie}"


    
class ContratTransport(models.Model):
    pk_contrat = models.CharField(max_length=250, primary_key=True, editable=False)

    conteneur = models.ForeignKey("Conteneur", on_delete=models.CASCADE)
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, null=True, blank=True)
    transitaire = models.ForeignKey("Transitaire", on_delete=models.SET_NULL, null=True, blank=True)
    entreprise = models.ForeignKey("Entreprise", on_delete=models.CASCADE)

    camion = models.ForeignKey("Camion", on_delete=models.CASCADE)
    chauffeur = models.ForeignKey("Chauffeur", on_delete=models.CASCADE)

    numero_bl = models.CharField(max_length=100, unique=True)
    destinataire = models.CharField(max_length=200)

    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    avance_transport = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    reliquat_transport = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )

    caution = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
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

    def clean(self):
        """Validation personnalisée des montants et champs obligatoires"""
        super().clean()

        # Vérifier les champs obligatoires en utilisant les IDs
        errors = {}

        if not self.camion_id:
            errors['camion'] = 'Le camion est obligatoire'
        if not self.chauffeur_id:
            errors['chauffeur'] = 'Le chauffeur est obligatoire'
        if not self.client_id:
            errors['client'] = 'Le client est obligatoire'
        if not self.transitaire_id:
            errors['transitaire'] = 'Le transitaire est obligatoire'

        # Vérifier la disponibilité du camion et du chauffeur
        if self.camion_id and self.chauffeur_id:
            # Vérifier si le camion est déjà affecté à une mission en cours
            missions_camion = Mission.objects.filter(
                contrat__camion_id=self.camion_id,
                statut='en cours'
            )
            # Exclure le contrat actuel si on est en mode édition
            if self.pk_contrat:
                missions_camion = missions_camion.exclude(contrat__pk_contrat=self.pk_contrat)

            if missions_camion.exists():
                # Récupérer l'objet camion pour afficher son immatriculation
                try:
                    camion = Camion.objects.get(pk=self.camion_id)
                    errors['camion'] = f'Le camion {camion.immatriculation} est déjà affecté à une mission en cours'
                except Camion.DoesNotExist:
                    errors['camion'] = 'Le camion sélectionné est déjà affecté à une mission en cours'

            # Vérifier si le chauffeur est déjà affecté à une mission en cours
            missions_chauffeur = Mission.objects.filter(
                contrat__chauffeur_id=self.chauffeur_id,
                statut='en cours'
            )
            # Exclure le contrat actuel si on est en mode édition
            if self.pk_contrat:
                missions_chauffeur = missions_chauffeur.exclude(contrat__pk_contrat=self.pk_contrat)

            if missions_chauffeur.exists():
                # Récupérer l'objet chauffeur pour afficher son nom
                try:
                    chauffeur = Chauffeur.objects.get(pk=self.chauffeur_id)
                    errors['chauffeur'] = f'Le chauffeur {chauffeur.nom} {chauffeur.prenom} est déjà affecté à une mission en cours'
                except Chauffeur.DoesNotExist:
                    errors['chauffeur'] = 'Le chauffeur sélectionné est déjà affecté à une mission en cours'

        # Vérifier que l'avance ne dépasse pas le montant total
        if self.avance_transport and self.montant_total:
            if self.avance_transport > self.montant_total:
                errors['avance_transport'] = 'L\'avance ne peut pas dépasser le montant total'

        # Vérifier que la caution n'est pas trop élevée (max 50% du montant)
        if self.caution and self.montant_total:
            if self.caution > self.montant_total * Decimal('0.5'):
                errors['caution'] = 'La caution ne peut pas dépasser 50% du montant total'

        # Vérifier que la date de retour est après la date de début
        if self.date_debut and self.date_limite_retour:
            if self.date_limite_retour < self.date_debut:
                errors['date_limite_retour'] = 'La date limite de retour doit être après la date de début'

        if errors:
            raise ValidationError(errors)

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

        # Calcul automatique de la date limite de retour : date_debut + 23 jours
        if self.date_debut:
            from datetime import timedelta
            self.date_limite_retour = self.date_debut + timedelta(days=23)

        # Calcul automatique du reliquat
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

    prix_transport = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    avance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    caution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    solde = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
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
                fields=['camion', 'contrat_transport', 'client', 'transitaire', 'date'],
                name='unique_presta_transport'
            )
        ]

    def __str__(self):
        return (f"{self.pk_presta_transport}{self.prix_transport}{self.avance}{self.caution}{self.solde}{self.date}")

# Choix de statut pour les cautions
STATUT_CAUTION_CHOICES = [
    ('en_attente', 'En attente'),
    ('remboursee', 'Remboursée'),
    ('non_remboursee', 'Non remboursée'),
    ('consommee', 'Consommée'),
]

class Cautions(models.Model):
    pk_caution = models.CharField(max_length=250, primary_key=True)
    conteneur = models.ForeignKey(Conteneur, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.SET_NULL, blank=True, null=True)
    transitaire = models.ForeignKey(Transitaire, on_delete=models.SET_NULL, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.SET_NULL, blank=True, null=True)
    camion = models.ForeignKey(Camion, on_delete=models.SET_NULL, blank=True, null=True)
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CAUTION_CHOICES,
        default='en_attente',
        help_text="Statut de la caution"
    )
    montant_rembourser = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )

    def clean(self):
        """Validation personnalisée pour les cautions"""
        super().clean()

        errors = {}

        # Si la caution est marquée comme remboursée, le montant remboursé doit être rempli
        if self.statut == 'remboursee':
            if not self.montant_rembourser or self.montant_rembourser <= 0:
                errors['montant_rembourser'] = (
                    'Le montant remboursé doit être supérieur à 0 si la caution est marquée comme remboursée. '
                    f'Veuillez saisir le montant remboursé (montant de la caution : {self.montant} FCFA)'
                )

        # Vérifier que le montant remboursé ne dépasse pas le montant de la caution
        if self.montant_rembourser and self.montant:
            if self.montant_rembourser > self.montant:
                errors['montant_rembourser'] = (
                    f'Le montant remboursé ({self.montant_rembourser} FCFA) ne peut pas dépasser '
                    f'le montant de la caution ({self.montant} FCFA)'
                )

        # Si la caution n'est pas remboursée, le montant remboursé devrait être 0
        if self.statut not in ['remboursee', 'consommee'] and self.montant_rembourser > 0:
            errors['montant_rembourser'] = (
                f'Le montant remboursé est de {self.montant_rembourser} FCFA mais la caution n\'est pas marquée comme remboursée ou consommée. '
                f'Changez le statut ou mettez le montant à 0.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.pk_caution:
           base = f"{self.conteneur.pk_conteneur if self.conteneur else ''}{self.contrat.pk_contrat if self.contrat else ''}"
           base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
           slug = slugify(base)[:220]
           self.pk_caution = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.pk_caution}, {self.conteneur}, {self.contrat}, {self.transitaire} {self.client}, {self.chauffeur}, {self.camion}, {self.montant}, {self.statut}, {self.montant_rembourser}"

class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250, primary_key=True)
    origine = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    frais_route = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    frais_carburant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )

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
    origine = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    itineraire = models.TextField(
        blank=True,
        default='Itinéraire à compléter',
        help_text="Décrivez l'itinéraire détaillé de la mission"
    )
    frais_trajet = models.ForeignKey(FraisTrajet, on_delete=models.SET_NULL, blank=True, null=True)
    contrat = models.ForeignKey(ContratTransport, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_MISSION_CHOICES, default='en cours')

    def clean(self):
        """Validation des dates par rapport au contrat"""
        super().clean()
        errors = {}

        # Vérifier que les champs obligatoires sont remplis
        if not self.origine or not self.origine.strip():
            errors['origine'] = 'L\'origine est obligatoire'
        if not self.destination or not self.destination.strip():
            errors['destination'] = 'La destination est obligatoire'
        if not self.itineraire or not self.itineraire.strip():
            errors['itineraire'] = 'L\'itinéraire est obligatoire'

        # Vérifier la concordance des dates avec le contrat
        if self.contrat and self.date_depart:
            # La date de départ de la mission doit être >= date_debut du contrat
            if self.date_depart < self.contrat.date_debut:
                errors['date_depart'] = f'La date de départ ({self.date_depart}) doit être >= à la date de début du contrat ({self.contrat.date_debut})'

        # Vérifier la date de retour si elle existe
        if self.date_retour:
            # La date de retour doit être après la date de départ
            if self.date_depart and self.date_retour < self.date_depart:
                errors['date_retour'] = 'La date de retour doit être après la date de départ'

            # La date de retour devrait être <= date_limite_retour du contrat
            if self.contrat and self.date_retour > self.contrat.date_limite_retour:
                errors['date_retour'] = f'⚠️ La date de retour ({self.date_retour}) dépasse la date limite du contrat ({self.contrat.date_limite_retour}). Cela peut entraîner des pénalités.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Générer la clé primaire si elle n'existe pas
        if not self.pk_mission:
            base = (
                f"{self.prestation_transport.pk_presta_transport}_"
                f"{self.contrat.pk_contrat}_"
                f"{self.origine}_{self.destination}_"
                f"{self.date_depart}"
            )
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_mission = slugify(base)[:250]

        # Valider avant de sauvegarder (sauf si validate=False passé en kwargs)
        validate = kwargs.pop('validate', True)
        if validate:
            self.full_clean()

        super().save(*args, **kwargs)

    def terminer_mission(self, date_retour=None):
        """Méthode pour terminer proprement une mission avec validation de la date"""
        from django.utils import timezone

        if date_retour is None:
            date_retour = timezone.now().date()

        # Vérifier que la date de retour est cohérente
        if date_retour < self.date_depart:
            raise ValidationError(
                f'La date de retour ({date_retour}) ne peut pas être avant la date de départ ({self.date_depart})'
            )

        # Vérifier si la date dépasse la limite du contrat
        if date_retour > self.contrat.date_limite_retour:
            jours_retard = (date_retour - self.contrat.date_limite_retour).days
            penalite = jours_retard * 25000  # 25 000 FCFA par jour
            raise ValidationError(
                f'⚠️ ATTENTION: La date de retour ({date_retour}) dépasse la date limite du contrat ({self.contrat.date_limite_retour}) '
                f'de {jours_retard} jour(s). Pénalité estimée: {penalite} FCFA. '
                f'Confirmez-vous cette date de retour?'
            )

        self.date_retour = date_retour
        self.statut = 'terminée'
        self.save()

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
        return (f"{self.pk_mission}"
                 f"{self.date_depart}" 
                 f" {self.date_retour}" 
                f"{self.origine}"
                 f"{self.destination}"
                    f"{self.frais_trajet} "
                f"{self.contrat}"
                 f"{self.statut}")

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

    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    commission_transitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    caution_est_retiree = models.BooleanField(default=False)

    date_paiement = models.DateField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=50, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)

    # Nouveau champ pour valider le paiement
    est_valide = models.BooleanField(default=False)
    date_validation = models.DateTimeField(blank=True, null=True)

    def clean(self):
        """Validation avant sauvegarde - empêcher la validation si mission non terminée ou caution non remboursée"""
        super().clean()

        # Si on essaie de valider le paiement
        if self.est_valide:
            # Vérifier que la mission est terminée
            if self.mission.statut != 'terminée':
                raise ValidationError(
                    f"❌ Impossible de valider le paiement! "
                    f"La mission est actuellement '{self.mission.statut}'. "
                    f"Vous devez d'abord terminer la mission avant de valider le paiement."
                )

            # Vérifier l'état de la caution
            if self.caution:
                # La caution doit être remboursée ou consommée
                if self.caution.statut not in ['remboursee', 'consommee']:
                    raise ValidationError(
                        f"❌ Impossible de valider le paiement! "
                        f"La caution de {self.caution.montant} FCFA a le statut '{self.caution.get_statut_display()}'. "
                        f"Veuillez mettre à jour le statut de la caution (Remboursée ou Consommée) avant de valider le paiement."
                    )

        # Vérifier que la commission ne dépasse pas le montant total
        if self.commission_transitaire and self.montant_total:
            if self.commission_transitaire > self.montant_total:
                raise ValidationError({
                    'commission_transitaire': 'La commission ne peut pas dépasser le montant total'
                })

        # Vérifier que la commission n'est pas trop élevée (max 30% du montant)
        if self.commission_transitaire and self.montant_total:
            if self.commission_transitaire > self.montant_total * Decimal('0.3'):
                raise ValidationError({
                    'commission_transitaire': 'La commission ne peut pas dépasser 30% du montant total'
                })

    def valider_paiement(self):
        """Méthode pour valider le paiement avec vérification de la mission et de la caution

        IMPORTANT: Cette méthode ne modifie JAMAIS la caution elle-même.
        Elle enregistre seulement l'état de la caution au moment de la validation.
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError

        # Vérifier que la mission est terminée
        if self.mission.statut != 'terminée':
            raise ValidationError(
                f"❌ La mission n'est pas terminée (statut: {self.mission.statut}). "
                f"Vous devez terminer la mission avant de valider le paiement."
            )

        # Vérifier l'état de la caution
        if self.caution:
            # La caution doit être remboursée ou consommée
            if self.caution.statut not in ['remboursee', 'consommee']:
                raise ValidationError(
                    f"❌ Impossible de valider le paiement! "
                    f"La caution de {self.caution.montant} FCFA a le statut '{self.caution.get_statut_display()}'. "
                    f"Veuillez d'abord mettre à jour le statut de la caution (Remboursée ou Consommée)."
                )

        # IMPORTANT: Sauvegarder l'état de la caution AVANT validation pour traçabilité
        # On ne modifie PAS la caution, on enregistre juste son état dans le paiement
        caution_state = {
            'statut': self.caution.statut if self.caution else 'en_attente',
            'montant_rembourser': self.caution.montant_rembourser if self.caution else 0,
            'montant': self.caution.montant if self.caution else 0,
        }

        # Marquer le paiement comme validé
        self.est_valide = True
        self.date_validation = timezone.now()

        # Enregistrer si la caution était remboursée ou consommée au moment de la validation
        # (Ne modifie PAS la caution elle-même!)
        if self.caution and caution_state['statut'] in ['remboursee', 'consommee']:
            self.caution_est_retiree = True

        # Ajouter l'état de la caution dans l'observation pour traçabilité
        observation_caution = (
            f"\n--- État de la caution au moment de la validation ---\n"
            f"Montant caution: {caution_state['montant']} FCFA\n"
            f"Statut: {self.caution.get_statut_display() if self.caution else 'N/A'}\n"
            f"Montant remboursé: {caution_state['montant_rembourser']} FCFA\n"
            f"Date validation: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        )

        if self.observation:
            self.observation += observation_caution
        else:
            self.observation = observation_caution

        # Sauvegarder le paiement (NE TOUCHE PAS À LA CAUTION!)
        self.save()

        # Log pour vérifier que la caution n'est pas modifiée
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Paiement {self.pk_paiement} validé. "
            f"Caution {self.caution.pk_caution if self.caution else 'N/A'} "
            f"PRÉSERVÉE (montant: {caution_state['montant']}, "
            f"statut: {caution_state['statut']})"
        )

    def save(self, *args, **kwargs):
        if not self.pk_paiement:
            base = f"{self.mission}{self.caution}{self.prestation}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            self.pk_paiement = slugify(base)[:250]

        # Valider avant de sauvegarder
        self.full_clean()

        super().save(*args, **kwargs)


    class Meta:
         #unique_together = ('mission', 'caution',"prestation")
         # Simule une clé composite
        constraints = [models.UniqueConstraint(fields=['mission', 'caution','prestation'], name='unique_mission_caution')]  # Alternative

    def __str__(self):
        statut_validation = "✅ Validé" if self.est_valide else "⏳ En attente"
        return (
            f"{self.mission.pk_mission} - {statut_validation} - "
            f"{self.montant_total}€ ({self.mission.statut})"
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

    def has_mecaniciens(self):
        """Vérifie si la réparation a au moins un mécanicien assigné"""
        return ReparationMecanicien.objects.filter(reparation=self).exists()

    def get_mecaniciens(self):
        """Retourne la liste des mécaniciens assignés à cette réparation"""
        return Mecanicien.objects.filter(
            reparationmecanicien__reparation=self
        )

    def get_cout_total(self):
        """Calcule le coût total (coût de base + pièces)"""
        cout_pieces = PieceReparee.objects.filter(reparation=self).aggregate(
            total=models.Sum(models.F('quantite') * models.F('cout_unitaire'))
        )['total'] or 0
        return self.cout + cout_pieces

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
