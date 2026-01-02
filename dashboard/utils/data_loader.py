"""
Module pour charger et gérer les données.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache
import logging
import sys

# Ajouter la racine du projet au path pour importer config
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config import TRAIN_DATA_PATH, TEST_DATA_PATH, DATA_RAW
except ImportError:
    # Fallback si config n'est pas disponible
    TRAIN_DATA_PATH = project_root / "data" / "raw" / "train.csv"
    TEST_DATA_PATH = project_root / "data" / "raw" / "test.csv"
    DATA_RAW = project_root / "data" / "raw"

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_train_data():
    """
    Charger les données d'entraînement.
    Utilise le cache pour éviter de recharger à chaque fois.
    
    Returns:
        pd.DataFrame: DataFrame des données d'entraînement
    """
    if not TRAIN_DATA_PATH.exists():
        logger.warning(f"Fichier de données non trouvé: {TRAIN_DATA_PATH}")
        return None
    
    try:
        df = pd.read_csv(TRAIN_DATA_PATH)
        logger.info(f"Données chargées: {len(df)} observations, {len(df.columns)} colonnes")
        return df
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {e}")
        return None


@lru_cache(maxsize=1)
def load_test_data():
    """
    Charger les données de test.
    
    Returns:
        pd.DataFrame: DataFrame des données de test
    """
    if not TEST_DATA_PATH.exists():
        logger.warning(f"Fichier de données de test non trouvé: {TEST_DATA_PATH}")
        return None
    
    try:
        df = pd.read_csv(TEST_DATA_PATH)
        logger.info(f"Données de test chargées: {len(df)} observations, {len(df.columns)} colonnes")
        return df
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données de test: {e}")
        return None


def get_numeric_columns(df):
    """Obtenir les colonnes numériques."""
    if df is None:
        return []
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df):
    """Obtenir les colonnes catégorielles."""
    if df is None:
        return []
    return df.select_dtypes(include=['object']).columns.tolist()


def get_unique_values(df, column):
    """Obtenir les valeurs uniques d'une colonne."""
    if df is None or column not in df.columns:
        return []
    return sorted(df[column].dropna().unique().tolist())


def get_column_statistics(df, column):
    """Obtenir les statistiques d'une colonne numérique."""
    if df is None or column not in df.columns:
        return {}
    
    if df[column].dtype in [np.number]:
        return {
            'min': float(df[column].min()),
            'max': float(df[column].max()),
            'mean': float(df[column].mean()),
            'median': float(df[column].median()),
            'std': float(df[column].std())
        }
    return {}

