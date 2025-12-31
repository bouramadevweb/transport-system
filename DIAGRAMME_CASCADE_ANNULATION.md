# Diagrammes: Cascade d'Annulation

**Date:** 30 décembre 2024

---

## 📊 Scénario 1: Annulation Mission (Actuel)

```
┌─────────────────────────────────────────────────────────┐
│         Mission.annuler_mission(raison)                 │
│         Fichier: mission.py:384-450                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────┐
        │    MISSION                    │
        │  statut = 'annulée' ✅        │
        │  itineraire += note           │
        └───────────────────────────────┘
                        │
        ┌───────────────┴────────────────────────────┐
        │                                            │
        ↓                                            ↓
┌──────────────────┐                        ┌──────────────────┐
│    CONTRAT       │                        │    CAUTIONS      │
│  RESTE ACTIF ⚠️  │                        │  statut =        │
│  commentaire +=  │                        │  'annulee' ✅    │
│  "ANNULÉ..."     │                        │  (TOUTES)        │
└──────────────────┘                        └──────────────────┘
        │
        ↓
┌──────────────────────────────────────┐
│         PAIEMENTS                    │
│  if paiement.est_valide == False:    │
│     observation += "ANNULÉ..." ⚠️    │
│  else:                               │
│     NON MODIFIÉ ❌                   │
└──────────────────────────────────────┘

RÉSULTAT:
✅ Mission annulée
✅ Cautions annulées
⚠️  Contrat pas annulé (juste commentaire)
⚠️  Paiements non validés: note ajoutée
❌ Paiements validés: AUCUN changement
```

---

## 📊 Scénario 2: Suppression Contrat (Actuel - DANGEREUX)

```
┌─────────────────────────────────────────────────────────┐
│         contrat.delete()                                │
│         Fichier: contrat_views.py:98                    │
│         ⚠️  SUPPRESSION BRUTALE - PERTE DE DONNÉES      │
└─────────────────────────────────────────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────┐
        │    CONTRAT                    │
        │  SUPPRIMÉ ❌                  │
        │  Disparaît de la BDD          │
        └───────────────────────────────┘
                        │
        ┌───────────────┴────────────────────────────┐
        │  CASCADE                    SET_NULL       │
        ↓                                            ↓
┌──────────────────┐                        ┌──────────────────┐
│    MISSIONS      │                        │    CAUTIONS      │
│  SUPPRIMÉES ❌   │                        │  contrat_id =    │
│  (CASCADE)       │                        │  NULL ⚠️         │
│                  │                        │  Orphelines      │
└──────────────────┘                        └──────────────────┘
        │
        │ CASCADE
        ↓
┌──────────────────┐                        ┌──────────────────┐
│   PAIEMENTS      │                        │   PRESTATIONS    │
│  SUPPRIMÉS ❌    │                        │  SUPPRIMÉES ❌   │
│  (CASCADE via    │                        │  (CASCADE)       │
│   mission)       │                        │                  │
└──────────────────┘                        └──────────────────┘

RÉSULTAT:
❌ Contrat: DISPARU
❌ Missions: DISPARUES
❌ Paiements: DISPARUS (données financières perdues!)
❌ Prestations: DISPARUES
⚠️  Cautions: ORPHELINES (contrat_id=NULL mais pas annulées)
❌ AUCUNE TRAÇABILITÉ
```

---

## 📊 Scénario 3: Annulation Contrat (PROPOSÉ - SÉCURISÉ)

