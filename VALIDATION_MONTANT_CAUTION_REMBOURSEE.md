# Validation du montant remboursé pour les cautions

## 📋 Vue d'ensemble

Les cautions doivent maintenant avoir un **montant remboursé rempli** (> 0) si elles sont marquées comme "remboursées". Cette validation garantit la cohérence des données financières.

## 🎯 Objectif

Éviter les erreurs de saisie où une caution serait marquée comme remboursée mais sans montant remboursé renseigné, ce qui rendrait la comptabilité incohérente.

## ⚙️ Validations implémentées

### 1. Validation dans le modèle Cautions (models.py:659-694)

```python
def clean(self):
    errors = {}

    # Vérification 1: est_rembourser et non_rembourser mutuellement exclusifs
    if self.est_rembourser and self.non_rembourser:
        errors = 'Une caution ne peut pas être à la fois remboursée et non remboursable'

    # Vérification 2: Si remboursée, montant_rembourser doit être > 0
    if self.est_rembourser:
        if not self.montant_rembourser or self.montant_rembourser <= 0:
            errors = 'Le montant remboursé doit être > 0'

    # Vérification 3: montant_rembourser <= montant caution
    if self.montant_rembourser > self.montant:
        errors = 'Le montant remboursé ne peut pas dépasser le montant de la caution'

    # Vérification 4: Si montant_rembourser > 0, est_rembourser doit être True
    if not self.est_rembourser and self.montant_rembourser > 0:
        errors = 'Cochez "est_rembourser" si un montant est remboursé'
```

### 2. Validation dans le formulaire (form.py:353-416)

Le formulaire `CautionsForm` appelle automatiquement la validation du modèle via sa méthode `clean()`, convertissant les erreurs en messages d'erreur de formulaire.

### 3. Interface utilisateur améliorée (caution_form.html)

#### Alertes dynamiques

L'interface affiche des alertes qui changent selon l'état de la caution :

| État | Couleur | Message |
|------|---------|---------|
| Remboursée | 🟢 Vert | ✅ Caution remboursée : Vérifiez que le montant est correct |
| Non remboursable | 🟡 Orange | ⚠️ Caution non remboursable (pénalité, retenue, etc.) |
| En attente | 🔵 Bleu | ℹ️ Cochez "Est remboursée" et saisissez le montant |

#### Comportement automatique

**Quand on coche "Est remboursée" :**
- ✅ Décoche automatiquement "Non remboursable"
- ✅ Active le champ "Montant remboursé"
- ✅ Copie automatiquement le montant de la caution dans le montant remboursé
- ✅ Met en surbrillance le champ (fond bleu, bordure épaisse)
- ✅ Change l'alerte en vert avec message de confirmation

**Quand on coche "Non remboursable" :**
- ✅ Décoche automatiquement "Est remboursée"
- ✅ Met le montant remboursé à 0
- ✅ Désactive le champ "Montant remboursé" (grisé)
- ✅ Change l'alerte en orange avec avertissement

**Quand on décoche tout :**
- ✅ Réinitialise le montant remboursé à 0
- ✅ Enlève la surbrillance
- ✅ Affiche l'alerte d'aide par défaut (bleue)

## 📊 Scénarios de validation

### Scénario 1 : Remboursement complet ✅
```
Montant caution: 50000 FCFA
est_rembourser: ✅ True
montant_rembourser: 50000 FCFA
Résultat: ✅ VALIDATION OK
```

### Scénario 2 : Remboursement partiel ✅
```
Montant caution: 50000 FCFA
est_rembourser: ✅ True
montant_rembourser: 40000 FCFA (10000 FCFA de pénalité)
Résultat: ✅ VALIDATION OK
```

### Scénario 3 : Caution non remboursable ✅
```
Montant caution: 50000 FCFA
non_rembourser: ✅ True
montant_rembourser: 0 FCFA
Résultat: ✅ VALIDATION OK
```

### Scénario 4 : Erreur - Remboursée sans montant ❌
```
Montant caution: 50000 FCFA
est_rembourser: ✅ True
montant_rembourser: 0 FCFA
Résultat: ❌ VALIDATION ÉCHOUÉE
Erreur: "Le montant remboursé doit être supérieur à 0"
```

### Scénario 5 : Erreur - Les deux cases cochées ❌
```
est_rembourser: ✅ True
non_rembourser: ✅ True
Résultat: ❌ VALIDATION ÉCHOUÉE
Erreur: "Une caution ne peut pas être à la fois remboursée et non remboursable"
```

