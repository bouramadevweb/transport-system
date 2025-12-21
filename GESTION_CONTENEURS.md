# 🚢 Gestion Automatique des Conteneurs

## Vue d'ensemble

Le système gère désormais automatiquement le **statut des conteneurs** pour empêcher qu'un même conteneur soit assigné à plusieurs missions simultanément.

---

## 📊 Statuts des Conteneurs

Un conteneur peut avoir 3 statuts:

| Statut | Description | Disponible pour mission? |
|--------|-------------|--------------------------|
| **au_port** | Conteneur au port, disponible | ✅ Oui |
| **en_mission** | Conteneur assigné à une mission en cours | ❌ Non |
| **en_maintenance** | Conteneur en réparation/maintenance | ❌ Non |

---

## 🔄 Cycle de Vie Automatique

### 1. **Création d'un Contrat/Mission**

Quand vous créez un nouveau contrat de transport:

```
AVANT
├─ Vérification du conteneur
│  ├─ ✅ Conteneur disponible (au_port) → OK, créer le contrat
│  └─ ❌ Conteneur en mission → ERREUR, bloquer la création
│
PENDANT (si OK)
├─ Créer le contrat
├─ Créer la mission (statut: en cours)
└─ 🆕 Marquer conteneur comme "en_mission"
```

**Fichier**: `transport/signals.py:200-220` + `283-289`

### 2. **Fin de Mission (Terminée)**

Quand vous terminez une mission:

```
ACTION
├─ Mission.terminer_mission()
│  ├─ Marquer mission comme "terminée"
│  └─ 🆕 Retourner conteneur au port (statut: au_port)
│
RÉSULTAT
└─ Conteneur disponible pour une nouvelle mission
```

**Fichier**: `transport/models.py:901-906`

### 3. **Annulation de Mission**

Quand vous annulez une mission:

```
ACTION
├─ Mission.annuler_mission()
│  ├─ Annuler mission
│  ├─ Annuler contrat
│  ├─ Annuler cautions
│  ├─ Annuler paiements
│  └─ 🆕 Retourner conteneur au port (statut: au_port)
│
RÉSULTAT
└─ Conteneur disponible pour réutilisation
```

**Fichier**: `transport/models.py:971-976`

---

## 🚨 Messages d'Erreur

### Erreur 1: Conteneur déjà en mission

**Quand**: Tentative de créer un contrat avec un conteneur déjà assigné

```
❌ ERREUR

🚫 Impossible de créer le contrat: le conteneur CONT-12345
est déjà en mission vers Dakar.
Attendez que la mission se termine et que le conteneur soit retourné au port.
```

**Solution**:
- Terminez d'abord la mission en cours
- Ou choisissez un autre conteneur disponible

### Erreur 2: Conteneur en maintenance

**Quand**: Tentative d'utiliser un conteneur en maintenance

```
❌ ERREUR

🚫 Le conteneur CONT-12345 n'est pas disponible
(statut actuel: En maintenance)
```

**Solution**:
- Attendre la fin de la maintenance
- Ou choisir un autre conteneur

---

## 🔍 Vérifications Disponibles

### Méthodes du modèle Conteneur

```python
# Vérifier si un conteneur est disponible
if conteneur.est_disponible():
    print("✅ Conteneur disponible!")
else:
    print("❌ Conteneur non disponible")

# Voir quelle mission utilise le conteneur
mission = conteneur.get_mission_en_cours()
if mission:
    print(f"En mission vers {mission.destination}")

# Marquer manuellement comme en mission
conteneur.mettre_en_mission()

# Retourner manuellement au port
conteneur.retourner_au_port()
```

**Fichier**: `transport/models.py:442-462`

---

## 📝 Logs et Traçabilité

Toutes les actions sur les conteneurs sont enregistrées dans les logs:

```
✅ Mission créée: MISSION-ABC123
🚢 Conteneur CONT-12345 marqué comme 'en_mission'

... plus tard ...

✅ Mission terminée
🚢 Conteneur CONT-12345 retourné au port (disponible)
```

