# Projet Machine Learning - Prédiction des Prix Immobiliers

## Projet Laplace Immo

Ce projet est réalisé dans le cadre du cours de Machine Learning I dispensé aux Élèves Ingénieurs Statisticiens Économistes (ISE-2) à l'École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE).

### Contexte

Vous êtes data scientist chez Laplace Immo, un réseau national d'agences immobilières. L'objectif est de fournir aux équipes un algorithme de prédiction des prix des maisons. Avec 79 variables explicatives décrivant (presque) tous les aspects des maisons résidentielles à Ames (Iowa, US), ce projet vise à construire un modèle de prédiction du prix final de chaque maison.

## Structure du Projet

```
ProjetMachine-Learning-House-prices-prediction/
│
├── data/                          # Données du projet
│   ├── raw/                       # Données brutes (train.csv, test.csv)
│   ├── interim/                  # Données intermédiaires
│   └── processed/                 # Données traitées
│
├── notebooks/                      # Notebooks Jupyter
│   ├── exploration_base_donnees.ipynb    # Exploration des données
│   ├── house_price_01_analyse.ipynb      # Analyse exploratoire
│   └── house_price_02_essais.ipynb       # Tests de modèles
│
├── src/                           # Code source Python
│   ├── __init__.py
│   ├── data_processing.py         # Traitement et nettoyage des données
│   ├── feature_engineering.py     # Création de features
│   ├── modeling.py                # Entraînement et évaluation des modèles
│   ├── explainability.py          # Module d'explicabilité SHAP
│   ├── sensitivity_analysis.py    # Analyse de sensibilité
│   └── utils.py                   # Fonctions utilitaires
│
├── tests/                         # Tests unitaires
│   ├── __init__.py
│   ├── test_data_processing.py
│   ├── test_feature_engineering.py
│   ├── test_modeling.py
│   └── test_utils.py
│
├── output/                        # Résultats et sorties
│   ├── figures/                   # Graphiques et visualisations
│   ├── models/                    # Modèles sauvegardés
│   ├── tables/                    # Tableaux de résultats
│   └── submission.csv              # Fichier de soumission
│
├── docs/                          # Documentation
│   ├── Description_Variables_Dataset.docx    # Description des variables (Word)
│   ├── Dictionnaire_Variables_Francais.docx  # Dictionnaire français (Word)
│   ├── GESTION_VALEURS_MANQUANTES_OUTLIERS.md  # Gestion valeurs manquantes et outliers
│   ├── KURTOSIS.md                # Explication du kurtosis
│   ├── TRANSFORMATION_LOGARITHMIQUE.md  # Justification transformation log
│   ├── INNOVATIONS.md              # Documentation des innovations
│   ├── PROJECT_SUMMARY.md         # Résumé du projet
│   └── project_description.pdf    # Description du projet
│
├── scripts/                        # Scripts utilitaires
│   ├── mlflow/                    # Scripts MLFlow
│   │   ├── run_mlflow.sh
│   │   └── run_mlflow.bat
│   ├── run_api.sh                 # Script pour lancer l'API
│   ├── run_api.bat
│   ├── run_dashboard.sh           # Script pour lancer le dashboard
│   └── run_dashboard.bat
├── api/                           # API REST
│   └── app.py                     # Application FastAPI
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # Pipeline CI/CD GitHub Actions
│
├── mlruns/                        # MLFlow tracking (généré automatiquement)
│
├── train.py                       # Script principal d'entraînement
├── app.py                         # Dashboard Streamlit
├── GUIDE_ACCES.md                 # Guide d'accès aux services (API, Dashboard)
├── requirements.txt               # Dépendances Python
├── requirements_api.txt           # Dépendances API et Dashboard
├── Dockerfile                     # Configuration Docker
├── docker-compose.yml             # Orchestration Docker
├── README_INNOVATIONS.md          # Documentation des innovations
├── setup.py                       # Configuration du package
├── pytest.ini                     # Configuration pytest
├── .flake8                        # Configuration flake8
├── pyproject.toml                 # Configuration des outils
├── .gitignore                     # Fichiers à ignorer par Git
└── README.md                      # Ce fichier
```

## Installation

### Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/house-price-prediction.git
cd house-price-prediction
```

2. Créer un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
pip install -r requirements_api.txt  # Pour l'API et le dashboard
```

Ou installer le package en mode développement :
```bash
pip install -e .
```

## Utilisation

### 1. Exploration des Données

Exécuter le notebook d'exploration pour comprendre les données :
```bash
jupyter notebook notebooks/exploration_base_donnees.ipynb
```

### 2. Analyse Exploratoire

Exécuter le notebook d'analyse exploratoire :
```bash
jupyter notebook notebooks/house_price_01_analyse.ipynb
```

### 3. Tests de Modèles

Exécuter le notebook de tests de modèles :
```bash
jupyter notebook notebooks/house_price_02_essais.ipynb
```

### 4. Entraînement via Script

Pour entraîner le modèle directement via ligne de commande :
```bash
python train.py
```

### 5. Visualisation des Expériences MLFlow

Pour visualiser les expériences MLFlow :
```bash
# Sur Linux/Mac
./scripts/mlflow/run_mlflow.sh

# Sur Windows
scripts\mlflow\run_mlflow.bat

# Ou manuellement
mlflow ui
```

Puis ouvrir http://localhost:5000 dans votre navigateur.

**Note :** Pour plus d'informations sur l'accès aux services, consultez [GUIDE_ACCES.md](GUIDE_ACCES.md).

## Tests

### Exécuter tous les tests

```bash
pytest
```

### Exécuter avec couverture de code

```bash
pytest --cov=src --cov-report=html
```

## CI/CD

Le projet utilise GitHub Actions pour l'intégration et le déploiement continus. Le pipeline CI/CD :

1. **Tests** : Exécute les tests unitaires sur Python 3.9, 3.10, et 3.11
2. **Linting** : Vérifie le code avec flake8
3. **Formatage** : Vérifie le formatage avec black
4. **Couverture** : Génère des rapports de couverture de code
5. **Build** : Entraîne le modèle sur la branche main

## Modèles Testés

Le projet teste plusieurs algorithmes de machine learning :

1. **Linear Regression** : Modèle de base pour référence
2. **Ridge Regression** : Régularisation L2
3. **Lasso Regression** : Régularisation L1 avec sélection de features
4. **Random Forest** : Modèle d'ensemble basé sur les arbres de décision
5. **Gradient Boosting** : Boosting avec arbres de décision
6. **XGBoost** : Implémentation optimisée du gradient boosting
7. **LightGBM** : Modèle final sélectionné (meilleures performances)

### Modèle Final

Le modèle final sélectionné est **LightGBM** avec les hyperparamètres suivants :
- `n_estimators`: 500
- `max_depth`: 7
- `learning_rate`: 0.03
- `num_leaves`: 31
- `feature_fraction`: 0.8
- `bagging_fraction`: 0.8
- `bagging_freq`: 5
- `min_child_samples`: 20

## Innovations du Projet

Ce projet inclut deux innovations principales qui le distinguent des projets standards :

### 1. Dashboard Interactif avec Streamlit

Interface web interactive permettant de :
- Visualiser les prédictions
- Explorer les données
- Tester différents scénarios
- Voir l'impact des variables sur le prix

**Utilisation :**
```bash
# Lancer le dashboard (Linux/Mac)
./scripts/run_dashboard.sh

# Lancer le dashboard (Windows)
scripts\run_dashboard.bat

# Ou manuellement
streamlit run app.py

# Accéder au dashboard
# http://localhost:8501
```

**Fonctionnalités :**
- Prédiction interactive avec formulaire
- Analyse de sensibilité des variables
- Visualisation SHAP pour l'explicabilité
- Recommandations d'amélioration

### 2. Pipeline de Déploiement Complet

Pipeline complet incluant :
- Containerisation avec Docker
- Déploiement sur cloud (AWS Lambda)
- Monitoring du modèle en production
- Retraining automatique (optionnel)

**Containerisation Docker :**
```bash
# Lancer avec docker-compose
docker-compose up

# Services disponibles :
# - API : http://localhost:8000
# - Dashboard : http://localhost:8501
```

**Déploiement AWS Lambda :**
```bash
# Déploiement automatique
cd lambda
./deploy.sh manual  # Linux/Mac
deploy.bat manual    # Windows
```

