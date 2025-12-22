"""
Audit.Py

Modèles pour audit
"""

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from .choices import *

class Notification(models.Model):
    """Modèle pour gérer les notifications utilisateur"""
    NOTIFICATION_TYPES = [
        ('mission_terminee', 'Mission terminée'),
        ('paiement_valide', 'Paiement validé'),
        ('mission_retard', 'Mission en retard'),
        ('reparation_urgente', 'Réparation urgente'),
        ('caution_bloquee', 'Caution bloquée'),
        ('info', 'Information'),
        ('alerte', 'Alerte'),
    ]

    ICON_CHOICES = [
        ('check-circle', 'Succès'),
        ('exclamation-triangle', 'Avertissement'),
        ('info-circle', 'Information'),
        ('times-circle', 'Erreur'),
        ('bell', 'Notification'),
    ]

    COLOR_CHOICES = [
        ('success', 'Vert'),
        ('warning', 'Orange'),
        ('info', 'Bleu'),
        ('danger', 'Rouge'),
        ('primary', 'Bleu primaire'),
    ]

    pk_notification = models.CharField(max_length=250, primary_key=True, editable=False)
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='bell')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relations optionnelles pour lier la notification à un objet spécifique
    mission = models.ForeignKey("Mission", on_delete=models.CASCADE, null=True, blank=True)
    paiement = models.ForeignKey("PaiementMission", on_delete=models.CASCADE, null=True, blank=True)
    reparation = models.ForeignKey("Reparation", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['utilisateur', '-created_at']),
            models.Index(fields=['utilisateur', 'is_read']),
        ]

    def save(self, *args, **kwargs):
        if not self.pk_notification:
            base = f"{self.utilisateur.pk_utilisateur}{self.type_notification}{self.created_at or now()}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '')
            slug = slugify(base)[:240]
            self.pk_notification = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.utilisateur.email} ({'Lu' if self.is_read else 'Non lu'})"

class AuditLog(models.Model):
    """
    Modèle pour enregistrer l'historique des actions importantes
    ============================================================

    Ce modèle permet de tracer toutes les opérations critiques effectuées
    dans le système (création, modification, suppression d'objets).

    Utilisation:
    - Automatique via signals pour les modèles critiques
    - Manuelle dans les vues pour les actions spécifiques

    Exemple:
        AuditLog.objects.create(
            utilisateur=request.user,
            action='VALIDER_PAIEMENT',
            model_name='PaiementMission',
            object_id=paiement.pk_paiement,
            object_repr=str(paiement),
            changes={'est_valide': {'old': False, 'new': True}}
        )
    """

    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('VALIDER_PAIEMENT', 'Validation de paiement'),
        ('TERMINER_MISSION', 'Terminer mission'),
        ('ANNULER_MISSION', 'Annuler mission'),
        ('BLOQUER_CAUTION', 'Bloquer caution'),
        ('DEBLOQUER_CAUTION', 'Débloquer caution'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('CHANGE_PASSWORD', 'Changement de mot de passe'),
    ]

    pk_audit = models.CharField(max_length=250, primary_key=True, editable=False)

    # Qui a fait l'action
    utilisateur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Utilisateur qui a effectué l'action"
    )

    # Quand
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Quoi
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Type d'action effectuée"
    )

    # Sur quel objet
    model_name = models.CharField(
        max_length=100,
        help_text="Nom du modèle concerné (ex: Mission, PaiementMission)"
    )
    object_id = models.CharField(
        max_length=250,
        help_text="ID de l'objet concerné"
    )
    object_repr = models.TextField(
        help_text="Représentation textuelle de l'objet",
        blank=True
    )

    # Détails
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dictionnaire des changements effectués (format: {'champ': {'old': valeur, 'new': valeur}})"
    )

    # Métadonnées supplémentaires
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Adresse IP de l'utilisateur"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent du navigateur"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['utilisateur', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action']),
        ]
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"

    def save(self, *args, **kwargs):
        if not self.pk_audit:
            base = f"audit{self.utilisateur.pk_utilisateur if self.utilisateur else 'system'}{self.action}{self.timestamp or now()}"
            base = base.replace(',', '').replace(';', '').replace(' ', '').replace('-', '').replace(':', '')
            slug = slugify(base)[:240]
            self.pk_audit = f"{slug}-{uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        user = self.utilisateur.email if self.utilisateur else 'Système'
        return f"{self.get_action_display()} - {self.model_name} #{self.object_id[:8]}... par {user} le {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def log_action(cls, utilisateur, action, model_name, object_id, object_repr='', changes=None, request=None):
        """
        Méthode helper pour créer facilement un log d'audit

        Args:
            utilisateur: Instance de Utilisateur
            action: Code de l'action (voir ACTION_CHOICES)
            model_name: Nom du modèle (str)
            object_id: ID de l'objet (str)
            object_repr: Représentation textuelle de l'objet (str)
            changes: Dictionnaire des changements (dict)
            request: HttpRequest pour récupérer IP et user agent

        Returns:
            Instance AuditLog créée
        """
        ip_address = None
        user_agent = ''

        if request:
            # Récupérer l'IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Récupérer le user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        return cls.objects.create(
            utilisateur=utilisateur,
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

# =======================
# GESTION DE LA PAIE
# =======================

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

