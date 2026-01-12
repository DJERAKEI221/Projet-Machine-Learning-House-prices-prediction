"""
Configuration du projet et gestion des chemins relatifs.
Ce module centralise tous les chemins du projet pour une utilisation cohérente.
"""

from pathlib import Path
import os

# Chemin racine du projet (où se trouve ce fichier)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Chemins des données
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_INTERIM = DATA_DIR / "interim"
DATA_PROCESSED = DATA_DIR / "processed"

# Chemins des outputs
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_FIGURES = OUTPUT_DIR / "figures"
OUTPUT_MODELS = OUTPUT_DIR / "models"
OUTPUT_TABLES = OUTPUT_DIR / "tables"
OUTPUT_SUBMISSION = OUTPUT_DIR / "submission.csv"

# Chemins du dashboard
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
DASHBOARD_ASSETS = DASHBOARD_DIR / "assets"
DASHBOARD_IMAGES = DASHBOARD_DIR / "images"

# Chemins du code source
SRC_DIR = PROJECT_ROOT / "src"

# Chemins des notebooks
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Chemins de la documentation
DOCS_DIR = PROJECT_ROOT / "docs"

# Chemins des tests
TESTS_DIR = PROJECT_ROOT / "tests"

# Chemins MLFlow
MLRUNS_DIR = PROJECT_ROOT / "mlruns"

# === MLflow Configuration ===

# URI du serveur MLflow (local UI)
# - Local UI: "http://127.0.0.1:5000"
# - Local sans UI: f"file://{MLRUNS_DIR}"
# - Serveur distant: "http://<ip_serveur>:5000"
MLFLOW_TRACKING_URI = f"file://{MLRUNS_DIR}"

# Nom par défaut de l'expérience MLflow
MLFLOW_EXPERIMENT_NAME = "house-price-prediction"
# Fichiers spécifiques
MODEL_PATH = OUTPUT_MODELS / "final_model.pkl"
TRAIN_DATA_PATH = DATA_RAW / "train.csv"
TEST_DATA_PATH = DATA_RAW / "test.csv"

# Créer les dossiers s'ils n'existent pas
def ensure_directories():
    """Créer les dossiers nécessaires s'ils n'existent pas."""
    directories = [
        DATA_RAW,
        DATA_INTERIM,
        DATA_PROCESSED,
        OUTPUT_DIR,
        OUTPUT_FIGURES,
        OUTPUT_MODELS,
        OUTPUT_TABLES,
        DASHBOARD_ASSETS,
        DASHBOARD_IMAGES,
        MLRUNS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    return True

# Fonction pour obtenir un chemin relatif depuis n'importe où
def get_path(*path_parts):
    """
    Obtenir un chemin absolu depuis la racine du projet.
    
    Args:
        *path_parts: Parties du chemin
        
    Returns:
        Path: Chemin absolu
    """
    return PROJECT_ROOT.joinpath(*path_parts)

# Fonction pour obtenir un chemin relatif (pour affichage)
def get_relative_path(path):
    """
    Obtenir un chemin relatif depuis la racine du projet.
    
    Args:
        path: Chemin absolu ou relatif
        
    Returns:
        Path: Chemin relatif depuis PROJECT_ROOT
    """
    path = Path(path)
    if path.is_absolute():
        try:
            return path.relative_to(PROJECT_ROOT)
        except ValueError:
            return path
    return path

# Initialiser les dossiers au chargement du module
ensure_directories()

# Informations du projet
PROJECT_NAME = "Laplace Immo - House Price Prediction"
PROJECT_VERSION = "1.0.0"