```
┌─────────────────────────────────────────────────────────┐
│         ContratTransport.annuler_contrat(raison)        │
│         NOUVELLE MÉTHODE PROPOSÉE                       │
│         ✅ ANNULATION PROPRE AVEC TRAÇABILITÉ           │
└─────────────────────────────────────────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────┐
        │    CONTRAT                    │
        │  statut = 'annule' ✅         │
        │  commentaire += raison        │
        │  CONSERVÉ en BDD              │
        └───────────────────────────────┘
                        │
        ┌───────────────┴────────────────────────────┐
        │                                            │
        ↓                                            ↓
┌──────────────────┐                        ┌──────────────────┐
│    MISSIONS      │                        │    CAUTIONS      │
│  Pour chaque:    │                        │  Pour chaque:    │
│  .annuler_       │                        │  statut =        │
│   mission()      │                        │  'annulee' ✅    │
│  statut =        │                        │                  │
│  'annulée' ✅    │                        │  CONSERVÉES      │
│                  │                        │  en BDD          │
│  CONSERVÉES      │                        └──────────────────┘
│  en BDD          │
└──────────────────┘
        │
        │ Via annuler_mission()
        ↓
┌──────────────────────────────────────┐
│         PAIEMENTS                    │
│  Pour TOUS les paiements:            │
│                                      │
│  if paiement.est_valide:             │
│     statut = 'annule' ✅             │
│     observation += "VALIDÉ MAIS      │
│     MISSION ANNULÉE - VÉRIFIER       │
│     REMBOURSEMENT" ⚠️                │
│  else:                               │
│     statut = 'annule' ✅             │
│     observation += "ANNULÉ" ✅       │
│                                      │
│  CONSERVÉS en BDD                    │
└──────────────────────────────────────┘
        │
        ↓
┌──────────────────┐
│   PRESTATIONS    │
│  Note dans       │
│  commentaire     │
│  du contrat      │
│                  │
│  CONSERVÉES      │
│  en BDD          │
└──────────────────┘

RÉSULTAT:
✅ Contrat: statut='annule', CONSERVÉ
✅ Missions: TOUTES annulées, CONSERVÉES
✅ Paiements: TOUS annulés, CONSERVÉS
✅ Cautions: TOUTES annulées, CONSERVÉES
✅ Prestations: CONSERVÉES (note dans contrat)
✅ TRAÇABILITÉ COMPLÈTE
✅ Audit possible
✅ Historique intact
```

---

## 🔍 Comparaison Détaillée

### Relations `on_delete` - AVANT (Actuel)

```
ContratTransport
    ├─> Mission (CASCADE) ─────────> SUPPRESSION ❌
    │       └─> PaiementMission (CASCADE) ─> SUPPRESSION ❌
    │
    ├─> Cautions (SET_NULL) ───────> FK → NULL ⚠️
    │
    └─> PrestationDeTransports (CASCADE) ─> SUPPRESSION ❌
```

**Problème:** Tout disparaît sans trace!

---

### Relations `on_delete` - APRÈS (Proposé)

```
ContratTransport
    ├─> Mission (PROTECT) ─────────> ERREUR si missions existent ✅
    │       └─> PaiementMission (CASCADE préservé)
    │
    ├─> Cautions (PROTECT) ────────> ERREUR si cautions existent ✅
    │
    └─> PrestationDeTransports (PROTECT) ─> ERREUR si prestations ✅
```

**Solution:** Impossible de supprimer → Force l'utilisation d'annuler_contrat() ✅

---

## 📋 Tableau Récapitulatif

| Action | Méthode Actuelle | Impact | Recommandation | Impact |
|--------|------------------|--------|----------------|--------|
| **Annuler Mission** | `mission.annuler_mission()` | ⚠️ Partiel | Modifier méthode | ✅ Complet |
| **Annuler Contrat** | ❌ N'existe pas | N/A | Créer méthode | ✅ Complet |
| **Supprimer Contrat** | `contrat.delete()` | ❌ Tout perdu | Bloquer + message | ✅ Protégé |

---

## 🎯 Flux Recommandé

### Cas 1: Annulation d'une Mission Isolée

```
Utilisateur → Bouton "Annuler Mission"
    ↓
Mission.annuler_mission(raison)
    ↓
✅ Mission annulée (statut='annulée')
✅ Cautions annulées (statut='annulee')
✅ Paiements annulés (statut='annule')
⚠️  Contrat reste actif (autres missions possibles)
```

**Utilisation:** Mission annulée mais contrat continue avec autres missions

---

### Cas 2: Annulation d'un Contrat Complet

```
Utilisateur → Bouton "Annuler Contrat"
    ↓
ContratTransport.annuler_contrat(raison)
    ↓
✅ Contrat annulé (statut='annule')
✅ TOUTES missions annulées (cascade)
✅ TOUTES cautions annulées
✅ TOUS paiements annulés
✅ Prestations conservées avec note
    ↓
Log détaillé:
  "Contrat BL-12345 annulé:
   - 5 missions annulées
   - 3 cautions annulées
   - 8 paiements annulés
   Raison: Client a annulé commande"
```

**Utilisation:** Annuler tout le contrat et garder la traçabilité

---

### Cas 3: Tentative de Suppression

