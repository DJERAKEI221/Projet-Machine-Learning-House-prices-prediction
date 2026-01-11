#!/usr/bin/env python
"""
Script utilitaire pour intégrer MLFlow dans les notebooks.
Ce script peut être utilisé pour tracker les expériences MLFlow.
"""

import mlflow
import mlflow.sklearn
from pathlib import Path
import sys

# Chemin racine du projet
project_root = Path(__file__).parent.parent
mlruns_dir = project_root / "mlruns"

# Créer le dossier mlruns s'il n'existe pas
mlruns_dir.mkdir(parents=True, exist_ok=True)

# Configurer MLFlow
mlflow.set_tracking_uri(f"file://{mlruns_dir.absolute()}")


def setup_mlflow_experiment(experiment_name="house-price-prediction"):
    """
    Configurer une expérience MLFlow.
    
    Args:
        experiment_name: Nom de l'expérience
        
    Returns:
        experiment_id: ID de l'expérience
    """
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Expérience créée: {experiment_name} (ID: {experiment_id})")
        else:
            experiment_id = experiment.experiment_id
            print(f"Expérience existante: {experiment_name} (ID: {experiment_id})")
        
        mlflow.set_experiment(experiment_name)
        return experiment_id
    except Exception as e:
        print(f"Erreur lors de la configuration de MLFlow: {e}")
        return None


def log_model_metrics(metrics_dict, params_dict=None, tags_dict=None):
    """
    Logger des métriques dans MLFlow.
    
    Args:
        metrics_dict: Dictionnaire de métriques à logger
        params_dict: Dictionnaire de paramètres à logger (optionnel)
        tags_dict: Dictionnaire de tags à logger (optionnel)
    """
    try:
        if params_dict:
            mlflow.log_params(params_dict)
        
        if metrics_dict:
            mlflow.log_metrics(metrics_dict)
        
        if tags_dict:
            mlflow.set_tags(tags_dict)
        
        print(f"Métriques loggées: {list(metrics_dict.keys())}")
    except Exception as e:
        print(f"Erreur lors du logging MLFlow: {e}")


if __name__ == "__main__":
    # Exemple d'utilisation
    setup_mlflow_experiment()
    
    with mlflow.start_run():
        # Exemple de logging
        log_model_metrics(
            metrics_dict={"rmse": 25000.0, "r2": 0.85},
            params_dict={"model": "XGBoost", "n_estimators": 500},
            tags_dict={"dataset": "house-prices"}
        )
        print("\nExemple d'exécution MLFlow terminé")
        print(f"Consultez les résultats avec: mlflow ui --backend-store-uri file://{mlruns_dir.absolute()}")
