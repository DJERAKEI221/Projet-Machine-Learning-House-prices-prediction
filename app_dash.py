"""
Point d'entrée pour lancer le dashboard Dash.
Utilise l'application modulaire dans dashboard/app.py
Gère les chemins relatifs depuis la racine du projet.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Importer config pour initialiser les chemins
try:
    import config
    print(f"✅ Configuration chargée depuis: {config.PROJECT_ROOT}")
except ImportError:
    print("⚠️  Module config non trouvé, utilisation des chemins par défaut")

# Vérifier les dépendances avant de lancer
try:
    import dash
    import dash_bootstrap_components as dbc
    import plotly
except ImportError as e:
    print("=" * 60)
    print("❌ ERREUR: Dépendances manquantes")
    print("=" * 60)
    print(f"Module manquant: {e.name}")
    print("\n📦 Installation des dépendances:")
    print("   pip install -r requirements_api.txt")
    print("\nOu installer manuellement:")
    print("   pip install dash dash-bootstrap-components plotly")
    print("=" * 60)
    sys.exit(1)

try:
    from dashboard.app import app
except ImportError as e:
    print("=" * 60)
    print("❌ ERREUR: Impossible d'importer le module dashboard")
    print("=" * 60)
    print(f"Erreur: {e}")
    print("\nVérifiez que:")
    print("  1. Vous êtes dans le répertoire racine du projet")
    print("  2. Le dossier 'dashboard' existe")
    print("  3. Tous les fichiers __init__.py sont présents")
    print("=" * 60)
    sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Démarrage du Dashboard Dash")
    print("=" * 60)
    print("📊 Dashboard disponible sur: http://localhost:8050")
    print("=" * 60)
    print("\n💡 Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        app.run_server(debug=True, host="127.0.0.1", port=8050)
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        print("\nVérifiez que:")
        print("  - Le port 8050 n'est pas déjà utilisé")
        print("  - Toutes les dépendances sont installées")
        print("  - Le modèle est entraîné (optionnel)")
        sys.exit(1)

