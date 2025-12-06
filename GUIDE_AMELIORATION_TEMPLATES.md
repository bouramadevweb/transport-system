# 🚀 Guide Rapide: Améliorer vos Templates

Ce guide vous explique comment appliquer rapidement les améliorations modernes à vos templates de liste.

---

## 📦 Fichiers Inclus

Tous les fichiers nécessaires sont déjà créés:

```
transport/
├── static/
│   ├── css/
│   │   └── table-styles.css          # Styles globaux
│   └── js/
│       └── table-enhancements.js     # Fonctionnalités JS
└── templates/
    ├── admin.html                     # Template de base (mis à jour)
    └── transport/
        └── prestations/
            └── prestation_transport_list.html  # Exemple complet
```

---

## ⚡ Démarrage Rapide (3 étapes)

### Étape 1: Copier la structure HTML

Ouvrez votre template de liste (ex: `camion_list.html`) et remplacez le contenu par cette structure:

```django
{% extends "admin.html" %}

{% block page_title %}Liste des [Votre Modèle] | Gestion Transport{% endblock %}

{% block title %}Liste des [Votre Modèle]{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- COPIEZ DEPUIS ICI -->

    <!-- 1. Header avec recherche -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
        <h2 class="mb-0">
            <i class="fas fa-[VOTRE-ICONE] text-primary me-2"></i>
            {{ title }}
        </h2>
        <div class="d-flex gap-2 align-items-center flex-wrap">
            <!-- Barre de recherche -->
            <div class="input-group" style="max-width: 300px;">
                <span class="input-group-text bg-white border-end-0">
                    <i class="fas fa-search text-muted"></i>
                </span>
                <input type="text" id="searchInput" class="form-control border-start-0"
                       placeholder="Rechercher...">
            </div>
            <!-- Export CSV -->
            <button class="btn btn-outline-success btn-sm" onclick="exportToCSV('nom_fichier')"
                    title="Exporter en CSV">
                <i class="fas fa-file-csv me-1"></i> CSV
            </button>
            <!-- Bouton Nouveau -->
            <a href="{% url '[VOTRE_URL_CREATE]' %}" class="btn btn-primary">
                <i class="fas fa-plus me-1"></i> Nouveau [Modèle]
            </a>
        </div>
    </div>

    <!-- 2. Statistiques (OPTIONNEL) -->
    <div class="row mb-4">
        <div class="col-md-4 col-sm-6 mb-3">
            <div class="card border-primary shadow-sm h-100">
                <div class="card-body text-center">
                    <i class="fas fa-[ICONE] fa-2x text-primary mb-2"></i>
                    <h3 class="text-primary mb-1">{{ objects.count }}</h3>
                    <p class="text-muted mb-0 small">Total</p>
                </div>
            </div>
        </div>
        <!-- Ajoutez d'autres cartes si nécessaire -->
    </div>

    <!-- 3. Table -->
    {% if objects %}
    <div class="card shadow-sm border-0">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0" id="[nomModele]Table">
                    <thead class="table-light">
                        <tr>
                            <th class="sortable" data-column="0">
                                <i class="fas fa-[ICONE] me-2"></i>Colonne 1
                                <i class="fas fa-sort sort-icon"></i>
                            </th>
                            <!-- Ajoutez vos colonnes -->
                            <th class="text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for obj in objects %}
                        <tr>
                            <td>
                                <strong>{{ obj.champ }}</strong><br>
                                <small class="text-muted">{{ obj.sous_info }}</small>
                            </td>
                            <!-- Vos données -->
                            <td class="text-center">
                                <div class="btn-group" role="group">
                                    <a href="{% url '[URL_UPDATE]' obj.pk %}"
                                       class="btn btn-sm btn-outline-warning"
                                       title="Modifier">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <a href="{% url '[URL_DELETE]' obj.pk %}"
                                       class="btn btn-sm btn-outline-danger"
                                       onclick="return confirm('Êtes-vous sûr?')"
                                       title="Supprimer">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    {% else %}
    <div class="alert alert-info shadow-sm">
        <i class="fas fa-info-circle me-2"></i>
        Aucun élément. <a href="{% url '[URL_CREATE]' %}" class="alert-link">Ajouter le premier</a>
    </div>
    {% endif %}

    <!-- JUSQU'ICI -->
</div>
{% endblock %}
```

