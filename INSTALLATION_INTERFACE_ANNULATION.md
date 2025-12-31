# Installation Interface d'Annulation

**Date:** 30 décembre 2024
**Statut:** En cours d'installation

---

## ✅ CE QUI A ÉTÉ FAIT

### 1. Backend Complet ✅

- ✅ Champ `statut` dans ContratTransport
- ✅ Champ `statut_paiement` dans PaiementMission
- ✅ Méthode `annuler_contrat()` implémentée
- ✅ Méthode `annuler_mission()` améliorée
- ✅ Protection `delete_contrat()` activée
- ✅ Migrations appliquées
- ✅ Tests réussis (100%)

### 2. Vues d'Annulation Créées ✅

**Fichier:** `transport/views/annulation_views.py`

Vues créées:
- `annuler_contrat_view(request, pk)` - Annuler un contrat avec UI
- `annuler_mission_view(request, pk)` - Annuler une mission avec UI
- `contrats_annules_list(request)` - Liste des contrats annulés
- `missions_annulees_list(request)` - Liste des missions annulées

---

## 🚧 À FAIRE POUR ACTIVER L'INTERFACE

### Étape 1: Ajouter les URLs

**Fichier à modifier:** `transport/urls.py`

```python
# Ajouter ces imports en haut du fichier
from .views.annulation_views import (
    annuler_contrat_view,
    annuler_mission_view,
    contrats_annules_list,
    missions_annulees_list,
)

# Ajouter ces URLs dans urlpatterns
urlpatterns = [
    # ... URLs existantes ...

    # Annulation de contrats et missions
    path('contrats/<str:pk>/annuler/', annuler_contrat_view, name='annuler_contrat'),
    path('missions/<str:pk>/annuler/', annuler_mission_view, name='annuler_mission'),
    path('contrats/annules/', contrats_annules_list, name='contrats_annules_list'),
    path('missions/annulees/', missions_annulees_list, name='missions_annulees_list'),
]
```

---

### Étape 2: Exporter les Vues

**Fichier à modifier:** `transport/views/__init__.py`

```python
# Ajouter cet import avec les autres
from .annulation_views import (
    annuler_contrat_view,
    annuler_mission_view,
    contrats_annules_list,
    missions_annulees_list,
)
```

---

### Étape 3: Créer les Templates

#### Template 1: `transport/templates/transport/contrat/annuler_confirm.html`

```django
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h4 class="mb-0">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Confirmation d'Annulation de Contrat
                    </h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Attention:</strong> Cette action va annuler le contrat et tous les objets liés.
                        Les données seront conservées pour traçabilité mais marquées comme annulées.
                    </div>

                    <h5>Informations du Contrat</h5>
                    <table class="table table-sm">
                        <tr>
                            <th width="200">Numéro BL:</th>
                            <td><strong>{{ contrat.numero_bl }}</strong></td>
                        </tr>
                        <tr>
                            <th>Client:</th>
                            <td>{{ contrat.client.nom }}</td>
                        </tr>
                        <tr>
                            <th>Transitaire:</th>
                            <td>{{ contrat.transitaire.nom }}</td>
                        </tr>
                        <tr>
                            <th>Montant Total:</th>
                            <td><strong>{{ contrat.montant_total }} CFA</strong></td>
                        </tr>
                        <tr>
                            <th>Date Début:</th>
                            <td>{{ contrat.date_debut|date:"d/m/Y" }}</td>
                        </tr>
                    </table>

                    <hr>

                    <h5>Objets qui seront Annulés</h5>
                    <div class="row text-center mb-3">
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6>Missions</h6>
                                    <h3 class="text-primary">{{ nb_missions }}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6>Cautions</h6>
                                    <h3 class="text-warning">{{ nb_cautions }}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6>Paiements</h6>
                                    <h3 class="text-info">{{ nb_paiements }}</h3>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="alert alert-info">
                        <i class="fas fa-check-circle me-2"></i>
                        <strong>Traçabilité:</strong> Tous ces objets seront conservés en base de données
                        avec un statut "annulé" pour permettre l'audit et la traçabilité complète.
                    </div>

                    <form method="post">
                        {% csrf_token %}

                        <div class="mb-3">
                            <label for="raison" class="form-label">
                                <strong>Raison de l'Annulation *</strong>
                            </label>
                            <textarea
                                name="raison"
                                id="raison"
                                class="form-control"
                                rows="3"
                                required
                                placeholder="Ex: Client a annulé la commande, Problème technique, etc."
                            ></textarea>
                            <small class="text-muted">
                                Cette raison sera enregistrée dans le commentaire du contrat pour traçabilité.
                            </small>
                        </div>

                        <div class="d-flex justify-content-between">
                            <a href="{% url 'contrat_list' %}" class="btn btn-secondary">
                                <i class="fas fa-times me-2"></i>Annuler
                            </a>
                            <button type="submit" class="btn btn-danger">
                                <i class="fas fa-ban me-2"></i>Confirmer l'Annulation
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### Template 2: `transport/templates/transport/missions/annuler_confirm.html`

```django
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h4 class="mb-0">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Confirmation d'Annulation de Mission
                    </h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Attention:</strong> Cette action va annuler la mission et tous les objets liés.
                    </div>

                    <h5>Informations de la Mission</h5>
                    <table class="table table-sm">
                        <tr>
                            <th width="200">Origine:</th>
                            <td>{{ mission.origine }}</td>
                        </tr>
                        <tr>
                            <th>Destination:</th>
                            <td>{{ mission.destination }}</td>
                        </tr>
                        <tr>
                            <th>Date Départ:</th>
                            <td>{{ mission.date_depart|date:"d/m/Y" }}</td>
                        </tr>
                        <tr>
                            <th>Contrat:</th>
                            <td>{{ mission.contrat.numero_bl }}</td>
                        </tr>
                    </table>

                    <hr>

                    <h5>Objets qui seront Annulés</h5>
                    <div class="row text-center mb-3">
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6>Cautions</h6>
                                    <h3 class="text-warning">{{ nb_cautions }}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6>Paiements</h6>
                                    <h3 class="text-info">{{ nb_paiements }}</h3>
                                </div>
                            </div>
                        </div>
                    </div>

                    <form method="post">
                        {% csrf_token %}

                        <div class="mb-3">
                            <label for="raison" class="form-label">
                                <strong>Raison de l'Annulation *</strong>
                            </label>
                            <textarea
                                name="raison"
                                id="raison"
                                class="form-control"
                                rows="3"
                                required
                                placeholder="Ex: Problème technique, Annulation client, etc."
                            ></textarea>
                        </div>

                        <div class="d-flex justify-content-between">
                            <a href="{% url 'mission_list' %}" class="btn btn-secondary">
                                <i class="fas fa-times me-2"></i>Annuler
                            </a>
                            <button type="submit" class="btn btn-danger">
                                <i class="fas fa-ban me-2"></i>Confirmer l'Annulation
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### Étape 4: Ajouter les Boutons dans les Listes

