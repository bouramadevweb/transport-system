#!/usr/bin/env python3
"""
Script pour corriger les ForeignKey qui n'utilisent pas de chaînes de caractères
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / 'transport' / 'models'

def fix_foreignkeys_in_file(file_path):
    """
    Remplace ForeignKey(ModelName, ...) par ForeignKey("ModelName", ...)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Pattern pour trouver ForeignKey(NomModele, ...)
    # où NomModele commence par une majuscule et n'est pas entre quotes
    pattern = r'ForeignKey\(([A-Z][a-zA-Z0-9_]*),\s*'

    def replace_func(match):
        model_name = match.group(1)
        return f'ForeignKey("{model_name}", '

    content = re.sub(pattern, replace_func, content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 Correction des ForeignKey dans les modèles...")

    updated_count = 0

    # Parcourir tous les fichiers .py dans models/
    for py_file in MODELS_DIR.glob('*.py'):
        if py_file.name in ['__init__.py', 'choices.py']:
            continue

        if fix_foreignkeys_in_file(py_file):
            print(f"✅ {py_file.name} mis à jour")
            updated_count += 1
        else:
            print(f"✓ {py_file.name} déjà OK")

    print(f"\n✨ {updated_count} fichiers corrigés!")

if __name__ == '__main__':
    main()
