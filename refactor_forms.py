#!/usr/bin/env python3
"""
Script de refactorisation automatique de form.py

Ce script lit form.py et le divise en modules logiques selon les catégories de formulaires.
"""

import os
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
FORMS_FILE = BASE_DIR / 'transport' / 'form.py'
FORMS_DIR = BASE_DIR / 'transport' / 'forms'

# Mapping des classes vers leurs modules
FORMS_MAPPING = {
    'user_forms.py': [
        'EntrepriseForm',
        'InscriptionUtilisateurForm',
        'ConnexionForm',
    ],
    'personnel_forms.py': [
        'ChauffeurForm',
        'AffectationForm',
        'MecanicienForm',
    ],
    'vehicle_forms.py': [
        'CamionForm',
        'ConteneurForm',
        'ReparationForm',
        'ReparationMecanicienForm',
        'PieceRepareeForm',
    ],
    'commercial_forms.py': [
        'TransitaireForm',
        'ClientForm',
        'CompagnieConteneurForm',
        'FournisseurForm',
    ],
    'mission_forms.py': [
        'MissionForm',
        'MissionConteneurForm',
        'FraisTrajetForm',
    ],
    'contrat_forms.py': [
        'ContratTransportForm',
        'PrestationDeTransportsForm',
    ],
    'finance_forms.py': [
        'CautionsForm',
        'PaiementMissionForm',
    ],
}


def extract_class_code(content, class_name):
    """
    Extrait le code complet d'une classe depuis le contenu du fichier.
    """
    # Pattern pour trouver la classe
    pattern = rf'^(class\s+{class_name}\s*\([^)]*\):.*?)(?=^class\s+|\Z)'

    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).rstrip() + '\n\n'
    return None


def get_common_imports():
    """
    Retourne les imports communs pour tous les modules.
    """
    return """from django import forms
from django.core.exceptions import ValidationError

"""


def create_forms_module(module_name, forms_code, extra_imports=''):
    """
    Crée un module de formulaires avec le code des classes.
    """
    title = module_name.replace('_', ' ').title().replace('.py', '')
    domain = module_name.replace('_forms.py', '').replace('_', ' ')

    header = f'"""\n{title}\n\nFormulaires pour {domain}\n"""\n\n'

    imports = get_common_imports() + extra_imports

    content = header + imports + '\n' + forms_code

    return content


def main():
    print("🚀 Démarrage de la refactorisation de form.py...")

    # Créer le dossier forms s'il n'existe pas
    FORMS_DIR.mkdir(exist_ok=True)
    print(f"✅ Dossier {FORMS_DIR} créé/vérifié")

    # Lire le contenu de form.py
    print(f"📖 Lecture de {FORMS_FILE}...")
    with open(FORMS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pour chaque module à créer
    for module_name, class_names in FORMS_MAPPING.items():
        print(f"\n📝 Création du module {module_name}...")

        forms_code = ''
        missing_forms = []

        # Extraire chaque classe
        for class_name in class_names:
            class_code = extract_class_code(content, class_name)
            if class_code:
                forms_code += class_code
                print(f"  ✓ {class_name}")
            else:
                missing_forms.append(class_name)
                print(f"  ✗ {class_name} (non trouvée)")

        if forms_code:
            # Déterminer les imports spécifiques
            extra_imports = ''

            if module_name == 'user_forms.py':
                extra_imports = 'from django.contrib.auth.forms import UserCreationForm\n'

            # Tous les modules ont besoin d'importer les modèles
            extra_imports += 'from ..models import (\n'

            # Déterminer quels modèles importer selon le module
            if 'user' in module_name:
                extra_imports += '    Entreprise, Utilisateur\n'
            elif 'personnel' in module_name:
                extra_imports += '    Chauffeur, Affectation, Mecanicien, Camion\n'
            elif 'vehicle' in module_name:
                extra_imports += '    Camion, Conteneur, Reparation, ReparationMecanicien, PieceReparee,\n'
                extra_imports += '    Mecanicien, Fournisseur\n'
            elif 'commercial' in module_name:
                extra_imports += '    Transitaire, Client, CompagnieConteneur, Fournisseur\n'
            elif 'mission' in module_name:
                extra_imports += '    Mission, MissionConteneur, FraisTrajet\n'
            elif 'contrat' in module_name:
                extra_imports += '    ContratTransport, PrestationDeTransports, Conteneur, Camion, Chauffeur,\n'
                extra_imports += '    Mission\n'
            elif 'finance' in module_name:
                extra_imports += '    Cautions, PaiementMission\n'

            extra_imports += ')\n'

            # Créer le module
            module_content = create_forms_module(module_name, forms_code, extra_imports)

            # Sauvegarder le fichier
            module_path = FORMS_DIR / module_name
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_content)

            print(f"✅ Module {module_name} créé avec {len(class_names) - len(missing_forms)} formulaires")

        if missing_forms:
            print(f"⚠️  Formulaires manquants: {', '.join(missing_forms)}")

    print("\n" + "="*60)
    print("✨ Refactorisation de form.py terminée!")
    print("="*60)
    print("\n📋 Prochaines étapes:")
    print("1. Créer __init__.py pour ré-exporter tous les formulaires")
    print("2. Vérifier les imports")
    print("3. Renommer form.py en form_old.py comme backup")
    print("4. Tester l'application")


if __name__ == '__main__':
    main()
