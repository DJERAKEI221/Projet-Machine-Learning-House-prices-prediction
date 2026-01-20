<div align="center">

# 🏠 House Prices Prediction

**Projet Machine Learning - Prédiction des Prix Immobiliers**

*Développé dans le cadre du cours de Machine Learning I - ENSAE*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Latest-orange.svg)](https://scikit-learn.org/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-purple.svg)](https://mlflow.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)

---

</div>

## 📋 Table des Matières

- [À Propos](#-à-propos)
- [Objectifs](#-objectifs)
- [Résultats Clés](#-résultats-clés)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Modèles et Performance](#-modèles-et-performance)
- [Équipe](#-équipe)
- [Références](#-références)
- **Prédiction précise** : Développer un modèle performant pour prédire le prix de vente des maisons
- **Analyse approfondie** : Identifier les variables les plus importantes pour la prédiction
- **Pipeline complet** : Mettre en place un workflow de bout en bout, de l'exploration à la déploiement
- **MLflow** : Intégrer MLflow pour le suivi des expériences, tests unitaires et CI/CD

---

## 📖 À Propos

Ce projet développe un **modèle de machine learning performant** pour prédire le prix de vente des maisons en utilisant des techniques avancées de régression. 

Le dataset provient de la compétition Kaggle **"House Prices: Advanced Regression Techniques"** et contient **79 variables explicatives** décrivant les caractéristiques des maisons (surface, qualité, localisation, équipements, etc.).

**Contexte académique** : Projet réalisé dans le cadre du cours de **Machine Learning I** dispensé aux **Élèves Ingénieurs Statisticiens Économistes (ISE-2)** à l'**École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE)**.

---

## 🎯 Objectifs

| Objectif | Description |
|----------|-------------|
| **🎯 Prédiction Précise** | Développer un modèle performant avec erreur minimale |
| **🔍 Analyse Approfondie** | Identifier les variables les plus importantes |
| **⚙️ Pipeline Complet** | Workflow de bout en bout, de l'exploration au déploiement |
| **🏆 Qualité du code et suivi** | MLflow, tests unitaires, CI/CD |
| **📊 Visualisation** | Dashboard interactif pour exploration et prédiction |

---

## 🏆 Résultats Clés

### Modèle Final : ElasticNet avec Transformation Logarithmique

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **MAE** | $14,892.69 | Erreur moyenne absolue (métrique principale) |
| **RMSE** | $23,067.47 | Erreur quadratique moyenne |
| **R²** | 0.9306 | 93.06% de variance expliquée |
| **MAPE** | 8.90% | Erreur relative moyenne |

**Performance** : Le modèle retenu (ElasticNet_WithTransform) présente le meilleur MAE parmi **16 configurations testées** (8 modèles × 2 versions : avec/sans transformation logarithmique).

---

## 🏗️ Architecture

### Structure du Projet

```
ProjetMachine-Learning-House-prices-prediction/
├── 📁 data/                    # Gestion des données
│   ├── raw/                    # Données brutes
│   ├── interim/                # Données intermédiaires
│   └── processed/              # Données nettoyées
├── 📁 notebooks/
│   ├── exploration_base_donnees.ipynb    # Exploration et analyse des données
│   ├── traitement.ipynb                   # Nettoyage et préparation des données
│   ├── feat_engeneering_modeling.ipynb         # Feature engineering et modélisation
│   ├── data/processed/                   # Exports intermédiaires
│   └── output/                          # Modèles et préprocesseurs sauvegardés
│       ├── models/                       # Modèle final (model_final.joblib)
│       └── preprocess/                   # Préprocesseurs sauvegardés
├── 📁 notebooks/              # Notebooks d'analyse
│   ├── exploration_base_donnees.ipynb
│   ├── traitement.ipynb
│   └── feat_engeneering_modeling.ipynb
│
├── 📁 scripts/                # Scripts utilitaires
│   ├── train_model.py
│   ├── integrate_mlflow.py
│   └── run_mlflow_ui.py
│
├── 📁 src/                    # Code source modulaire
│   ├── feature_engineering.py
│   └── model_pipline.py
│
├── 📁 dashboard/              # Application Streamlit
│   ├── app.py
│   └── assets/
├── 📁 tests/                  # Tests unitaires
├── 📁 docs/                   # Documentation détaillée
└── 📁 mlruns/                 # Stockage MLflow
```

### Pipeline de Machine Learning

```
Données Brutes → Nettoyage → Exploration → Feature Engineering 
    → Entraînement → Sélection → Déploiement (Dashboard)
```

**Composants principaux** :
- **Preprocessing** : ColumnTransformer avec imputation et encodage
- **Modèles** : 8 algorithmes testés (linéaires et basés sur arbres)
- **Optimisation** : GridSearchCV avec validation croisée 5-fold
- **Tracking** : MLflow pour suivi des expériences

---

## ⚙️ Installation

### Prérequis

| Composant | Version Minimale | Recommandée |
|-----------|------------------|-------------|
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 4 GB | 8 GB+ |
| **Espace disque** | 2 GB | 5 GB+ |

### Installation des Dépendances

```
# Cloner le repository
git clone <repository-url>
cd ProjetMachine-Learning-House-prices-prediction

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Dépendances Principales

- `scikit-learn` ≥1.0.0 - Machine Learning
- `pandas` ≥1.3.0 - Manipulation de données
- `numpy` ≥1.21.0 - Calculs numériques
- `streamlit` ≥1.0.0 - Dashboard interactif
- `mlflow` ≥1.20.0 - Tracking d'expériences
- `xgboost`, `lightgbm` - Gradient Boosting

---

## 🚀 Utilisation

### Notebooks d'Analyse

1. **Exploration** : `notebooks/exploration_base_donnees.ipynb`
2. **Traitement** : `notebooks/traitement.ipynb`
3. **Modélisation** : `notebooks/feat_engeneering_modeling.ipynb`

### Dashboard Interactif

```
cd dashboard
streamlit run app.py
```

Le dashboard permet de :
- 📊 Visualiser les performances des modèles
- 🔍 Explorer les données et prédictions
- 💰 Faire des prédictions interactives
- 📈 Analyser les erreurs et résidus

### MLflow UI

```
python scripts/run_mlflow_ui.py
```

### Tests

```
pytest tests/ -v --cov=src --cov-report=html

├── docs/                                # Documentation détaillée
│
├── tests/                               # Tests unitaires
├── mlruns/                              # Stockage MLflow (expériences)
├── requirements.txt                     # Dépendances principales
├── requirements_api.txt                 # Dépendances
└── README.md                            # Ce fichier
```

---

## 🤖 Modèles et Performance

### Modèles Testés

| Catégorie | Modèles | Description |
|-----------|---------|-------------|
| **Linéaires** | LinearRegression, Ridge, Lasso, ElasticNet | Régularisation L1/L2 |
| **Arbres** | RandomForest, GradientBoosting, XGBoost, LightGBM | Ensemble et boosting |

### Optimisation

- **GridSearchCV** : Recherche exhaustive des hyperparamètres
- **Validation croisée** : 5-fold cross-validation
- **Métriques** : MAE (priorité), RMSE, R², MAPE
- **Transformation** : Évaluation avec et sans transformation logarithmique de la cible

### Feature Engineering

- **Nouvelles features** : âges (HouseAge, RemodAge, GarageAge), surfaces totales (TotalSF, TotalPorchSF), équipements (TotalBath)
- **Encodage** : One-Hot Encoding (nominales), Ordinal Encoding (ordinales)
- **Transformation** : Transformation logarithmique pour variables asymétriques
=======
- Analyse descriptive complète
- Détection et traitement des valeurs manquantes structurelles
- Identification des outliers
- Analyse de corrélation pour variables quantitatives
- Tests ANOVA pour variables qualitatives
- Traduction et mapping des variables

### 3. Feature Engineering et Modélisation (`feat_engeneering_modeling.ipynb`)

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

## 🧪 Qualité et Tests

### Outils de Qualité

- ✅ **Pytest** : Tests unitaires avec couverture de code
- ✅ **Flake8** : Vérification PEP 8
- ✅ **Black** : Formatage automatique
- ✅ **MLflow** : Tracking des expériences
- ✅ **GitHub Actions** : CI/CD automatisé

### Métriques de Qualité

- Couverture de code pour tous les modules principaux
- Conformité PEP 8 vérifiée automatiquement
- Documentation complète avec docstrings
- Versioning des expériences avec MLflow

---

## 👥 Équipe

### 🎓 Supervision

**Mme Mously DIAW**  
*Superviseur du projet*  
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black.svg)](https://github.com/MouslyDiaw)

### 👨‍💻 Auteurs

<table>
<tr>
<td align="center">
<a href="https://www.linkedin.com/in/mohamadi-bassirou-compaore-04a712300">
<img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
</a><br/>
<strong>Compaoré BASSIROU</strong><br/>
📧 mohamadibassirou@gmail.com

</td>
<td align="center">
<a href="https://www.linkedin.com/in/samba-dieng-b13650247">
<img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
</a><br/>
<strong>Samba DIENG</strong><br/>
📧 sambadieng122003@gmail.com
</td>
<td align="center">
<a href="https://www.linkedin.com/in/djerake%C3%AF-mistalengar-086b3a21b/">
<img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
</a><br/>
<strong>Yves Mistalengar DJERAKEI</strong><br/>
📧 yvesdjerake@gmail.com
</td>
</tr>
<tr>
<td align="center">
<a href="https://www.linkedin.com/in/dyvana-seunkam-8aa93b340">
<img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
</a><br/>
<strong>Divana KERENCIA</strong><br/>
📧 dyvanaseukam@gmail.com
</td>
<td align="center">
<strong>Ange Emilson RAYAN</strong><br/>
📧 rayanemil20@gmail.com
</td>
</tr>
</table>

---

## 📖 Références

### 📚 Dataset

- [House Prices: Advanced Regression Techniques](https://www.kaggle.com/c/house-prices-advanced-regression-techniques) - Kaggle Competition
- [Dataset Description](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data) - Documentation complète

### 🔗 Technologies et Documentation
- [Cours machine learning I ENSAE-ISE2](https://www.canva.com/design/DAFPHR8GPhw/1YOoExutK-dY2TmVuYQ6mw/edit)
- [Scikit-learn](https://scikit-learn.org/) - Machine Learning
- [Pandas](https://pandas.pydata.org/) - Manipulation de données
- [Streamlit](https://streamlit.io/) - Dashboard interactif
- [MLflow](https://mlflow.org/) - Gestion d'expériences ML
- [XGBoost](https://xgboost.readthedocs.io/) - Gradient Boosting
- [LightGBM](https://lightgbm.readthedocs.io/) - Gradient Boosting optimisé
  
---

<div align="center">

### 📅 Dernière mise à jour : 2026

**École nationale de la Statistique et de l'Analyse économique Pierre NDIAYE (ENSAE)**


[⬆ Retour en haut](#-table-des-matières)

</div>
