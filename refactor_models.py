#!/usr/bin/env python3
"""
Script de refactorisation automatique de models.py

Ce script lit models.py et le divise en modules logiques selon les catégories de modèles.
"""

import os
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
MODELS_FILE = BASE_DIR / 'transport' / 'models.py'
MODELS_DIR = BASE_DIR / 'transport' / 'models'

# Mapping des classes vers leurs modules
MODELS_MAPPING = {
    'choices.py': [
        # Toutes les constantes CHOICES
        'STATUT_ENTREPRISE_CHOICES',
        'ROLE_UTILISATEUR_CHOICES',
        'FIABILITE_CHOICES',
        'ETAT_PAIEMENT_CHOICES',
        'TYPE_CLIENT_CHOICES',
        'STATUT_CONTENEUR_CHOICES',
        'STATUT_CAUTION_CONTRAT_CHOICES',
        'STATUT_MISSION_CHOICES',
        'STATUT_CAUTION_CHOICES',
        'MOIS_CHOICES',
        'STATUT_SALAIRE_CHOICES',
        'MODE_PAIEMENT_SALAIRE_CHOICES',
    ],
    'user.py': [
        'UtilisateurManager',
        'Entreprise',
        'Utilisateur',
    ],
    'personnel.py': [
        'Chauffeur',
        'Mecanicien',
        'Affectation',
    ],
    'salary.py': [
        'Salaire',
        'Prime',
        'Deduction',
    ],
    'vehicle.py': [
        'Camion',
        'CompagnieConteneur',
        'Conteneur',
        'Reparation',
        'ReparationMecanicien',
        'PieceReparee',
        'Fournisseur',
    ],
    'commercial.py': [
        'Transitaire',
        'Client',
    ],
    'mission.py': [
        'FraisTrajet',
        'Mission',
        'MissionConteneur',
    ],
    'contrat.py': [
        'ContratTransport',
        'PrestationDeTransports',
    ],
    'finance.py': [
        'Cautions',
        'PaiementMission',
    ],
    'audit.py': [
        'Notification',
        'AuditLog',
    ],
}


def extract_class_or_constant(content, name):
    """
    Extrait le code complet d'une classe ou d'une constante depuis le contenu du fichier.
    """
    # Pour les constantes (variables en majuscules)
    if name.isupper() and 'CHOICES' in name:
        pattern = rf'^({name}\s*=\s*\[.*?\])\s*$'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1) + '\n\n'

    # Pour les classes
    pattern = rf'^(class\s+{name}\s*\([^)]*\):.*?)(?=^class\s+|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).rstrip() + '\n\n'
    return None


def get_common_imports():
    """
    Retourne les imports communs pour tous les modules.
    """
    return """from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

"""


def create_choices_module(choices_code):
    """
    Crée le module choices.py avec toutes les constantes.
    """
    header = '''"""
Constantes et choix pour les modèles

Ce module contient toutes les constantes CHOICES utilisées dans les modèles.
"""

'''
    return header + choices_code


def create_model_module(module_name, models_code, extra_imports=''):
    """
    Crée un module de modèles avec le code des classes.
    """
    title = module_name.replace('_', ' ').title().replace('.py', '')
    domain = module_name.replace('.py', '').replace('_', ' ')

    header = f'"""\n{title}\n\nModèles pour {domain}\n"""\n\n'

    imports = get_common_imports()

    # Import des choices
    imports += "from .choices import *\n"

    # Imports supplémentaires
    imports += extra_imports

    content = header + imports + '\n' + models_code

    return content


def main():
    print("🚀 Démarrage de la refactorisation de models.py...")

    # Créer le dossier models s'il n'existe pas
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"✅ Dossier {MODELS_DIR} créé/vérifié")

    # Lire le contenu de models.py
    print(f"📖 Lecture de {MODELS_FILE}...")
    with open(MODELS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Traiter d'abord le module choices.py
    print(f"\n📝 Création du module choices.py...")
    choices_code = ''
    for choice_name in MODELS_MAPPING['choices.py']:
        choice_code = extract_class_or_constant(content, choice_name)
        if choice_code:
            choices_code += choice_code
            print(f"  ✓ {choice_name}")
        else:
            print(f"  ✗ {choice_name} (non trouvée)")

    if choices_code:
        module_content = create_choices_module(choices_code)
        module_path = MODELS_DIR / 'choices.py'
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
        print(f"✅ Module choices.py créé")

    # Pour chaque module à créer (sauf choices.py)
    for module_name, class_names in MODELS_MAPPING.items():
        if module_name == 'choices.py':
            continue

        print(f"\n📝 Création du module {module_name}...")

        models_code = ''
        missing_models = []

        # Extraire chaque classe
        for class_name in class_names:
            class_code = extract_class_or_constant(content, class_name)
            if class_code:
                models_code += class_code
                print(f"  ✓ {class_name}")
            else:
                missing_models.append(class_name)
                print(f"  ✗ {class_name} (non trouvée)")

        if models_code:
            # Déterminer les imports spécifiques
            extra_imports = ''

            if module_name == 'user.py':
                extra_imports = 'from django.contrib.auth.models import AbstractUser, BaseUserManager\n'

            if module_name in ['personnel.py', 'mission.py', 'contrat.py', 'finance.py', 'salary.py']:
                # Ces modules peuvent avoir des références croisées
                extra_imports += '# Imports circulaires gérés dans les méthodes\n'

            # Créer le module
            module_content = create_model_module(module_name, models_code, extra_imports)

            # Sauvegarder le fichier
            module_path = MODELS_DIR / module_name
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_content)

            print(f"✅ Module {module_name} créé avec {len(class_names) - len(missing_models)} modèles")

        if missing_models:
            print(f"⚠️  Modèles manquants: {', '.join(missing_models)}")

    print("\n" + "="*60)
    print("✨ Refactorisation de models.py terminée!")
    print("="*60)
    print("\n📋 Prochaines étapes:")
    print("1. Créer __init__.py pour ré-exporter tous les modèles")
    print("2. Vérifier les imports circulaires")
    print("3. Tester les migrations Django")
    print("4. Renommer models.py en models_old.py comme backup")


if __name__ == '__main__':
    main()
