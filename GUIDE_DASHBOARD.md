# Guide d'Utilisation du Dashboard

## Table des Matières

1. [Introduction](#introduction)
2. [Accès au Dashboard](#accès-au-dashboard)
3. [Dashboard Principal](#dashboard-principal)
4. [Dashboard Financier](#dashboard-financier)
5. [Filtres et Personnalisation](#filtres-et-personnalisation)
6. [Interprétation des KPIs](#interprétation-des-kpis)
7. [Alertes et Notifications](#alertes-et-notifications)
8. [Export de Données](#export-de-données)
9. [FAQ](#faq)

---

## Introduction

Le nouveau système de dashboard vous offre une vue d'ensemble complète de votre activité de transport en temps réel.

**Avantages** :
- 📊 Visualisation instantanée des KPIs clés
- 📈 Graphiques interactifs pour analyser les tendances
- ⚡ Alertes automatiques pour les missions en retard
- 💰 Suivi financier détaillé
- 🎯 Prise de décision basée sur les données

---

## Accès au Dashboard

### URLs Disponibles

| Dashboard | URL | Description |
|-----------|-----|-------------|
| **Principal** | `/dashboard/home/` | Vue d'ensemble complète |
| **Financier** | `/dashboard/financier/` | Analyse financière détaillée |
| **Ancien** | `/dashboard/` | Dashboard simple (obsolète) |

### Navigation

Dans le menu principal, cliquez sur :
1. **Dashboard** → Dashboard Principal
2. **Finances** → Dashboard Financier

---

## Dashboard Principal

### Section 1 : KPIs en Un Coup d'Œil

Quatre cartes principales affichent les métriques essentielles :

#### 🚚 Missions en Cours
```
Missions en cours: 15
/ 247 total
```
**Interprétation** :
- Nombre actuel de missions actives
- Total de toutes les missions depuis le début
- Carte bleue : Missions en cours

#### 💰 CA Total
```
CA Total: 12 500 000 FCFA
CA Net: 11 200 000 FCFA
```
**Interprétation** :
- CA Total = Somme de tous les paiements validés
- CA Net = CA Total - Commissions transitaires
- Carte verte : Chiffre d'affaires

#### ✅ Taux de Réussite
```
Taux de réussite: 85.2%
210 missions terminées
```
**Interprétation** :
- % de missions terminées avec succès
- Missions terminées / Total missions
- Carte bleue claire : Performance

#### 📦 Conteneurs Disponibles
```
Conteneurs disponibles: 23
/ 50 total
```
**Interprétation** :
- Nombre de conteneurs au port (disponibles)
- Total de conteneurs dans le système
- Carte orange : Ressources

---

### Section 2 : Alertes Urgentes

Zone rouge qui s'affiche si des problèmes nécessitent votre attention.

**Types d'alertes** :
- ⚠️ **Missions en retard** : Missions dont la date limite est dépassée
- 🚢 **Conteneurs bloqués** : Conteneurs en mission depuis trop longtemps
- 💸 **Cautions non remboursées** : Cautions en attente de traitement

**Exemple** :
```
🚨 Alertes (3)

Mission MISS-ABC123 en retard
- Départ: 15/11/2025
- Chauffeur: Jean Dupont
- Destination: Bamako
```

**Action recommandée** :
1. Cliquer sur l'ID de la mission pour voir les détails
2. Contacter le chauffeur
3. Terminer ou annuler la mission

---

### Section 3 : Graphiques

#### Graphique 1 : Évolution des Missions (6 mois)

**Courbes** :
- 🔵 **Total** : Toutes les missions créées
- 🟢 **Terminées** : Missions complétées avec succès
- 🔴 **Annulées** : Missions annulées

**Utilisation** :
- Identifier les tendances mensuelles
- Comparer performance d'un mois à l'autre
- Détecter les périodes creuses

**Exemple d'analyse** :
```
Si les annulations augmentent → Investiguer les causes
Si les terminées baissent → Problème opérationnel possible
```

#### Graphique 2 : Chiffre d'Affaires (6 mois)

**Barres** :
- 🔵 **CA Total** : Revenus bruts
- 🔴 **Commissions** : Coûts transitaires

**Utilisation** :
- Suivre l'évolution du CA
- Comparer avec les objectifs mensuels
- Analyser la rentabilité

#### Graphique 3 : Statut des Missions (Camembert)

**Segments** :
- 🔵 En cours
- 🟢 Terminées
- 🔴 Annulées

**Interprétation** :
- Si "En cours" > 30% → Bonne activité
- Si "Annulées" > 15% → Attention, problème à résoudre

---

### Section 4 : Taux d'Occupation des Ressources

Barres de progression montrant l'utilisation des ressources.

#### Conteneurs
```
━━━━━━━━━━━━━━━━━━░░░░ 75%
38 / 50 conteneurs
```
**Objectif idéal** : 70-80%
- Trop bas (< 50%) → Sous-utilisation, perte de revenus
- Trop haut (> 90%) → Risque de surcharge

#### Camions
```
━━━━━━━━━━━━━━░░░░░░░░ 65%
26 / 40 camions
```

#### Chauffeurs
```
━━━━━━━━━━━━━━━━░░░░░░ 70%
35 / 50 chauffeurs
```

---

### Section 5 : Top 5 Clients

Tableau des meilleurs clients par nombre de missions.

```
┌─────────────────┬──────────┬──────────┐
│ Client          │ Type     │ Missions │
├─────────────────┼──────────┼──────────┤
│ MAERSK SA       │ Entreprise│   45    │
│ CMA CGM         │ Entreprise│   38    │
│ Amadou DIALLO   │ Particulier│  22    │
│ MSC Afrique     │ Entreprise│   19    │
│ Fatou KANE      │ Particulier│  15    │
└─────────────────┴──────────┴──────────┘
```

**Utilisation** :
- Identifier vos clients VIP
- Prioriser le service pour ces clients
- Analyser leur profil pour prospecter

---

### Section 6 : Statistiques Financières

Résumé financier complet.

```
┌────────────────────────┬──────────────────┐
│ CA Total               │ 12 500 000 FCFA │
│ Commissions            │  1 300 000 FCFA │
│ CA Net                 │ 11 200 000 FCFA │
│ CA en attente          │  2 100 000 FCFA │
│ Cautions bloquées      │  3 500 000 FCFA │
│ Coût réparations       │    750 000 FCFA │
└────────────────────────┴──────────────────┘
```

**Formules** :
- CA Net = CA Total - Commissions
- Bénéfice = CA Net - Coût réparations
- Trésorerie disponible = CA Net - Cautions bloquées

---

## Dashboard Financier

### Accès
`/dashboard/financier/`

### KPIs Financiers

#### CA Total
Somme de tous les paiements validés sur la période.

#### CA Net
CA Total - Commissions transitaires

#### CA Moyen
CA Total ÷ Nombre de paiements

**Exemple** :
```
CA Total: 12 500 000 FCFA
Paiements: 50
CA Moyen: 250 000 FCFA par mission
```

### Graphique CA par Semaine

Évolution du chiffre d'affaires sur les 8 dernières semaines.

**Utilisation** :
- Identifier les semaines les plus rentables
- Détecter les baisses anormales
- Planifier les ressources

### Top 10 Clients par CA

Classement des clients générant le plus de revenus.

**Différence avec Top 5** :
- Top 5 missions → Volume d'activité
- Top 10 CA → Valeur financière

Un client peut être dans le Top 10 CA mais pas dans le Top 5 missions (missions à forte valeur).

### Répartition CA : Entreprises vs Particuliers

Graphique montrant la part du CA par type de client.

**Exemple** :
- Entreprises : 75% du CA
- Particuliers : 25% du CA

**Stratégie** :
- Si Entreprises > 80% → Dépendance risquée, diversifier
- Si Particuliers < 10% → Opportunité de croissance

---

## Filtres et Personnalisation

### Filtres de Période

Menu déroulant en haut à droite :

```
┌─────────────────┐
│ Période:        │
│ ☐ 7 jours       │
│ ☑ 30 jours      │ ← Sélectionné
│ ☐ 90 jours      │
│ ☐ 1 an          │
│ ☐ Tout          │
└─────────────────┘
```

**Conseils** :
- **7 jours** : Suivi quotidien, détection rapide
- **30 jours** : Vue mensuelle standard
- **90 jours** : Analyse trimestrielle
- **1 an** : Tendances annuelles
- **Tout** : Vue historique complète

**Le filtre s'applique automatiquement** en sélectionnant une option.

---

## Interprétation des KPIs

### Taux de Réussite

**Formule** : (Missions terminées ÷ Total missions) × 100

**Valeurs de référence** :
- < 70% → 🔴 Problème sérieux
- 70-80% → 🟡 À améliorer
- 80-90% → 🟢 Bon
- > 90% → 🟢 Excellent

**Causes d'un faible taux** :
- Problèmes logistiques
- Mauvaise planification
- Clients peu fiables

### Taux d'Occupation

**Formule** : (Ressources utilisées ÷ Total ressources) × 100

**Valeurs de référence** :
- < 50% → Sous-utilisation
- 50-70% → Utilisation normale
- 70-85% → **Optimal**
- > 85% → Risque de surcharge

### CA en Attente

Montant des paiements non validés.

**Interprétation** :
- Élevé → Risque de trésorerie
- Faible → Bonne gestion

**Action** : Valider les paiements rapidement après retour mission.

---

## Alertes et Notifications

### Missions en Retard

**Déclenchement** : Date de départ + 23 jours

**Pénalité** : 25 000 FCFA par jour de retard

**Actions** :
1. Contacter le chauffeur immédiatement
2. Vérifier la localisation du conteneur
3. Estimer la date de retour
4. Terminer la mission dès le retour

### Cautions Non Remboursées

**Déclenchement** : Statut = "en_attente" depuis > 7 jours

**Risque** : Trésorerie bloquée

**Actions** :
1. Vérifier l'état du conteneur
2. Calculer les pénalités éventuelles
3. Rembourser ou consommer la caution
4. Valider le paiement final

---

## Export de Données

### Depuis le Dashboard

Bien que le dashboard n'ait pas de bouton d'export direct, vous pouvez :

1. **Imprimer en PDF** :
   - Clic droit → Imprimer
   - Destination : Enregistrer au format PDF

2. **Export Excel des Listes** :
   - Aller sur la liste correspondante (Missions, Paiements)
   - Cliquer sur "Export Excel" ou "Export CSV"

### Depuis les Listes

```
/missions/export/excel/  → Export Excel missions
/missions/export/csv/    → Export CSV missions
/paiements/export/excel/ → Export Excel paiements
/paiements/export/csv/   → Export CSV paiements
```

---

## FAQ

### Q1 : Pourquoi le CA affiché ne correspond pas à mes calculs ?

**R** : Le dashboard affiche uniquement les **paiements validés**. Vérifiez que tous vos paiements ont bien été validés.

### Q2 : Les graphiques ne s'affichent pas

**R** : Vérifiez votre connexion internet. Les graphiques utilisent Chart.js, chargé depuis un CDN.

**Solution hors ligne** :
```bash
# Télécharger Chart.js localement
npm install chart.js
# ou
wget https://cdn.jsdelivr.net/npm/chart.js/dist/chart.umd.min.js
```

### Q3 : Comment actualiser les données du dashboard ?

**R** : Rechargez simplement la page (F5 ou Ctrl+R). Les données sont calculées en temps réel.

### Q4 : Puis-je personnaliser les périodes de filtre ?

**R** : Actuellement, les périodes sont fixes (7, 30, 90, 365 jours). Pour une période personnalisée, exportez les données et utilisez Excel.

### Q5 : Quelle est la différence entre CA Total et CA Net ?

**R** :
- **CA Total** = Tous les paiements reçus
- **CA Net** = CA Total - Commissions transitaires

Le CA Net représente votre revenu réel.

### Q6 : Pourquoi certaines missions n'apparaissent pas dans les graphiques ?

**R** : Les graphiques utilisent les filtres de période. Une mission créée il y a 1 an n'apparaîtra pas si le filtre est sur "30 jours".

### Q7 : Comment savoir si une mission va être en retard ?

**R** : Consultez la section "Alertes". Les missions proches de la limite (> 20 jours) devraient être surveillées manuellement.

---

## Raccourcis Clavier

| Touche | Action |
|--------|--------|
| `F5` | Actualiser le dashboard |
| `Ctrl + P` | Imprimer / Exporter PDF |
| `Ctrl + F` | Rechercher dans la page |

---

## Bonnes Pratiques

### 1. Consultez le Dashboard Quotidiennement

**Routine recommandée** (chaque matin) :
- ✅ Vérifier les alertes
- ✅ Contrôler les missions en cours
- ✅ Vérifier le taux d'occupation
- ✅ Valider les paiements en attente

### 2. Analysez les Tendances Hebdomadairement

**Chaque lundi** :
- 📊 Comparer le CA de la semaine précédente
- 📈 Analyser les graphiques mensuels
- 🎯 Ajuster les objectifs si nécessaire

### 3. Rapports Mensuels

**Fin de chaque mois** :
- 📄 Générer un export Excel des missions
- 💰 Analyser le CA mensuel
- 📊 Comparer avec les objectifs

---

## Support

Pour toute question :
1. Consulter ce guide
2. Vérifier la documentation technique : `OPTIMISATIONS_PERFORMANCES.md`
3. Contacter le support technique

---

**Version**: 1.0
**Date**: 2025-12-21
**Auteur**: Système de Transport