### Étape 2: Personnaliser

Remplacez les placeholders:
- `[Votre Modèle]` → "Camions", "Chauffeurs", etc.
- `[VOTRE-ICONE]` → "truck", "user", "box", etc. ([Liste d'icônes](https://fontawesome.com/search?o=r&m=free))
- `[VOTRE_URL_CREATE]` → "create_camion", etc.
- `[nomModele]` → "camion", "chauffeur", etc.

### Étape 3: Ajouter JS (si statistiques)

Si vous avez des statistiques à calculer, ajoutez avant `{% endblock %}`:

```django
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Exemple: calculer le total de la colonne 3
    calculateColumnStatistics(
        '[nomModele]Table',    // ID de la table
        [3],                   // Index des colonnes à totaliser
        ['totalMontant']       // IDs des éléments <h3> à mettre à jour
    );
});
</script>
```

---

## 📖 Exemples Concrets

### Exemple 1: Liste des Camions

```django
{% extends "admin.html" %}

{% block title %}Liste des Camions{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
        <h2 class="mb-0">
            <i class="fas fa-truck text-primary me-2"></i>
            {{ title }}
        </h2>
        <div class="d-flex gap-2">
            <div class="input-group" style="max-width: 300px;">
                <span class="input-group-text bg-white border-end-0">
                    <i class="fas fa-search text-muted"></i>
                </span>
                <input type="text" id="searchInput" class="form-control border-start-0"
                       placeholder="Rechercher...">
            </div>
            <button class="btn btn-outline-success btn-sm" onclick="exportToCSV('camions')">
                <i class="fas fa-file-csv me-1"></i> CSV
            </button>
            <a href="{% url 'create_camion' %}" class="btn btn-primary">
                <i class="fas fa-plus me-1"></i> Nouveau camion
            </a>
        </div>
    </div>

    <!-- Statistiques -->
    <div class="row mb-4">
        <div class="col-md-4 mb-3">
            <div class="card border-primary shadow-sm">
                <div class="card-body text-center">
                    <i class="fas fa-truck fa-2x text-primary mb-2"></i>
                    <h3 class="text-primary mb-1">{{ camions.count }}</h3>
                    <p class="text-muted mb-0 small">Total camions</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="card border-success shadow-sm">
                <div class="card-body text-center">
                    <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
                    <h3 class="text-success mb-1">{{ camions_disponibles }}</h3>
                    <p class="text-muted mb-0 small">Disponibles</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="card border-warning shadow-sm">
                <div class="card-body text-center">
                    <i class="fas fa-wrench fa-2x text-warning mb-2"></i>
                    <h3 class="text-warning mb-1">{{ camions_reparation }}</h3>
                    <p class="text-muted mb-0 small">En réparation</p>
                </div>
            </div>
        </div>
    </div>

    {% if camions %}
    <div class="card shadow-sm border-0">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0" id="camionsTable">
                    <thead class="table-light">
                        <tr>
                            <th class="sortable" data-column="0">
                                <i class="fas fa-hashtag me-2"></i>Immatriculation
                                <i class="fas fa-sort sort-icon"></i>
                            </th>
                            <th class="sortable" data-column="1">
                                <i class="fas fa-tag me-2"></i>Modèle
                                <i class="fas fa-sort sort-icon"></i>
                            </th>
                            <th class="sortable" data-column="2">
                                <i class="fas fa-info-circle me-2"></i>Statut
                                <i class="fas fa-sort sort-icon"></i>
                            </th>
                            <th class="text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for camion in camions %}
                        <tr>
                            <td>
                                <strong>{{ camion.immatriculation }}</strong>
                            </td>
                            <td>{{ camion.modele }}</td>
                            <td>
                                {% if camion.est_disponible %}
                                    <span class="badge bg-success">Disponible</span>
                                {% else %}
                                    <span class="badge bg-warning">Occupé</span>
                                {% endif %}
                            </td>
                            <td class="text-center">
                                <div class="btn-group">
                                    <a href="{% url 'update_camion' camion.pk %}"
                                       class="btn btn-sm btn-outline-warning">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <a href="{% url 'delete_camion' camion.pk %}"
                                       class="btn btn-sm btn-outline-danger"
                                       onclick="return confirm('Supprimer ce camion?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    {% else %}
    <div class="alert alert-info shadow-sm">
        <i class="fas fa-info-circle me-2"></i>
        Aucun camion. <a href="{% url 'create_camion' %}">Ajouter le premier</a>
    </div>
    {% endif %}
</div>
{% endblock %}
```

---

## 🎨 Cheat Sheet: Icônes par Modèle

| Modèle | Icône FontAwesome |
|--------|-------------------|
| Camions | `fa-truck` |
| Chauffeurs | `fa-user-tie` |
| Clients | `fa-user` |
| Transitaires | `fa-dolly` |
| Conteneurs | `fa-box` |
| Contrats | `fa-file-contract` |
| Missions | `fa-route` |
| Paiements | `fa-credit-card` |
| Cautions | `fa-shield-alt` |
| Prestations | `fa-file-invoice` |
| Réparations | `fa-wrench` |
| Entreprises | `fa-building` |
| Fournisseurs | `fa-store` |

[Rechercher plus d'icônes](https://fontawesome.com/search?o=r&m=free)

---

## 🎯 Badges de Statut

```html
<!-- Succès / Validé / Actif -->
<span class="badge bg-success">Statut</span>

<!-- En attente / Warning -->
<span class="badge bg-warning">Statut</span>

<!-- Erreur / Annulé -->
<span class="badge bg-danger">Statut</span>

<!-- Info / En cours -->
<span class="badge bg-info">Statut</span>

<!-- Secondaire / Inactif -->
<span class="badge bg-secondary">Statut</span>
```

---

## ⚙️ Fonctionnalités Automatiques

### ✅ Déjà incluses (aucune config nécessaire)
- Recherche en temps réel
- Tri des colonnes
- Export CSV
- Design responsive
- Animations

### 🔧 À configurer (optionnel)
- Calcul des statistiques (voir Étape 3)
- Filtres avancés
- Pagination

---

## 🐛 Dépannage

### La recherche ne fonctionne pas
**Cause**: L'ID du champ de recherche n'est pas `searchInput`
**Solution**: Assurez-vous que votre input a `id="searchInput"`

### Le tri ne fonctionne pas
**Cause**: Manque l'attribut `data-column` ou la classe `sortable`
**Solution**: Vérifiez que vos `<th>` ont:
```html
<th class="sortable" data-column="0">
```

### L'export CSV est vide
**Cause**: L'ID de la table ne se termine pas par "Table"
**Solution**: Nommez votre table `id="[nom]Table"` (ex: `camionsTable`)

### Les styles ne s'appliquent pas
**Cause**: Les fichiers statiques ne sont pas collectés
**Solution**:
```bash
./venv/bin/python manage.py collectstatic
```

---

## 📚 Ressources

- **Exemple complet**: `transport/templates/transport/prestations/prestation_transport_list.html`
- **Documentation**: `AMELIORATIONS_TEMPLATES.md`
- **CSS**: `transport/static/css/table-styles.css`
- **JS**: `transport/static/js/table-enhancements.js`

---

## ✨ Astuces Pro

### 1. Montants colorés
```html
<td><span class="text-success fw-bold">{{ montant }}€</span></td>
```

### 2. Sous-informations
```html
<td>
    <strong>{{ principal }}</strong><br>
    <small class="text-muted">{{ secondaire }}</small>
</td>
```

### 3. Confirmation personnalisée
```html
onclick="return confirm('Message personnalisé?')"
```

### 4. Tooltips
```html
<button title="Texte du tooltip">...</button>
```

---

**Bon développement! 🚀**
