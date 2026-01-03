# Dashboard Dash - Architecture Modulaire

## Structure du Projet

```
dashboard/
├── __init__.py
├── app.py                    # Application principale Dash
├── components/               # Composants réutilisables
│   ├── __init__.py
│   ├── header.py            # Header du dashboard
│   ├── sidebar.py           # Sidebar de navigation
│   ├── prediction_form.py   # Formulaire de prédiction
│   └── charts.py            # Composants de graphiques
├── pages/                    # Pages du dashboard
│   ├── __init__.py
│   ├── prediction.py        # Page de prédiction
│   ├── sensitivity.py       # Page d'analyse de sensibilité
│   ├── explainability.py    # Page d'explicabilité SHAP
│   └── recommendations.py   # Page de recommandations
├── utils/                    # Utilitaires
│   ├── __init__.py
│   ├── data_loader.py       # Chargement des données
│   └── model_loader.py      # Chargement du modèle
└── assets/                   # Ressources statiques
    ├── __init__.py
    └── style.css            # Styles CSS personnalisés
```

## Architecture Modulaire

### Composants (`components/`)
Composants réutilisables pour construire l'interface :
- **header.py** : En-tête avec logo et titre
- **sidebar.py** : Navigation latérale
- **prediction_form.py** : Formulaire interactif pour les prédictions
- **charts.py** : Graphiques Plotly réutilisables

### Pages (`pages/`)
Pages principales du dashboard :
- **prediction.py** : Prédiction de prix avec formulaire
- **sensitivity.py** : Analyse de sensibilité des variables
- **explainability.py** : Explications SHAP
- **recommendations.py** : Recommandations d'amélioration

### Utilitaires (`utils/`)
Fonctions utilitaires :
- **data_loader.py** : Chargement et gestion des données
- **model_loader.py** : Chargement du modèle et prédictions

### Assets (`assets/`)
Ressources statiques :
- **style.css** : Styles CSS personnalisés pour le design moderne

## Design

Le dashboard utilise :
- **Dash Bootstrap Components** : Composants Bootstrap pour Dash
- **Plotly** : Graphiques interactifs
- **Font Awesome** : Icônes
- **CSS personnalisé** : Design moderne avec animations

### Couleurs Principales
- **Primary** : #2E86AB (Bleu)
- **Secondary** : #A23B72 (Rose/Magenta)
- **Accent** : #F18F01 (Orange)
- **Success** : #06A77D (Vert)

## Utilisation

### Lancer le Dashboard

```bash
# Méthode 1 : Via le script
python dashboard/app.py

# Méthode 2 : Via le module
python -m dashboard.app

# Méthode 3 : Via les scripts
scripts/run_dashboard.bat  # Windows
./scripts/run_dashboard.sh  # Linux/Mac
```

### Accéder au Dashboard

Ouvrir dans le navigateur : **http://localhost:8050**

## Fonctionnalités

1. **Prédiction Interactive** : Formulaire avec sliders et dropdowns
2. **Analyse de Sensibilité** : Impact des variables sur le prix
3. **Explicabilité SHAP** : Visualisations des explications
4. **Recommandations** : Suggestions d'amélioration

## Dépendances

Voir `requirements_api.txt` pour les dépendances complètes :
- `dash>=2.14.0`
- `dash-bootstrap-components>=1.5.0`
- `plotly>=5.18.0`

## Avantages de l'Architecture Modulaire

✅ **Maintenabilité** : Code organisé et facile à maintenir
✅ **Réutilisabilité** : Composants réutilisables
✅ **Scalabilité** : Facile d'ajouter de nouvelles pages
✅ **Testabilité** : Chaque module peut être testé indépendamment
✅ **Lisibilité** : Structure claire et logique

