# Guide MLFlow - Tracking des Expériences

Ce guide explique comment utiliser MLFlow pour tracker les expériences de machine learning dans ce projet.

## Installation

MLFlow est déjà inclus dans `requirements.txt`. Pour l'installer :

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Lancer l'Interface MLFlow UI

Pour visualiser les résultats du tracking :

```bash
# Option 1: Utiliser le script fourni
python scripts/run_mlflow_ui.py

# Option 2: Commande directe
mlflow ui --backend-store-uri file://./mlruns --port 5000
```

L'interface sera accessible sur : **http://localhost:5000**

### 2. Intégrer MLFlow dans les Notebooks

Pour intégrer MLFlow dans vos notebooks, utilisez le script utilitaire :

```python
# Dans un notebook
import sys
from pathlib import Path
sys.path.insert(0, str(Path("../scripts").resolve()))

from integrate_mlflow import setup_mlflow_experiment, log_model_metrics
import mlflow

# Configurer l'expérience
setup_mlflow_experiment("house-price-prediction")

# Dans une boucle d'entraînement
with mlflow.start_run():
    # Logger les paramètres
    mlflow.log_params({
        "model": "XGBoost",
        "n_estimators": 500,
        "max_depth": 5,
        "learning_rate": 0.01
    })
    
    # Entraîner le modèle
    model.fit(X_train, y_train)
    
    # Calculer les métriques
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    
    train_rmse = calculate_rmse(y_train, train_pred)
    val_rmse = calculate_rmse(y_val, val_pred)
    
    # Logger les métriques
    mlflow.log_metrics({
        "train_rmse": train_rmse,
        "val_rmse": val_rmse,
        "train_r2": r2_score(y_train, train_pred),
        "val_r2": r2_score(y_val, val_pred)
    })
    
    # Logger le modèle
    mlflow.sklearn.log_model(model, "model")
```

### 3. Structure des Expériences

Les expériences MLFlow sont stockées dans `mlruns/`. Chaque run contient :
- **Métriques** : RMSE, R², MAE, etc.
- **Paramètres** : Hyperparamètres du modèle
- **Tags** : Métadonnées (dataset, version, etc.)
- **Artifacts** : Modèles sauvegardés, graphiques

### 4. Visualiser les Résultats

Une fois MLFlow UI lancé :
1. Ouvrir http://localhost:5000 dans votre navigateur
2. Sélectionner l'expérience "house-price-prediction"
3. Comparer les différents runs
4. Visualiser les métriques, paramètres et graphiques
5. Télécharger les modèles

## Intégration avec GitHub Actions

Le workflow CI/CD peut être configuré pour :
- Lancer MLFlow UI dans un job séparé
- Uploader les artifacts MLFlow
- Comparer les performances entre runs

## Notes

- Le dossier `mlruns/` est dans `.gitignore` (ne pas commiter les runs)
- MLFlow UI doit être lancé localement pour visualiser les résultats
- Pour la production, utiliser MLFlow Tracking Server (optionnel)
