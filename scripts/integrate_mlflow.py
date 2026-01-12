#!/usr/bin/env python
"""
Script d'intégration MLflow pour le suivi des expériences.
Utilisation:
    python scripts/integrate_mlflow.py --train
"""

import mlflow
import mlflow.sklearn
import argparse
from pathlib import Path
import sys

# === Configuration import src & config ===
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

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