### Scénario 6 : Erreur - Montant remboursé > caution ❌
```
Montant caution: 50000 FCFA
est_rembourser: ✅ True
montant_rembourser: 60000 FCFA
Résultat: ❌ VALIDATION ÉCHOUÉE
Erreur: "Le montant remboursé (60000 FCFA) ne peut pas dépasser le montant de la caution (50000 FCFA)"
```

### Scénario 7 : Erreur - Montant sans case cochée ❌
```
est_rembourser: ❌ False
montant_rembourser: 30000 FCFA
Résultat: ❌ VALIDATION ÉCHOUÉE
Erreur: "Le montant remboursé est de 30000 FCFA mais la caution n'est pas marquée comme remboursée"
```

## 🎨 Workflow utilisateur

```
1. Utilisateur ouvre le formulaire de caution
         ↓
2. Saisit le montant de la caution (ex: 50000 FCFA)
         ↓
3. Coche "Est remboursée"
         ↓
4. JavaScript copie automatiquement 50000 dans "Montant remboursé"
         ↓
5. Champ surligné en bleu, alerte verte affichée
         ↓
6. Utilisateur peut ajuster le montant si remboursement partiel
         ↓
7. Soumet le formulaire
         ↓
8. Validation JavaScript (montant > 0)
         ↓
9. Validation Django (toutes les règles)
         ↓
10. ✅ Caution sauvegardée avec cohérence garantie
```

## 💡 Messages d'erreur

### Erreur 1 : Montant remboursé manquant
```
❌ Le montant remboursé doit être supérieur à 0 si la caution est marquée comme remboursée.
   Veuillez saisir le montant remboursé (montant de la caution : 50000 FCFA)
```

### Erreur 2 : Les deux cases cochées
```
❌ Une caution ne peut pas être à la fois remboursée et non remboursable
```

### Erreur 3 : Montant trop élevé
```
❌ Le montant remboursé (60000 FCFA) ne peut pas dépasser le montant de la caution (50000 FCFA)
```

### Erreur 4 : Incohérence montant/statut
```
❌ Le montant remboursé est de 30000 FCFA mais la caution n'est pas marquée comme remboursée.
   Cochez "est_rembourser" ou mettez le montant à 0.
```

## ✅ Avantages

1. **Cohérence financière** : Impossible de marquer une caution comme remboursée sans montant
2. **Automatisation** : Copie automatique du montant de la caution
3. **Prévention des erreurs** : Validation à plusieurs niveaux (JavaScript + Django)
4. **Expérience utilisateur** : Interface intuitive avec aide visuelle
5. **Flexibilité** : Permet les remboursements partiels
6. **Sécurité** : Double validation (client + serveur)
7. **Feedback immédiat** : Alertes en temps réel selon l'état

## 🔧 Fichiers modifiés

| Fichier | Modifications |
|---------|---------------|
| `models.py` (Cautions) | 4 validations dans clean() |
| `form.py` (CautionsForm) | Validation globale avec clean() |
| `caution_form.html` | JavaScript interactif + alertes dynamiques |

## 🔗 Intégration avec PaiementMission

Cette validation s'intègre parfaitement avec la validation de paiement :

```
Créer contrat
    ↓
Mission terminée
    ↓
Rembourser caution (AVEC montant > 0) ✅
    ↓
Valider paiement ✅
```

Sans montant remboursé :
```
Mission terminée ✅
Caution marquée "remboursée" mais montant = 0 ❌
→ Validation bloquée au niveau du formulaire caution
→ Impossible d'arriver à la validation du paiement
```

## 📝 Notes importantes

1. Le champ `montant_rembourser` est **obligatoire** si `est_rembourser = True`
2. Le JavaScript copie automatiquement le montant de la caution, mais l'utilisateur peut l'ajuster
3. Si `non_rembourser = True`, le montant remboursé est automatiquement mis à 0 et désactivé
4. Les deux checkboxes sont mutuellement exclusives (JavaScript + validation serveur)
5. La validation JavaScript alerte avant soumission si le montant est invalide
6. La validation Django est la garantie finale de cohérence

## 🚀 Améliorations futures possibles

- [ ] Historique des remboursements avec dates
- [ ] Calcul automatique des pénalités déduites du remboursement
- [ ] Notification par email au client lors du remboursement
- [ ] Rapport de réconciliation des cautions
- [ ] Export comptable des remboursements de cautions
