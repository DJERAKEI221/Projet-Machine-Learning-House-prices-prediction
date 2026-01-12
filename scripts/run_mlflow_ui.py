#!/usr/bin/env python
"""
Script pour lancer l'interface MLFlow UI.
Utilisation:
    python scripts/run_mlflow_ui.py
"""

import subprocess
import sys
from pathlib import Path

# Chemin racine du projet
project_root = Path(__file__).resolve().parents[1]
mlruns_dir = project_root / "mlruns"

# Créer le dossier mlruns si nécessaire
mlruns_dir.mkdir(parents=True, exist_ok=True)

PORT = 5000

print("=" * 60)
print(" Démarrage de MLFlow UI")
print("=" * 60)
print(f"Dossier MLRuns: {mlruns_dir}")
print(f"URL interface: http://127.0.0.1:{PORT}")
print("=" * 60)

try:
    subprocess.run(
        [
            "mlflow", "ui",
            "--backend-store-uri", f"file://{mlruns_dir}",
            "--host", "127.0.0.1",
            "--port", str(PORT),
        ],
        cwd=project_root
    )
except KeyboardInterrupt:
    print("\n MLFlow UI arrêté")
    sys.exit(0)
except FileNotFoundError:
    print("ERREUR: MLFlow n'est pas installé.")
    print("Installez-le via : pip install mlflow")
    sys.exit(1)
