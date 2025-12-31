# Guide de Test - Système de Stationnement

## Date: 29 décembre 2024

---

## ✅ Vérifications Préliminaires

### 1. Serveur de développement
- ✅ Serveur Django en cours sur http://127.0.0.1:8000/
- ✅ Aucune erreur au démarrage
- ✅ Toutes les URLs configurées correctement

### 2. URLs Configurées
```
✅ /missions/<pk>/bloquer-stationnement/
✅ /missions/<pk>/marquer-dechargement/
✅ /missions/<pk>/calculer-stationnement/
✅ /missions/<pk>/preview-frais-stationnement/  (NOUVEAU!)
```

---

## 🧪 Tests Manuels à Effectuer

### Test 1: Modal de Confirmation ⭐⭐⭐⭐⭐

**Objectif:** Vérifier que le modal de confirmation s'affiche avec les bons calculs

**Étapes:**
1. Se connecter comme **manager** ou **admin**
2. Aller à **Missions** → Sélectionner une mission **"en cours"** avec `date_arrivee` renseignée
3. Cliquer sur **"Marquer déchargement"** (ou accéder via liste missions)
4. Sélectionner une date de déchargement (par défaut: aujourd'hui)
5. Cliquer sur **"Aperçu et Confirmation"** (bouton vert)

**Vérifications:**
- [ ] Le modal s'ouvre avec un fond sombre (backdrop)
- [ ] En-tête jaune avec titre "Aperçu des frais de stationnement"
- [ ] **Carte 1 (bleue):** Période de stationnement
  - [ ] Date arrivée affichée correctement
  - [ ] Date déchargement affichée correctement
  - [ ] Jours total calculé
  - [ ] Jours gratuits utilisés calculé
- [ ] **Carte 2 (rouge):** Frais de stationnement
  - [ ] Jours facturables affiché en gros et rouge
  - [ ] Tarif journalier: "25 000 CFA"
  - [ ] Montant total en h2 rouge
- [ ] **Carte 3 (grise):** Détail du calcul
  - [ ] Liste à puces avec étapes
  - [ ] Icônes (✅, ℹ️, 💰, 📅, 🔢)
  - [ ] Si gratuit: Message vert "Aucun frais à facturer"
  - [ ] Si payant: Calcul détaillé avec formule
- [ ] Bouton "Annuler" ferme le modal
- [ ] Bouton "Confirmer" soumet le formulaire

**Cas de test:**
- Mission arrivée lundi, déchargement mercredi (même semaine) → **0 CFA** (dans période gratuite)
- Mission arrivée lundi, déchargement jeudi semaine suivante → **25 000 CFA** (1 jour facturable)
- Mission arrivée samedi, déchargement mercredi suivant → **0 CFA** (période gratuite commence lundi)

---

### Test 2: Aperçu en Temps Réel ⭐⭐⭐⭐⭐

**Objectif:** Vérifier que la carte d'aperçu se met à jour automatiquement

**Étapes:**
1. Aller sur la page **"Marquer déchargement"** (même mission que Test 1)
2. Observer la page **AVANT** de sélectionner une date

**Vérifications initiales:**
- [ ] Carte "Aperçu en temps réel" **non visible** (display: none)

**Étapes suite:**
3. Sélectionner une date de déchargement
4. Observer **immédiatement** (sans cliquer ailleurs)

**Vérifications après sélection:**
- [ ] Carte "Aperçu en temps réel" **apparaît** automatiquement
- [ ] En-tête avec gradient violet (#667eea → #764ba2)
- [ ] Message de chargement: "Calcul en cours..." avec spinner (quelques millisecondes)
- [ ] **4 métriques affichées** en colonnes:
  - [ ] Jours total (neutre)
  - [ ] Jours gratuits (vert)
  - [ ] Jours facturables (rouge, grande police)
  - [ ] Montant total (rouge sur fond jaune)
- [ ] Message en bas:
  - [ ] Si gratuit: Icône ✅ verte + "Aucun frais - Déchargement dans la période gratuite"
  - [ ] Si payant: Icône 💰 rouge + "N jour(s) facturable(s) × 25 000 CFA = X CFA"

**Test de réactivité:**
5. Changer la date plusieurs fois
6. Observer que la carte se met à jour **à chaque changement**

**Vérifications:**
- [ ] Pas de délai perceptible
- [ ] Valeurs changent instantanément
- [ ] Pas d'erreur dans la console (F12)

---

### Test 3: Endpoint AJAX ⭐⭐⭐⭐

**Objectif:** Vérifier que l'endpoint serveur répond correctement

**Étapes:**
1. Rester sur la page "Marquer déchargement"
2. Ouvrir **DevTools** (F12) → Onglet **Network**
3. Sélectionner une date de déchargement
4. Observer les requêtes réseau

**Vérifications dans Network:**
- [ ] Une requête GET à `/missions/<pk>/preview-frais-stationnement/?date_dechargement=YYYY-MM-DD`
- [ ] Status: **200 OK**
- [ ] Type: **xhr** (AJAX)
- [ ] Temps de réponse: < 500ms

**Cliquer sur la requête → Onglet Response:**

**Structure JSON attendue:**
```json
{
  "success": true,
  "jours_total": 10,
  "jours_gratuits": 3,
  "jours_facturables": 5,
  "montant": 125000.0,
  "montant_formatted": "125 000",
  "debut_gratuit": "2024-12-18",
  "fin_gratuit": "2024-12-20",
  "debut_facturation": "2024-12-21",
  "date_arrivee": "2024-12-16",
  "date_dechargement": "2024-12-26",
  "message": "5 jour(s) facturable(s) × 25 000 CFA = 125 000 CFA",
  "statut": "payant",
  "tarif_journalier": 25000.0
}
```

**Vérifications:**
- [ ] `success: true`
- [ ] Tous les champs présents
- [ ] Valeurs cohérentes (jours_facturables × 25000 = montant)
- [ ] `montant_formatted` avec espace comme séparateur de milliers

**Test d'erreur:**
5. Dans l'URL du navigateur, modifier manuellement pour tester une date invalide:
   `/missions/<pk>/preview-frais-stationnement/?date_dechargement=2024-13-99`

**Vérifications:**
- [ ] Status: **400 Bad Request**
- [ ] JSON: `{"success": false, "message": "Format de date invalide..."}`

---

### Test 4: Cohérence des Calculs ⭐⭐⭐⭐⭐

**Objectif:** Vérifier que les 3 méthodes de calcul donnent le même résultat

**Scénario de test:**
- Date arrivée: **Lundi 18 décembre 2024**
- Date déchargement: **Jeudi 28 décembre 2024**

**Calcul attendu:**
```
Arrivée: Lundi 18/12
Période gratuite: 18/12 (lun) → 20/12 (mer) = 3 jours ouvrables
Fin période gratuite: Mercredi 20/12
Début facturation: Jeudi 21/12
Déchargement: Jeudi 28/12

Jours facturables: 21, 22, 23, 24, 25, 26, 27, 28 = 8 jours
Montant: 8 × 25 000 = 200 000 CFA
```

**Méthode 1: Aperçu temps réel (AJAX)**
- [ ] Jours facturables: **8**
- [ ] Montant: **200 000 CFA**

**Méthode 2: Modal confirmation (JavaScript)**
- [ ] Jours facturables: **8**
- [ ] Montant: **200 000 CFA**
- [ ] Détail calcul affiche: "8 jour(s) × 25 000 CFA = 200 000 CFA"

**Méthode 3: Soumission réelle**
1. Confirmer le déchargement
2. Vérifier dans la base de données:

```bash
python manage.py shell
>>> from transport.models import Mission
>>> mission = Mission.objects.get(pk_mission='<pk>')
>>> print(f"Jours: {mission.jours_stationnement_facturables}, Montant: {mission.montant_stationnement}")
```

- [ ] Jours: **8**
- [ ] Montant: **200000.00**

**✅ Les 3 méthodes doivent donner exactement le même résultat**

---

### Test 5: Validation et Sécurité ⭐⭐⭐⭐

**Objectif:** Vérifier que les validations fonctionnent

#### A. Permissions

**Étapes:**
1. Se déconnecter
2. Se connecter comme **utilisateur simple** (non-manager)
3. Essayer d'accéder à `/missions/<pk>/marquer-dechargement/`

**Vérifications:**
- [ ] Redirection ou message d'erreur "Accès refusé"
- [ ] **Impossible** d'accéder à la page

**Étapes:**
4. Se reconnecter comme **manager** ou **admin**
5. Accéder à la même URL

**Vérifications:**
- [ ] Accès autorisé
- [ ] Page s'affiche correctement

#### B. Validation Date Future

**Étapes:**
1. Sur la page "Marquer déchargement"
2. Essayer de sélectionner une date **dans le futur** (demain ou après)

**Vérifications:**
- [ ] HTML input `max="{{ today|date:'Y-m-d' }}"` empêche la sélection
- [ ] Si contourné (modification HTML), validation serveur rejette

#### C. Validation Date Cohérence

**Étapes:**
1. Modifier le HTML pour permettre une date avant `date_arrivee`
2. Soumettre le formulaire

**Vérifications:**
- [ ] Message d'erreur: "❌ La date de déchargement ne peut pas être avant la date d'arrivée"
- [ ] Formulaire **non soumis**

#### D. Double Blocage

**Étapes:**
1. Aller sur une mission **déjà bloquée** (avec date_arrivee)
2. Accéder à `/missions/<pk>/bloquer-stationnement/`

**Vérifications:**
- [ ] Message d'avertissement: "⚠️ Cette mission est déjà bloquée..."
- [ ] Redirection vers liste missions
- [ ] Mission **non modifiée**

---

### Test 6: Intégration Paiement ⭐⭐⭐⭐⭐

**Objectif:** Vérifier que les frais sont automatiquement inclus dans les paiements

**Étapes:**
1. Terminer le déchargement d'une mission avec **frais de stationnement > 0**
2. Vérifier dans la base que:
   - `mission.jours_stationnement_facturables > 0`
   - `mission.montant_stationnement > 0`
3. Aller à **Paiements** → **Créer un paiement** pour cette mission
4. Sauvegarder le paiement

**Vérifications en base:**
```bash
python manage.py shell
>>> from transport.models import PaiementMission
>>> paiement = PaiementMission.objects.filter(mission__pk_mission='<pk>').first()
>>> print(f"Frais stationnement: {paiement.frais_stationnement}")
>>> print(f"Observation:\n{paiement.observation}")
```

**Attendu:**
- [ ] `frais_stationnement` = montant mission (ex: 125000.00)
- [ ] `observation` contient:
  ```
  --- Frais de stationnement ---
  Jours facturables: 5
  Montant: 125000.00 CFA
  Date arrivée: 16/12/2024
  Date déchargement: 26/12/2024
  ```

**Vérifications dans l'interface:**
5. Aller à **Paiements** → **Liste des paiements**
6. Trouver le paiement créé

**Colonnes visibles:**
- [ ] Colonne **"Frais Stationnement"** existe
- [ ] Montant affiché en **rouge gras**: "125 000 CFA"
- [ ] Sous le montant: "(5 jours)" en petit gris

**Cliquer sur le paiement pour voir détails:**
- [ ] Section "Observations" contient le détail des frais
- [ ] Dates, jours et montant corrects

---

### Test 7: Design et Responsiveness ⭐⭐⭐

**Objectif:** Vérifier que le design est cohérent et responsive

#### A. Desktop (>= 992px)

**Vérifications carte aperçu:**
- [ ] 4 colonnes bien alignées
- [ ] Espace entre les métriques (gap)
- [ ] Gradient violet visible dans l'en-tête

**Vérifications modal:**
- [ ] Largeur modal: `modal-lg` (large)
- [ ] 3 cartes empilées verticalement
- [ ] Cartes avec bordures colorées (bleu, rouge, gris)
- [ ] Texte lisible

#### B. Tablet (768px - 991px)

**Étapes:**
1. Redimensionner fenêtre à ~800px
2. Ouvrir page "Marquer déchargement"

**Vérifications:**
- [ ] Aperçu: Métriques passent en 2 lignes (2 colonnes)
- [ ] Modal reste lisible
- [ ] Pas de scroll horizontal

#### C. Mobile (< 768px)

**Étapes:**
1. Ouvrir DevTools → Toggle device toolbar (Ctrl+Shift+M)
2. Sélectionner iPhone ou autre mobile

**Vérifications:**
- [ ] Aperçu: Métriques en 1 colonne (empilées)
- [ ] Modal: Largeur 100% avec padding
- [ ] Boutons accessibles
- [ ] Texte lisible (pas trop petit)

---

### Test 8: Console Browser (Erreurs JavaScript) ⭐⭐⭐⭐

**Objectif:** Vérifier qu'il n'y a aucune erreur JavaScript

**Étapes:**
1. Ouvrir **DevTools** (F12) → Onglet **Console**
2. Recharger la page "Marquer déchargement"
3. Sélectionner une date
4. Ouvrir le modal
5. Confirmer

**Vérifications:**
- [ ] **Aucune erreur rouge** dans la console
- [ ] Aucun warning critique
- [ ] Logs éventuels (si présents) sont informatifs uniquement

**Erreurs à NE PAS voir:**
- ❌ `Uncaught ReferenceError`
- ❌ `TypeError: Cannot read property`
- ❌ `Uncaught SyntaxError`
- ❌ `Failed to fetch`

---

## 📊 Résultats Attendus

### Checklist Complète

**Tests Fonctionnels:**
- [ ] Test 1: Modal de confirmation ✅
- [ ] Test 2: Aperçu temps réel ✅
- [ ] Test 3: Endpoint AJAX ✅
- [ ] Test 4: Cohérence calculs ✅
- [ ] Test 5: Validation et sécurité ✅
- [ ] Test 6: Intégration paiement ✅
- [ ] Test 7: Design responsive ✅
- [ ] Test 8: Aucune erreur console ✅

**Critères de Succès:**
- ✅ Tous les tests passent
- ✅ 0 erreur JavaScript
- ✅ 0 erreur serveur
- ✅ UX fluide et intuitive
- ✅ Calculs toujours cohérents

---

## 🐛 Problèmes Connus Potentiels

### Problème 1: Modal ne s'affiche pas
**Symptômes:** Clic sur "Aperçu et Confirmation" ne fait rien

**Causes possibles:**
- Bootstrap JS non chargé
- Erreur JavaScript bloquante

**Vérifications:**
1. Console: Y a-t-il une erreur?
2. Network: bootstrap.bundle.min.js chargé?
3. Tester: `typeof bootstrap` dans console → doit retourner "object"

**Solution:**
- Vérifier `admin.html` inclut bien Bootstrap

### Problème 2: Aperçu temps réel ne se met pas à jour
**Symptômes:** Carte reste avec "Calcul en cours..." ou ne s'affiche pas

**Causes possibles:**
- Endpoint AJAX non accessible
- CORS bloqué (peu probable en dev)
- URL incorrecte

**Vérifications:**
1. Network: Y a-t-il une requête à `preview-frais-stationnement`?
2. Status de la requête? 200, 404, 500?
3. Console: Erreur fetch?

**Solution:**
- Vérifier URL dans urls.py
- Vérifier vue exportée dans __init__.py
- Redémarrer serveur Django

### Problème 3: Calculs incohérents
**Symptômes:** JavaScript calcule différent du serveur

**Causes possibles:**
- Logique JavaScript diverge du Python
- Gestion weekends différente
- Timezone

**Vérifications:**
1. Comparer ligne par ligne:
   - JavaScript: `calculateFees()` (ligne ~368)
   - Python: `preview_frais_stationnement()` (ligne ~612)
2. Dates identiques?

**Solution:**
- Corriger la logique divergente
- Ajouter logs pour debugger

---

## 💡 Conseils de Test

### Bons Scénarios de Test

**Scénario 1: Gratuit (aucun frais)**
- Arrivée: Lundi
- Déchargement: Mercredi (même semaine)
- **Attendu:** 0 CFA

**Scénario 2: 1 jour facturable**
- Arrivée: Lundi
- Déchargement: Jeudi semaine suivante
- **Attendu:** 25 000 CFA

**Scénario 3: Arrivée weekend**
- Arrivée: Samedi
- Déchargement: Mercredi suivant
- **Attendu:** 0 CFA (période gratuite commence lundi)

**Scénario 4: Longue durée**
- Arrivée: Lundi
- Déchargement: 2 semaines après
- **Attendu:** ~7 jours = 175 000 CFA

**Scénario 5: Weekend inclus dans facturation**
- Arrivée: Lundi 1er
- Déchargement: Lundi 8
- Période gratuite: 1, 2, 3 (L, M, M)
- Facturation: 4 (J), 5 (V), 6 (S), 7 (D), 8 (L) = **5 jours**
- **Attendu:** 125 000 CFA

---

## 📝 Rapport de Test

### Template à remplir après tests:

```
Date test: __________
Testeur: __________
Environnement: Développement / Staging / Production

RÉSULTATS:

Test 1 - Modal confirmation: ✅ / ❌
Notes: _______________

Test 2 - Aperçu temps réel: ✅ / ❌
Notes: _______________

Test 3 - Endpoint AJAX: ✅ / ❌
Notes: _______________

Test 4 - Cohérence calculs: ✅ / ❌
Notes: _______________

Test 5 - Validation sécurité: ✅ / ❌
Notes: _______________

Test 6 - Intégration paiement: ✅ / ❌
Notes: _______________

Test 7 - Design responsive: ✅ / ❌
Notes: _______________

Test 8 - Console erreurs: ✅ / ❌
Notes: _______________

PROBLÈMES IDENTIFIÉS:
1. _______________
2. _______________

RECOMMANDATIONS:
_______________

STATUT FINAL: ✅ Prêt pour production / ❌ Corrections nécessaires
```

---

## ✅ Validation Finale

**Avant de passer en production:**

- [ ] Tous les tests manuels passent
- [ ] Aucune erreur console
- [ ] Aucune erreur serveur
- [ ] Tests sur Chrome, Firefox, Safari
- [ ] Tests sur mobile réel (optionnel mais recommandé)
- [ ] Backup base de données effectué
- [ ] Documentation utilisateur créée
- [ ] Formation managers effectuée

---

**Document créé le:** 29 décembre 2024
**Version:** 1.0
**Statut:** Prêt pour test

**Bonne chance avec les tests! 🚀**