#### Dans `contrat_list.html`:

```django
<!-- Ajouter ce bouton dans la colonne Actions -->
{% if contrat.statut == 'actif' %}
    <a href="{% url 'annuler_contrat' contrat.pk_contrat %}"
       class="btn btn-sm btn-warning"
       title="Annuler ce contrat">
        <i class="fas fa-ban"></i> Annuler
    </a>
{% else %}
    <span class="badge bg-secondary">{{ contrat.get_statut_display }}</span>
{% endif %}
```

#### Dans `mission_list.html`:

```django
<!-- Ajouter ce bouton dans la colonne Actions -->
{% if mission.statut == 'en cours' %}
    <a href="{% url 'annuler_mission' mission.pk_mission %}"
       class="btn btn-sm btn-warning"
       title="Annuler cette mission">
        <i class="fas fa-ban"></i> Annuler
    </a>
{% elif mission.statut == 'annulée' %}
    <span class="badge bg-danger">Annulée</span>
{% endif %}
```

---

## 🎯 UTILISATION UNE FOIS ACTIVÉ

### Annuler un Contrat via l'Interface

1. Aller sur la liste des contrats
2. Cliquer sur le bouton "Annuler" à côté du contrat
3. Remplir la raison de l'annulation
4. Confirmer

**Résultat:**
- Contrat: statut = 'annule'
- Missions: toutes annulées
- Cautions: toutes annulées
- Paiements: tous annulés
- Message de confirmation affiché

---

### Voir les Contrats Annulés

**URL:** `/contrats/annules/`

Liste tous les contrats annulés avec:
- Numéro BL
- Client
- Date d'annulation
- Raison
- Nombre de missions associées

---

## 📋 CHECKLIST D'INSTALLATION

- [ ] Modifier `transport/urls.py` (ajouter les 4 URLs)
- [ ] Modifier `transport/views/__init__.py` (exporter les vues)
- [ ] Créer `transport/templates/transport/contrat/annuler_confirm.html`
- [ ] Créer `transport/templates/transport/missions/annuler_confirm.html`
- [ ] Modifier `contrat_list.html` (ajouter bouton Annuler)
- [ ] Modifier `mission_list.html` (ajouter bouton Annuler)
- [ ] Tester l'annulation d'un contrat test
- [ ] Tester l'annulation d'une mission test
- [ ] Vérifier les listes d'annulations

---

## 🚀 COMMANDES DE TEST

```bash
# Démarrer le serveur
python manage.py runserver

# Tester les URLs
# http://127.0.0.1:8000/contrats/<pk>/annuler/
# http://127.0.0.1:8000/missions/<pk>/annuler/
# http://127.0.0.1:8000/contrats/annules/
# http://127.0.0.1:8000/missions/annulees/
```

---

## ✅ RÉSUMÉ

**Backend:** ✅ Complet et testé
**Vues:** ✅ Créées
**Templates:** 📋 Instructions fournies
**URLs:** 📋 Instructions fournies

**Une fois les étapes 1-4 complétées, l'interface sera opérationnelle!**

---

**Document créé le:** 30 décembre 2024
**Statut:** Instructions prêtes
**Action requise:** Compléter les étapes 1-4
