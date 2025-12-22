# Système de Gestion des Salaires

## Vue d'ensemble

Le système de gestion des salaires permet de gérer la paie des chauffeurs et des autres employés de l'entreprise de transport.

## Fonctionnalités

### 1. Gestion des salaires

#### Création d'un salaire
- Sélection du type d'employé (Chauffeur ou Autre employé)
- Sélection de la période (mois et année)
- Définition du salaire de base
- Calcul des heures supplémentaires avec taux horaire
- Choix du mode de paiement
- Ajout de notes optionnelles

#### Workflow des statuts
1. **Brouillon** : Salaire créé mais pas encore validé
2. **Validé** : Salaire approuvé, prêt au paiement
3. **Payé** : Paiement effectué avec date enregistrée

### 2. Primes

Les primes peuvent être ajoutées à un salaire :
- Prime de rendement
- Prime exceptionnelle
- Prime de transport
- Etc.

Chaque prime comprend :
- Type de prime
- Montant
- Description optionnelle

### 3. Déductions

Les déductions peuvent être appliquées sur un salaire :
- Avances sur salaire
- Impôts et taxes
- Cotisations sociales
- Retenues diverses

Chaque déduction comprend :
- Type de déduction
- Montant
- Description optionnelle

### 4. Calcul automatique

Le système calcule automatiquement :
- **Montant heures supplémentaires** = Heures supp × Taux horaire
- **Total primes** = Somme de toutes les primes
- **Total déductions** = Somme de toutes les déductions
- **Salaire brut** = Salaire base + Heures supp + Primes
- **Salaire net** = Salaire brut - Déductions

## Accès au système

### Menu
Le système est accessible depuis le menu principal :
- **Finance** → **Gestion des Salaires**

### URL
- Liste des salaires : `/salaires/`
- Créer un salaire : `/salaires/create/`
- Détails d'un salaire : `/salaires/<pk>/`
- Modifier un salaire : `/salaires/<pk>/update/`

## Permissions

Accès réservé aux rôles :
- **ADMIN**
- **COMPTABLE**

## Structure des données

### Modèle Salaire

```python
class Salaire(models.Model):
    pk_salaire = CharField(primary_key=True)
    chauffeur = ForeignKey(Chauffeur, null=True, blank=True)  # Exclusif avec utilisateur
    utilisateur = ForeignKey(Utilisateur, null=True, blank=True)  # Exclusif avec chauffeur
    mois = IntegerField(choices=MOIS_CHOICES)
    annee = IntegerField()
    salaire_base = DecimalField(max_digits=10, decimal_places=2)
    heures_supplementaires = DecimalField(max_digits=6, decimal_places=2, default=0)
    taux_heure_supp = DecimalField(max_digits=10, decimal_places=2, default=0)
    total_primes = DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = DecimalField(max_digits=10, decimal_places=2, default=0)
    salaire_net = DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = CharField(choices=['brouillon', 'valide', 'paye'], default='brouillon')
    date_paiement = DateField(null=True, blank=True)
    mode_paiement = CharField(choices=['especes', 'virement', 'cheque', 'mobile'], null=True)
    notes = TextField(blank=True)
```

### Modèle Prime

```python
class Prime(models.Model):
    pk_prime = CharField(primary_key=True)
    salaire = ForeignKey(Salaire, on_delete=CASCADE, related_name='primes')
    type_prime = CharField(max_length=100)
    montant = DecimalField(max_digits=10, decimal_places=2)
    description = TextField(blank=True)
```

### Modèle Deduction

```python
class Deduction(models.Model):
    pk_deduction = CharField(primary_key=True)
    salaire = ForeignKey(Salaire, on_delete=CASCADE, related_name='deductions')
    type_deduction = CharField(max_length=100)
    montant = DecimalField(max_digits=10, decimal_places=2)
    description = TextField(blank=True)
```

## Routes disponibles

### Gestion des salaires
- `GET /salaires/` - Liste de tous les salaires
- `GET /salaires/create/` - Formulaire de création
- `POST /salaires/create/` - Créer un nouveau salaire
- `GET /salaires/<pk>/` - Détails d'un salaire
- `GET /salaires/<pk>/update/` - Formulaire de modification
- `POST /salaires/<pk>/update/` - Modifier un salaire
- `GET /salaires/<pk>/delete/` - Confirmation de suppression
- `POST /salaires/<pk>/delete/` - Supprimer un salaire
- `GET /salaires/<pk>/valider/` - Valider un salaire (brouillon → validé)
- `GET /salaires/<pk>/payer/` - Formulaire de paiement
- `POST /salaires/<pk>/payer/` - Marquer comme payé (validé → payé)

### Gestion des primes
- `POST /salaires/<salaire_pk>/primes/add/` - Ajouter une prime
- `GET /primes/<pk>/delete/` - Supprimer une prime

### Gestion des déductions
- `POST /salaires/<salaire_pk>/deductions/add/` - Ajouter une déduction
- `GET /deductions/<pk>/delete/` - Supprimer une déduction

## Templates créés

