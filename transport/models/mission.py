"""
Mission.Py

Modèles pour mission
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import hashlib

from .choices import *
# Imports circulaires gérés dans les méthodes

class FraisTrajet(models.Model):
    pk_frais = models.CharField(max_length=250, primary_key=True, editable=False)

    # Relations avec Mission et Contrat
    mission = models.ForeignKey("Mission", on_delete=models.CASCADE, related_name='frais_trajets', null=True, blank=True)
    contrat = models.ForeignKey("ContratTransport", on_delete=models.CASCADE, null=True, blank=True)

    # Type de trajet
    type_trajet = models.CharField(
        max_length=10,
        choices=[('aller', 'Aller'), ('retour', 'Retour')],
        default='aller',
        help_text="Type de trajet: aller ou retour"
    )

    # Date du trajet
    date_trajet = models.DateField(
        null=True,
        blank=True,
        help_text="Date du trajet (généralement la date de départ pour l'aller, date de retour pour le retour)"
    )

    # Informations du trajet
    origine = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    frais_route = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Frais de route pour ce trajet"
    )
    frais_carburant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Frais de carburant pour ce trajet"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['mission', 'contrat', 'type_trajet'],
                name='unique_frais_par_mission_type'
            )
        ]
        verbose_name = "Frais de trajet"
        verbose_name_plural = "Frais de trajets"
        ordering = ['date_trajet', 'type_trajet']

    def save(self, *args, **kwargs):
        # Générer pk_frais automatiquement si non défini
        if not self.pk_frais:
            if self.mission and self.contrat and self.date_trajet:
                # Nouveau format: hash de mission_id + contrat_id (tronqué) + date + type
                # Utiliser hash pour gérer les mission_pk très longs
                mission_hash = hashlib.md5(self.mission.pk_mission.encode()).hexdigest()[:10]
                contrat_id = str(self.contrat.pk_contrat)[:30]
                base = f"{mission_hash}_{contrat_id}_{self.date_trajet}_{self.type_trajet}"
            else:
                # Ancien format (pour données existantes): origine_destination_montants
                base = f"{self.origine}_{self.destination}_{int(self.frais_route)}_{int(self.frais_carburant)}"
            self.pk_frais = slugify(base)[:250]
        super().save(*args, **kwargs)

    def __str__(self):
        # Informations de base
        type_str = self.type_trajet.upper()
        trajet_str = f"{self.origine} → {self.destination}"
        montant_total = self.frais_route + self.frais_carburant

        # Informations contextuelles
        mission_str = f"Mission: {self.mission.pk_mission[:20]}..." if self.mission else "Aucune mission"
        camion_str = f"Camion: {self.contrat.camion.immatriculation}" if self.contrat and self.contrat.camion else "Aucun camion"
        chauffeur_str = f"Chauffeur: {self.contrat.chauffeur.nom}" if self.contrat and self.contrat.chauffeur else "Aucun chauffeur"
        date_str = f"Date: {self.date_trajet}" if self.date_trajet else "Date non définie"

        return f"{type_str} | {mission_str} | {camion_str} | {chauffeur_str} | {date_str} | {trajet_str} | {montant_total} FCFA"

class Mission(models.Model):
    pk_mission = models.CharField(max_length=250, primary_key=True, editable=False)
    prestation_transport = models.ForeignKey("PrestationDeTransports", on_delete=models.CASCADE)
    date_depart = models.DateField(db_index=True)
    date_retour = models.DateField(blank=True, null=True, db_index=True)
    origine = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    itineraire = models.TextField(
        blank=True,
        help_text="Décrivez l'itinéraire détaillé de la mission"
    )
    contrat = models.ForeignKey("ContratTransport", on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_MISSION_CHOICES, default='en cours', db_index=True)

    # Gestion du stationnement (demurrage)
    date_arrivee = models.DateField(
        blank=True,
        null=True,
        help_text="Date d'arrivée du camion à destination"
    )
    date_dechargement = models.DateField(
        blank=True,
        null=True,
        help_text="Date effective du déchargement"
    )
    statut_stationnement = models.CharField(
        max_length=20,
        choices=[
            ('attente', 'En attente'),
            ('en_stationnement', 'En stationnement (frais applicables)'),
            ('decharge', 'Déchargé')
        ],
        default='attente',
        help_text="Statut du stationnement"
    )
    jours_stationnement_facturables = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Nombre de jours de stationnement facturables (après les 3 jours gratuits)"
    )
    montant_stationnement = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Montant total des frais de stationnement (25 000 CFA/jour)"
    )

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

    def calculer_jours_ouvrables(self, date_debut, date_fin):
        """
        Calcule le nombre de jours ouvrables entre deux dates (exclut samedi et dimanche)

        Args:
            date_debut: Date de début
            date_fin: Date de fin

        Returns:
            int: Nombre de jours ouvrables
        """
        from datetime import timedelta

        if not date_debut or not date_fin:
            return 0

        jours_ouvrables = 0
        current_date = date_debut

        while current_date <= date_fin:
            # 0 = lundi, 6 = dimanche
            # On compte seulement du lundi (0) au vendredi (4)
            if current_date.weekday() < 5:  # Lundi à vendredi
                jours_ouvrables += 1
            current_date += timedelta(days=1)

        return jours_ouvrables

    def calculer_frais_stationnement(self):
        """
        Calcule les frais de stationnement (demurrage)

        Règles mises à jour:
        - 3 premiers jours ouvrables (lun-ven) gratuits
        - Si arrivée le weekend, les 3 jours gratuits commencent le lundi suivant
        - À partir du 4ème jour ouvrable: TOUS les jours comptent (y compris sam/dim)
        - Tarif: 25 000 CFA par jour après la période gratuite
        - Pas de jours fériés exclus

        Returns:
            dict: Informations sur les frais de stationnement
        """
        if not self.date_arrivee:
            return {
                'jours_total': 0,
                'jours_gratuits': 0,
                'jours_facturables': 0,
                'montant': Decimal('0.00'),
                'message': 'Date d\'arrivée non renseignée'
            }

        from datetime import timedelta
        from django.utils import timezone

        # Date de fin: déchargement si renseigné, sinon aujourd'hui
        date_fin = self.date_dechargement or timezone.now().date()

        # Constantes
        JOURS_GRATUITS = 3
        TARIF_JOUR = Decimal('25000.00')  # 25 000 CFA

        # Étape 1: Trouver le début de la période gratuite
        # Si arrivée en weekend, décaler au lundi suivant
        date_debut_gratuit = self.date_arrivee
        while date_debut_gratuit.weekday() >= 5:  # 5=samedi, 6=dimanche
            date_debut_gratuit += timedelta(days=1)

        # Étape 2: Compter 3 jours ouvrables à partir de là (période gratuite)
        jours_ouvrables_comptes = 0
        current_date = date_debut_gratuit
        date_fin_gratuit = None

        while jours_ouvrables_comptes < JOURS_GRATUITS:
            if current_date.weekday() < 5:  # Lundi à vendredi
                jours_ouvrables_comptes += 1
                if jours_ouvrables_comptes == JOURS_GRATUITS:
                    date_fin_gratuit = current_date
                    break
            current_date += timedelta(days=1)

        # Étape 3: À partir du jour suivant la fin de la période gratuite,
        # compter TOUS les jours calendaires (y compris weekends) jusqu'au déchargement
        if date_fin <= date_fin_gratuit:
            # Déchargement pendant la période gratuite
            jours_facturables = 0
        else:
            # Compter tous les jours calendaires après la période gratuite
            jours_facturables = (date_fin - date_fin_gratuit).days

        # Calculer le montant
        montant = jours_facturables * TARIF_JOUR

        # Déterminer le statut
        if jours_facturables > 0:
            statut = 'en_stationnement'
        else:
            statut = 'attente'

        if self.date_dechargement:
            statut = 'decharge'

        # Calculer le nombre total de jours calendaires depuis l'arrivée
        jours_total = (date_fin - self.date_arrivee).days + 1

        message = f"{jours_total} jours total depuis arrivée, {JOURS_GRATUITS} jours ouvrables gratuits, {jours_facturables} jours facturables"

        return {
            'jours_total': jours_total,
            'jours_gratuits': JOURS_GRATUITS,
            'jours_facturables': jours_facturables,
            'montant': montant,
            'statut': statut,
            'message': message
        }

    def bloquer_pour_stationnement(self, date_arrivee=None):
        """
        Bloque la mission pour stationnement et calcule les frais

        Args:
            date_arrivee: Date d'arrivée du camion (par défaut aujourd'hui)
        """
        from django.utils import timezone

        if date_arrivee is None:
            date_arrivee = timezone.now().date()

        self.date_arrivee = date_arrivee

        # Calculer les frais
        frais_info = self.calculer_frais_stationnement()

        # Mettre à jour les champs
        self.jours_stationnement_facturables = frais_info['jours_facturables']
        self.montant_stationnement = frais_info['montant']
        self.statut_stationnement = frais_info['statut']

        self.save()

        return frais_info

    def marquer_dechargement(self, date_dechargement=None):
        """
        Marque la mission comme déchargée et calcule les frais finaux

        Args:
            date_dechargement: Date effective du déchargement (par défaut aujourd'hui)

        Returns:
            dict: Informations sur les frais finaux
        """
        from django.utils import timezone

        if date_dechargement is None:
            date_dechargement = timezone.now().date()

        if not self.date_arrivee:
            raise ValidationError('❌ La date d\'arrivée doit être renseignée avant le déchargement')

        if date_dechargement < self.date_arrivee:
            raise ValidationError(
                f'❌ La date de déchargement ({date_dechargement}) ne peut pas être avant la date d\'arrivée ({self.date_arrivee})'
            )

        self.date_dechargement = date_dechargement
        self.statut_stationnement = 'decharge'

        # Calculer les frais finaux
        frais_info = self.calculer_frais_stationnement()

        self.jours_stationnement_facturables = frais_info['jours_facturables']
        self.montant_stationnement = frais_info['montant']

        self.save()

        return frais_info

    def terminer_mission(self, date_retour=None, force=False):
        """Méthode pour terminer proprement une mission avec validation de la date

        Args:
            date_retour: Date de retour effective (par défaut aujourd'hui)
            force: Si True, force la terminaison même en retard

        Returns:
            dict: Informations sur la pénalité si en retard
        """
        from django.utils import timezone

        if date_retour is None:
            date_retour = timezone.now().date()

        # Vérifier que la date de retour est cohérente
        if date_retour < self.date_depart:
            raise ValidationError(
                f'❌ La date de retour ({date_retour}) ne peut pas être avant la date de départ ({self.date_depart})'
            )

        info_penalite = {
            'en_retard': False,
            'jours_retard': 0,
            'penalite': 0,
            'message': ''
        }

        # Vérifier si la date dépasse la limite du contrat
        if date_retour > self.contrat.date_limite_retour:
            jours_retard = (date_retour - self.contrat.date_limite_retour).days
            penalite = jours_retard * 25000  # 25 000 FCFA par jour

            info_penalite = {
                'en_retard': True,
                'jours_retard': jours_retard,
                'penalite': penalite,
                'message': f'⚠️ Mission terminée avec {jours_retard} jour(s) de retard. Pénalité: {penalite} FCFA'
            }

            # Si force=False, lever une erreur avec les infos
            if not force:
                raise ValidationError(
                    f'⚠️ ATTENTION: La date de retour ({date_retour}) dépasse la date limite du contrat ({self.contrat.date_limite_retour}) '
                    f'de {jours_retard} jour(s). Pénalité: {penalite} FCFA. '
                    f'Confirmez pour terminer quand même.'
                )

        self.date_retour = date_retour
        self.statut = 'terminée'
        self.save()

        # 🆕 RETOURNER LE CONTENEUR AU PORT
        if self.contrat and self.contrat.conteneur:
            self.contrat.conteneur.retourner_au_port()
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🚢 Conteneur {self.contrat.conteneur.numero_conteneur} retourné au port (disponible)")

        return info_penalite

    def annuler_mission(self, raison=''):
        """Annule une mission et tous les objets liés en cascade

        Args:
            raison: Raison de l'annulation

        Cette méthode annule automatiquement:
        - La mission elle-même
        - Le contrat de transport associé
        - Les cautions associées
        - Les paiements associés
        """
        if self.statut == 'terminée':
            raise ValidationError('❌ Impossible d\'annuler une mission déjà terminée.')

        if self.statut == 'annulée':
            raise ValidationError('⚠️ Cette mission est déjà annulée.')

        from django.utils import timezone
        date_annulation = timezone.now()

        # 1. Annuler la mission
        self.statut = 'annulée'

        # Ajouter la raison dans l'itinéraire si fournie
        if raison:
            if not self.itineraire:
                self.itineraire = ''
            self.itineraire += f'\n\n--- MISSION ANNULÉE ---\nRaison: {raison}\nDate annulation: {date_annulation.strftime("%d/%m/%Y %H:%M")}'
        else:
            if not self.itineraire:
                self.itineraire = ''
            self.itineraire += f'\n\n--- MISSION ANNULÉE ---\nDate annulation: {date_annulation.strftime("%d/%m/%Y %H:%M")}'

        self.save()

        # 2. Annuler le contrat de transport associé
        if self.contrat:
            if not self.contrat.commentaire:
                self.contrat.commentaire = ''
            self.contrat.commentaire += f'\n\n🚫 CONTRAT ANNULÉ\nMission annulée le {date_annulation.strftime("%d/%m/%Y %H:%M")}\nRaison: {raison if raison else "Non spécifiée"}'
            self.contrat.save()

        # 3. Annuler toutes les cautions associées
        from .finance import Cautions
        cautions = Cautions.objects.filter(contrat=self.contrat)
        for caution in cautions:
            if caution.statut != 'annulee':
                caution.statut = 'annulee'
                caution.save()

        # 4. Marquer les paiements associés comme annulés
        from .finance import PaiementMission
        paiements = PaiementMission.objects.filter(mission=self)
        for paiement in paiements:
            # MODIFIÉ: Annuler TOUS les paiements (validés ou non)
            if not paiement.observation:
                paiement.observation = ''

            if paiement.est_valide:
                # Paiement déjà validé - ajouter un avertissement
                paiement.observation += (
                    f'\n\n⚠️ PAIEMENT VALIDÉ MAIS MISSION ANNULÉE\n'
                    f'Mission annulée le {date_annulation.strftime("%d/%m/%Y %H:%M")}\n'
                    f'Raison: {raison if raison else "Non spécifiée"}\n'
                    f'ACTION REQUISE: Vérifier si remboursement nécessaire'
                )
            else:
                # Paiement non validé - marquer comme annulé
                paiement.observation += (
                    f'\n\n❌ PAIEMENT ANNULÉ\n'
                    f'Mission annulée le {date_annulation.strftime("%d/%m/%Y %H:%M")}\n'
                    f'Raison: {raison if raison else "Non spécifiée"}'
                )

            # Marquer le statut comme annulé pour TOUS les paiements
            paiement.statut_paiement = 'annule'
            paiement.save()

        # 🆕 5. RETOURNER LE CONTENEUR AU PORT (car mission annulée)
        if self.contrat and self.contrat.conteneur:
            self.contrat.conteneur.retourner_au_port()
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🚢 Conteneur {self.contrat.conteneur.numero_conteneur} retourné au port (mission annulée)")

    @property
    def frais_trajet_aller(self):
        """Retourne le frais de trajet aller de cette mission"""
        try:
            return self.frais_trajets.get(type_trajet='aller')
        except:
            return None

    @property
    def frais_trajet_retour(self):
        """Retourne le frais de trajet retour de cette mission"""
        try:
            return self.frais_trajets.get(type_trajet='retour')
        except:
            return None

    def get_total_frais_trajet(self):
        """Calcule le total des frais de trajet (aller + retour)"""
        total = Decimal('0.00')
        for frais in self.frais_trajets.all():
            total += frais.frais_route + frais.frais_carburant
        return total

    def get_type_transport(self):
        """
        Retourne le type de transport de la mission

        Returns:
            str: 'aller_retour', 'aller_simple', ou 'sans_trajet'
        """
        has_aller = self.frais_trajet_aller is not None
        has_retour = self.frais_trajet_retour is not None

        if has_aller and has_retour:
            return 'aller_retour'
        elif has_aller:
            return 'aller_simple'
        else:
            return 'sans_trajet'

    def get_type_transport_display(self):
        """
        Retourne le libellé du type de transport

        Returns:
            str: Libellé lisible du type de transport
        """
        type_map = {
            'aller_retour': 'Aller-Retour',
            'aller_simple': 'Aller simple',
            'sans_trajet': 'Sans trajet'
        }
        return type_map.get(self.get_type_transport(), 'Inconnu')

    def get_type_transport_badge(self):
        """
        Retourne le badge HTML pour le type de transport

        Returns:
            dict: {'icon': '...', 'color': '...', 'label': '...'}
        """
        type_transport = self.get_type_transport()

        badges = {
            'aller_retour': {
                'icon': 'fa-exchange-alt',
                'color': 'success',
                'label': 'Aller-Retour',
                'title': 'Mission avec trajet aller et retour'
            },
            'aller_simple': {
                'icon': 'fa-arrow-right',
                'color': 'info',
                'label': 'Aller simple',
                'title': 'Mission avec trajet aller uniquement'
            },
            'sans_trajet': {
                'icon': 'fa-exclamation-circle',
                'color': 'warning',
                'label': 'Sans trajet',
                'title': 'Aucun trajet enregistré pour cette mission'
            }
        }

        return badges.get(type_transport, badges['sans_trajet'])

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
        return (f"{self.pk_mission} - "
                f"{self.origine} → {self.destination} - "
                f"Départ: {self.date_depart} - "
                f"Statut: {self.statut}")

# ici nest pas encore faite

class MissionConteneur(models.Model):
    mission = models.ForeignKey("Mission", on_delete=models.CASCADE)
    conteneur = models.ForeignKey("Conteneur", on_delete=models.CASCADE)

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

    