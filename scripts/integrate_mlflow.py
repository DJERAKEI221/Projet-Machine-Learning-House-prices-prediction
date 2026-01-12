#!/usr/bin/env python
"""
Utilitaires MLflow pour le projet House Prices.
Objectifs :
- Centraliser la configuration du tracking (URI locale file://.../mlruns)
- Simplifier la création d'une expérience
- Fournir un helper pour logger params, métriques, tags, modèle et artefacts
"""

import sys
from pathlib import Path
from typing import Dict, Optional

import mlflow
import mlflow.sklearn

# Chemin racine du projet
project_root = Path(__file__).parent.parent
mlruns_dir = project_root / "mlruns"

# Créer le dossier mlruns s'il n'existe pas
mlruns_dir.mkdir(parents=True, exist_ok=True)

# Configurer MLflow (tracking local)
mlflow.set_tracking_uri(f"file://{mlruns_dir.absolute()}")


def setup_mlflow_experiment(experiment_name: str = "house-price-prediction") -> Optional[str]:
    """
    Crée (si besoin) et active une expérience MLflow.
    Retourne l'ID de l'expérience ou None en cas d'erreur.
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
        print(f"Erreur lors de la configuration de MLflow: {e}")
        return None


def log_run(
    model,
    metrics: Dict[str, float],
    params: Optional[Dict[str, str]] = None,
    tags: Optional[Dict[str, str]] = None,
    artifact_path: str = "model",
    run_name: Optional[str] = None,
):
    """
    Helper compact pour logger un run MLflow (params + métriques + modèle).
    - model : pipeline scikit-learn (préprocesseur inclus si déjà packagé)
    - metrics : dict de métriques (floats)
    - params : dict de paramètres (ex: best_params_)
    - tags : dict de tags (ex: cible, version de features)
    - artifact_path : sous-dossier pour le modèle loggé
    - run_name : nom du run (optionnel)
    """
    with mlflow.start_run(run_name=run_name):
        if params:
            mlflow.log_params(params)
        if metrics:
            mlflow.log_metrics(metrics)
        if tags:
            mlflow.set_tags(tags)

        # Log du modèle (scikit-learn)
        mlflow.sklearn.log_model(model, artifact_path=artifact_path)


if __name__ == "__main__":
    # Exemple minimal
    setup_mlflow_experiment()
    
    # Exemple : logger un run factice sans modèle (metrics only)
    with mlflow.start_run(run_name="demo_no_model"):
        mlflow.log_params({"model": "demo", "note": "exemple"})
        mlflow.log_metrics({"rmse": 25000.0, "r2": 0.85})
        mlflow.set_tags({"dataset": "house-prices"})

    print("\nExemple terminé. Consultez: mlflow ui --backend-store-uri file://{}".format(mlruns_dir.absolute()))
