# Projet Machine Learning - Prédiction des Prix Immobiliers

## Projet Laplace Immo


Projet réalisé dans le cadre du cours de Machine Learning I dispensé aux Élèves Ingénieurs Statisticiens Économistes (ISE-2) à l'École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE).

Ce projet vise à développer un modèle de machine learning capable de prédire avec précision le prix de vente des maisons en utilisant des techniques avancées de régression. Le dataset utilisé provient de la compétition Kaggle "House Prices: Advanced Regression Techniques" et contient 79 variables explicatives décrivant différentes caractéristiques des maisons.

---

## Objectifs

- **Prédiction précise** : Développer un modèle performant pour prédire le prix de vente des maisons
- **Analyse approfondie** : Identifier les variables les plus importantes pour la prédiction
- **Pipeline complet** : Mettre en place un workflow de bout en bout, de l'exploration à la déploiement
- **Pratiques professionnelles** : Intégrer MLflow pour le suivi des expériences, tests unitaires et CI/CD

---

## Structure du Projet

```
ProjetMachine-Learning-House-prices-prediction/
├── data/
│   ├── raw/                  # Données brutes (train.csv, test.csv, description)
│   ├── interim/              # Données intermédiaires
│   └── processed/            # Données nettoyées et prêtes pour l'entraînement
│
├── notebooks/
│   ├── exploration_base_donnees.ipynb    # Exploration et analyse des données
│   ├── traitement.ipynb                   # Nettoyage et préparation des données
│   ├── feature_engineering.ipynb         # Feature engineering et modélisation
│   ├── api_fastapi.ipynb                 # API FastAPI pour l'inférence
│   ├── data/processed/                   # Exports intermédiaires
│   └── output/                          # Modèles et préprocesseurs sauvegardés
│       ├── models/                       # Modèle final (model_final.joblib)
│       └── preprocess/                   # Préprocesseurs sauvegardés
│
├── scripts/
│   ├── integrate_mlflow.py              # Utilitaires pour MLflow
│   ├── run_mlflow_ui.py                 # Lancement de l'interface MLflow
│   ├── save_final_model.py              # Sauvegarde du modèle final
│   ├── check_pep8.py                    # Vérification PEP 8
│   └── format_code.py                   # Formatage automatique du code
│
├── src/
│   ├── feature_engineering.py           # Module de feature engineering
│   └── model_pipline.py                # Pipeline de modélisation
│
├── dashboard/                           # Application Dash interactive
│   ├── components/                      # Composants réutilisables
│   ├── pages/                           # Pages du dashboard
│   └── utils/                           # Utilitaires
│
├── output/
│   ├── figures/                         # Graphiques générés
│   └── tables/                          # Tableaux d'analyse
│
├── docs/                                # Documentation détaillée
│   ├── GESTION_VALEURS_MANQUANTES_OUTLIERS.md
│   ├── SELECTION_VARIABLES_MODELE.md
│   └── TRANSFORMATION_LOGARITHMIQUE.md
│
├── tests/                               # Tests unitaires
├── mlruns/                              # Stockage MLflow (expériences)
├── requirements.txt                     # Dépendances principales
├── requirements_api.txt                 # Dépendances pour l'API
└── README.md                            # Ce fichier
```

---

## Pipeline de Machine Learning

Le projet suit un pipeline structuré en plusieurs étapes :

### 1. Traitement et Nettoyage (`traitement.ipynb`)

- Gestion des valeurs manquantes structurelles (NA = absence de caractéristique)
- Imputation des valeurs manquantes non structurelles
- Traitement des outliers avec méthodes IQR


### 2. Exploration des Données (`exploration_base_donnees.ipynb`)

- Analyse descriptive complète
- Détection et traitement des valeurs manquantes structurelles
- Identification des outliers
- Analyse de corrélation pour variables quantitatives
- Tests ANOVA pour variables qualitatives
- Traduction et mapping des variables

### 3. Feature Engineering et Modélisation (`feature_engineering.ipynb`)

- Création de nouvelles features
- Encodage des variables catégorielles (One-Hot, Ordinal)
- Transformation des variables asymétriques (log, Box-Cox)
- Transformation logarithmique de la variable cible (SalePrice)
- Entraînement et comparaison de plusieurs modèles :
  - Ridge, Lasso, ElasticNet
  - Random Forest
  - Gradient Boosting
  - LightGBM
  - XGBoost
- Optimisation des hyperparamètres avec GridSearchCV
- Sélection du meilleur modèle
- Sauvegarde du modèle final et des métadonnées

---

### Documentation Principale

- **`README.md`** (ce fichier) : Vue d'ensemble du projet
- **`README_CI_CD.md`** : Guide CI/CD, tests et qualité de code
- **`README_MLFLOW.md`** : Guide d'utilisation de MLflow

---

## Tests et Qualité de Code

Le projet utilise :

- **GitHub Actions** : Pipeline CI/CD automatisé
- **Pytest** : Tests unitaires avec couverture de code
- **Flake8** : Vérification de la conformité PEP 8
- **Black** : Formatage automatique du code
- **MLflow** : Tracking des expériences et métriques

---

## Auteurs et Licence

Projet Machine Learning ISE-2 ENSAE

École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE)

**Sous la supervision de :** Mme Mously DIAW | [GitHub](https://github.com/MouslyDiaw)

**Auteurs :**
- Compaoré BASSIROU : [LinkedIn](https://www.linkedin.com/in/mohamadi-bassirou-compaore-04a712300)
- Samba DIENG : sambadieng122003@gmail.com | [LinkedIn](https://www.linkedin.com/in/samba-dieng-b13650247)
- Yves Mistalengar DJERAKEI : yvesdjerake@gmail.com | [LinkedIn](https://www.linkedin.com/in/djerake%C3%AF-mistalengar-086b3a21b/)
- Divana KERENCIA : dyvanaseukam@gmail.com | [LinkedIn](https://www.linkedin.com/in/dyvana-seunkam-8aa93b340)
- Ange Emilson RAYAN : rayanemil20@gmail.com

Ce projet est réalisé dans le cadre académique.

---

## Références

### Dataset

- **House Prices: Advanced Regression Techniques** : [Données](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)



**Dernière mise à jour** : 2026
