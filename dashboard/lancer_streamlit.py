"""
================================================================================
LANCEUR SIMPLE POUR SPYDER
================================================================================
Copiez-collez ce code dans la console IPython de Spyder
ou exécutez ce fichier directement
================================================================================
"""

import subprocess
import os
import sys
from pathlib import Path

# Configuration
# Utiliser l'exécutable Python actuel (plus portable)
PYTHON = sys.executable
DASHBOARD_DIR = Path(__file__).parent.absolute() if '__file__' in dir() else Path.cwd()
DASHBOARD_FILE = DASHBOARD_DIR / "app.py"

# Changer de répertoire
os.chdir(DASHBOARD_DIR)

print("🚀 Lancement du dashboard Streamlit...")
print(f"📁 Répertoire: {DASHBOARD_DIR}")
print(f"🌐 URL: http://localhost:8501")
print("\n⏳ Le dashboard va s'ouvrir dans votre navigateur...\n")

# Lancer Streamlit
subprocess.Popen(
    [PYTHON, "-m", "streamlit", "run", str(DASHBOARD_FILE)],
    cwd=DASHBOARD_DIR
)

print("✅ Dashboard lancé!")
print("📝 Pour arrêter, fermez la fenêtre de Streamlit ou utilisez Ctrl+C")