1. **salaire_list.html** - Liste des salaires avec filtres et statistiques
2. **salaire_form.html** - Formulaire de création/modification
3. **salaire_detail.html** - Détails avec primes, déductions et actions
4. **salaire_confirm_delete.html** - Confirmation de suppression
5. **salaire_payer.html** - Formulaire de paiement

## Fonctionnalités de filtrage

La liste des salaires peut être filtrée par :
- **Mois** : Janvier à Décembre
- **Année** : Années disponibles dans la base
- **Statut** : Brouillon, Validé, Payé
- **Employé** : Recherche par nom ou email

## Statistiques affichées

Sur la page de liste :
- **Total Salaires** : Nombre total de salaires enregistrés
- **Total Payé** : Somme des salaires payés (en FCFA)
- **En Attente** : Nombre de salaires en statut "brouillon"
- **Validés** : Nombre de salaires en statut "validé"

## Contraintes de sécurité

1. **Contrainte d'unicité** : Un employé ne peut avoir qu'un seul salaire par période (mois + année)
2. **Contrainte de validation** : Un salaire doit être lié soit à un chauffeur, soit à un utilisateur (pas les deux)
3. **Mise à jour automatique** : Les totaux de primes et déductions sont recalculés automatiquement lors de l'ajout/suppression

## Migration

Migration créée : `0016_gestion_paie.py`
- Création des tables Salaire, Prime, Deduction
- Ajout des index sur (mois, annee) et statut
- Contrainte de validation pour chauffeur/utilisateur

## Fichiers modifiés/créés

### Backend
- `transport/models.py` - Ajout des modèles Salaire, Prime, Deduction
- `transport/salary_views.py` - 11 vues pour la gestion complète
- `transport/migrations/0016_gestion_paie.py` - Migration de base de données

### Frontend
- `transport/templates/transport/salaires/salaire_list.html`
- `transport/templates/transport/salaires/salaire_form.html`
- `transport/templates/transport/salaires/salaire_detail.html`
- `transport/templates/transport/salaires/salaire_confirm_delete.html`
- `transport/templates/transport/salaires/salaire_payer.html`

### Configuration
- `transport/urls.py` - Ajout de 11 routes pour les salaires
- `transport/templates/admin.html` - Ajout du lien dans le menu Finance

## Utilisation

### Créer un salaire

1. Aller dans **Finance** → **Gestion des Salaires**
2. Cliquer sur **Nouveau salaire**
3. Sélectionner le type d'employé (Chauffeur ou Employé)
4. Choisir l'employé concerné
5. Définir la période (mois et année)
6. Renseigner le salaire de base
7. (Optionnel) Ajouter des heures supplémentaires avec le taux horaire
8. (Optionnel) Choisir le mode de paiement
9. (Optionnel) Ajouter des notes
10. Cliquer sur **Créer le salaire**

### Ajouter des primes et déductions

1. Ouvrir les détails d'un salaire
2. Dans la section **Primes**, cliquer sur **Ajouter**
3. Renseigner le type, montant et description
4. Dans la section **Déductions**, cliquer sur **Ajouter**
5. Renseigner le type, montant et description

### Valider et payer un salaire

1. Ouvrir les détails d'un salaire en statut "Brouillon"
2. Cliquer sur **Valider ce salaire**
3. Le statut passe à "Validé"
4. Cliquer sur **Marquer comme payé**
5. Renseigner la date et le mode de paiement
6. Confirmer le paiement
7. Le statut passe à "Payé"

## Notes importantes

- ⚠️ Un salaire ne peut être modifié que s'il est en statut "Brouillon"
- ⚠️ Les salaires "Payés" ne peuvent plus être modifiés
- ⚠️ La suppression d'un salaire supprime également toutes ses primes et déductions
- ⚠️ Il est recommandé de vérifier toutes les primes et déductions avant de valider un salaire
- ℹ️ Le salaire net est recalculé automatiquement à chaque modification

## Exemple de flux complet

```
1. Créer un salaire pour "Jean DUPONT" - Janvier 2025
   - Salaire base: 500,000 FCFA
   - Heures supp: 10h × 5,000 FCFA = 50,000 FCFA
   - Statut: Brouillon

2. Ajouter des primes:
   - Prime de rendement: 30,000 FCFA
   - Prime de transport: 20,000 FCFA
   - Total primes: 50,000 FCFA

3. Ajouter des déductions:
   - Avance: 100,000 FCFA
   - Cotisations: 25,000 FCFA
   - Total déductions: 125,000 FCFA

4. Calcul automatique:
   - Salaire brut = 500,000 + 50,000 + 50,000 = 600,000 FCFA
   - Salaire net = 600,000 - 125,000 = 475,000 FCFA

5. Valider le salaire → Statut: Validé

6. Enregistrer le paiement:
   - Date: 05/02/2025
   - Mode: Virement bancaire
   - Statut: Payé
```

## Assistance

Pour toute question ou problème, contactez l'administrateur système.

---

**Version** : 1.0
**Date de création** : 22 Décembre 2025
**Auteur** : Système de Gestion Transport
