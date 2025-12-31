# Guide Utilisateur - Gestion du Stationnement

## 📖 Manuel pour Managers

**Version:** 1.0
**Date:** 29 décembre 2024
**Public:** Managers et Administrateurs

---

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Qu'est-ce que le Stationnement (Demurrage)?](#quest-ce-que-le-stationnement)
3. [Règles de Facturation](#règles-de-facturation)
4. [Guide Étape par Étape](#guide-étape-par-étape)
5. [Comprendre l'Aperçu en Temps Réel](#comprendre-laperçu-en-temps-réel)
6. [Utiliser le Modal de Confirmation](#utiliser-le-modal-de-confirmation)
7. [Exemples Concrets](#exemples-concrets)
8. [Questions Fréquentes](#questions-fréquentes)
9. [Résolution de Problèmes](#résolution-de-problèmes)
10. [Conseils et Bonnes Pratiques](#conseils-et-bonnes-pratiques)

---

## Introduction

### Pourquoi ce Guide?

Ce guide vous explique comment utiliser le nouveau système de gestion du stationnement dans l'application de transport. Vous apprendrez à:

- ✅ Bloquer une mission quand un camion arrive
- ✅ Marquer le déchargement et calculer les frais
- ✅ Comprendre l'aperçu en temps réel
- ✅ Utiliser le modal de confirmation
- ✅ Éviter les erreurs courantes

### À Qui s'Adresse ce Guide?

Ce guide est destiné aux **managers** et **administrateurs** qui gèrent les missions de transport et doivent:

- Enregistrer l'arrivée des camions
- Marquer le déchargement
- Calculer et facturer les frais de stationnement

### Accès Requis

⚠️ **Important:** Seuls les utilisateurs avec le rôle **Manager** ou **Administrateur** peuvent accéder aux fonctionnalités de stationnement.

Si vous ne pouvez pas accéder à ces fonctions, contactez votre administrateur système.

---

## Qu'est-ce que le Stationnement?

### Définition

Le **stationnement** (aussi appelé **demurrage**) correspond au temps pendant lequel un camion reste sur le site en attendant d'être déchargé.

### Pourquoi Facturer le Stationnement?

Lorsqu'un camion reste trop longtemps sur le site, cela génère des frais. L'entreprise facture donc ces frais au client après une période gratuite de 3 jours ouvrables.

### Processus en 2 Étapes

```
1. BLOQUER POUR STATIONNEMENT
   ↓
   Le camion arrive → Enregistrer la date d'arrivée

2. MARQUER LE DÉCHARGEMENT
   ↓
   Le camion est déchargé → Calculer les frais
```

---

## Règles de Facturation

### 📅 Période Gratuite: 3 Jours Ouvrables

**Jours ouvrables** = Lundi à Vendredi (pas les weekends)

Les **3 premiers jours ouvrables** sont **GRATUITS**.

### 💰 Tarif: 25 000 CFA/Jour

À partir du **4ème jour ouvrable**, chaque jour est facturé **25 000 CFA**, **y compris les weekends**.

### 🔑 Règles Importantes

#### Règle 1: Les 3 Jours Gratuits

| Arrivée | Période Gratuite Commence | Fin Période Gratuite |
|---------|---------------------------|----------------------|
| Lundi | Lundi | Mercredi |
| Mardi | Mardi | Jeudi |
| Mercredi | Mercredi | Vendredi |
| Jeudi | Jeudi | Lundi suivant |
| Vendredi | Vendredi | Mardi suivant |
| **Samedi** | **Lundi suivant** | Mercredi suivant |
| **Dimanche** | **Lundi suivant** | Mercredi suivant |

⚠️ **Si le camion arrive un weekend, la période gratuite commence le lundi suivant.**

#### Règle 2: Tous les Jours Comptent Après la Période Gratuite

Après la période gratuite, **TOUS les jours** sont facturés, y compris:
- ✅ Samedi
- ✅ Dimanche
- ✅ Jours fériés

**Exemple:**
```
Arrivée: Lundi 1er
Période gratuite: Lundi 1, Mardi 2, Mercredi 3
Déchargement: Lundi 8

Jours facturables:
Jeudi 4, Vendredi 5, Samedi 6, Dimanche 7, Lundi 8 = 5 JOURS
Frais: 5 × 25 000 = 125 000 CFA
```

---

## Guide Étape par Étape

### Étape 1: Bloquer une Mission pour Stationnement

#### Quand?
Dès que le camion **arrive** sur le site.

#### Comment?

**1. Aller sur la Liste des Missions**
- Menu: **Missions** → **Liste des missions**

**2. Trouver la Mission**
- Cherchez la mission concernée
- Vérifiez que le statut est **"En cours"**

**3. Cliquer sur "Bloquer pour Stationnement"**
- Dans la colonne **Actions**, cliquez sur l'icône de parking 🅿️
- Ou cliquez sur le bouton **"Bloquer pour stationnement"**

**4. Remplir le Formulaire**

📋 **Informations affichées:**
- Détails de la mission (origine, destination, chauffeur, camion)
- Date de départ de la mission
- Instructions de facturation

📝 **Informations à saisir:**
- **Date d'arrivée du camion** (obligatoire)
  - ⚠️ Ne peut pas être dans le futur
  - ⚠️ Ne peut pas être avant la date de départ de la mission

💡 **Aperçu en Temps Réel:**
- Une carte s'affiche automatiquement
- Montre la période gratuite calculée
- Affiche quand la facturation commence

**5. Valider**
- Cliquez sur **"Bloquer pour Stationnement"**
- Message de confirmation s'affiche

✅ **Résultat:**
- La mission est marquée comme "En stationnement"
- La date d'arrivée est enregistrée
- Le système commence à compter les jours

#### ⚠️ Cas Particuliers

**Si la mission est déjà bloquée:**
- Message d'avertissement s'affiche
- Impossible de bloquer à nouveau
- Si erreur de date, contactez un administrateur

**Si la mission n'est pas "en cours":**
- Impossible de bloquer
- Terminez d'abord les étapes précédentes

---

### Étape 2: Marquer le Déchargement

#### Quand?
Dès que le camion **est déchargé** et prêt à partir.

#### Comment?

**1. Aller sur la Mission**
- Menu: **Missions** → **Liste des missions**
- Trouvez la mission bloquée

**2. Cliquer sur "Marquer Déchargement"**
- Dans **Actions**, cliquez sur l'icône ✅
- Ou bouton **"Marquer le déchargement"**

**3. Vérifier les Informations**

📋 **Page affiche:**
- **Détails de la mission**
  - Itinéraire (origine → destination)
  - Chauffeur et camion affectés
  - Client et conteneur
  - Date d'arrivée (déjà enregistrée)

- **Règles de facturation**
  - Rappel des 3 jours gratuits
  - Tarif de 25 000 CFA/jour

**4. Sélectionner la Date de Déchargement**

📅 **Champ "Date de déchargement":**
- Par défaut: Date d'aujourd'hui
- Vous pouvez changer si besoin
- ⚠️ Ne peut pas être dans le futur
- ⚠️ Ne peut pas être avant la date d'arrivée

**5. Observer l'Aperçu en Temps Réel** ⭐ NOUVEAU!

Dès que vous sélectionnez une date, une **carte d'aperçu** apparaît automatiquement:

```
┌─────────────────────────────────────────────────┐
│ 👁️ Aperçu en temps réel                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  Jours total: 10    Jours gratuits: 3          │
│  Jours facturables: 5    Montant: 125 000 CFA  │
│                                                 │
│  💰 5 jour(s) × 25 000 CFA = 125 000 CFA       │
└─────────────────────────────────────────────────┘
```

**Cette carte vous montre:**
- 📊 Nombre de jours total (calendrier)
- ✅ Nombre de jours gratuits utilisés
- 💰 Nombre de jours facturables
- 💵 **Montant total à facturer** (en rouge)

👍 **Changez la date** → L'aperçu se met à jour **instantanément**!

**6. Cliquer sur "Aperçu et Confirmation"** ⭐ NOUVEAU!

Au lieu de valider directement, vous pouvez d'abord voir un **aperçu détaillé**.

Un **modal** (fenêtre popup) s'ouvre avec:

```
┌───────────────────────────────────────────────┐
│ 🧮 Aperçu des frais de stationnement          │
├───────────────────────────────────────────────┤
│                                               │
│ ┌─ Période de stationnement ─────────────┐   │
│ │ Date arrivée: 18/12/2024              │   │
│ │ Date déchargement: 26/12/2024         │   │
│ │ Jours total: 9    Jours gratuits: 3   │   │
│ └───────────────────────────────────────┘   │
│                                               │
│ ┌─ Frais de stationnement ────────────────┐  │
│ │ Jours facturables: 4                   │  │
│ │ Tarif: 25 000 CFA/jour                 │  │
│ │ MONTANT TOTAL: 100 000 CFA            │  │
│ └────────────────────────────────────────┘  │
│                                               │
│ ┌─ Détail du calcul ──────────────────────┐  │
│ │ ✅ Arrivée: 18/12/2024                  │  │
│ │ ℹ️ Période gratuite: 18-20/12           │  │
│ │ ✅ 3 jours gratuits                     │  │
│ │ 💰 Facturation commence: 21/12          │  │
│ │ 📅 Déchargement: 26/12                  │  │
│ │ 🔢 4 jours × 25 000 = 100 000 CFA      │  │
│ └─────────────────────────────────────────┘  │
│                                               │
│         [Annuler]    [Confirmer] ✅           │
└───────────────────────────────────────────────┘
```

**7. Vérifier et Confirmer**

Dans le modal:
- ✅ Vérifiez les **dates**
- ✅ Vérifiez les **jours calculés**
- ✅ Vérifiez le **montant**
- ✅ Lisez le **détail du calcul**

Si tout est correct:
- Cliquez sur **"Confirmer"**

Si vous voulez changer la date:
- Cliquez sur **"Annuler"**
- Changez la date
- Recommencez

**8. Validation Finale**

Après avoir cliqué "Confirmer":
- ✅ La mission est marquée comme "Déchargée"
- ✅ Les frais sont enregistrés
- ✅ Un paiement sera créé automatiquement avec les frais inclus
- ✅ Message de succès s'affiche

---

## Comprendre l'Aperçu en Temps Réel

### Qu'est-ce que c'est?

L'**aperçu en temps réel** est une carte qui apparaît automatiquement quand vous sélectionnez une date de déchargement.

### Pourquoi c'est utile?

- ✅ Voir **instantanément** les frais avant de valider
- ✅ Tester **plusieurs dates** pour comparer
- ✅ Éviter les **surprises** après validation
- ✅ Planifier la **date optimale** de déchargement

### Comment lire l'aperçu?

#### Métrique 1: Jours Total
**Exemple:** `10`

📅 Nombre de jours **calendrier** entre arrivée et déchargement.

**Calcul:** Si arrivée le 18 et déchargement le 26:
- 18, 19, 20, 21, 22, 23, 24, 25, 26 = **9 jours**

#### Métrique 2: Jours Gratuits
**Exemple:** `3` (en vert)

✅ Nombre de jours ouvrables gratuits **utilisés**.

**Maximum:** 3 jours ouvrables

Si vous déchargez avant la fin de la période gratuite, ce nombre peut être inférieur à 3.

#### Métrique 3: Jours Facturables
**Exemple:** `5` (en rouge, grande police)

💰 Nombre de jours qui seront **facturés**.

**C'est le nombre le plus important!**

Si ce nombre est **0**, c'est **GRATUIT** ✅

#### Métrique 4: Montant Total
**Exemple:** `125 000 CFA` (en rouge sur fond jaune)

💵 **Montant total à facturer au client**.

**Calcul:** Jours facturables × 25 000 CFA

#### Message en Bas

**Si gratuit:**
```
✅ Aucun frais - Déchargement dans la période gratuite
```
→ En vert, avec icône de validation

**Si payant:**
```
💰 5 jour(s) facturable(s) × 25 000 CFA = 125 000 CFA
```
→ En rouge, avec détail du calcul

---

## Utiliser le Modal de Confirmation

### Pourquoi un Modal?

Le modal vous donne une **dernière chance de vérifier** avant de confirmer. C'est une sécurité pour éviter les erreurs.

### Structure du Modal

Le modal contient **3 cartes**:

#### Carte 1: Période de Stationnement (Bleue)

**Informations:**
- Date d'arrivée (fixe)
- Date de déchargement (que vous avez choisie)
- Jours total (calendrier)
- Jours gratuits utilisés

**À vérifier:**
- ✅ Les dates sont correctes
- ✅ Le nombre de jours total semble juste

#### Carte 2: Frais de Stationnement (Rouge)

**Informations:**
- **Jours facturables** (en gros)
- Tarif journalier (25 000 CFA)
- **MONTANT TOTAL** (en très gros)

**À vérifier:**
- ✅ Le nombre de jours facturables
- ✅ Le montant total (c'est ce qui sera facturé!)

#### Carte 3: Détail du Calcul (Grise)

**Informations (sous forme de liste):**
- ✅ Arrivée du camion
- ℹ️ Période gratuite commence (si arrivée weekend)
- ✅ 3 jours gratuits jusqu'au X
- 💰 Facturation commence le X
- 📅 Déchargement le X
- 🔢 Calcul: N jours × 25 000 = Total

**À faire:**
- 📖 **Lisez étape par étape**
- ✅ Vérifiez que la logique est correcte
- 💡 Utilisez cette explication pour le client si besoin

### Boutons du Modal

#### Bouton "Annuler" (Gris)
- Ferme le modal
- **Rien n'est enregistré**
- Vous pouvez changer la date et recommencer

#### Bouton "Confirmer" (Vert) ✅
- Ferme le modal
- **Valide le déchargement**
- Enregistre la date et les frais
- **IRRÉVERSIBLE** (ne peut pas être annulé facilement)

### Conseils d'Utilisation

1. **Prenez votre temps**
   - Ne cliquez pas trop vite sur "Confirmer"
   - Lisez tous les détails

2. **Vérifiez DEUX FOIS**
   - Les dates
   - Le montant
   - Le calcul

3. **Si doute → Annuler**
   - Mieux vaut annuler et revérifier
   - Que de valider une erreur

4. **Utilisez le détail**
   - La carte "Détail du calcul" explique tout
   - Gardez une capture d'écran si besoin
   - Pour justifier auprès du client

---

## Exemples Concrets

### Exemple 1: Déchargement Rapide (Gratuit)

**Situation:**
- Client décharge rapidement
- Pas de retard

**Données:**
- Arrivée: **Lundi 18 décembre**
- Déchargement: **Mercredi 20 décembre**

**Calcul:**
```
Période gratuite: Lundi 18, Mardi 19, Mercredi 20 (3 jours)
Déchargement: Mercredi 20 (dernier jour gratuit)

Jours facturables: 0
Frais: 0 CFA
```

**Aperçu affiche:**
```
Jours total: 3
Jours gratuits: 3
Jours facturables: 0
Montant: 0 CFA

✅ Aucun frais - Déchargement dans la période gratuite
```

✅ **Résultat:** Client ne paie rien, tout est dans la période gratuite.

---

### Exemple 2: Petit Retard (1 Jour)

**Situation:**
- Client décharge juste après la période gratuite
- 1 seul jour de retard

**Données:**
- Arrivée: **Lundi 18 décembre**
- Déchargement: **Jeudi 21 décembre**

**Calcul:**
```
Période gratuite: Lundi 18, Mardi 19, Mercredi 20 (3 jours)
Fin période gratuite: Mercredi 20
Déchargement: Jeudi 21 (1 jour après)

Jours facturables: 1
Frais: 1 × 25 000 = 25 000 CFA
```

**Aperçu affiche:**
```
Jours total: 4
Jours gratuits: 3
Jours facturables: 1
Montant: 25 000 CFA

💰 1 jour(s) facturable(s) × 25 000 CFA = 25 000 CFA
```

💰 **Résultat:** Client paie 25 000 CFA pour 1 jour de retard.

---

### Exemple 3: Retard Moyen (5 Jours avec Weekend)

**Situation:**
- Client a du retard
- Le déchargement tombe après un weekend

**Données:**
- Arrivée: **Lundi 18 décembre**
- Déchargement: **Lundi 25 décembre**

**Calcul:**
```
Période gratuite: Lundi 18, Mardi 19, Mercredi 20 (3 jours)
Fin période gratuite: Mercredi 20
Début facturation: Jeudi 21

Jours facturables:
- Jeudi 21: Jour 1 ✅
- Vendredi 22: Jour 2 ✅
- Samedi 23: Jour 3 ✅ (weekend compte!)
- Dimanche 24: Jour 4 ✅ (weekend compte!)
- Lundi 25: Jour 5 ✅

Total: 5 jours
Frais: 5 × 25 000 = 125 000 CFA
```

**Aperçu affiche:**
```
Jours total: 8
Jours gratuits: 3
Jours facturables: 5
Montant: 125 000 CFA

💰 5 jour(s) facturable(s) × 25 000 CFA = 125 000 CFA
```

⚠️ **Note:** Les weekends comptent dans les jours facturables!

💰 **Résultat:** Client paie 125 000 CFA.

---

### Exemple 4: Arrivée Weekend

**Situation:**
- Camion arrive le weekend
- La période gratuite commence le lundi suivant

**Données:**
- Arrivée: **Samedi 23 décembre**
- Déchargement: **Jeudi 28 décembre**

**Calcul:**
```
Arrivée: Samedi 23
⚠️ Weekend → Période gratuite commence LUNDI 25

Période gratuite: Lundi 25, Mardi 26, Mercredi 27 (3 jours)
Fin période gratuite: Mercredi 27
Déchargement: Jeudi 28 (1 jour après)

Jours facturables: 1
Frais: 1 × 25 000 = 25 000 CFA
```

**Aperçu affiche:**
```
Jours total: 6 (du samedi au jeudi)
Jours gratuits: 3
Jours facturables: 1
Montant: 25 000 CFA

💰 1 jour(s) facturable(s) × 25 000 CFA = 25 000 CFA
```

**Modal - Détail du calcul:**
```
✅ Arrivée du camion: 23/12/2024
ℹ️ Arrivée le weekend → Période gratuite commence le 25/12/2024
✅ 3 jours gratuits jusqu'au: 27/12/2024
💰 Facturation commence le: 28/12/2024
📅 Déchargement: 28/12/2024
🔢 Calcul: 1 jour × 25 000 CFA = 25 000 CFA
```

💡 **Astuce:** Si arrivée weekend, expliquez au client que la période gratuite commence le lundi.

---

### Exemple 5: Longue Durée (2 Semaines)

**Situation:**
- Client a un gros retard
- Déchargement après 2 semaines

**Données:**
- Arrivée: **Lundi 18 décembre**
- Déchargement: **Lundi 1er janvier** (14 jours après)

**Calcul:**
```
Période gratuite: Lundi 18, Mardi 19, Mercredi 20 (3 jours)
Fin période gratuite: Mercredi 20
Début facturation: Jeudi 21

Jours facturables:
21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31 déc + 1er jan = 12 jours

Frais: 12 × 25 000 = 300 000 CFA
```

**Aperçu affiche:**
```
Jours total: 15
Jours gratuits: 3
Jours facturables: 12
Montant: 300 000 CFA

💰 12 jour(s) facturable(s) × 25 000 CFA = 300 000 CFA
```

💰 **Résultat:** Client paie 300 000 CFA.

⚠️ **Attention:** Frais importants! Communiquez régulièrement avec le client pour éviter les surprises.

---

## Questions Fréquentes

### Q1: Que se passe-t-il si je bloque une mission déjà bloquée?

**R:** Le système vous empêche de bloquer deux fois.

**Message affiché:**
```
⚠️ Cette mission est déjà bloquée pour stationnement depuis le XX/XX/XXXX.
```

**Solution:** Si vous devez changer la date d'arrivée, contactez un administrateur.

---

### Q2: Puis-je modifier la date d'arrivée après avoir bloqué?

**R:** Non, pas directement.

**Solution:**
1. Marquez d'abord le déchargement (avec frais = 0 si besoin)
2. Ou contactez un administrateur pour réinitialiser

---

### Q3: Les weekends comptent-ils dans les jours facturables?

**R:** **OUI!** Les weekends comptent après la période gratuite.

**Exemple:**
```
Période gratuite: Lundi, Mardi, Mercredi (3 jours ouvrables)
Après: Jeudi, Vendredi, Samedi ✅, Dimanche ✅ = 4 jours facturés
```

---

### Q4: Et les jours fériés?

**R:** Les jours fériés sont **traités comme des jours normaux**.

- Période gratuite: Les jours fériés ne comptent PAS comme jours ouvrables
- Facturation: Les jours fériés comptent comme tous les autres jours

---

### Q5: Que faire si le client conteste les frais?

**R:** Utilisez le **détail du calcul** du modal.

**Étapes:**
1. Allez sur la mission
2. Cliquez "Marquer déchargement" (même si déjà fait)
3. Sélectionnez la date de déchargement
4. Ouvrez le modal
5. Prenez une **capture d'écran** de la carte "Détail du calcul"
6. Envoyez au client avec explication

Le détail montre:
- Date arrivée
- Période gratuite
- Date début facturation
- Calcul exact

---

### Q6: Puis-je tester une date avant de valider?

**R:** **OUI!** C'est exactement le but de l'aperçu en temps réel.

**Méthode:**
1. Allez sur "Marquer déchargement"
2. Changez la date plusieurs fois
3. Observez l'aperçu se mettre à jour
4. Comparez les montants
5. Choisissez la meilleure date
6. Validez

---

### Q7: L'aperçu en temps réel est-il fiable?

**R:** **OUI, à 100%!**

L'aperçu utilise le **même calcul** que le serveur. Le montant affiché sera exactement celui enregistré.

---

### Q8: Que se passe-t-il après avoir marqué le déchargement?

**R:** Automatiquement:

1. ✅ Mission marquée comme "Déchargée"
2. ✅ Frais de stationnement enregistrés
3. ✅ Note détaillée ajoutée dans observations
4. ✅ Quand vous créerez un paiement pour cette mission:
   - Les frais seront **automatiquement inclus**
   - Une ligne "Frais Stationnement" sera visible
   - Le total sera correct

---

### Q9: Puis-je annuler un déchargement?

**R:** **Difficile.** Une fois validé, c'est enregistré.

**Si vous devez annuler:**
- Contactez immédiatement un administrateur
- Expliquez la situation
- L'admin peut modifier manuellement en base de données

**Conseil:** Vérifiez BIEN avant de confirmer!

---

### Q10: Pourquoi dois-je bloquer ET marquer le déchargement?

**R:** Ce sont **2 actions distinctes**:

**Bloquer (Arrivée):**
- Le camion arrive
- On commence à compter les jours
- Période gratuite démarre

**Marquer déchargement:**
- Le camion est déchargé
- On calcule le total des jours
- On facture si dépassement

Sans les deux dates, impossible de calculer les frais!

---

## Résolution de Problèmes

### Problème 1: Je ne vois pas le bouton "Bloquer pour Stationnement"

**Cause possible:** Vous n'avez pas les permissions.

**Solution:**
1. Vérifiez que vous êtes connecté comme **Manager** ou **Admin**
2. Si non, contactez votre administrateur système
3. Demandez les droits d'accès

---

### Problème 2: Message "Cette mission est déjà bloquée"

**Cause:** La mission a déjà une date d'arrivée.

**Solution:**
- C'est normal! Ne bloquez pas deux fois
- Passez directement à "Marquer le déchargement"
- Si la date d'arrivée est fausse, contactez un admin

---

### Problème 3: L'aperçu en temps réel ne s'affiche pas

**Cause possible:**
- JavaScript désactivé
- Problème de connexion
- Erreur technique

**Solution:**
1. Rechargez la page (F5)
2. Videz le cache du navigateur (Ctrl+Shift+Del)
3. Essayez un autre navigateur (Firefox, Chrome)
4. Si le problème persiste, contactez le support IT

**Contournement:** Même sans l'aperçu, le modal fonctionne. Cliquez "Aperçu et Confirmation" pour voir les frais.

---

### Problème 4: Le modal ne s'ouvre pas

**Cause possible:** Erreur JavaScript

**Solution:**
1. Rechargez la page
2. Vérifiez que vous avez sélectionné une date
3. Essayez un autre navigateur
4. Contactez le support IT

---

### Problème 5: Les calculs semblent faux

**Symptômes:**
- Le nombre de jours ne correspond pas
- Le montant semble incorrect

**Vérifications:**
1. **Dates correctes?**
   - Date arrivée: XX/XX/XXXX
   - Date déchargement: XX/XX/XXXX

2. **Jours ouvrables?**
   - Comptez Lun-Ven uniquement pour période gratuite
   - Période gratuite = 3 jours ouvrables

3. **Weekend dans la période?**
   - Si arrivée weekend → Commence lundi
   - Après période gratuite → Weekends comptent

**Si toujours incorrect:**
- Prenez une capture d'écran
- Notez les dates exactes
- Contactez le support IT avec ces informations

---

### Problème 6: Erreur "Date ne peut pas être dans le futur"

**Cause:** Vous essayez de mettre une date future.

**Solution:**
- Utilisez la date d'aujourd'hui ou avant
- Si vous devez vraiment utiliser une date future, attendez ce jour-là
- Pour anticiper, utilisez l'aperçu pour voir les frais futurs sans valider

---

### Problème 7: Erreur "Date déchargement avant date arrivée"

**Cause:** Logique impossible (déchargé avant d'arriver).

**Solution:**
- Vérifiez la date d'arrivée (visible sur la page)
- Sélectionnez une date de déchargement >= date arrivée
- Si date arrivée fausse, contactez un admin

---

## Conseils et Bonnes Pratiques

### 🎯 Bloquer Immédiatement

**Pourquoi?**
- Le compteur démarre dès l'arrivée
- Oublier de bloquer = Perte de traçabilité
- Risque de litige avec le client

**Bonne pratique:**
- Dès qu'un camion arrive → Bloquer immédiatement
- Notez l'heure d'arrivée (commentaire si besoin)
- Informez le client que le stationnement a démarré

---

### 📅 Utiliser l'Aperçu pour Planifier

**Scénario:**
Client demande: "Si je décharge demain, combien je paie?"

**Méthode:**
1. Allez sur "Marquer déchargement"
2. Sélectionnez la date de demain
3. Consultez l'aperçu
4. Communiquez le montant au client
5. N'appuyez PAS sur confirmer
6. Annulez ou fermez la page

**Résultat:** Vous avez l'info sans valider!

---

### 💡 Utiliser le Modal pour Expliquer

**Scénario:**
Client ne comprend pas pourquoi il paie.

**Méthode:**
1. Ouvrez le modal
2. Allez dans "Détail du calcul"
3. Prenez une capture d'écran
4. Envoyez au client avec explication:

**Message type:**
```
Bonjour [Client],

Voici le détail des frais de stationnement:

📅 Arrivée camion: 18/12/2024
✅ Période gratuite (3 jours ouvrables): 18, 19, 20 décembre
💰 Facturation démarre: 21/12/2024
📅 Déchargement: 26/12/2024

Jours facturables: 21, 22, 23, 24, 25, 26 = 6 jours
Tarif: 25 000 CFA/jour
Total: 6 × 25 000 = 150 000 CFA

Cordialement,
[Votre nom]
```

---

### 📊 Vérifier Avant de Confirmer

**Checklist avant de cliquer "Confirmer":**
- [ ] Date d'arrivée correcte?
- [ ] Date de déchargement correcte?
- [ ] Jours total cohérent?
- [ ] Jours facturables attendu?
- [ ] Montant justifiable auprès du client?
- [ ] Client informé du montant?

Si **toutes les cases cochées** → Confirmez

Si **un doute** → Annulez et vérifiez

---

### 📸 Garder une Trace

**Bonne pratique:**
Avant de confirmer, prenez une **capture d'écran** du modal.

**Pourquoi?**
- Preuve en cas de litige
- Documentation pour comptabilité
- Référence pour discussions avec client

**Comment?**
- Windows: Touche **Impr. Écran** ou **Windows + Shift + S**
- Mac: **Cmd + Shift + 4**
- Sauvegardez avec nom explicite: `Stationnement_[Client]_[Date].png`

---

### 🔔 Communiquer avec le Client

**Timing de communication:**

**Jour 1 (Arrivée):**
```
"Votre camion est arrivé. La période gratuite de 3 jours ouvrables commence aujourd'hui."
```

**Jour 3 (Fin période gratuite):**
```
"Rappel: La période gratuite se termine aujourd'hui.
À partir de demain, des frais de 25 000 CFA/jour s'appliquent."
```

**Si retard prévu:**
```
"Votre déchargement est prévu le [date].
Les frais de stationnement seront de [montant] CFA."
```

**Résultat:**
- Client informé
- Pas de surprise
- Moins de contestations

---

### ⚡ Décharger le Plus Tôt Possible

**Recommandation au client:**
Encouragez le déchargement **AVANT** la fin de la période gratuite.

**Bénéfices:**
- Client ne paie rien
- Libère l'espace
- Bon pour la relation commerciale

**Communication:**
```
"Je vous conseille de décharger avant [fin période gratuite]
pour éviter les frais de stationnement."
```

---

## 📞 Support et Contact

### Qui Contacter?

**Pour questions techniques:**
- Support IT: [email/téléphone]
- Heures: [horaires]

**Pour questions métier:**
- Manager: [nom]
- Email: [email]

**Pour urgences:**
- Hotline: [numéro]
- Disponible 24/7

---

## 📚 Ressources Complémentaires

### Documents Liés

1. **AMELIORATIONS_UX_STATIONNEMENT.md**
   - Documentation technique complète
   - Pour développeurs et IT

2. **GUIDE_TEST_STATIONNEMENT.md**
   - Procédures de test
   - Pour validation qualité

3. **SYNTHESE_COMPLETE_AMELIORATIONS.md**
   - Vue d'ensemble du projet
   - Historique des changements

---

## ✅ Checklist Rapide

Imprimez et gardez à portée de main:

### Pour Bloquer une Mission

- [ ] Camion est arrivé physiquement
- [ ] Mission est "en cours"
- [ ] Date d'arrivée correcte (pas dans le futur)
- [ ] Informer le client de l'arrivée
- [ ] Valider le blocage

### Pour Marquer le Déchargement

- [ ] Camion est déchargé
- [ ] Mission était déjà bloquée
- [ ] Sélectionner date de déchargement
- [ ] Consulter l'aperçu en temps réel
- [ ] Ouvrir le modal
- [ ] Vérifier les 3 cartes
- [ ] Lire le détail du calcul
- [ ] Prendre capture d'écran (optionnel)
- [ ] Confirmer
- [ ] Informer le client du montant

---

**Guide créé le:** 29 décembre 2024
**Version:** 1.0
**Auteur:** Équipe Développement
**Pour:** Managers et Administrateurs

**N'hésitez pas à contacter le support si vous avez des questions!** 📞
