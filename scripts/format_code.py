#!/usr/bin/env python
"""
Script pour formater le code avec Black (conformité PEP 8).
Utilisation: python scripts/format_code.py
"""

import subprocess
import sys
from pathlib import Path

# Chemin racine du projet
project_root = Path(__file__).parent.parent

print("=" * 60)
print("Formatage du code avec Black")
print("=" * 60)

# Fichiers à formater
paths_to_format = [
    "src",
    "dashboard",
    "config.py",
    "setup.py",
    "scripts"
]

try:
    # Vérifier si black est installé
    result = subprocess.run(
        ["black", "--version"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("ERREUR: black n'est pas installé")
        print("Installez black avec: pip install black")
        sys.exit(1)
    
    # Construire la commande black
    cmd = [
        "black",
        "--line-length=127",
        "--target-version=py39",
        "--target-version=py310",
        "--target-version=py311"
    ]
    
    # Ajouter les chemins à formater
    for path in paths_to_format:
        full_path = project_root / path
        if full_path.exists():
            cmd.append(str(path))
    
    # Exécuter black
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✓ Code formaté avec succès")
        if result.stdout:
            print(result.stdout)
        sys.exit(0)
    else:
        print("\n✗ Erreurs lors du formatage:")
        print(result.stderr)
        sys.exit(1)
        
except FileNotFoundError:
    print("ERREUR: black n'est pas installé")
    print("Installez black avec: pip install black")
    sys.exit(1)
except Exception as e:
    print(f"ERREUR: {e}")
    sys.exit(1)
