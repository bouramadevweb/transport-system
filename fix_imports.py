#!/usr/bin/env python3
"""
Script pour ajouter automatiquement les imports manquants dans les modules de vues
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
VIEWS_DIR = BASE_DIR / 'transport' / 'views'

# Mapping des modèles utilisés dans chaque module
MODELS_IMPORTS = {
    'auth_views.py': ['Utilisateur'],
    'entreprise_views.py': ['Entreprise'],
    'personnel_views.py': ['Chauffeur', 'Affectation', 'Mecanicien'],
    'vehicle_views.py': ['Camion', 'Conteneur', 'Reparation', 'ReparationMecanicien', 'PieceReparee'],
    'commercial_views.py': ['Transitaire', 'Client', 'CompagnieConteneur', 'Fournisseur'],
    'mission_views.py': ['Mission', 'MissionConteneur'],
    'contrat_views.py': ['ContratTransport', 'PrestationDeTransports', 'Conteneur', 'Camion', 'Chauffeur'],
    'finance_views.py': ['Cautions', 'PaiementMission'],
    'frais_views.py': ['FraisTrajet'],
    'dashboard_views.py': ['Chauffeur', 'Camion', 'Mission', 'Reparation', 'PaiementMission', 'Affectation', 'Client', 'Notification', 'AuditLog', 'Entreprise'],
    'ajax_views.py': ['Chauffeur', 'Camion', 'Affectation'],
    'pdf_views.py': ['ContratTransport'],
}

# Mapping des formulaires utilisés dans chaque module
FORMS_IMPORTS = {
    'auth_views.py': ['InscriptionUtilisateurForm', 'ConnexionForm'],
    'entreprise_views.py': ['EntrepriseForm'],
    'personnel_views.py': ['ChauffeurForm', 'AffectationForm', 'MecanicienForm'],
    'vehicle_views.py': ['CamionForm', 'ConteneurForm', 'ReparationForm', 'ReparationMecanicienForm', 'PieceRepareeForm'],
    'commercial_views.py': ['TransitaireForm', 'ClientForm', 'CompagnieConteneurForm', 'FournisseurForm'],
    'mission_views.py': ['MissionForm', 'MissionConteneurForm'],
    'contrat_views.py': ['ContratTransportForm', 'PrestationDeTransportsForm'],
    'finance_views.py': ['CautionsForm', 'PaiementMissionForm'],
    'frais_views.py': ['FraisTrajetForm'],
    'dashboard_views.py': [],
    'ajax_views.py': [],
    'pdf_views.py': [],
}

# Mapping des decorators utilisés dans chaque module
DECORATORS_IMPORTS = {
    'entreprise_views.py': ['can_delete_data'],
    'personnel_views.py': ['can_delete_data'],
    'vehicle_views.py': ['can_delete_data'],
    'commercial_views.py': ['can_delete_data'],
    'mission_views.py': ['can_delete_data'],
    'contrat_views.py': ['can_delete_data'],
    'finance_views.py': ['can_delete_data', 'can_validate_payment'],
    'frais_views.py': ['can_delete_data'],
    'dashboard_views.py': [],
}


def add_imports_to_module(module_path, models, forms, decorators):
    """
    Ajoute les imports manquants à un module
    """
    # Lire le contenu actuel
    with open(module_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trouver la position après les imports existants
    lines = content.split('\n')
    insert_index = 0

    # Trouver la dernière ligne d'import ou la fin du docstring
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            insert_index = i + 1
        elif i > 0 and not line.strip().startswith('"""') and not line.strip().startswith('#'):
            if insert_index > 0:
                break

    # Construire les nouveaux imports
    new_imports = []

    if models:
        models_str = ', '.join(models)
        new_imports.append(f'from ..models import ({models_str})')

    if forms:
        forms_str = ', '.join(forms)
        new_imports.append(f'from ..form import ({forms_str})')

    if decorators:
        decorators_str = ', '.join(decorators)
        new_imports.append(f'from ..decorators import ({decorators_str})')

    # Insérer les nouveaux imports
    if new_imports:
        lines.insert(insert_index, '\n'.join(new_imports))
        lines.insert(insert_index + 1, '')

    # Réécrire le fichier
    new_content = '\n'.join(lines)
    with open(module_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(new_imports)


def main():
    print("🔧 Ajout des imports manquants...")

    for module_file in MODELS_IMPORTS.keys():
        module_path = VIEWS_DIR / module_file

        if not module_path.exists():
            print(f"⚠️  {module_file} n'existe pas, ignoré")
            continue

        models = MODELS_IMPORTS.get(module_file, [])
        forms = FORMS_IMPORTS.get(module_file, [])
        decorators = DECORATORS_IMPORTS.get(module_file, [])

        imports_added = add_imports_to_module(module_path, models, forms, decorators)

        if imports_added > 0:
            print(f"✅ {module_file}: {imports_added} imports ajoutés")
            if models:
                print(f"   - Models: {', '.join(models)}")
            if forms:
                print(f"   - Forms: {', '.join(forms)}")
            if decorators:
                print(f"   - Decorators: {', '.join(decorators)}")
        else:
            print(f"✓ {module_file}: déjà à jour")

    print("\n✨ Imports ajoutés avec succès!")


if __name__ == '__main__':
    main()
