# Calcul automatique de la date limite de retour

## 📋 Vue d'ensemble

La date limite de retour des contrats de transport est désormais **calculée automatiquement** en ajoutant **23 jours** à la date de début du contrat.

## 🎯 Objectif

Conformément aux clauses du contrat de transport, le transporteur dispose de **23 jours** pour ramener les conteneurs vides à Dakar. Cette règle est maintenant automatisée pour :
- Éviter les erreurs de calcul manuel
- Garantir la cohérence des dates
- Faciliter la gestion des contrats

## ⚙️ Fonctionnement

### 1. Calcul côté serveur (Backend)

Dans le modèle `ContratTransport` (models.py:560-563):

```python
# Calcul automatique de la date limite de retour : date_debut + 23 jours
if self.date_debut:
    from datetime import timedelta
    self.date_limite_retour = self.date_debut + timedelta(days=23)
```

**Quand est-ce calculé?**
- À chaque sauvegarde du contrat (création ou modification)
- Dès que `date_debut` est définie

### 2. Calcul côté client (Frontend)

Dans le formulaire de contrat (contrat_form.html):

```javascript
function calculerDateLimiteRetour() {
    const dateDebut = new Date(dateDebutInput.value);
    dateDebut.setDate(dateDebut.getDate() + 23);
    dateLimiteRetourInput.value = formatDate(dateDebut);
}
```

**Quand est-ce calculé?**
- Au chargement de la page (si date_debut existe)
- À chaque modification de la date de début (événement `onchange`)

### 3. Interface utilisateur

Le champ `date_limite_retour` dans le formulaire :
- ✅ Est en **lecture seule** (readonly)
- ✅ A un **fond grisé** pour indiquer qu'il est automatique
- ✅ Se met à jour **instantanément** quand on change la date de début
- ✅ Affiche une **info-bulle** : "Calculée automatiquement : Date début + 23 jours"

## 📊 Exemples

| Date de début | Date limite de retour | Jours |
|---------------|----------------------|-------|
| 2025-01-01    | 2025-01-24          | 23    |
| 2025-12-25    | 2026-01-17          | 23    |
| 2025-02-05    | 2025-02-28          | 23    |

## 🔄 Migration des données existantes

### Commande de mise à jour

Pour recalculer les dates limites de retour des contrats existants :

```bash
# Voir les modifications qui seraient appliquées (sans modifier)
python manage.py update_contrat_dates --dry-run

# Appliquer réellement les modifications
python manage.py update_contrat_dates
```

### Résultat de la migration

```
✅ RÉSUMÉ:
  • 6 contrat(s) mis à jour
  • 0 contrat(s) déjà correct(s)
  • 0 erreur(s)
```

## ⚠️ Validation et pénalités

### Validation dans le modèle

La date limite de retour est validée pour s'assurer qu'elle est **après** la date de début :

```python
if self.date_limite_retour < self.date_debut:
    errors['date_limite_retour'] = 'La date limite de retour doit être après la date de début'
```

### Pénalités de retard

Dans le modèle `Mission`, la méthode `terminer_mission()` calcule automatiquement les pénalités :

```python
if date_retour > self.contrat.date_limite_retour:
    jours_retard = (date_retour - self.contrat.date_limite_retour).days
    penalite = jours_retard * 25000  # 25 000 FCFA par jour
    raise ValidationError(f"Pénalité estimée: {penalite} FCFA")
```

**Exemple :**
- Date limite : 2025-01-24
- Date retour : 2025-01-29
- Retard : 5 jours
- **Pénalité : 125 000 FCFA**

## 🎨 Apparence visuelle

Dans le formulaire, le champ date limite de retour :
- Fond grisé (`background-color: #e9ecef`)
- Fond bleu clair après calcul (`background-color: #d1ecf1`)
- Curseur non modifiable (`readonly`)

## 🔧 Code technique

### Fichiers modifiés

1. **models.py (ligne 560-563)** : Calcul automatique dans `save()`
2. **form.py (ligne 246-258)** : Champ en readonly avec event handler
3. **contrat_form.html (ligne 38-71)** : JavaScript pour calcul temps réel
4. **update_contrat_dates.py** : Commande de migration

### Workflow complet

```
Utilisateur saisit date_debut
         ↓
JavaScript calcule date_limite_retour (affichage immédiat)
         ↓
Utilisateur soumet le formulaire
         ↓
Django save() recalcule date_limite_retour (garantie côté serveur)
         ↓
Contrat sauvegardé avec date_limite_retour = date_debut + 23 jours
         ↓
Mission créée avec validation des dates
         ↓
Terminer mission : calcul automatique des pénalités si retard
```

## ✅ Avantages

1. **Cohérence** : Toutes les dates limites respectent la règle des 23 jours
2. **Automatisation** : Plus d'erreur de calcul manuel
3. **Transparence** : L'utilisateur voit le calcul en temps réel
4. **Conformité** : Respect des clauses contractuelles
5. **Gestion des pénalités** : Calcul automatique en cas de retard
6. **Expérience utilisateur** : Interface intuitive et réactive

## 📝 Notes importantes

1. Le calcul est **toujours effectué côté serveur** lors de la sauvegarde, garantissant la cohérence des données même si JavaScript est désactivé.

2. Le champ est en **lecture seule** dans le formulaire, mais peut être modifié programmatiquement si nécessaire (par exemple, pour des cas exceptionnels).

3. Les **contrats existants** ont été mis à jour automatiquement avec la commande `update_contrat_dates`.

4. La règle des **23 jours** est conforme aux clauses du contrat de transport mentionnées dans le PDF généré.

## 🚀 Prochaines étapes possibles

- [ ] Ajouter un paramètre configurable pour le nombre de jours (actuellement fixé à 23)
- [ ] Créer un rapport des missions en retard
- [ ] Notification automatique 3 jours avant la date limite
- [ ] Dashboard avec statistiques de respect des délais
