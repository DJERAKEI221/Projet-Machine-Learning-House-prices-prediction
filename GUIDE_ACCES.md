# Guide d'Accès aux Services

## IMPORTANT : Adresses à utiliser

**NE PAS utiliser** `http://0.0.0.0:8000` dans votre navigateur !

**UTILISER** `http://localhost:8000` ou `http://127.0.0.1:8000`

## Services Disponibles

### 1. API REST (FastAPI)

**Lancer l'API :**
```powershell
& "D:/Spyder/Python/python.exe" -m uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload
```

**Accéder à l'API :**
- API principale : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs
- Documentation ReDoc : http://localhost:8000/redoc

**Tester l'API :**
```powershell
# Test simple
curl http://localhost:8000/

# Test de santé
curl http://localhost:8000/health
```

### 2. Dashboard Streamlit

**Lancer le Dashboard :**
```powershell
& "D:/Spyder/Python/python.exe" -m streamlit run app.py
```

**Accéder au Dashboard :**
- Dashboard : http://localhost:8501

### 3. MLFlow UI

**Lancer MLFlow :**
```powershell
mlflow ui
```

**Accéder à MLFlow :**
- MLFlow UI : http://localhost:5000

## Explication Technique

- **`0.0.0.0`** : Adresse d'écoute du serveur (écoute sur toutes les interfaces réseau)
- **`localhost` ou `127.0.0.1`** : Adresse à utiliser dans votre navigateur pour accéder aux services

Le serveur écoute sur `0.0.0.0` pour accepter les connexions, mais vous devez utiliser `localhost` dans votre navigateur.

## Dépannage

Si vous obtenez "ERR_ADDRESS_INVALID" :
1. Vérifiez que le service est bien lancé
2. Utilisez `localhost` ou `127.0.0.1` au lieu de `0.0.0.0`
3. Vérifiez que le port n'est pas déjà utilisé

Pour vérifier si un port est utilisé :
```powershell
Get-NetTCPConnection -LocalPort 8000
```

