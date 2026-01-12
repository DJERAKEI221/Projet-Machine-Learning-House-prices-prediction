import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# =========================
# CONFIG MLflow
# =========================
mlflow.set_tracking_uri("file:../mlruns")
mlflow.set_experiment("house-price-model-testing")


def evaluate_model(y_true, y_pred):
    """Compute evaluation metrics."""
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2


def main():

    print("===== Loading Dataset =====")
    df = pd.read_csv("data/processed/train_final.csv")

    # On assume que la colonne cible s'appelle 'SalePrice'
    target_col = "SalePrice"
    assert target_col in df.columns, f"colonne cible {target_col} introuvable"

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # =========================
    # MODELES
    # =========================
    models = {
        "LightGBM": LGBMRegressor(
            n_estimators=500, max_depth=6, learning_rate=0.01, num_leaves=31,
            feature_fraction=0.9, bagging_fraction=0.9, bagging_freq=5,
            min_child_samples=20, random_state=42, n_jobs=-1, verbose=-1
        ),
        "XGBoost": XGBRegressor(
            n_estimators=500, max_depth=5, learning_rate=0.01, subsample=0.9,
            colsample_bytree=0.9, min_child_weight=3, random_state=42, n_estimators_thread=1
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=300, max_depth=12, min_samples_split=5, min_samples_leaf=2,
            random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=300, max_depth=5, learning_rate=0.01,
            min_samples_split=5, min_samples_leaf=2, random_state=42
        )
    }

    best_rmse = np.inf
    best_model = None
    best_model_name = None

    print("===== Training & Logging =====")

    for name, model in models.items():

        print(f"📌 Training: {name}")

        with mlflow.start_run(run_name=name):

            # Log hyperparams du modèle
            params = model.get_params()
            mlflow.log_params(params)

            # Fit
            model.fit(X_train, y_train)

            # Predict
            y_pred = model.predict(X_test)

            # Compute metrics
            rmse, mae, r2 = evaluate_model(y_test, y_pred)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("r2", r2)

            # Log modèle
            mlflow.sklearn.log_model(model, "model")

            print(f"✔ {name} done: RMSE={rmse:.4f}")

            if rmse < best_rmse:
                best_rmse = rmse
                best_model = model
                best_model_name = name

    print("===== Best Model Selection =====")
    print(f" Best Model: {best_model_name} (RMSE={best_rmse:.4f})")

    # Sauvegarde best model localement
    os.makedirs("output/models", exist_ok=True)
    best_model_path = f"output/models/best_model.pkl"
    import joblib
    joblib.dump(best_model, best_model_path)

    print(f"📁 Best model saved to: {best_model_path}")

    # Log le best_model dans MLflow
    with mlflow.start_run(run_name="best_model"):
        mlflow.log_param("best_model_name", best_model_name)
        mlflow.log_metric("best_model_rmse", best_rmse)
        mlflow.sklearn.log_model(best_model, "best_model")

    print(" Training completed successfully !")


if __name__ == "__main__":
    main()
