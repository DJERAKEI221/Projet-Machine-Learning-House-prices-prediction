# Projet Machine Learning - Prédiction des Prix Immobiliers

## Projet Laplace Immo

Ce projet est réalisé dans le cadre du cours de Machine Learning I dispensé aux Élèves Ingénieurs Statisticiens Économistes (ISE-2) à l'École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE).

## Table des Matières

1. [Description du Projet](#description-du-projet)
2. [Objectifs](#objectifs)
3. [Structure du Projet](#structure-du-projet)
4. [Installation](#installation)
5. [Utilisation](#utilisation)
6. [Organisation du Répertoire](#organisation-du-répertoire)
7. [Fonctionnalités Principales](#fonctionnalités-principales)
8. [Résultats et Analyses](#résultats-et-analyses)
9. [Documentation](#documentation)
10. [CI/CD et Tests](#cicd-et-tests)
11. [Auteurs et Licence](#auteurs-et-licence)
12. [Références](#références)

## Description du Projet

Ce projet vise à prédire le prix de vente des maisons en utilisant des techniques avancées de machine learning. Le dataset utilisé provient de la compétition Kaggle "House Prices: Advanced Regression Techniques" et contient 79 variables explicatives décrivant différentes caractéristiques des maisons (qualité, surface, localisation, etc.).

Le projet comprend une pipeline complète de machine learning, allant de l'exploration des données à la création d'un modèle de prédiction, en passant par le feature engineering, l'entraînement de modèles multiples, et le déploiement via un dashboard interactif.

## Objectifs

- **Prédiction précise** : Développer un modèle capable de prédire avec précision le prix de vente des maisons
- **Analyse approfondie** : Identifier les variables les plus importantes pour la prédiction du prix
- **Visualisation interactive** : Créer un dashboard web interactif pour explorer les données et faire des prédictions
- **Pratiques professionnelles** : Mettre en place un pipeline CI/CD, des tests unitaires, et un suivi des expériences avec MLFlow
- **Documentation complète** : Documenter chaque étape du processus et les décisions prises

## Structure du Projet

```
ProjetMachine-Learning-House-prices-prediction/
├── dashboard/                # App Dash (app.py, components/, pages/, utils/, assets/)
├── data/
│   ├── raw/                  # Données brutes (ex: data_description.txt)
│   ├── processed/            # Données nettoyées / features
│   └── interim/
├── docs/                     # Docs et analyses (MD, PDF, DOCX)
├── notebooks/
│   ├── api_fastapi.ipynb     # API FastAPI légère pour l'inférence
│   ├── exploration_base_donnees.ipynb
│   ├── feature_engineering.ipynb
│   ├── traitement.ipynb
│   ├── data/processed/*.csv  # Exports intermédiaires depuis notebooks
│   └── output/*.joblib       # Modèles/artefacts sauvegardés
├── scripts/
│   ├── integrate_mlflow.py   # Helpers MLflow (tracking local)
│   ├── run_mlflow_ui.py      # Lancement de l'UI MLflow (http://localhost:5000)
│   ├── save_final_model.py   # Sauvegarde du modèle final
│   ├── check_pep8.py / format_code.py
│   └── autres utilitaires (fix_*.py, replace_r_squared.py)
├── src/
│   └── feature_engineering.py
├── output/
│   ├── figures/*.png         # Graphiques générés
│   ├── models_modele/        # (répertoire prévu pour modèles)
│   └── tables/*.csv
├── mlruns/                   # Stockage local MLflow (expériences)
├── tests/                    # Tests unitaires (pytest)
├── config.py, pyproject.toml, requirements*.txt, setup.py, README_*.md
└── README.md (ce fichier)
```

## Installation

### Prérequis

- Python 3.9, 3.10 ou 3.11
- pip (gestionnaire de paquets Python)
- Git (pour cloner le repository)

### Installation des Dépendances

```bash
# Cloner le repository
git clone <url-du-repository>
cd ProjetMachine-Learning-House-prices-prediction

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances principales
pip install -r requirements.txt

# Installer les dépendances pour le dashboard
pip install -r requirements_api.txt

# Installer le package en mode développement (optionnel)
pip install -e .
```

### Dépendances Principales

- **Machine Learning** : scikit-learn, XGBoost, LightGBM
- **Traitement des données** : pandas, numpy, scipy
- **Visualisation** : matplotlib, seaborn, plotly
- **Dashboard** : dash, dash-bootstrap-components
- **Tracking** : mlflow
- **Tests** : pytest, pytest-cov
- **Qualité de code** : flake8, black
- **Utilitaires** : joblib (sauvegarde modèles)

## Utilisation

### 1. Exploration des Données

```bash
# Lancer Jupyter
jupyter notebook

# Ouvrir notebooks/exploration_base_donnees.ipynb
# Suivre les cellules pour explorer les données
```

### 2. Feature Engineering

```bash
# Ouvrir notebooks/feature_engineering.ipynb
# Exécuter les cellules pour créer les features
```

### 3. Entraînement du Modèle

```bash
# Ouvrir notebooks/modeling_modele.ipynb
# Exécuter les cellules pour entraîner le modèle
```

### 4. Dashboard Interactif

```bash
# Depuis la racine du projet
cd dashboard
python app.py

# Ou directement
python dashboard/app.py

# Accéder au dashboard
# http://localhost:8050
```

### 5. MLFlow UI (Tracking des Expériences)

```bash
# Lancer l'interface MLFlow
pip install mlflow           # si non installé (depuis le même environnement que Jupyter)
python scripts/run_mlflow_ui.py

# Accéder à l'interface
# http://localhost:5000
```

Dans un notebook Jupyter, installez-le avec la magie pour le kernel actif :

```python
%pip install mlflow
```

### 6. Tests Unitaires

```bash
# Exécuter tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ -v --cov=src --cov-report=html
```

### 7. Vérification de Code

```bash
# Vérifier la conformité PEP 8
python scripts/check_pep8.py

# Formater le code
python scripts/format_code.py
```

## Organisation du Répertoire

### Dashboard (`dashboard/`)

Application Dash interactive permettant de visualiser les données et faire des prédictions. Architecture modulaire avec séparation des composants, pages et callbacks.

**Composants principaux** :
- `app.py` : Point d'entrée de l'application
- `components/` : Composants réutilisables (graphiques, header, sidebar, formulaires)
- `pages/` : Pages du dashboard (dashboard principal, prédiction, sensibilité, explicabilité, recommandations)
- `utils/` : Utilitaires pour le chargement des données et du modèle
- `assets/` : Ressources statiques (CSS, images)

### Données (`data/`)

Organisation des données selon le principe de "raw data" : les données brutes ne sont jamais modifiées.

- **`raw/`** : Données originales du dataset Kaggle (train.csv, test.csv, description)
- **`interim/`** : Données intermédiaires (optionnel, pour étapes temporaires)
- **`processed/`** : Données traitées à utiliser pour l'entraînement
  - `*_cleaned.csv` : Données nettoyées (valeurs manquantes traitées)
  - `*_outliers_treated.csv` : Données après traitement des outliers
  - `*_features.csv` : Données avec features créées
  - `*_final.csv` : Données finales prêtes pour l'entraînement

### Documentation (`docs/`)

Documentation détaillée sur différents aspects du projet :

- **`GESTION_VALEURS_MANQUANTES_OUTLIERS.md`** : Stratégies de gestion des valeurs manquantes et outliers
- **`SELECTION_VARIABLES_MODELE.md`** : Sélection objective des variables pour le modèle
- **`TRANSFORMATION_LOGARITHMIQUE.md`** : Justification des transformations logarithmiques

### Notebooks (`notebooks/`)

Notebooks Jupyter organisés par étape du pipeline :

1. **`exploration_base_donnees.ipynb`** : Exploration complète des données
   - Analyse descriptive
   - Détection des valeurs manquantes
   - Traitement des outliers
   - Analyse de corrélation
   - Tests ANOVA pour variables qualitatives

2. **`feature_engineering.ipynb`** : Création et transformation des features
   - Création de nouvelles features
   - Encodage des variables catégorielles
   - Transformation des variables asymétriques

3. **`modeling_modele.ipynb`** : Entraînement et évaluation des modèles
   - Comparaison de plusieurs algorithmes (LightGBM, XGBoost, Random Forest, Gradient Boosting)
   - Sélection du meilleur modèle
   - Métriques d'évaluation

4. **`explainability.ipynb`** : Analyse d'explicabilité avec SHAP

5. **`sensitivity_analysis.ipynb`** : Analyse de sensibilité des variables

### Résultats (`output/`)

- **`figures/`** : Tous les graphiques générés (corrélations, distributions, importance des features, etc.)
- **`models_modele/`** : Modèles entraînés et résultats
  - `model_modele.pkl` : Modèle sauvegardé
  - `submission_modele.csv` : Prédictions sur le test set
  - `model_comparison_modele.csv` : Comparaison des performances
  - `final_metrics_modele.txt` : Métriques finales
- **`tables/`** : Tableaux d'analyse (ex: variables sans valeurs manquantes)

### Code Source (`src/`)

Modules Python réutilisables :

- **`feature_engineering.py`** : Classe `FeatureEngineer` pour le feature engineering
  - `create_features()` : Création de nouvelles features
  - `encode_categorical()` : Encodage des variables catégorielles
  - `transform_skewed_features()` : Transformation des variables asymétriques

### Tests (`tests/`)

Tests unitaires organisés par module :

- `test_feature_engineering.py` : Tests pour le module feature engineering
- `test_data_processing.py` : Tests pour data processing (désactivés si module inexistant)
- `test_modeling.py` : Tests pour modeling (désactivés si module inexistant)
- `test_utils.py` : Tests pour utilitaires (désactivés si module inexistant)

### Scripts (`scripts/`)

Scripts utilitaires pour le développement :

- `check_pep8.py` : Vérification de la conformité PEP 8
- `format_code.py` : Formatage automatique du code avec Black
- `integrate_mlflow.py` : Utilitaires pour intégrer MLFlow dans les notebooks
- `run_mlflow_ui.py` : Lancement de l'interface MLFlow UI

## Fonctionnalités Principales

### 1. Pipeline de Machine Learning Complet

- **Exploration des données** : Analyses statistiques approfondies
- **Feature engineering** : Création de nouvelles features et transformations
- **Modélisation** : Comparaison de plusieurs algorithmes (LightGBM, XGBoost, Random Forest, Gradient Boosting)
- **Évaluation** : Métriques complètes (RMSE, MAE, R²)

### 2. Dashboard Interactif

- **Visualisation des données** : Graphiques interactifs avec filtres dynamiques
- **Prédictions interactives** : Formulaire pour prédire le prix d'une maison
- **Analyse de sensibilité** : Impact de chaque variable sur le prix
- **Explicabilité** : Visualisations SHAP pour comprendre les prédictions
- **Recommandations** : Suggestions pour améliorer la valeur d'une maison

### 3. Analyses Statistiques Approfondies

- **Corrélation** : Identification des variables quantitatives importantes
- **ANOVA** : Identification des variables qualitatives significatives
- **Traitement des outliers** : Transformation contextuelle (pas de suppression)
- **Transformation logarithmique** : Normalisation de la variable cible

### 4. CI/CD et Tests

- **GitHub Actions** : Pipeline CI/CD automatisé
- **Tests unitaires** : Couverture de code avec pytest
- **Qualité de code** : Vérification PEP 8 et formatage automatique
- **MLFlow** : Tracking des expériences et métriques

## Résultats et Analyses

### Analyse ANOVA - Variables Qualitatives Significatives

Une analyse ANOVA (Analysis of Variance) a été réalisée pour identifier les variables qualitatives ayant un impact significatif sur le prix de vente. Les résultats montrent que **20 variables qualitatives** sont statistiquement significatives (p < 0.05).

#### Top 10 Variables Qualitatives les Plus Significatives

| Variable | F-statistique | p-value | Taille effet (η²) |
|----------|---------------|---------|-------------------|
| Neighborhood | 67.90 | 2.55e-216 | 0.5318 |
| ExterQual | 471.16 | 6.77e-214 | 0.4926 |
| BsmtQual | 329.58 | 5.50e-202 | 0.4754 |
| KitchenQual | 425.78 | 1.54e-198 | 0.4673 |
| GarageFinish | 216.33 | 4.82e-116 | 0.3083 |
| FireplaceQu | 121.67 | 1.05e-107 | 0.2950 |
| Foundation | 100.99 | 1.48e-91 | 0.2578 |
| GarageType | 81.17 | 1.06e-87 | 0.2510 |
| BsmtFinType1 | 65.97 | 1.19e-72 | 0.2141 |
| HeatingQC | 118.11 | 1.87e-68 | 0.1958 |

**Principales conclusions** :
1. **Neighborhood** (η² = 0.532) : Le quartier explique **53.2%** de la variance du prix - facteur le plus important
2. **ExterQual** (η² = 0.493) : La qualité des matériaux extérieurs explique **49.3%** de la variance
3. **BsmtQual** (η² = 0.475) : La hauteur du sous-sol explique **47.5%** de la variance
4. **KitchenQual** (η² = 0.467) : La qualité de la cuisine explique **46.7%** de la variance

Ces 4 variables à elles seules expliquent une grande partie de la variance des prix.

### Variables Quantitatives Importantes

Les variables quantitatives les plus corrélées avec le prix (|r| > 0.5) :

1. OverallQual (0.798)
2. GrLivArea (0.736)
3. TotalBsmtSF (0.653)
4. GarageCars (0.640)
5. 1stFlrSF (0.635)

Pour plus de détails, consultez [`docs/SELECTION_VARIABLES_MODELE.md`](docs/SELECTION_VARIABLES_MODELE.md).

## Documentation

### Documentation Principale

- **`README.md`** (ce fichier) : Vue d'ensemble complète du projet
- **`README_CI_CD.md`** : Guide CI/CD, tests et qualité de code
- **`README_MLFLOW.md`** : Guide d'utilisation de MLFlow
- **`dashboard/README.md`** : Documentation du dashboard

### Documentation Détaillée (`docs/`)

- **`GESTION_VALEURS_MANQUANTES_OUTLIERS.md`** : Stratégies de gestion des valeurs manquantes et outliers
- **`SELECTION_VARIABLES_MODELE.md`** : Sélection objective des variables
- **`TRANSFORMATION_LOGARITHMIQUE.md`** : Justification des transformations logarithmiques

## CI/CD et Tests

Le projet utilise GitHub Actions pour l'intégration continue, Pytest pour les tests unitaires, et MLFlow pour le tracking des expériences.

### Pipeline CI/CD

Le workflow GitHub Actions (`/.github/workflows/ci.yml`) exécute automatiquement :

- **Lint PEP 8** : Vérification de la conformité avec flake8
- **Formatage** : Vérification du formatage avec Black
- **Tests unitaires** : Exécution des tests avec pytest
- **Couverture de code** : Upload des rapports de couverture

### Commandes Rapides

```bash
# Exécuter les tests
pytest tests/ -v

# Lancer MLFlow UI
python scripts/run_mlflow_ui.py

# Vérifier PEP 8
python scripts/check_pep8.py

# Formater le code
python scripts/format_code.py
```

### Documentation

- **CI/CD et Tests** : Voir [README_CI_CD.md](README_CI_CD.md)
- **MLFlow** : Voir [README_MLFLOW.md](README_MLFLOW.md)

## Auteurs et Licence

**Équipe Laplace Immo** - Projet Machine Learning ISE-2 ENSAE

École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE)

### Contribution

Ce projet est réalisé dans le cadre académique. Pour toute question ou suggestion, veuillez ouvrir une issue sur le repository.

### Licence

Ce projet est réalisé dans le cadre académique.

## Références

### Dataset

- **House Prices: Advanced Regression Techniques** : [Kaggle Competition](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)

### Documentation Technique

- **MLFlow** : [https://www.mlflow.org/](https://www.mlflow.org/)
- **LightGBM** : [https://lightgbm.readthedocs.io/](https://lightgbm.readthedocs.io/)
- **XGBoost** : [https://xgboost.readthedocs.io/](https://xgboost.readthedocs.io/)
- **Dash** : [https://dash.plotly.com/](https://dash.plotly.com/)
- **GitHub Actions** : [https://docs.github.com/en/actions](https://docs.github.com/en/actions)

### Standards de Code

- **PEP 8** : [https://www.python.org/dev/peps/pep-0008/](https://www.python.org/dev/peps/pep-0008/)
- **Black** : [https://black.readthedocs.io/](https://black.readthedocs.io/)
- **Flake8** : [https://flake8.pycqa.org/](https://flake8.pycqa.org/)

---

**Dernière mise à jour** : 2024
