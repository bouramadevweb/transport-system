#!/usr/bin/env python3
"""
Script pour mettre à jour les imports de form vers forms
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
VIEWS_DIR = BASE_DIR / 'transport' / 'views'

def fix_imports_in_file(file_path):
    """
    Remplace 'from ..form import' par 'from ..forms import' dans un fichier
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Remplacer les imports
    content = content.replace('from ..form import', 'from ..forms import')

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 Mise à jour des imports form → forms...")

    updated_count = 0

    # Parcourir tous les fichiers .py dans views/
    for py_file in VIEWS_DIR.glob('*.py'):
        if py_file.name == '__init__.py':
            continue

        if fix_imports_in_file(py_file):
            print(f"✅ {py_file.name} mis à jour")
            updated_count += 1
        else:
            print(f"✓ {py_file.name} déjà à jour")

    print(f"\n✨ {updated_count} fichiers mis à jour!")

if __name__ == '__main__':
    main()
