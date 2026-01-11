#!/usr/bin/env python
"""
Script pour lancer l'interface web MLFlow UI.
Utilisation: python scripts/run_mlflow_ui.py
"""

import subprocess
import sys
from pathlib import Path

# Chemin racine du projet
project_root = Path(__file__).parent.parent

# Chemin du dossier mlruns
mlruns_dir = project_root / "mlruns"

# Créer le dossier mlruns s'il n'existe pas
mlruns_dir.mkdir(parents=True, exist_ok=True)

# Port par défaut
port = 5000

print("=" * 60)
print("Démarrage de l'interface MLFlow UI")
print("=" * 60)
print(f"Dossier MLRuns: {mlruns_dir}")
print(f"URL: http://localhost:{port}")
print("=" * 60)
print("\nAppuyez sur Ctrl+C pour arrêter le serveur\n")

try:
    # Lancer MLFlow UI
    subprocess.run(
        ["mlflow", "ui", "--backend-store-uri", f"file://{mlruns_dir.absolute()}", "--port", str(port)],
        cwd=project_root
    )
except KeyboardInterrupt:
    print("\n\nMLFlow UI arrêté")
    sys.exit(0)
except FileNotFoundError:
    print("\nERREUR: MLFlow n'est pas installé")
    print("Installez MLFlow avec: pip install mlflow")
    sys.exit(1)
