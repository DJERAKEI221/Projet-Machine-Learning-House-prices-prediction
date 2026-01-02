"""
Script principal pour l'entraînement du modèle de prédiction des prix immobiliers.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

from src.data_processing import DataProcessor
from src.feature_engineering import FeatureEngineer
from src.modeling import ModelTrainer
from src.utils import prepare_data, calculate_rmse, create_submission
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor
import mlflow

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale pour l'entraînement du modèle."""
    logger.info("Démarrage de l'entraînement du modèle...")
    
    # Configuration MLFlow
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("house_price_prediction")
    
    # Chargement des données
    logger.info("Chargement des données...")
    processor = DataProcessor(data_dir="data/raw")
    train_df, test_df = processor.load_data()
    
    # Nettoyage
    logger.info("Nettoyage des données...")
    train_clean = processor.handle_missing_values(train_df, is_train=True)
    test_clean = processor.handle_missing_values(test_df, is_train=False)
    train_clean = processor.remove_outliers(train_clean, target_col='SalePrice')
    
    # Feature engineering
    logger.info("Feature engineering...")
    fe = FeatureEngineer()
    train_fe = fe.create_features(train_clean)
    test_fe = fe.create_features(test_clean)
    
    # Préparation des données
    logger.info("Préparation des données pour la modélisation...")
    X_train, y_train, X_test = prepare_data(train_fe, test_fe, target_col='SalePrice')
    
    # Transformation log de la variable cible
    y_train_log = np.log1p(y_train)
    
    # Encodage des variables catégorielles
    categorical_cols = processor.get_categorical_columns(X_train)
    X_train_encoded = fe.encode_categorical(X_train, categorical_cols, encoding_type='ordinal')
    X_test_encoded = fe.encode_categorical(X_test, categorical_cols, encoding_type='ordinal')
    
    # One-hot encoding
    remaining_cats = [col for col in categorical_cols 
                     if col in X_train_encoded.columns 
                     and X_train_encoded[col].dtype == 'object']
    X_train_final = pd.get_dummies(X_train_encoded, columns=remaining_cats, prefix=remaining_cats)
    X_test_final = pd.get_dummies(X_test_encoded, columns=remaining_cats, prefix=remaining_cats)
    
    # Aligner les colonnes
    common_cols = [col for col in X_train_final.columns if col in X_test_final.columns]
    X_train_final = X_train_final[common_cols]
    X_test_final = X_test_final[common_cols]
    
    for col in X_train_final.columns:
        if col not in X_test_final.columns:
            X_test_final[col] = 0
    X_test_final = X_test_final[X_train_final.columns]
    
    # Transformation des variables asymétriques
    numeric_cols = processor.get_numeric_columns(X_train_final)
    X_train_transformed = fe.transform_skewed_features(X_train_final, numeric_cols, threshold=0.75)
    X_test_transformed = fe.transform_skewed_features(X_test_final, numeric_cols, threshold=0.75)
    
    # Split train/validation
    X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
        X_train_transformed, y_train_log, test_size=0.2, random_state=42
    )
    
    # Entraînement du modèle
    logger.info("Entraînement du modèle LightGBM...")
    final_model = LGBMRegressor(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.03,
        num_leaves=31,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=5,
        min_child_samples=20,
        random_state=42,
        n_jobs=-1
    )
    
    # Entraînement sur toutes les données
    final_model.fit(X_train_transformed, y_train_log)
    
    # Évaluation
    train_pred_log = final_model.predict(X_train_transformed)
    val_pred_log = final_model.predict(X_val_split)
    
    train_pred = np.expm1(train_pred_log)
    val_pred = np.expm1(val_pred_log)
    y_train_actual = np.expm1(y_train_log)
    y_val_actual = np.expm1(y_val_split)
    
    train_rmse = calculate_rmse(y_train_actual, train_pred)
    val_rmse = calculate_rmse(y_val_actual, val_pred)
    
    logger.info(f"Train RMSE: {train_rmse:.2f}")
    logger.info(f"Validation RMSE: {val_rmse:.2f}")
    
    # Logging MLFlow
    with mlflow.start_run(run_name="final_model"):
        mlflow.log_params({
            'n_estimators': 500,
            'max_depth': 7,
            'learning_rate': 0.03,
            'num_leaves': 31
        })
        mlflow.log_metrics({
            'train_rmse': train_rmse,
            'val_rmse': val_rmse
        })
        mlflow.sklearn.log_model(final_model, "model")
    
    # Prédictions sur le test set
    logger.info("Génération des prédictions sur le test set...")
    test_pred_log = final_model.predict(X_test_transformed)
    test_pred = np.expm1(test_pred_log)
    
    # Sauvegarder les prédictions
    test_ids = test_df['Id']
    create_submission(test_pred, test_ids, output_path='output/submission.csv')
    
    # Sauvegarder le modèle
    trainer = ModelTrainer()
    trainer.save_model(final_model, 'output/models/final_model.pkl')
    
    logger.info("Entraînement terminé avec succès!")
    logger.info(f"Modèle sauvegardé dans output/models/final_model.pkl")
    logger.info(f"Prédictions sauvegardées dans output/submission.csv")


if __name__ == "__main__":
    main()


