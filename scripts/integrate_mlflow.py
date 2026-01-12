#!/usr/bin/env python
"""
<<<<<<< HEAD
Utilitaires MLflow pour le projet House Prices.
Objectifs :
- Centraliser la configuration du tracking (URI locale file://.../mlruns)
- Simplifier la création d'une expérience
- Fournir un helper pour logger params, métriques, tags, modèle et artefacts
=======
Script d'intégration MLflow pour le suivi des expériences.
Utilisation:
    python scripts/integrate_mlflow.py --train
>>>>>>> 03d89c5e545767813a0e754bd48ea5c3fa8a4b3a
"""

import sys
from pathlib import Path
from typing import Dict, Optional

import mlflow
import mlflow.sklearn
<<<<<<< HEAD
=======
import argparse
from pathlib import Path
import sys
>>>>>>> 03d89c5e545767813a0e754bd48ea5c3fa8a4b3a

# === Configuration import src & config ===
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

<<<<<<< HEAD
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
=======
from config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME
from src.model_pipeline import load_data, build_model


def setup_experiment():
    """ Configure l'expérience MLflow """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # Vérifie si l'expérience existe
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(MLFLOW_EXPERIMENT_NAME)
        print(f" Expérience MLflow créée: {MLFLOW_EXPERIMENT_NAME}")
    else:
        print(f" Expérience MLflow existante: {MLFLOW_EXPERIMENT_NAME}")

    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def train_and_log():
    """ Entraîne le modèle et log dans MLFlow """
    X_train, X_test, y_train, y_test = load_data()
    model, params = build_model()

    with mlflow.start_run():
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)

        # Logging MLFlow
        mlflow.log_params(params)
        mlflow.log_metric("r2", score)
        mlflow.sklearn.log_model(model, artifact_path="model")

        print(f" Score modèle = {score:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Lancer l'entraînement avec MLflow")
    args = parser.parse_args()

    setup_experiment()

    if args.train:
        train_and_log()
    else:
        print("ℹ MLFlow configuré. Utilisez --train pour lancer un run.")
>>>>>>> 03d89c5e545767813a0e754bd48ea5c3fa8a4b3a
