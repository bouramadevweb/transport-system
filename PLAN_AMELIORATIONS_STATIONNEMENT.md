# Plan d'Améliorations - Système de Stationnement (Demurrage)

## Date: 29 décembre 2024

## Vue d'ensemble

Le système de stationnement est **fonctionnel** mais présente plusieurs lacunes critiques qui affectent:
- L'intégration avec le système de paiement
- La validation des données
- L'expérience utilisateur
- Le reporting financier

---

## 🔴 PRIORITÉ CRITIQUE (À faire immédiatement)

### 1. **Intégration des frais de stationnement avec le système de paiement**

**Problème actuel:**
- Le montant du stationnement (`mission.montant_stationnement`) est calculé mais **NON inclus automatiquement** dans `PaiementMission`
- Les utilisateurs doivent manuellement ajouter ces frais, risque d'erreurs

**Solution requise:**
```python
# Dans PaiementMission model, ajouter:
frais_stationnement = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=Decimal('0.00'),
    help_text="Frais de stationnement (demurrage)"
)

# Dans la méthode save():
def save(self, *args, **kwargs):
    if self.mission and self.mission.montant_stationnement:
        self.frais_stationnement = self.mission.montant_stationnement
        # Ajouter au montant total
        self.montant_total = self.montant_base + self.frais_stationnement
    super().save(*args, **kwargs)
```

**Fichiers à modifier:**
- `transport/models/finance.py`
- `transport/views/finance_views.py`
- `transport/templates/transport/finances/paiement_mission_list.html`

**Impact:** ⭐⭐⭐⭐⭐ (Financier critique)

---

### 2. **Corriger les erreurs d'import dans mission.py**

**Problème actuel:**
```python
# Ligne 428-429 dans mission.py
from models import Cautions  # ❌ ImportError
from models import PaiementMission  # ❌ ImportError
```

**Solution:**
```python
# Utiliser import relatif:
from .finance import Cautions, PaiementMission
```

**Fichiers à modifier:**
- `transport/models/mission.py` (lignes 401-416)

**Impact:** ⭐⭐⭐⭐⭐ (Bug bloquant)

---

### 3. **Ajouter confirmation avant "Marquer le déchargement"**

**Problème actuel:**
- Pas de modal de confirmation
- Utilisateur peut soumettre par erreur
- Pas d'aperçu des frais calculés avant validation

**Solution:**
Ajouter un modal Bootstrap avec aperçu des frais:
```html
<!-- Modal de confirmation -->
<div class="modal fade" id="confirmDechargementModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-success text-white">
                <h5 class="modal-title">Confirmer le déchargement</h5>
            </div>
            <div class="modal-body">
                <p><strong>Date d'arrivée:</strong> {{ mission.date_arrivee }}</p>
                <p><strong>Date de déchargement:</strong> <span id="datePreview"></span></p>
                <hr>
                <h6>Calcul des frais:</h6>
                <div id="feesPreview">
                    <!-- Rempli par JavaScript -->
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                <button type="button" class="btn btn-success" id="confirmBtn">Confirmer</button>
            </div>
        </div>
    </div>
</div>
```

**Fichiers à modifier:**
- `transport/templates/transport/missions/marquer_dechargement.html`

**Impact:** ⭐⭐⭐⭐ (UX importante)

---

### 4. **Empêcher le double blocage**

**Problème actuel:**
- Si l'utilisateur clique deux fois sur "Bloquer pour stationnement", il peut créer des frais en double
- Pas de vérification si `date_arrivee` est déjà définie

**Solution:**
```python
# Dans bloquer_stationnement view:
@login_required
def bloquer_stationnement(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)

    # ✅ AJOUTER CETTE VÉRIFICATION:
    if mission.date_arrivee:
        messages.warning(request,
            f'⚠️ Cette mission est déjà bloquée depuis le {mission.date_arrivee.strftime("%d/%m/%Y")}. '
            f'Utilisez "Marquer le déchargement" ou modifiez la mission.'
        )
        return redirect('mission_list')

    # ... reste du code
```

**Fichiers à modifier:**
- `transport/views/mission_views.py`

