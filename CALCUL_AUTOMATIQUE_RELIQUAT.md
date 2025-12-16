# Calcul automatique du reliquat de transport

## 📋 Vue d'ensemble

Le reliquat de transport est désormais **calculé automatiquement** en temps réel lors de la saisie du formulaire de contrat.

**Formule :**
```
Reliquat = Montant Total - Avance Transport
```

## ⚙️ Fonctionnement

### 1. Calcul côté serveur (Backend)

Dans le modèle `ContratTransport` (models.py:566):

```python
self.reliquat_transport = Decimal(self.montant_total) - Decimal(self.avance_transport)
```

**Quand est-ce calculé?**
- À chaque sauvegarde du contrat
- Garantit la cohérence des données

### 2. Calcul côté client (Frontend)

Dans le formulaire de contrat (contrat_form.html):

```javascript
function calculerReliquat() {
    const montantTotal = parseFloat(montantTotalInput.value) || 0;
    const avanceTransport = parseFloat(avanceTransportInput.value) || 0;
    const reliquat = montantTotal - avanceTransport;
    reliquatTransportInput.value = reliquat.toFixed(2);
}
```

**Quand est-ce calculé?**
- Au chargement de la page (si les valeurs existent)
- À chaque modification du montant total (événements `onchange` et `oninput`)
- À chaque modification de l'avance transport (événements `onchange` et `oninput`)

### 3. Interface utilisateur

Le champ `reliquat_transport` dans le formulaire :
- ✅ Est en **lecture seule** (readonly)
- ✅ A un **fond grisé** pour indiquer qu'il est automatique
- ✅ Se met à jour **instantanément** quand on change le montant total ou l'avance
- ✅ Change de **couleur selon le résultat** (voir ci-dessous)

## 🎨 Indications visuelles

Le champ reliquat change de couleur selon la situation :

### 🔴 Reliquat négatif (avance > montant total)
- **Fond rouge clair** : `#f8d7da`
- **Texte rouge foncé** : `#721c24`
- **Message** : "⚠️ Attention : L'avance dépasse le montant total"
- **Validation** : Erreur bloquante lors de la soumission

### 🟢 Reliquat à zéro (avance = montant total)
- **Fond vert clair** : `#d4edda`
- **Texte vert foncé** : `#155724`
- **Message** : "✅ Paiement intégral en avance"
- **Validation** : OK

### 🔵 Reliquat positif (situation normale)
- **Fond bleu clair** : `#d1ecf1`
- **Texte bleu foncé** : `#0c5460`
- **Message** : "Calculé automatiquement : Montant total - Avance"
- **Validation** : OK

## 📊 Exemples

| Montant Total | Avance Transport | Reliquat | Couleur | Statut |
|---------------|------------------|----------|---------|--------|
| 1 000 000 FCFA | 300 000 FCFA | 700 000 FCFA | 🔵 Bleu | OK |
| 500 000 FCFA | 500 000 FCFA | 0 FCFA | 🟢 Vert | OK |
| 800 000 FCFA | 900 000 FCFA | -100 000 FCFA | 🔴 Rouge | ❌ Erreur |

## ✅ Validation

### Côté serveur (models.py:539-541)

```python
if self.avance_transport > self.montant_total:
    errors['avance_transport'] = 'L\'avance ne peut pas dépasser le montant total'
```

**Résultat :**
- Empêche la sauvegarde du contrat
- Affiche un message d'erreur clair à l'utilisateur

### Côté client (JavaScript)

Le calcul en temps réel permet de voir immédiatement :
- Si l'avance dépasse le montant total (rouge)
- Le montant exact du reliquat à payer
- La validation visuelle avant même de soumettre le formulaire

## 🔧 Configuration technique

### Champs du formulaire (form.py)

**Montant Total :**
```python
'montant_total': forms.NumberInput(attrs={
    'id': 'id_montant_total',
    'step': '0.01',
    'min': '0',
    'onchange': 'calculerReliquat()',
    'oninput': 'calculerReliquat()'
})
```

**Avance Transport :**
```python
'avance_transport': forms.NumberInput(attrs={
    'id': 'id_avance_transport',
    'step': '0.01',
    'min': '0',
    'onchange': 'calculerReliquat()',
    'oninput': 'calculerReliquat()'
})
```

**Reliquat Transport :**
```python
'reliquat_transport': forms.NumberInput(attrs={
    'id': 'id_reliquat_transport',
    'readonly': True,
    'style': 'background-color: #e9ecef;'
})
```

## 🚀 Workflow utilisateur

```
1. Utilisateur saisit le montant total
         ↓
2. JavaScript calcule et affiche le reliquat immédiatement
         ↓
3. Utilisateur saisit l'avance transport
         ↓
4. JavaScript recalcule le reliquat en temps réel
         ↓
5. Indication visuelle selon le résultat (bleu/vert/rouge)
         ↓
6. Utilisateur soumet le formulaire
         ↓
7. Django recalcule côté serveur (garantie de cohérence)
         ↓
8. Validation : erreur si avance > montant total
         ↓
9. Contrat sauvegardé avec reliquat correct
```

## 💡 Avantages

1. **Feedback immédiat** : L'utilisateur voit le reliquat en temps réel
2. **Prévention des erreurs** : Indication visuelle si avance > montant total
3. **Cohérence** : Double calcul (client + serveur) garantit la précision
4. **Expérience utilisateur** : Interface intuitive avec couleurs indicatives
5. **Validation stricte** : Impossible de sauvegarder si avance > montant total
6. **Précision** : Calcul avec 2 décimales

## 📝 Notes importantes

1. Le calcul JavaScript utilise `parseFloat()` et affiche avec `.toFixed(2)` pour une précision de 2 décimales.

2. Le calcul côté serveur utilise `Decimal` pour une précision maximale en finances.

3. Le champ est **toujours en lecture seule** pour éviter toute modification manuelle.

4. Les événements `onchange` ET `oninput` sont utilisés pour une réactivité maximale.

5. Le calcul se fait même si les valeurs sont à 0 ou vides (convertit en 0 par défaut).

## 🔗 Intégration avec les autres calculs automatiques

Le formulaire de contrat calcule automatiquement :
- ✅ **Reliquat** = Montant Total - Avance
- ✅ **Date limite retour** = Date début + 23 jours

Ces deux calculs fonctionnent indépendamment et simultanément.
