# transport-system

# 📘 Spécification technique – Identifiants sécurisés personnalisés

## 🎯 Objectif

Ce document décrit la logique utilisée pour la **génération des identifiants primaires (`pk_*`)** dans le projet de gestion d’entreprise de transport.  
Contrairement aux modèles Django par défaut, **aucune clé auto-incrémentée (`id`) n’est utilisée**.  
Ce choix vise à améliorer la **sécurité**, la **traçabilité** et la **portabilité** des données.

---

## 🔒 Principe de conception

### 1. Pas d’auto-incrémentation

Chaque modèle utilise un champ de type `CharField` comme **clé primaire**, nommé de manière explicite :

```python
pk_chauffeur = models.CharField(max_length=250, primary_key=True, editable=False)
