"""
Utility functions for the house price prediction project.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_data(train_df: pd.DataFrame, test_df: pd.DataFrame, 
                target_col: str = 'SalePrice') -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Prepare data for modeling by separating features and target.
    
    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame
        target_col: Name of target column
        
    Returns:
        Tuple of (X_train, y_train, X_test)
    """
    # Separate target from features
    if target_col in train_df.columns:
        y_train = train_df[target_col]
        X_train = train_df.drop(columns=[target_col])
    else:
        raise ValueError(f"Target column '{target_col}' not found in training data")
    
    # Test data (no target)
    X_test = test_df.copy()
    
    # Align columns
    common_cols = [col for col in X_train.columns if col in X_test.columns]
    X_train = X_train[common_cols]
    X_test = X_test[common_cols]
    
    logger.info(f"Prepared data: X_train shape {X_train.shape}, X_test shape {X_test.shape}")
    
    return X_train, y_train, X_test


def create_submission(predictions: np.ndarray, test_ids: pd.Series, 
                     output_path: str = "output/submission.csv"):
    """
    Create submission file in the required format.
    
    Args:
        predictions: Model predictions
        test_ids: Test set IDs
        output_path: Path to save submission file
    """
    submission = pd.DataFrame({
        'Id': test_ids,
        'SalePrice': predictions
    })
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output_path, index=False)
    logger.info(f"Submission file saved to {output_path}")


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Root Mean Squared Error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        RMSE value
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def get_feature_importance(model: Any, feature_names: list, top_n: int = 20) -> pd.DataFrame:
    """
    Get feature importance from a model.
    
    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        DataFrame with feature importance
    """
    if hasattr(model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df.head(top_n)
    else:
        logger.warning("Model does not have feature_importances_ attribute")
        return pd.DataFrame()


def select_features_by_correlation(train_df: pd.DataFrame, 
                                   target_col: str = 'SalePrice',
                                   min_target_corr: float = 0.3,
                                   max_feature_corr: float = 0.85) -> List[str]:
    """
    Sélectionne les features basées sur la corrélation :
    - Garde toutes les variables très corrélées à la variable cible
    - Élimine les variables explicatives corrélées entre elles
    
    Args:
        train_df: DataFrame d'entraînement avec la variable cible
        target_col: Nom de la variable cible
        min_target_corr: Corrélation minimale avec la cible pour être retenue (valeur absolue)
        max_feature_corr: Corrélation maximale entre features pour éviter la multicolinéarité
        
    Returns:
        Liste des noms de features sélectionnées
    """
    logger.info("=" * 80)
    logger.info("SELECTION DE FEATURES PAR CORRELATION")
    logger.info("=" * 80)
    
    # Séparer les features et la cible
    if target_col not in train_df.columns:
        raise ValueError(f"Variable cible '{target_col}' non trouvée dans les données")
    
    # Sélectionner uniquement les colonnes numériques
    numeric_cols = train_df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
    
    # Calculer les corrélations avec la variable cible
    target_correlations = train_df[numeric_cols + [target_col]].corr()[target_col].abs()
    target_correlations = target_correlations.drop(target_col)
    
    # Étape 1 : Sélectionner les variables très corrélées à la cible
    highly_correlated = target_correlations[target_correlations >= min_target_corr].index.tolist()
    
    logger.info(f"\nÉtape 1 : Variables corrélées à {target_col} (|corr| >= {min_target_corr})")
    logger.info(f"Nombre de variables sélectionnées : {len(highly_correlated)}")
    
    if len(highly_correlated) == 0:
        logger.warning(f"Aucune variable avec corrélation >= {min_target_corr} trouvée")
        return []
    
    # Afficher les corrélations
    corr_df = pd.DataFrame({
        'Variable': highly_correlated,
        'Corrélation': [target_correlations[var] for var in highly_correlated]
    }).sort_values('Corrélation', ascending=False)
    
    logger.info(f"\nTop variables corrélées à {target_col}:")
    for idx, row in corr_df.head(20).iterrows():
        logger.info(f"  {row['Variable']}: {row['Corrélation']:.4f}")
    
    # Étape 2 : Éliminer les variables corrélées entre elles
    logger.info(f"\nÉtape 2 : Élimination des variables corrélées entre elles (|corr| > {max_feature_corr})")
    
    # Calculer la matrice de corrélation entre les features sélectionnées
    feature_corr_matrix = train_df[highly_correlated].corr().abs()
    
    # Créer un masque pour ignorer la diagonale (corrélation avec soi-même)
    np.fill_diagonal(feature_corr_matrix.values, 0)
    
    # Trouver les paires de variables très corrélées
    selected_features = highly_correlated.copy()
    removed_features = []
    
    # Parcourir la matrice de corrélation
    for i, var1 in enumerate(highly_correlated):
        if var1 not in selected_features:
            continue
        
        for var2 in highly_correlated[i+1:]:
            if var2 not in selected_features:
                continue
            
            corr_value = feature_corr_matrix.loc[var1, var2]
            
            if corr_value > max_feature_corr:
                # Garder celle qui a la meilleure corrélation avec la cible
                corr1_with_target = target_correlations[var1]
                corr2_with_target = target_correlations[var2]
                
                if corr1_with_target >= corr2_with_target:
                    # Garder var1, retirer var2
                    if var2 in selected_features:
                        selected_features.remove(var2)
                        removed_features.append({
                            'variable': var2,
                            'corr_with_target': corr2_with_target,
                            'corr_with': var1,
                            'corr_value': corr_value
                        })
                        logger.info(f"  Retiré '{var2}' (corr avec cible: {corr2_with_target:.4f}, corr avec '{var1}': {corr_value:.4f})")
                else:
                    # Garder var2, retirer var1
                    if var1 in selected_features:
                        selected_features.remove(var1)
                        removed_features.append({
                            'variable': var1,
                            'corr_with_target': corr1_with_target,
                            'corr_with': var2,
                            'corr_value': corr_value
                        })
                        logger.info(f"  Retiré '{var1}' (corr avec cible: {corr1_with_target:.4f}, corr avec '{var2}': {corr_value:.4f})")
                        break  # var1 a été retiré, passer à la suivante
    
    logger.info(f"\nRésumé de la sélection :")
    logger.info(f"  Variables initiales (corrélées à cible) : {len(highly_correlated)}")
    logger.info(f"  Variables retirées (multicolinéarité) : {len(removed_features)}")
    logger.info(f"  Variables finales sélectionnées : {len(selected_features)}")
    
    logger.info(f"\nVariables finales sélectionnées ({len(selected_features)}):")
    for var in sorted(selected_features):
        corr_val = target_correlations[var]
        logger.info(f"  {var}: {corr_val:.4f}")
    
    logger.info("=" * 80)
    
    return selected_features


