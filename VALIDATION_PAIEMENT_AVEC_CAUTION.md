# Validation de paiement avec vérification de la caution

## 📋 Vue d'ensemble

La validation d'un paiement de mission nécessite maintenant **deux conditions obligatoires** :
1. ✅ La mission doit être **terminée**
2. ✅ La caution doit être **remboursée** OU marquée comme **"non à rembourser"**

## 🎯 Objectif

Garantir que les cautions sont correctement gérées avant de valider un paiement, évitant ainsi les oublis de remboursement et assurant une gestion financière rigoureuse.

## ⚙️ Fonctionnement

### 1. Modèle Cautions

Le modèle `Cautions` possède trois états possibles :

| Champ | Type | Description |
|-------|------|-------------|
| `est_rembourser` | Boolean | True si la caution a été remboursée au client |
| `non_rembourser` | Boolean | True si la caution ne doit pas être remboursée (pénalité, retenue, etc.) |
| `montant_rembourser` | Decimal | Montant effectivement remboursé |

**États valides pour validation du paiement :**
- ✅ `est_rembourser = True` (caution remboursée)
- ✅ `non_rembourser = True` (caution non à rembourser)
- ❌ Les deux à False (caution en attente)

### 2. Validation dans le modèle PaiementMission

#### Dans la méthode `clean()` (models.py:880-902)

```python
if self.est_valide:
    # Vérifier que la mission est terminée
    if self.mission.statut != 'terminée':
        raise ValidationError(...)

    # Vérifier l'état de la caution
    if self.caution:
        if not self.caution.est_rembourser and not self.caution.non_rembourser:
            raise ValidationError(
                f"La caution de {self.caution.montant} FCFA n'a pas encore été remboursée."
            )
```

#### Dans la méthode `valider_paiement()` (models.py:918-948)

```python
def valider_paiement(self):
    # Vérifier mission terminée
    if self.mission.statut != 'terminée':
        raise ValidationError(...)

    # Vérifier état de la caution
    if self.caution:
        if not self.caution.est_rembourser and not self.caution.non_rembourser:
            raise ValidationError(...)

    # Validation OK
    self.est_valide = True
    self.date_validation = timezone.now()

    # Si caution remboursée, marquer caution_est_retiree = True
    if self.caution and self.caution.est_rembourser:
        self.caution_est_retiree = True

    self.save()
```

### 3. Vue valider_paiement_mission (views.py:764-815)

La vue vérifie l'état de la caution et passe les informations au template :

```python
# Vérifier l'état de la caution
caution = paiement.caution
caution_ok = False
caution_message = ""

if caution:
    if caution.est_rembourser:
        caution_ok = True
        caution_message = f"✅ Caution remboursée ({caution.montant_rembourser} FCFA)"
    elif caution.non_rembourser:
        caution_ok = True
        caution_message = "✅ Caution marquée comme 'non à rembourser'"
    else:
        caution_ok = False
        caution_message = f"❌ Caution non remboursée ({caution.montant} FCFA)"
```

**Validation lors de la soumission :**
```python
if not caution_ok:
    messages.error(request,
        f"❌ Impossible de valider! La caution de {caution.montant} FCFA "
        f"n'a pas été remboursée."
    )
    return redirect('paiement_mission_list')
```

### 4. Interface utilisateur (Template)

#### Alertes visuelles

**Caution non remboursée :**
```html
<div class="alert alert-warning">
    ⚠️ Caution non remboursée!
    ❌ Caution non remboursée (50000 FCFA en attente)
    Vous devez rembourser la caution avant de valider le paiement.
    [Bouton: Gérer la caution]
</div>
```

**Caution OK :**
```html
<div class="alert alert-success">
    ✅ Caution OK!
    ✅ Caution remboursée (50000 FCFA sur 50000 FCFA)
</div>
```

#### Section Caution

| Caution remboursée | Caution non remboursée | Caution "non à rembourser" |
|-------------------|------------------------|----------------------------|
| 🟢 Bordure verte | 🟡 Bordure orange | 🔵 Bordure bleue |
| Badge: ✅ Remboursée | Badge: ⏳ En attente | Badge: ℹ️ Non à rembourser |
| Montant remboursé affiché | Alerte "doit être remboursée" | Aucune alerte |

#### Bouton de validation

