# 📁 Structure des Fichiers Requis

Le dashboard cherche tous les fichiers nécessaires dans le dossier `dashboard/output/`

## 📂 Structure Attendue

```
dashboard/
├── app.py
└── output/
    ├── models/                    # Modèles et préprocesseurs
    │   ├── preprocessor.joblib
    │   ├── best_model.joblib (ou best_gradientboosting.joblib, best_xgboost.joblib, etc.)
    │   ├── y_test_log.npy
    │   └── y_pred_*_log.npy
    │
    ├── analysis/                   # Analyses et importances
    │   └── feature_importance_*.csv
    │
    ├── predictions/                # Prédictions et soumissions
    │   └── kaggle_submission_*.csv
    │
    └── data/                       # Données (optionnel)
        ├── train_clean.csv
        └── test_clean.csv
```

## 📋 Fichiers Requis

### 1. Modèles (`output/models/`)
- **preprocessor.joblib** - Préprocesseur scikit-learn
- **best_model.joblib** ou **best_gradientboosting.joblib** ou **best_xgboost.joblib** - Modèle entraîné
- **y_test_log.npy** - Données de test (optionnel)
- **y_pred_*_log.npy** - Prédictions sauvegardées (optionnel)

### 2. Analyses (`output/analysis/`)
- **feature_importance_*.csv** - Importance des variables (avec colonnes 'feature' et 'importance')

### 3. Prédictions (`output/predictions/`)
- **kaggle_submission_*.csv** - Fichiers de soumission avec colonnes 'Id' et 'SalePrice'

### 4. Données (`output/data/` ou `output/`)
- **train_clean.csv** - Données d'entraînement nettoyées
- **test_clean.csv** - Données de test (optionnel, pour calculer les métriques)

## 🔍 Ordre de Recherche

Le dashboard cherche les fichiers dans cet ordre :

### Pour les données d'entraînement :
1. `dashboard/output/train_clean.csv`
2. `dashboard/output/data/train_clean.csv`
3. `dashboard/train_clean.csv` (fallback)
4. Autres emplacements (fallback)

### Pour les modèles :
1. `dashboard/output/models/best_model.joblib`
2. `dashboard/output/models/best_gradientboosting.joblib`
3. `dashboard/output/models/best_xgboost.joblib`
4. `dashboard/output/models/best_randomforest.joblib`
5. `dashboard/output/models/best_lightgbm.joblib`

### Pour les données de test :
1. `dashboard/output/data/test_clean.csv`
2. `dashboard/output/test_clean.csv`
3. `dashboard/output/data/test.csv`
4. `dashboard/output/test.csv`

## ✅ Vérification

Pour vérifier que tous les fichiers sont présents, exécutez dans Spyder :

```python
from pathlib import Path

output_dir = Path("dashboard/output")
models_dir = output_dir / "models"
analysis_dir = output_dir / "analysis"
predictions_dir = output_dir / "predictions"

print("Modèles:")
for f in models_dir.glob("*.joblib"):
    print(f"  ✓ {f.name}")

print("\nAnalyses:")
for f in analysis_dir.glob("*.csv"):
    print(f"  ✓ {f.name}")

print("\nPrédictions:")
for f in predictions_dir.glob("*.csv"):
    print(f"  ✓ {f.name}")
```

## 🚨 Si des fichiers manquent

Le dashboard fonctionnera toujours mais certaines fonctionnalités seront limitées :
- **Sans données d'entraînement** : Les pages Exploration et Analyse ne fonctionneront pas
- **Sans modèle** : Le Simulateur ne fonctionnera pas
- **Sans prédictions** : La page Prédictions ne fonctionnera pas