**Impact:** ⭐⭐⭐⭐ (Prévention d'erreurs)

---

### 5. **Ajouter des permissions pour les opérations de stationnement**

**Problème actuel:**
- N'importe quel utilisateur connecté peut bloquer/marquer le déchargement
- Pas de contrôle d'accès

**Solution:**
```python
from transport.decorators import manager_or_admin_required

@login_required
@manager_or_admin_required  # ✅ AJOUTER
def bloquer_stationnement(request, pk):
    # ...

@login_required
@manager_or_admin_required  # ✅ AJOUTER
def marquer_dechargement(request, pk):
    # ...
```

**Fichiers à modifier:**
- `transport/views/mission_views.py`

**Impact:** ⭐⭐⭐⭐ (Sécurité)

---

## 🟠 PRIORITÉ HAUTE (Important pour l'utilisation)

### 6. **Aperçu des frais en temps réel avant validation**

**Amélioration:**
Ajouter un endpoint AJAX pour calculer les frais en temps réel:

```python
# Dans ajax_views.py
@login_required
def preview_frais_stationnement(request):
    """Calcule les frais sans sauvegarder"""
    mission_id = request.GET.get('mission_id')
    date_dechargement = request.GET.get('date_dechargement')

    mission = get_object_or_404(Mission, pk_mission=mission_id)

    # Créer un objet temporaire pour calculer
    temp_mission = mission
    temp_mission.date_dechargement = datetime.strptime(date_dechargement, '%Y-%m-%d').date()

    frais_info = temp_mission.calculer_frais_stationnement()

    return JsonResponse({
        'jours_facturables': frais_info['jours_facturables'],
        'montant': float(frais_info['montant']),
        'message': frais_info['message']
    })
```

**Fichiers à créer/modifier:**
- `transport/views/ajax_views.py`
- `transport/urls.py`
- `transport/templates/transport/missions/marquer_dechargement.html` (JavaScript)

**Impact:** ⭐⭐⭐⭐ (UX)

---

### 7. **Améliorer la colonne Stationnement dans mission_list**

**Problème actuel:**
- Trop d'informations entassées
- Difficile à lire sur mobile
- Pas cliquable pour voir les détails

**Solution:**
Créer un popover/tooltip avec détails:
```html
<td>
    {% if mission.date_arrivee %}
        <button type="button" class="btn btn-sm btn-link"
                data-bs-toggle="popover"
                data-bs-html="true"
                data-bs-content="
                    <strong>Arrivée:</strong> {{ mission.date_arrivee|date:'d/m/Y' }}<br>
                    <strong>Déchargement:</strong> {{ mission.date_dechargement|date:'d/m/Y'|default:'En cours' }}<br>
                    <strong>Jours facturables:</strong> {{ mission.jours_stationnement_facturables }}<br>
                    <strong>Montant:</strong> {{ mission.montant_stationnement|floatformat:0 }} CFA
                ">
            <span class="badge bg-{{ status_color }}">
                {{ mission.montant_stationnement|floatformat:0 }} CFA
            </span>
        </button>
    {% else %}
        <span class="text-muted">—</span>
    {% endif %}
</td>
```

**Fichiers à modifier:**
- `transport/templates/transport/missions/mission_list.html`

**Impact:** ⭐⭐⭐ (UX)

---

### 8. **Créer un tableau de bord des revenus de stationnement**

**Fonctionnalité manquante:**
Dashboard avec KPIs:
- Total des frais de stationnement ce mois
- Nombre de missions avec frais
- Durée moyenne de stationnement
- Top 5 des missions les plus coûteuses

**Fichiers à créer:**
- `transport/views/stationnement_reports.py`
- `transport/templates/transport/reports/stationnement_dashboard.html`
- `transport/urls.py` (nouvelle route)

**Impact:** ⭐⭐⭐ (Reporting)

---

### 9. **Ajouter des notifications pour les missions en stationnement**

**Fonctionnalité manquante:**
- Email/notification quand une mission entre en période facturable (jour 4)
- Alerte quotidienne des missions en stationnement
- Notification au client des frais encourus

**Solution:**
Utiliser le système de notifications existant + tâche cron:
```python
# Dans management/commands/check_stationnement.py
from django.core.management.base import BaseCommand
from transport.models import Mission, Notification
from datetime import date

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Missions en stationnement actif
        missions = Mission.objects.filter(
            date_arrivee__isnull=False,
            date_dechargement__isnull=True,
            statut='en cours'
        )

        for mission in missions:
            frais_info = mission.calculer_frais_stationnement()

            if frais_info['jours_facturables'] > 0:
                # Créer notification
                Notification.objects.create(
                    utilisateur=mission.contrat.client.utilisateur,
                    type_notification='STATIONNEMENT',
                    titre=f'Frais de stationnement - Mission {mission.pk_mission}',
                    message=f'Votre mission a {frais_info["jours_facturables"]} jours facturables. '
                            f'Montant actuel: {frais_info["montant"]} CFA',
                    lien=f'/missions/{mission.pk_mission}/'
                )
```

**Fichiers à créer:**
- `transport/management/commands/check_stationnement.py`
- Configuration cron (crontab ou Celery beat)

**Impact:** ⭐⭐⭐⭐ (Proactif)

---

## 🟡 PRIORITÉ MOYENNE (Amélioration continue)

### 10. **Permettre la modification des dates de stationnement**

**Fonctionnalité manquante:**
- Pas de formulaire pour corriger date_arrivee ou date_dechargement après saisie
- Obligation d'annuler la mission et recommencer

**Solution:**
Créer une vue `modifier_stationnement`:
```python
@login_required
@manager_or_admin_required
def modifier_stationnement(request, pk):
    mission = get_object_or_404(Mission, pk_mission=pk)

    if request.method == 'POST':
        # Sauvegarder anciennes valeurs pour audit
        old_arrivee = mission.date_arrivee
        old_dechargement = mission.date_dechargement

        # Mettre à jour
        mission.date_arrivee = request.POST.get('date_arrivee')
        mission.date_dechargement = request.POST.get('date_dechargement')

        # Recalculer
        frais_info = mission.calculer_frais_stationnement()
        mission.jours_stationnement_facturables = frais_info['jours_facturables']
        mission.montant_stationnement = frais_info['montant']
        mission.save()

        # Audit log
        AuditLog.log_action(
            utilisateur=request.user,
            action='UPDATE',
            model_name='Mission',
            object_id=mission.pk_mission,
            object_repr=f'Modification stationnement: {old_arrivee} → {mission.date_arrivee}',
            request=request
        )

        return redirect('mission_list')

    return render(request, 'transport/missions/modifier_stationnement.html', {'mission': mission})
```

**Impact:** ⭐⭐⭐ (Flexibilité)

---

### 11. **Export Excel des données de stationnement**

**Fonctionnalité manquante:**
- Pas d'export pour comptabilité
- Rapport mensuel des frais de stationnement

**Solution:**
Utiliser `openpyxl` ou `pandas`:
```python
import pandas as pd
from django.http import HttpResponse

@login_required
def export_stationnement(request):
    missions = Mission.objects.filter(
        montant_stationnement__gt=0
    ).select_related('contrat__client', 'contrat__chauffeur')

    data = []
    for m in missions:
        data.append({
            'Mission ID': m.pk_mission,
            'Client': m.contrat.client.nom,
            'Origine': m.origine,
            'Destination': m.destination,
            'Date Arrivée': m.date_arrivee,
            'Date Déchargement': m.date_dechargement,
            'Jours Facturables': m.jours_stationnement_facturables,
            'Montant (CFA)': float(m.montant_stationnement)
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="stationnement_report.xlsx"'

    df.to_excel(response, index=False)
    return response
```

**Impact:** ⭐⭐⭐ (Reporting)

---

### 12. **Rendre le tarif configurable**

**Problème actuel:**
- Tarif hardcodé: `25000 CFA`
- Pas de flexibilité

**Solution:**
Créer un modèle `ConfigurationStationnement`:
```python
class ConfigurationStationnement(models.Model):
    tarif_jour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('25000.00'),
        help_text="Tarif par jour de stationnement (CFA)"
    )
    jours_gratuits = models.IntegerField(
        default=3,
        help_text="Nombre de jours ouvrables gratuits"
    )
    actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Configuration Stationnement"
        verbose_name_plural = "Configurations Stationnement"

    @classmethod
    def get_current_config(cls):
        """Récupère la configuration active"""
        from django.utils import timezone
        today = timezone.now().date()

        return cls.objects.filter(
            actif=True,
            date_debut__lte=today,
            date_fin__gte=today
        ).first() or cls.objects.create(
            tarif_jour=Decimal('25000.00'),
            jours_gratuits=3,
            date_debut=today
        )
```

**Utilisation dans `calculer_frais_stationnement()`:
```python
def calculer_frais_stationnement(self):
    # ...
    config = ConfigurationStationnement.get_current_config()
    JOURS_GRATUITS = config.jours_gratuits
    TARIF_JOUR = config.tarif_jour
    # ...
```

**Impact:** ⭐⭐⭐ (Flexibilité)

---

### 13. **Validation côté serveur des dates**

**Problème actuel:**
- Validation principalement côté client (JavaScript)
- Risque de soumission de dates invalides

**Solution:**
Ajouter validation dans les vues:
```python
def bloquer_stationnement(request, pk):
    # ...
    if request.method == 'POST':
        date_arrivee_str = request.POST.get('date_arrivee')
        date_arrivee = datetime.strptime(date_arrivee_str, '%Y-%m-%d').date()

        # ✅ VALIDATIONS:
        from django.utils import timezone
        today = timezone.now().date()

        if date_arrivee > today:
            messages.error(request, '❌ La date d\'arrivée ne peut pas être dans le futur')
            return render(request, 'transport/missions/bloquer_stationnement.html', context)

        if date_arrivee < mission.date_depart:
            messages.error(request, '❌ La date d\'arrivée doit être >= date de départ de la mission')
            return render(request, 'transport/missions/bloquer_stationnement.html', context)

        # Continue...
```

**Impact:** ⭐⭐⭐ (Robustesse)

---

## 🟢 PRIORITÉ BASSE (Nice-to-have)

### 14. **Timeline visuelle du stationnement**

Vue calendrier montrant:
- Date départ → Date arrivée → Date déchargement
- Période gratuite en vert
- Période facturable en rouge

**Impact:** ⭐⭐ (Visualisation)

---

### 15. **Support des jours fériés**

Actuellement: "Aucun jour férié exclu"
Possibilité d'ajouter une table de jours fériés maliens et les exclure du calcul.

**Impact:** ⭐⭐ (Précision)

---

### 16. **Portail client pour contester les frais**

Interface pour les clients pour:
- Voir leurs frais de stationnement
- Contester avec justificatif
- Historique des contestations

**Impact:** ⭐ (Advanced)

---

## 📋 Plan d'implémentation suggéré

### Phase 1 - Corrections critiques (1-2 jours)
1. ✅ Corriger imports mission.py
2. ✅ Intégration PaiementMission
3. ✅ Ajouter permissions
4. ✅ Empêcher double blocage

### Phase 2 - Amélioration UX (2-3 jours)
5. ✅ Modal de confirmation
6. ✅ Aperçu frais en temps réel
7. ✅ Améliorer mission_list
8. ✅ Validation serveur

### Phase 3 - Fonctionnalités avancées (3-5 jours)
9. ✅ Dashboard stationnement
10. ✅ Notifications
11. ✅ Export Excel
12. ✅ Modification dates

### Phase 4 - Configuration (1-2 jours)
13. ✅ Tarif configurable
14. ✅ Timeline visuelle (optionnel)

---

## Résumé des fichiers à modifier

### Fichiers existants à modifier:
1. `transport/models/mission.py` - Corriger imports (ligne 401-416)
2. `transport/models/finance.py` - Ajouter frais_stationnement
3. `transport/views/mission_views.py` - Permissions, validations
4. `transport/views/ajax_views.py` - Endpoint preview
5. `transport/templates/transport/missions/bloquer_stationnement.html` - Validations
6. `transport/templates/transport/missions/marquer_dechargement.html` - Modal
7. `transport/templates/transport/missions/mission_list.html` - Popover
8. `transport/urls.py` - Nouvelles routes

### Nouveaux fichiers à créer:
9. `transport/models/configuration.py` - ConfigurationStationnement
10. `transport/views/stationnement_reports.py` - Rapports
11. `transport/templates/transport/reports/stationnement_dashboard.html`
12. `transport/templates/transport/missions/modifier_stationnement.html`
13. `transport/management/commands/check_stationnement.py` - Notifications auto

---

**Estimé total:** 8-12 jours de développement pour Phase 1-3
**ROI:** Amélioration significative de la précision financière et UX
