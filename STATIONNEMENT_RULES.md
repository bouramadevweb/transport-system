# Règles de Stationnement (Demurrage) - Documentation Technique

## Vue d'ensemble

Le système de stationnement permet de facturer les frais de parking lorsqu'un camion arrive à destination et attend le déchargement.

## Règles Métier

### Période Gratuite
- **3 premiers jours ouvrables gratuits** (lundi au vendredi uniquement)
- Si le camion arrive un **weekend (samedi ou dimanche)**, la période gratuite commence le **lundi suivant**
- Les weekends ne comptent PAS dans les 3 jours gratuits

### Période Facturable
- À partir du **4ème jour ouvrable**, la facturation commence
- **IMPORTANT**: Après le 4ème jour, **TOUS les jours comptent**, y compris les samedis et dimanches
- Tarif: **25 000 CFA par jour**
- Aucun jour férié n'est exclu du calcul

## Exemples de Calcul

### Exemple 1: Arrivée en semaine
- **Arrivée**: Lundi 6 janvier 2025
- **Déchargement**: Lundi 13 janvier 2025

**Calcul**:
1. Période gratuite commence: Lundi 6 janvier
2. Jours gratuits: Lundi 6, Mardi 7, Mercredi 8 (3 jours ouvrables)
3. Fin période gratuite: Mercredi 8 janvier
4. Jours facturables: Jeudi 9 → Lundi 13 = 5 jours
5. **Montant**: 5 × 25 000 = **125 000 CFA**

### Exemple 2: Arrivée le weekend
- **Arrivée**: Samedi 4 janvier 2025
- **Déchargement**: Vendredi 10 janvier 2025

**Calcul**:
1. Période gratuite commence: Lundi 6 janvier (décalage depuis samedi)
2. Jours gratuits: Lundi 6, Mardi 7, Mercredi 8 (3 jours ouvrables)
3. Fin période gratuite: Mercredi 8 janvier
4. Jours facturables: Jeudi 9 → Vendredi 10 = 2 jours
5. **Montant**: 2 × 25 000 = **50 000 CFA**

### Exemple 3: Déchargement pendant période gratuite
- **Arrivée**: Vendredi 3 janvier 2025
- **Déchargement**: Mardi 7 janvier 2025

**Calcul**:
1. Période gratuite commence: Vendredi 3 janvier
2. Jours gratuits: Vendredi 3, Lundi 6, Mardi 7 (3 jours ouvrables, skip weekend)
3. Fin période gratuite: Mardi 7 janvier
4. Déchargement = Fin période gratuite
5. **Montant**: **0 CFA** (aucun frais)

### Exemple 4: Longue période avec weekends facturés
- **Arrivée**: Mercredi 1er janvier 2025
- **Déchargement**: Lundi 13 janvier 2025

**Calcul**:
1. Période gratuite commence: Mercredi 1er janvier
2. Jours gratuits: Mercredi 1, Jeudi 2, Vendredi 3 (3 jours ouvrables)
3. Fin période gratuite: Vendredi 3 janvier
4. Jours facturables: Samedi 4 → Lundi 13 = 10 jours (inclut 2 weekends!)
5. **Montant**: 10 × 25 000 = **250 000 CFA**

## Implémentation Technique

### Modèle Django (Mission)

#### Nouveaux champs
```python
date_arrivee = models.DateField(blank=True, null=True)
date_dechargement = models.DateField(blank=True, null=True)
statut_stationnement = models.CharField(max_length=20, choices=[...], default='attente')
jours_stationnement_facturables = models.IntegerField(default=0)
montant_stationnement = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
```

#### Méthode principale: `calculer_frais_stationnement()`

**Algorithme en 3 étapes**:

1. **Trouver le début de la période gratuite**
   - Si `date_arrivee` est un samedi ou dimanche, décaler au lundi suivant
   - Sinon, utiliser `date_arrivee` directement

2. **Compter 3 jours ouvrables (période gratuite)**
   - À partir de la date de début gratuit
   - Compter uniquement lundi à vendredi
   - Ignorer samedi et dimanche
   - S'arrêter au 3ème jour ouvrable → `date_fin_gratuit`

3. **Calculer les jours facturables**
   - Si `date_dechargement <= date_fin_gratuit`: 0 jours facturables
   - Sinon: compter TOUS les jours calendaires (y compris weekends) entre `date_fin_gratuit` et `date_dechargement`
   - Montant = `jours_facturables × 25 000 CFA`

### Workflow Utilisateur

1. **Bloquer pour stationnement** (`bloquer_stationnement`)
   - Enregistrer la `date_arrivee`
   - Calculer les frais en cours
   - Changer le statut à `en_stationnement` si applicable

2. **Marquer le déchargement** (`marquer_dechargement`)
   - Enregistrer la `date_dechargement`
   - Calculer les frais finaux
   - Changer le statut à `decharge`

3. **Recalculer** (`calculer_stationnement`)
   - Permet de recalculer les frais à tout moment
   - Utile pour voir l'évolution en temps réel

## URLs

```python
path('missions/<str:pk>/bloquer-stationnement/', views.bloquer_stationnement, name='bloquer_stationnement')
path('missions/<str:pk>/marquer-dechargement/', views.marquer_dechargement, name='marquer_dechargement')
path('missions/<str:pk>/calculer-stationnement/', views.calculer_stationnement, name='calculer_stationnement')
```

## Tests

Un script de test complet est disponible: `test_stationnement_logic.py`

```bash
python test_stationnement_logic.py
```

Ce script teste les 4 scénarios principaux décrits ci-dessus.

## Notes Importantes

### Différence avec les anciennes règles

**❌ ANCIEN** (incorrect):
- Tous les weekends étaient exclus du calcul, même après le 4ème jour

**✅ NOUVEAU** (correct):
- Les weekends sont exclus uniquement pour les 3 jours gratuits
- Après le 4ème jour, les weekends sont facturés comme tous les autres jours

### Jours fériés
- **Aucun jour férié n'est exclu** du calcul
- Tous les jours calendaires comptent après la période gratuite

### Statuts de stationnement
- `attente`: Mission en attente, pas encore de frais
- `en_stationnement`: Frais applicables (au-delà des 3 jours gratuits)
- `decharge`: Mission déchargée, frais finaux calculés

## Historique des Modifications

**Version 2 (29/12/2024)**:
- Correction de la logique: les weekends comptent après le 4ème jour
- Mise à jour des templates avec les règles correctes
- Ajout de tests complets

**Version 1 (Initiale)**:
- Première implémentation (logique incorrecte)
- Exclusion de tous les weekends

---

**Document créé le**: 29 décembre 2024
**Dernière mise à jour**: 29 décembre 2024
**Auteur**: Claude Code
