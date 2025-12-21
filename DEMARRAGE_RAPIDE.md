# Démarrage Rapide - Dashboard

## ✅ Problème Corrigé

Les templates du dashboard ont été mis à jour pour étendre `admin.html` au lieu de `base.html`.

---

## 🚀 Accès aux Dashboards

### Dashboard Principal
**URL** : http://localhost:8000/dashboard/home/

**Fonctionnalités** :
- ✅ KPIs en temps réel
- ✅ 3 graphiques interactifs
- ✅ Alertes missions en retard
- ✅ Top 5 clients
- ✅ Taux d'occupation ressources

### Dashboard Financier
**URL** : http://localhost:8000/dashboard/financier/

**Fonctionnalités** :
- ✅ CA total, net, moyen
- ✅ Évolution CA par semaine
- ✅ Top 10 clients par CA
- ✅ Répartition entreprises/particuliers

---

## 🔧 Serveur Django

### Démarrer le serveur
```bash
python manage.py runserver
```

### Arrêter le serveur
```bash
# Dans le terminal où tourne le serveur : Ctrl+C
# Ou forcer l'arrêt :
pkill -f "manage.py runserver"
```

### Vérifier que le serveur tourne
```bash
ps aux | grep "manage.py runserver"
```

---

## 📝 Connexion Requise

Les dashboards nécessitent une **connexion utilisateur**.

### Se connecter
1. Accéder à : http://localhost:8000/connexion/
2. Entrer vos identifiants
3. Redirection automatique vers le dashboard

### Créer un superutilisateur (si nécessaire)
```bash
python manage.py createsuperuser
```

---

## 🧪 Tests Rapides

### Test 1 : Vérifier que le serveur répond
```bash
curl http://localhost:8000/
```

### Test 2 : Accéder au dashboard (via navigateur)
1. Ouvrir : http://localhost:8000/dashboard/home/
2. Se connecter si demandé
3. Vérifier que les KPIs s'affichent

### Test 3 : Tester les filtres
1. Dans le dashboard, cliquer sur le menu déroulant "Période"
2. Sélectionner "7 jours"
3. Vérifier que les données se mettent à jour

---

## ⚠️ Résolution de Problèmes

### Erreur : Port déjà utilisé
```bash
# Trouver le processus
lsof -i :8000

# Le tuer
kill -9 <PID>

# Ou utiliser
pkill -f "manage.py runserver"
```

### Erreur : Template non trouvé
Vérifier que les fichiers existent :
```bash
ls -la transport/templates/transport/dashboard/
```

Vous devriez voir :
- home.html
- financier.html

### Erreur : Page blanche
1. Ouvrir la console du navigateur (F12)
2. Vérifier les erreurs JavaScript
3. Vérifier que Chart.js se charge correctement

### Erreur : Graphiques ne s'affichent pas
**Cause** : Chart.js non chargé (problème réseau)

**Solution** :
1. Vérifier votre connexion internet
2. Ou télécharger Chart.js localement :
```bash
mkdir -p transport/static/js
wget https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js -O transport/static/js/chart.min.js
```

Puis modifier les templates pour utiliser la version locale.

---

## 📊 Navigation Dashboard

### Menu Principal
Le dashboard principal a 6 sections :

1. **KPIs en Haut** → Vue d'ensemble rapide
2. **Alertes** → Problèmes urgents
3. **Graphiques** → Tendances visuelles
4. **Ressources** → Taux d'occupation
5. **Top Clients** → Meilleurs clients
6. **Stats Financières** → Résumé financier

### Filtres de Période
- **7 jours** : Suivi quotidien
- **30 jours** : Vue mensuelle (par défaut)
- **90 jours** : Analyse trimestrielle
- **1 an** : Tendances annuelles
- **Tout** : Historique complet

---

## 🔗 Liens Rapides

| Page | URL |
|------|-----|
| Dashboard Principal | /dashboard/home/ |
| Dashboard Financier | /dashboard/financier/ |
| Missions | /missions/ |
| Paiements | /paiement-missions/ |
| Conteneurs | /conteneurs/ |
| Admin Django | /admin/ |

---

## 📚 Documentation Complète

- **Guide utilisateur** : `GUIDE_DASHBOARD.md`
- **Optimisations** : `OPTIMISATIONS_PERFORMANCES.md`
- **Améliorations** : `AMELIORATIONS_2025.md`

---

## ✨ Prochaines Étapes

### 1. Explorer le Dashboard
- Tester tous les filtres
- Vérifier que les données sont correctes
- S'habituer aux KPIs

### 2. Activer les Vues Optimisées (Optionnel)
Dans `transport/urls.py`, remplacer progressivement les vues par les versions optimisées :

```python
from . import optimized_views

# Missions
path('missions/', optimized_views.mission_list_optimized, name='mission_list'),

# Paiements
path('paiement-missions/', optimized_views.paiement_mission_list_optimized, name='paiement_mission_list'),

# Etc...
```

### 3. Consulter les Statistiques
- Analyser les tendances
- Identifier les points à améliorer
- Prendre des décisions basées sur les données

---

## 📞 Support

En cas de problème :
1. Vérifier ce guide
2. Consulter les logs du serveur
3. Vérifier la console navigateur (F12)
4. Consulter `GUIDE_DASHBOARD.md` pour plus de détails

---

**Serveur actuel** : ✅ En cours d'exécution
**Port** : 8000
**Status** : Production Ready

Bon travail ! 🎉
