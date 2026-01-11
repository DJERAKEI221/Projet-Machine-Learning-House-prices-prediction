# Guide CI/CD et Tests

Ce guide explique comment utiliser GitHub Actions, les tests unitaires et les outils de qualité de code.

## GitHub Actions

Le projet utilise GitHub Actions pour l'intégration continue (CI/CD). Le workflow est défini dans `.github/workflows/ci.yml`.

### Pipeline CI/CD

Le pipeline comprend deux jobs :

1. **Test** : Exécuté sur chaque push et pull request
   - Lint avec flake8 (vérification PEP 8)
   - Formatage avec black (vérification)
   - Tests unitaires avec pytest
   - Upload des rapports de couverture

2. **Build** : Exécuté uniquement sur la branche main
   - Vérification des artifacts du modèle

### Déclencheurs

Le workflow se déclenche sur :
- Push vers les branches `main` ou `develop`
- Pull requests vers `main` ou `develop`

### Matrices de test

Les tests sont exécutés sur plusieurs versions de Python :
- Python 3.9
- Python 3.10
- Python 3.11

## Tests Unitaires

### Structure des Tests

Les tests sont organisés dans le dossier `tests/` :
- `test_feature_engineering.py` : Tests pour le module feature_engineering
- `test_data_processing.py` : Tests désactivés (module n'existe pas)
- `test_modeling.py` : Tests désactivés (module n'existe pas)
- `test_utils.py` : Tests désactivés (module n'existe pas)

### Exécuter les Tests Localement

```bash
# Exécuter tous les tests
pytest tests/ -v

# Exécuter avec couverture de code
pytest tests/ -v --cov=src --cov-report=html

# Exécuter un fichier de test spécifique
pytest tests/test_feature_engineering.py -v

# Exécuter un test spécifique
pytest tests/test_feature_engineering.py::TestFeatureEngineer::test_initialization -v
```

### Configuration Pytest

La configuration est dans `pytest.ini` et `pyproject.toml` :
- Dossier des tests : `tests/`
- Fichiers de test : `test_*.py`
- Classes de test : `Test*`
- Options par défaut : verbose, traceback court

## Qualité de Code (PEP 8)

### Flake8

Flake8 vérifie la conformité PEP 8 du code.

**Configuration** : `.flake8`

**Exécuter localement** :
```bash
# Utiliser le script
python scripts/check_pep8.py

# Ou directement
flake8 src dashboard config.py --config=.flake8
```

### Black

Black formate automatiquement le code selon les standards PEP 8.

**Configuration** : `pyproject.toml`

**Exécuter localement** :
```bash
# Utiliser le script
python scripts/format_code.py

# Ou directement
black --line-length=127 src dashboard config.py
```

### Conformité dans GitHub Actions

Le workflow CI vérifie automatiquement :
- Erreurs de syntaxe Python (flake8)
- Conformité PEP 8 (flake8 avec continue-on-error)
- Formatage avec black (black --check)

## Scripts Utilitaires

### `scripts/check_pep8.py`

Vérifie la conformité PEP 8 du code source.

```bash
python scripts/check_pep8.py
```

### `scripts/format_code.py`

Formate le code avec Black.

```bash
python scripts/format_code.py
```

### `scripts/run_mlflow_ui.py`

Lance l'interface web MLFlow.

```bash
python scripts/run_mlflow_ui.py
```

### `scripts/integrate_mlflow.py`

Script utilitaire pour intégrer MLFlow dans les notebooks.

## Workflow Recommandé

1. **Développement local** :
   ```bash
   # Formater le code
   python scripts/format_code.py
   
   # Vérifier PEP 8
   python scripts/check_pep8.py
   
   # Exécuter les tests
   pytest tests/ -v
   ```

2. **Commit et Push** :
   - Les tests sont automatiquement exécutés via GitHub Actions
   - Vérifiez les résultats dans l'onglet "Actions" de GitHub

3. **Pull Request** :
   - Les tests doivent passer avant de merger
   - La couverture de code est vérifiée

## Notes

- Les tests pour `data_processing`, `modeling` et `utils` sont désactivés car ces modules n'existent pas actuellement
- Le workflow CI continue même en cas d'erreurs (continue-on-error: true) pour ne pas bloquer les développements
- MLFlow UI doit être lancé localement (non intégré dans GitHub Actions)
