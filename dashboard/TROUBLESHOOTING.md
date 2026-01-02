# Guide de Dépannage - Dashboard Dash

## Erreur: ModuleNotFoundError: No module named 'dashboard'

### Solution 1: Vérifier le répertoire de travail

Assurez-vous d'être dans le répertoire racine du projet :

```bash
# Vérifier le répertoire actuel
pwd  # Linux/Mac
cd   # Windows (affiche le répertoire)

# Aller dans le répertoire du projet
cd "C:\Users\pc\Desktop\ISE2 2024\MACHINE LEARNING\ProjetMachine-Learning-House-prices-prediction"
```

### Solution 2: Installer les dépendances

```bash
# Installer toutes les dépendances
pip install -r requirements_api.txt

# Ou installer manuellement
pip install dash dash-bootstrap-components plotly
```

### Solution 3: Vérifier la structure

Assurez-vous que la structure suivante existe :

```
ProjetMachine-Learning-House-prices-prediction/
├── dashboard/
│   ├── __init__.py
│   ├── app.py
│   ├── components/
│   ├── pages/
│   ├── utils/
│   └── assets/
└── app_dash.py
```

### Solution 4: Utiliser Python directement

Si les scripts ne fonctionnent pas, lancez directement :

```bash
python app_dash.py
```

## Erreur: ModuleNotFoundError: No module named 'dash'

### Solution

Installer Dash et ses dépendances :

```bash
pip install dash dash-bootstrap-components plotly
```

Vérifier l'installation :

```bash
python -c "import dash; print('Dash installé:', dash.__version__)"
```

## Erreur: Port déjà utilisé

### Solution

Changer le port dans `app_dash.py` :

```python
app.run_server(debug=True, host="127.0.0.1", port=8051)  # Changer le port
```

Ou tuer le processus utilisant le port :

```powershell
# Windows
netstat -ano | findstr :8050
taskkill /PID <PID> /F
```

## Erreur: Modèle non trouvé

### Solution

Le dashboard fonctionnera même sans modèle, mais certaines fonctionnalités seront limitées.

Pour entraîner le modèle :

```bash
python train.py
```

Le modèle sera sauvegardé dans `output/models/final_model.pkl`.

## Vérification Complète

Script de vérification :

```python
# verification.py
import sys
from pathlib import Path

print("Vérification de l'environnement...")
print(f"Python: {sys.executable}")
print(f"Répertoire: {Path.cwd()}")

# Vérifier les dépendances
deps = ['dash', 'dash_bootstrap_components', 'plotly', 'pandas', 'numpy']
missing = []
for dep in deps:
    try:
        __import__(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep} - MANQUANT")
        missing.append(dep)

if missing:
    print(f"\nInstaller avec: pip install {' '.join(missing)}")
else:
    print("\n✅ Toutes les dépendances sont installées!")

# Vérifier la structure
if Path("dashboard").exists():
    print("✅ Dossier dashboard trouvé")
else:
    print("❌ Dossier dashboard non trouvé")

if Path("app_dash.py").exists():
    print("✅ app_dash.py trouvé")
else:
    print("❌ app_dash.py non trouvé")
```

Lancer avec : `python verification.py`

