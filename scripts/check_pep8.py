#!/usr/bin/env python
"""
Script pour vérifier la conformité PEP 8 du code.
Utilisation: python scripts/check_pep8.py
"""

import subprocess
import sys
from pathlib import Path

# Chemin racine du projet
project_root = Path(__file__).parent.parent

print("=" * 60)
print("Vérification de la conformité PEP 8")
print("=" * 60)

# Fichiers à vérifier
paths_to_check = [
    "src",
    "dashboard",
    "config.py",
    "setup.py"
]

# Exclure certains fichiers/dossiers
exclude_patterns = [
    "__pycache__",
    ".git",
    "venv",
    "env",
    ".venv",
    "mlruns",
    "output",
    "data"
]

try:
    # Vérifier si flake8 est installé
    result = subprocess.run(
        ["flake8", "--version"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("ERREUR: flake8 n'est pas installé")
        print("Installez flake8 avec: pip install flake8")
        sys.exit(1)
    
    # Construire la commande flake8
    cmd = [
        "flake8",
        "--config=.flake8",
        "--count",
        "--statistics"
    ]
    
    # Ajouter les chemins à vérifier
    for path in paths_to_check:
        full_path = project_root / path
        if full_path.exists():
            cmd.append(str(path))
    
    # Exécuter flake8
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✓ Code conforme à PEP 8")
        sys.exit(0)
    else:
        print("\n✗ Erreurs de conformité PEP 8 détectées:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
        
except FileNotFoundError:
    print("ERREUR: flake8 n'est pas installé")
    print("Installez flake8 avec: pip install flake8")
    sys.exit(1)
except Exception as e:
    print(f"ERREUR: {e}")
    sys.exit(1)
