#!/usr/bin/env python3
"""
Script de refactorisation automatique de views.py

Ce script lit views.py et le divise en modules logiques selon les catégories de vues.
"""

import os
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
VIEWS_FILE = BASE_DIR / 'transport' / 'views.py'
VIEWS_DIR = BASE_DIR / 'transport' / 'views'

# Mapping des fonctions vers leurs modules
VIEWS_MAPPING = {
    'auth_views.py': [
        'inscription_utilisateur',
        'connexion_utilisateur',
        'logout_utilisateur',
        'user_profile',
        'user_settings',
        'rediriger_vers_connexion',
        'rediriger_erreur_serveur',
    ],
    'entreprise_views.py': [
        'liste_entreprises',
        'ajouter_entreprise',
        'modifier_entreprise',
        'supprimer_entreprise',
    ],
    'personnel_views.py': [
        'create_chauffeur',
        'chauffeur_list',
        'update_chauffeur',
        'chauffeur_delete',
        'affectation_list',
        'create_affectation',
        'update_affectation',
        'terminer_affectation',
        'delete_affectation',
        'mecanicien_list',
        'create_mecanicien',
        'update_mecanicien',
        'delete_mecanicien',
    ],
    'vehicle_views.py': [
        'camion_list',
        'create_camion',
        'update_camion',
        'delete_camion',
        'conteneur_list',
        'create_conteneur',
        'update_conteneur',
        'delete_conteneur',
        'reparation_list',
        'create_reparation',
        'update_reparation',
        'delete_reparation',
        'reparation_mecanicien_list',
        'create_reparation_mecanicien',
        'update_reparation_mecanicien',
        'delete_reparation_mecanicien',
        'piece_reparee_list',
        'create_piece_reparee',
        'update_piece_reparee',
        'delete_piece_reparee',
    ],
    'commercial_views.py': [
        'transitaire_list',
        'create_transitaire',
        'update_transitaire',
        'delete_transitaire',
        'client_list',
        'create_client',
        'update_client',
        'delete_client',
        'compagnie_list',
        'create_compagnie',
        'update_compagnie',
        'delete_compagnie',
        'fournisseur_list',
        'create_fournisseur',
        'update_fournisseur',
        'delete_fournisseur',
    ],
    'mission_views.py': [
        'mission_list',
        'create_mission',
        'update_mission',
        'delete_mission',
        'terminer_mission',
        'annuler_mission',
        'mission_conteneur_list',
        'create_mission_conteneur',
        'update_mission_conteneur',
        'delete_mission_conteneur',
    ],
    'contrat_views.py': [
        'contrat_list',
        'create_contrat',
        'update_contrat',
        'delete_contrat',
        'presta_transport_list',
        'create_presta_transport',
        'update_presta_transport',
        'delete_presta_transport',
    ],
    'finance_views.py': [
        'cautions_list',
        'create_caution',
        'update_caution',
        'delete_caution',
        'paiement_mission_list',
        'create_paiement_mission',
        'update_paiement_mission',
        'delete_paiement_mission',
        'valider_paiement_mission',
    ],
    'frais_views.py': [
        'frais_list',
        'create_frais',
        'update_frais',
        'delete_frais',
    ],
    'dashboard_views.py': [
        'dashboard',
        'help_page',
        'notifications_list',
        'mark_all_notifications_read',
        'tableau_bord_statistiques',
        'audit_log_list',
        'audit_log_detail',
    ],
    'ajax_views.py': [
        'get_chauffeur_from_camion',
        'get_camion_from_chauffeur',
    ],
    'pdf_views.py': [
        'pdf_contrat',
    ],
}


def extract_function_code(content, function_name):
    """
    Extrait le code complet d'une fonction depuis le contenu du fichier.
    """
    # Pattern pour trouver la fonction
    pattern = rf'^((?:@[\w.]+(?:\([^)]*\))?\s*)*def\s+{function_name}\s*\([^)]*\):.*?)(?=^(?:@|\ndef\s+|\Z))'

    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).rstrip() + '\n\n'
    return None


def get_common_imports():
    """
    Retourne les imports communs pour tous les modules.
    """
    return """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.http import JsonResponse

"""


def create_module(module_name, functions_code, extra_imports=''):
    """
    Crée un module de vues avec le code des fonctions.
    """
    header = f'"""\n{module_name.replace("_", " ").title().replace(".py", "")}\n\nVues pour {module_name.replace("_views.py", "").replace("_", " ")}\n"""\n\n'

    imports = get_common_imports() + extra_imports

    content = header + imports + functions_code

    return content


def main():
    print("🚀 Démarrage de la refactorisation de views.py...")

    # Créer le dossier views s'il n'existe pas
    VIEWS_DIR.mkdir(exist_ok=True)
    print(f"✅ Dossier {VIEWS_DIR} créé/vérifié")

    # Lire le contenu de views.py
    print(f"📖 Lecture de {VIEWS_FILE}...")
    with open(VIEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pour chaque module à créer
    for module_name, function_names in VIEWS_MAPPING.items():
        print(f"\n📝 Création du module {module_name}...")

        functions_code = ''
        missing_functions = []

        # Extraire chaque fonction
        for func_name in function_names:
            func_code = extract_function_code(content, func_name)
            if func_code:
                functions_code += func_code
                print(f"  ✓ {func_name}")
            else:
                missing_functions.append(func_name)
                print(f"  ✗ {func_name} (non trouvée)")

        if functions_code:
            # Déterminer les imports spécifiques
            extra_imports = ''
            if 'auth' in module_name:
                extra_imports = 'from django.contrib.auth import authenticate, login, logout, update_session_auth_hash\n'
                extra_imports += 'from django.contrib.auth.forms import PasswordChangeForm\n'
            elif 'pdf' in module_name:
                extra_imports = 'from reportlab.lib.pagesizes import A4\n'
                extra_imports += 'from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle\n'
                extra_imports += 'from io import BytesIO\n'

            # Créer le module
            module_content = create_module(module_name, functions_code, extra_imports)

            # Sauvegarder le fichier
            module_path = VIEWS_DIR / module_name
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_content)

            print(f"✅ Module {module_name} créé avec {len(function_names) - len(missing_functions)} fonctions")

        if missing_functions:
            print(f"⚠️  Fonctions manquantes: {', '.join(missing_functions)}")

    print("\n" + "="*60)
    print("✨ Refactorisation terminée!")
    print("="*60)
    print("\n📋 Prochaines étapes:")
    print("1. Vérifier les imports dans chaque module créé")
    print("2. Ajouter les imports manquants depuis form.py et models.py")
    print("3. Mettre à jour urls.py pour importer depuis views/")
    print("4. Renommer views.py en views_old.py comme backup")
    print("5. Tester l'application")


if __name__ == '__main__':
    main()