Le bouton "Valider le paiement" n'apparaît que si :
- ✅ Mission terminée
- ✅ Caution OK

Sinon, boutons alternatifs :
- "Terminer la mission d'abord" (si mission non terminée)
- "Gérer la caution d'abord" (si caution non remboursée)

## 📊 Workflow de validation

```
1. Utilisateur clique sur "Valider paiement"
         ↓
2. Système vérifie le statut de la mission
         ↓ (si terminée)
3. Système vérifie l'état de la caution
         ↓
4a. Caution remboursée → Validation possible
4b. Caution "non à rembourser" → Validation possible
4c. Caution en attente → BLOCAGE
         ↓ (si 4a ou 4b)
5. Validation du paiement
         ↓
6. Si caution remboursée: caution_est_retiree = True
         ↓
7. est_valide = True
         ↓
8. date_validation enregistrée
         ↓
9. ✅ Paiement validé!
```

## 🎨 Messages utilisateur

### Messages de succès
```
✅ Paiement validé avec succès! Montant: 1000000 FCFA
```

### Messages d'erreur

**Mission non terminée :**
```
❌ Impossible de valider! La mission est 'en cours'.
Terminez d'abord la mission.
```

**Caution non remboursée :**
```
❌ Impossible de valider! La caution de 50000 FCFA n'a pas été remboursée.
Veuillez rembourser la caution avant de valider le paiement.
```

## ✅ Scénarios de validation

### Scénario 1 : Validation normale
```
Mission: ✅ Terminée
Caution: ✅ Remboursée (50000 FCFA)
Résultat: ✅ VALIDATION AUTORISÉE
```

### Scénario 2 : Caution non à rembourser
```
Mission: ✅ Terminée
Caution: ✅ Marquée "non à rembourser" (pénalité)
Résultat: ✅ VALIDATION AUTORISÉE
```

### Scénario 3 : Caution en attente
```
Mission: ✅ Terminée
Caution: ❌ En attente (0 FCFA remboursés sur 50000 FCFA)
Résultat: ❌ VALIDATION BLOQUÉE
Action: Rembourser la caution d'abord
```

### Scénario 4 : Mission non terminée
```
Mission: ❌ En cours
Caution: ✅ Remboursée
Résultat: ❌ VALIDATION BLOQUÉE
Action: Terminer la mission d'abord
```

### Scénario 5 : Les deux conditions non remplies
```
Mission: ❌ En cours
Caution: ❌ En attente
Résultat: ❌ VALIDATION BLOQUÉE
Action: Terminer la mission ET rembourser la caution
```

## 🔧 Fichiers modifiés

| Fichier | Modifications |
|---------|---------------|
| `models.py` | Validation de la caution dans `PaiementMission.clean()` et `valider_paiement()` |
| `views.py` | Vérification de l'état de la caution dans `valider_paiement_mission()` |
| `valider_paiement.html` | Alertes visuelles, section caution améliorée, bouton conditionnel |

## 💡 Avantages

1. **Sécurité financière** : Impossible d'oublier de rembourser une caution
2. **Traçabilité** : État de la caution clairement affiché
3. **Flexibilité** : Option "non à rembourser" pour les cas spéciaux (pénalités)
4. **Expérience utilisateur** : Interface intuitive avec alertes visuelles
5. **Validation stricte** : Double vérification (modèle + vue)
6. **Automatisation** : `caution_est_retiree` coché automatiquement si caution remboursée

## 📝 Notes importantes

1. Le champ `caution_est_retiree` dans `PaiementMission` est automatiquement mis à `True` lors de la validation si la caution est remboursée.

2. Les deux états `est_rembourser` et `non_rembourser` sont mutuellement exclusifs dans la logique métier (même si techniquement les deux peuvent être à False).

3. L'utilisateur doit gérer la caution via la page "Gérer la caution" avant de pouvoir valider le paiement.

4. La validation bloquante empêche toute tentative de contournement via l'API ou la console.

## 🚀 Prochaines étapes possibles

- [ ] Ajouter une notification automatique quand une caution doit être remboursée
- [ ] Dashboard des cautions en attente de remboursement
- [ ] Historique des remboursements de caution
- [ ] Rapport mensuel des cautions
- [ ] Calcul automatique des pénalités de retard appliquées aux cautions