```
Utilisateur → Bouton "Supprimer Contrat"
    ↓
delete_contrat(pk)
    ↓
Vérification: contrat a des missions?
    ↓
    OUI → ❌ Erreur bloquée
          Message: "Impossible de supprimer!
          Le contrat a 5 missions.
          Utilisez l'annulation à la place."
    ↓
    NON → Vérification: contrat a des cautions?
        ↓
        OUI → ❌ Erreur bloquée
              Message: "Impossible de supprimer!
              Le contrat a 3 cautions.
              Utilisez l'annulation."
        ↓
        NON → ✅ Suppression autorisée
              (contrat vide, créé par erreur)
```

**Utilisation:** Empêcher perte de données, forcer annulation propre

---

## 🔐 Protection des Données

### Niveau 1: Protection Base de Données

```python
# mission.py
class Mission(models.Model):
    contrat = models.ForeignKey(
        "ContratTransport",
        on_delete=models.PROTECT  # ← Bloque suppression
    )
```

**Effet:** Django lève `ProtectedError` si on essaie de supprimer un contrat avec missions

---

### Niveau 2: Protection Vue

```python
# contrat_views.py
def delete_contrat(request, pk):
    # Vérification avant suppression
    if Mission.objects.filter(contrat=contrat).exists():
        messages.error(request, "❌ Impossible! Utilisez l'annulation")
        return redirect('contrat_list')
```

**Effet:** Message clair à l'utilisateur, redirection

---

### Niveau 3: Protection Interface

```html
<!-- Template -->
{% if contrat.a_des_missions %}
    <button disabled title="Impossible - contrat a des missions">
        Supprimer (désactivé)
    </button>
    <button href="{% url 'annuler_contrat' contrat.pk %}">
        Annuler (recommandé)
    </button>
{% else %}
    <button href="{% url 'delete_contrat' contrat.pk %}">
        Supprimer
    </button>
{% endif %}
```

**Effet:** Bouton grisé si contrat a des données, propose annulation

---

## 📊 Impact Financier de la Traçabilité

### Exemple Réel

**Contrat BL-12345:**
- Montant: 500 000 CFA
- 5 missions
- 3 cautions (150 000 CFA)
- 8 paiements

**AVANT (suppression):**
```
Contrat supprimé → TOUT DISPARU ❌
Impossible de:
  - Savoir combien a été payé
  - Retrouver les cautions
  - Auditer les opérations
  - Justifier auprès du client
```

**APRÈS (annulation):**
```
Contrat annulé → TOUT CONSERVÉ ✅
Traçabilité complète:
  - Historique des 8 paiements (350 000 CFA payés)
  - 3 cautions annulées (150 000 CFA à rembourser)
  - Raison d'annulation documentée
  - Audit financier possible
  - Justification client disponible
```

**Impact:** Protection juridique + transparence financière

---

## 🚨 Cas d'Usage Critiques

### Scénario 1: Litige Client

**Situation:** Client conteste une facture de 500 000 CFA

**AVANT (suppression):**
```
❌ Contrat supprimé
❌ Impossible de prouver ce qui a été facturé
❌ Pas de trace des paiements
❌ Litige perdu
```

**APRÈS (annulation):**
```
✅ Contrat annulé mais conservé
✅ Historique complet des 8 paiements
✅ Raison d'annulation documentée
✅ Preuve disponible pour tribunal
✅ Litige gagné
```

---

### Scénario 2: Audit Comptable

**Situation:** Audit annuel des finances

**AVANT (suppression):**
```
❌ Trous dans la comptabilité
❌ Paiements manquants
❌ Impossible de justifier les montants
❌ Audit échoué ⚠️
```

**APRÈS (annulation):**
```
✅ Tous les contrats présents (actifs + annulés)
✅ Tous les paiements tracés
✅ Cautions justifiées
✅ Audit réussi ✅
```

---

### Scénario 3: Analyse Business

**Situation:** Comprendre pourquoi 20% de contrats sont annulés

**AVANT (suppression):**
```
❌ Contrats annulés = supprimés
❌ Impossible d'analyser les raisons
❌ Pas de statistiques
❌ Impossible d'améliorer
```

**APRÈS (annulation):**
```
✅ Requête: SELECT * FROM contrats WHERE statut='annule'
✅ Analyse des raisons d'annulation
✅ Statistiques: 50% = "retard livraison", 30% = "problème qualité"
✅ Actions correctives identifiées
✅ Amélioration continue
```

---

**Créé le:** 30 décembre 2024
**Version:** 1.0

