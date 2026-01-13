#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    mean_absolute_percentage_error, max_error
)
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

import lightgbm as lgb

# =========================
# CONFIG MLflow
# =========================
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("house-price-model-testing")

RANDOM_STATE = 42
TARGET = "SalePrice"


# ============================================================
# UTILITAIRES METRIQUES
# ============================================================
def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def get_all_performances(value_train: tuple, values_test: tuple, metrics: list):
    test_perfs, train_perfs, metric_names = [], [], []
    for metric_func in metrics:
        metric_names.append(metric_func.__name__)
        train_perfs.append(metric_func(*value_train))
        test_perfs.append(metric_func(*values_test))
    return pd.DataFrame({"metric": metric_names, "train": train_perfs, "test": test_perfs})


METRICS_LOG = [
    r2_score, mean_squared_error, rmse,
    mean_absolute_error, mean_absolute_percentage_error, max_error
]


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
def load_data():
    train_path = "data/processed/train_outliers_treated.csv"
    test_path = "data/processed/test_outliers_treated.csv"

    assert os.path.exists(train_path), f"Fichier manquant: {train_path}"
    assert os.path.exists(test_path), f"Fichier manquant: {test_path}"

    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)

    assert TARGET in df_train.columns, f"{TARGET} absent dans train"

    print("📂 Données chargées")
    return df_train, df_test


# ============================================================
# MAIN
# ============================================================
def main():

    df_train, df_test = load_data()

    X = df_train.drop(columns=[TARGET])
    y_raw = df_train[TARGET]

    print(f"X: {X.shape} | y_raw: {y_raw.shape}")

    # LOG1P pour entrainement
    y = np.log1p(y_raw)

    # Split train/test interne
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE
    )

    print("✅ Split OK")
    print(f"Train: {X_train.shape} | Test: {X_test.shape}")

    # ===============================
    # PREPROCESSING (à adapter si besoin)
    # ===============================
    try:
        preprocessor
    except NameError:
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        num_cols = X_train.select_dtypes(include=["int64", "float64"]).columns
        cat_cols = X_train.select_dtypes(include=["object"]).columns

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
            ]
        )
        print("⚠️ preprocessor n'existait pas → pipeline par défaut ajouté")

    # ===============================
    # MODELES + GRIDSEARCH
    # ===============================
    models = {
        "Dummy": {
            "pipe": Pipeline([("preprocess", preprocessor), ("model", DummyRegressor(strategy="median"))]),
            "params": {}
        },
        "Ridge": {
            "pipe": Pipeline([("preprocess", preprocessor), ("model", Ridge())]),
            "params": {"model__alpha": [0.1, 0.5, 1.0, 2.0, 10.0]}
        },
        "Lasso": {
            "pipe": Pipeline([("preprocess", preprocessor), ("model", Lasso(max_iter=50000))]),
            "params": {"model__alpha": [1e-3, 1e-2, 1e-1]}
        },
        "RandomForest": {
            "pipe": Pipeline([("preprocess", preprocessor), ("model", RandomForestRegressor(random_state=42, n_jobs=-1))]),
            "params": {
                "model__n_estimators": [200, 400],
                "model__max_depth": [None, 10],
                "model__min_samples_leaf": [1, 5],
            }
        },
        "GradientBoosting": {
            "pipe": Pipeline([("preprocess", preprocessor), ("model", GradientBoostingRegressor(random_state=42))]),
            "params": {
                "model__n_estimators": [200, 400],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [3, 4]
            }
        },
        "LightGBM": {
            "pipe": Pipeline([("preprocess", preprocessor), ("model", lgb.LGBMRegressor(objective="regression", random_state=42))]),
            "params": {
                "model__n_estimators": [500, 1000],
                "model__learning_rate": [0.03, 0.05],
                "model__max_depth": [-1, 6],
                "model__num_leaves": [31, 63]
            }
        }
    }

    best_rmse = np.inf
    best_model = None
    best_name = None

    # ===============================
    # MLflow Logging
    # ===============================
    for name, obj in models.items():

        print(f"📌 Training: {name}")
        with mlflow.start_run(run_name=name):

            gs = GridSearchCV(
                estimator=obj["pipe"],
                param_grid=obj["params"],
                scoring="neg_root_mean_squared_error",
                cv=3,
                n_jobs=-1
            )

            t0 = time.time()
            gs.fit(X_train, y_train)
            duration = round(time.time() - t0, 3)

            best = gs.best_estimator_
            params = gs.best_params_

            # Predictions
            yhat_train = best.predict(X_train)
            yhat_test = best.predict(X_test)

            # Log metrics
            rmse_val = rmse(y_test, yhat_test)
            mlflow.log_metric("rmse", rmse_val)
            mlflow.log_metric("fit_time", duration)
            mlflow.log_params(params)

            print(f"✔ {name}: RMSE={rmse_val:.4f}")

            if rmse_val < best_rmse:
                best_rmse = rmse_val
                best_name = name
                best_model = best

    print(f"\n🏆 Best model: {best_name} (RMSE={best_rmse:.4f})")

    # ===============================
    # Sauvegarde BEST MODEL
    # ===============================
    os.makedirs("output/models", exist_ok=True)
    path = "output/models/best_model.pkl"
    joblib.dump(best_model, path)

    with mlflow.start_run(run_name="best_model"):
        mlflow.log_param("best_model", best_name)
        mlflow.log_metric("best_rmse", best_rmse)
        mlflow.sklearn.log_model(best_model, "best_model")

    print(f"📁 Best model saved at: {path}")


if __name__ == "__main__":
    main()
