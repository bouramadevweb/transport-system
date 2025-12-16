# Améliorations du modèle Mission

## 📋 Résumé des modifications

### ✅ Nouveaux champs

1. **itineraire** (TextField)
   - Description détaillée de l'itinéraire de la mission
   - Valeur par défaut: "Itinéraire à compléter"
   - Généré automatiquement lors de la création du contrat
   - Comprend: origine, destination, camion, chauffeur, dates, etc.

### ✅ Champs améliorés

1. **origine** et **destination**
   - Taille augmentée de 50 à 200 caractères
   - Permettent des adresses plus détaillées
   - Validation: ne peuvent pas être vides ou contenir seulement des espaces

### ✅ Validations ajoutées

#### Dans Mission.clean():

1. **Champs obligatoires**
   - Origine ne peut pas être vide
   - Destination ne peut pas être vide
   - Itinéraire ne peut pas être vide

2. **Validation des dates par rapport au contrat**
   - date_depart >= contrat.date_debut
   - date_retour >= date_depart (si date_retour existe)
   - Avertissement si date_retour > contrat.date_limite_retour (pénalités)

#### Dans Mission.terminer_mission():

1. **Validation de la date de retour**
   - date_retour >= date_depart
   - Calcul automatique des pénalités si retard
   - Erreur bloquante avec calcul de la pénalité (25 000 FCFA/jour)

### ✅ Formulaire amélioré

**MissionForm**:
- Widget Textarea pour l'itinéraire (6 lignes)
- Widget DateInput avec type="date" pour les dates
- Validation du formulaire appelle Mission.clean()
- Messages d'erreur clairs pour l'utilisateur

### ✅ Signal mis à jour

**creer_workflow_complet_contrat** (signals.py):
- Génère automatiquement un itinéraire détaillé
- Inclut toutes les informations pertinentes
- Format structuré et lisible

### ✅ Commande de gestion

**update_mission_itineraires**:
- Met à jour les missions existantes sans itinéraire
- Génère des itinéraires à partir des données existantes
- Usage: `python manage.py update_mission_itineraires`

## 🎯 Avantages

1. **Traçabilité complète**
   - Itinéraire détaillé pour chaque mission
   - Historique des trajets

2. **Prévention des erreurs**
   - Dates validées par rapport au contrat
   - Impossible de créer une mission avec des dates incohérentes

3. **Gestion des pénalités**
   - Calcul automatique des pénalités de retard
   - Alerte avant validation d'une date en retard

4. **Cohérence des données**
   - Dates de mission alignées avec le contrat
   - Validation à plusieurs niveaux (modèle, formulaire)

5. **Expérience utilisateur**
   - Messages d'erreur explicites
   - Itinéraire pré-rempli lors de la création
   - Interface intuitive pour les dates

## 📊 Workflow actuel

```
Création d'un Contrat
    ↓
Signal creer_workflow_complet_contrat
    ↓
Création Mission avec:
    - date_depart = contrat.date_debut
    - origine/destination du contrat
    - itineraire généré automatiquement
    - Validation des dates ✓
    ↓
Utilisateur peut modifier/compléter l'itinéraire
    ↓
Terminer la mission
    - Validation date_retour ✓
    - Calcul pénalités si retard ✓
    - Statut = 'terminée'
```

## 🔧 Migrations

- **0007_mission_itineraire**: Ajoute le champ itinéraire
- Missions existantes mises à jour avec `update_mission_itineraires`

## 📝 Notes importantes

1. Le champ itinéraire accepte blank=True pour faciliter la migration
2. La validation vérifie que l'itinéraire n'est pas vide lors de la sauvegarde
3. La méthode save() peut accepter `validate=False` pour sauter la validation (utilisé en migration)
4. Les pénalités sont calculées automatiquement: 25 000 FCFA/jour de retard
5. La date de retour peut dépasser la limite du contrat mais affiche un avertissement avec calcul de pénalité
