"""
Script pour convertir les fichiers Python du dossier src en notebooks Jupyter.
"""

import json
import re
from pathlib import Path

def create_notebook_from_python(python_file: Path, output_dir: Path):
    """
    Convertir un fichier Python en notebook Jupyter.
    
    Args:
        python_file: Chemin vers le fichier Python
        output_dir: Dossier de sortie pour le notebook
    """
    # Lire le contenu du fichier Python
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer le nom du notebook
    notebook_name = python_file.stem + '.ipynb'
    notebook_path = output_dir / notebook_name
    
    # Extraire le docstring du module
    module_doc = ""
    if content.startswith('"""') or content.startswith("'''"):
        doc_match = re.match(r'^"""(.*?)"""', content, re.DOTALL)
        if not doc_match:
            doc_match = re.match(r"^'''(.*?)'''", content, re.DOTALL)
        if doc_match:
            module_doc = doc_match.group(1).strip()
    
    # Créer la structure du notebook
    cells = []
    
    # Cellule 1: Titre et description
    title = python_file.stem.replace('_', ' ').title()
    markdown_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            f"# {title}\n\n",
            f"{module_doc}\n\n" if module_doc else "",
            "Ce notebook contient le code du module correspondant du dossier `src/`.\n\n",
            "## Structure\n\n",
            "- Imports et configuration\n",
            "- Classes et fonctions\n",
            "- Exemples d'utilisation"
        ]
    }
    cells.append(markdown_cell)
    
    # Cellule 2: Imports
    imports = []
    code_lines = content.split('\n')
    in_imports = True
    
    for line in code_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(line)
            elif in_imports and (stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('logger')):
                in_imports = False
                if line.strip() and not line.strip().startswith('#'):
                    break
    
    if imports:
        # Formater les imports avec des sauts de ligne
        formatted_imports = []
        for imp in imports:
            formatted_imports.append(imp)
            if not imp.endswith('\\'):
                formatted_imports.append("")
        
        code_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": formatted_imports[:-1] if formatted_imports[-1] == "" else formatted_imports
        }
        cells.append(code_cell)
    
    # Diviser le reste du code en sections logiques
    # D'abord, ajouter le code complet après les imports
    remaining_code = []
    skip_until = 0
    
    for i, line in enumerate(code_lines):
        if i < skip_until:
            continue
        
        stripped = line.strip()
        
        # Ignorer les imports déjà traités
        if stripped.startswith('import ') or stripped.startswith('from '):
            continue
        
        # Ignorer le docstring du module
        if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
            # Trouver la fin du docstring
            if '"""' in line[3:] or "'''" in line[3:]:
                continue
            # Docstring multi-lignes
            for j in range(i+1, len(code_lines)):
                if '"""' in code_lines[j] or "'''" in code_lines[j]:
                    skip_until = j + 1
                    break
            continue
        
        remaining_code.append(line)
    
    # Créer une cellule avec tout le code restant
    if remaining_code:
        # Nettoyer les lignes vides en début
        while remaining_code and not remaining_code[0].strip():
            remaining_code.pop(0)
        
        if remaining_code:
            cells.append(create_code_cell(remaining_code))
    
    # Créer le notebook
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.9.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Sauvegarder le notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print(f"OK: Cree {notebook_path}")

def create_code_cell(lines):
    """Créer une cellule de code à partir d'une liste de lignes."""
    # Nettoyer les lignes vides en fin
    while lines and not lines[-1].strip():
        lines.pop()
    
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines if lines else [""]
    }

def main():
    """Fonction principale."""
    # Chemins
    src_dir = Path("src")
    notebooks_dir = Path("notebooks")
    notebooks_dir.mkdir(exist_ok=True)
    
    # Fichiers à convertir (exclure __init__.py)
    python_files = [f for f in src_dir.glob("*.py") if f.name != "__init__.py"]
    
    print(f"Conversion de {len(python_files)} fichiers Python en notebooks...\n")
    
    for python_file in python_files:
        try:
            create_notebook_from_python(python_file, notebooks_dir)
        except Exception as e:
            print(f"ERREUR avec {python_file.name}: {e}")
    
    print(f"\nConversion terminee! {len(python_files)} notebooks crees dans {notebooks_dir}")

if __name__ == "__main__":
    main()

