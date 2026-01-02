"""
Module pour charger et gérer le modèle de prédiction.
"""

import joblib
from pathlib import Path
from functools import lru_cache
import logging
import sys

# Ajouter la racine du projet au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Importer config pour les chemins
try:
    from config import MODEL_PATH, SRC_DIR
except ImportError:
    # Fallback si config n'est pas disponible
    MODEL_PATH = project_root / "output" / "models" / "final_model.pkl"
    SRC_DIR = project_root / "src"

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_model():
    """
    Charger le modèle entraîné.
    Utilise le cache pour éviter de recharger à chaque fois.
    
    Returns:
        model: Modèle entraîné ou None
    """
    if not MODEL_PATH.exists():
        logger.warning(f"Modèle non trouvé: {MODEL_PATH}")
        logger.info("Entraînez d'abord le modèle avec: python train.py")
        return None
    
    try:
        model = joblib.load(MODEL_PATH)
        logger.info(f"Modèle chargé avec succès depuis {MODEL_PATH}")
        return model
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {e}")
        return None


def get_processors():
    """
    Obtenir les processeurs de données.
    
    Returns:
        tuple: (DataProcessor, FeatureEngineer)
    """
    processor = DataProcessor()
    feature_engineer = FeatureEngineer()
    return processor, feature_engineer


def predict_price(model, processor, feature_engineer, features_dict):
    """
    Faire une prédiction de prix.
    
    Args:
        model: Modèle entraîné
        processor: DataProcessor
        feature_engineer: FeatureEngineer
        features_dict: Dictionnaire des caractéristiques de la maison
        
    Returns:
        dict: Résultat de la prédiction avec prix et métadonnées
    """
    if model is None:
        return {
            'success': False,
            'error': 'Modèle non chargé'
        }
    
    try:
        import pandas as pd
        
        # Convertir en DataFrame
        house_df = pd.DataFrame([features_dict])
        
        # Preprocessing
        house_df = processor.handle_missing_values(house_df, is_train=False)
        house_df = feature_engineer.create_features(house_df)
        
        # Prédiction
        prediction = model.predict(house_df)[0]
        
        # Si le modèle prédit en log, convertir
        import numpy as np
        if prediction < 1000:  # Heuristique
            prediction = np.expm1(prediction)
        
        return {
            'success': True,
            'predicted_price': float(prediction),
            'confidence': 0.85  # Placeholder
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        return {
            'success': False,
            'error': str(e)
        }