**Fichiers de logs**: `logs/django_prod.log` (en production)

---

## 🎯 Cas d'Usage

### Scénario 1: Création Normal

```
1. Conteneur CONT-001 au port (statut: au_port)
2. Créer contrat → Mission vers Bamako
3. Conteneur CONT-001 automatiquement marqué "en_mission"
4. Tentative de créer 2ème contrat avec CONT-001 → ❌ BLOQUÉ
5. Mission terminée
6. Conteneur CONT-001 retourné "au_port" → ✅ Disponible
```

### Scénario 2: Annulation

```
1. Mission en cours avec CONT-002
2. Problème → Annuler la mission
3. Conteneur CONT-002 automatiquement retourné "au_port"
4. Peut créer nouvelle mission avec CONT-002 immédiatement
```

### Scénario 3: Maintenance

```
1. Conteneur CONT-003 nécessite réparation
2. Admin marque manuellement statut = "en_maintenance"
3. Impossible de créer mission avec CONT-003
4. Réparation terminée → Admin marque statut = "au_port"
5. Conteneur disponible pour missions
```

---

## 🛠️ Administration Django

Dans l'interface admin Django, vous pouvez:

1. **Voir le statut** de chaque conteneur
2. **Filtrer** les conteneurs par statut
3. **Modifier manuellement** le statut si nécessaire
4. **Voir l'historique** des changements (via AuditLog)

---

## 🔧 Commandes SQL Utiles

### Voir tous les conteneurs et leur statut

```sql
SELECT
    numero_conteneur,
    statut,
    (SELECT COUNT(*) FROM transport_mission m
     JOIN transport_contrattransport c ON m.contrat_id = c.pk_contrat
     WHERE c.conteneur_id = transport_conteneur.pk_conteneur
     AND m.statut = 'en cours') as missions_actives
FROM transport_conteneur;
```

### Trouver les conteneurs disponibles

```sql
SELECT numero_conteneur, compagnie_id, client_id
FROM transport_conteneur
WHERE statut = 'au_port'
ORDER BY numero_conteneur;
```

### Conteneurs bloqués avec leurs missions

```sql
SELECT
    c.numero_conteneur,
    c.statut,
    m.pk_mission,
    m.destination,
    m.statut as mission_statut,
    m.date_depart
FROM transport_conteneur c
LEFT JOIN transport_contrattransport ct ON ct.conteneur_id = c.pk_conteneur
LEFT JOIN transport_mission m ON m.contrat_id = ct.pk_contrat
WHERE c.statut = 'en_mission' AND m.statut = 'en cours';
```

---

## 📋 Checklist Migration Données Existantes

Si vous avez des conteneurs et missions existants:

1. **Mettre à jour les conteneurs en mission**:
```python
from transport.models import Conteneur, Mission

# Marquer comme "en_mission" tous les conteneurs avec mission active
missions_actives = Mission.objects.filter(statut='en cours')
for mission in missions_actives:
    if mission.contrat and mission.contrat.conteneur:
        conteneur = mission.contrat.conteneur
        conteneur.statut = 'en_mission'
        conteneur.save()
        print(f"✅ {conteneur.numero_conteneur} → en_mission")
```

2. **Tous les autres → au_port**:
```python
Conteneur.objects.filter(statut='').update(statut='au_port')
```

---

## 🚀 Évolutions Futures Possibles

- 📧 Notification email quand conteneur est retourné au port
- 📊 Rapport d'utilisation: temps moyen en mission par conteneur
- 🔔 Alerte si conteneur en mission depuis trop longtemps
- 📍 Tracking GPS intégré au statut
- 🔄 Statut "en_transit_retour" pour plus de précision

---

## 📞 Support

En cas de problème:
1. Vérifier les logs: `logs/django_prod.log`
2. Consulter l'historique: `/audit/`
3. Vérifier le statut du conteneur dans l'admin Django

---

**Version**: 1.0
**Date**: 2025-12-20
**Migration**: `0015_conteneur_statut.py`