**Documentation :**
- Guide complet : [docs/GUIDE_DEPLOIEMENT_AWS_LAMBDA.md](docs/GUIDE_DEPLOIEMENT_AWS_LAMBDA.md)
- Concepts : [docs/SERVERLESS_FUNCTIONS.md](docs/SERVERLESS_FUNCTIONS.md)

**Avantages :**
- ✅ Prêt pour la production
- ✅ Scaling automatique
- ✅ Environnement reproductible
- ✅ Monitoring intégré

Pour plus de détails, consultez [README_INNOVATIONS.md](README_INNOVATIONS.md) et [docs/INNOVATIONS.md](docs/INNOVATIONS.md).

## Documentation

La documentation complète est disponible dans le dossier `docs/` :

### Documentation Technique
- **Gestion des valeurs manquantes et outliers** : [`docs/GESTION_VALEURS_MANQUANTES_OUTLIERS.md`](docs/GESTION_VALEURS_MANQUANTES_OUTLIERS.md)
  - Stratégies de traitement des valeurs manquantes
  - Transformation contextuelle des outliers
  - Justification théorique et méthodologique

- **Transformation logarithmique** : [`docs/TRANSFORMATION_LOGARITHMIQUE.md`](docs/TRANSFORMATION_LOGARITHMIQUE.md)
  - Justification de l'utilisation de la transformation log
  - Impact sur les performances du modèle

- **Kurtosis** : [`docs/KURTOSIS.md`](docs/KURTOSIS.md)
  - Explication du concept de kurtosis
  - Analyse de la distribution de la variable cible

### Documentation des Variables
- **Description des variables** : `docs/Description_Variables_Dataset.docx`
- **Dictionnaire français** : `docs/Dictionnaire_Variables_Francais.docx`

### Autres Documents
- **Résumé du projet** : [`docs/PROJECT_SUMMARY.md`](docs/PROJECT_SUMMARY.md)
- **Innovations** : [`docs/INNOVATIONS.md`](docs/INNOVATIONS.md) et [`README_INNOVATIONS.md`](README_INNOVATIONS.md)
- **Guide d'accès** : [`GUIDE_ACCES.md`](GUIDE_ACCES.md) - Instructions pour accéder à l'API et au Dashboard

## Conventions de Code

Le projet suit les conventions PEP 8 pour le style de code Python :
- Utilisation de `flake8` pour le linting
- Utilisation de `black` pour le formatage automatique
- Longueur de ligne maximale : 127 caractères
- Documentation des fonctions et classes avec docstrings

## Traitement des Données

### Valeurs Manquantes
Le projet utilise une approche contextuelle pour traiter les valeurs manquantes :
- **Variables catégorielles optionnelles** : Remplies avec "None" (ex: PoolQC, Alley, Fence)
- **Variables numériques optionnelles** : Remplies avec 0 (ex: BsmtFinSF1, GarageArea)
- **Variables importantes** : Remplies avec le mode (ex: MSZoning, Electrical)
- **Variables contextuelles** : Médiane par groupe (ex: LotFrontage par quartier)

### Outliers
Au lieu de supprimer les outliers, le projet utilise une **transformation contextuelle** :
- **GrLivArea-SalePrice** : Ajustement du prix basé sur des maisons similaires avec transformation logarithmique
- **TotalBsmtSF** : Capping intelligent selon la cohérence avec GrLivArea
- **Préservation** : Toutes les observations sont conservées (aucune suppression)

Pour plus de détails, voir [`docs/GESTION_VALEURS_MANQUANTES_OUTLIERS.md`](docs/GESTION_VALEURS_MANQUANTES_OUTLIERS.md).

## Contribution

Ce projet est réalisé dans le cadre académique. Pour toute question ou suggestion, veuillez ouvrir une issue sur le repository.

## Auteurs

Équipe Laplace Immo - Projet Machine Learning ISE-2 ENSAE

## Licence

Ce projet est réalisé dans le cadre académique.

## Références

- Dataset : [House Prices: Advanced Regression Techniques](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)
- Documentation MLFlow : https://www.mlflow.org/
- Documentation LightGBM : https://lightgbm.readthedocs.io/
