# Serverless Functions pour le Modèle de Prédiction

## Qu'est-ce qu'une Serverless Function ?

Une **Serverless Function** (fonction sans serveur) est une fonction qui s'exécute dans le cloud sans que vous ayez à gérer l'infrastructure. Vous payez uniquement pour le temps d'exécution.

### Avantages
- ✅ **Pas de gestion de serveur** - Le cloud gère tout
- ✅ **Scaling automatique** - S'adapte à la charge
- ✅ **Pay-per-use** - Payez seulement ce que vous utilisez
- ✅ **Déploiement simple** - Juste uploader votre code
- ✅ **Haute disponibilité** - Géré par le cloud provider

### Inconvénients
- ❌ **Limites de temps** - Généralement 15 minutes max
- ❌ **Limites de mémoire** - 3-10 GB selon le provider
- ❌ **Cold start** - Premier appel peut être lent
- ❌ **Vendor lock-in** - Dépendance au provider

## Providers Disponibles

### 1. AWS Lambda
- **Langages** : Python, Node.js, Java, Go, .NET, Ruby
- **Timeout max** : 15 minutes
- **Mémoire max** : 10 GB
- **Prix** : ~$0.20 par million de requêtes

### 2. Azure Functions
- **Langages** : Python, Node.js, C#, Java, PowerShell
- **Timeout max** : 10 minutes (Consumption), illimité (Premium)
- **Mémoire max** : 3.5 GB (Consumption)
- **Prix** : ~$0.16 par million d'exécutions

### 3. Google Cloud Functions
- **Langages** : Python, Node.js, Go, Java
- **Timeout max** : 9 minutes (1st gen), 60 minutes (2nd gen)
- **Mémoire max** : 8 GB
- **Prix** : ~$0.40 par million d'invocations

### 4. Vercel Functions
- **Langages** : Python, Node.js, Go
- **Timeout max** : 10 secondes (Hobby), 60 secondes (Pro)
- **Idéal pour** : Applications web modernes

## Architecture Serverless pour notre Modèle

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────────┐
│  API Gateway    │  (Route les requêtes)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lambda Function│  (Notre modèle Python)
│  - Charge modèle│
│  - Prédiction   │
│  - Retour JSON  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S3 / EFS       │  (Stockage du modèle)
│  (Modèle .pkl)  │
└─────────────────┘
```

## Implémentation AWS Lambda

### Structure du Projet

```
lambda/
├── lambda_function.py      # Code principal de la fonction
├── requirements.txt        # Dépendances
├── model/                  # Modèle (ou pointer vers S3)
│   └── final_model.pkl
└── src/                    # Modules (copiés ou en layer)
    ├── data_processing.py
    ├── feature_engineering.py
    └── ...
```

### Code Lambda Function

```python
# lambda_function.py
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ajouter les modules au path
sys.path.insert(0, '/opt/python')  # Pour Lambda Layers
sys.path.insert(0, str(Path(__file__).parent))

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer

# Variables globales (chargées une fois au cold start)
model = None
processor = None
feature_engineer = None

def load_model():
    """Charger le modèle (appelé une seule fois)."""
    global model, processor, feature_engineer
    
    if model is None:
        # Option 1: Modèle dans le package Lambda
        model_path = Path(__file__).parent / "model" / "final_model.pkl"
        
        # Option 2: Modèle dans S3 (recommandé pour gros modèles)
        # import boto3
        # s3 = boto3.client('s3')
        # s3.download_file('bucket-name', 'model/final_model.pkl', '/tmp/model.pkl')
        # model_path = '/tmp/model.pkl'
        
        if model_path.exists():
            model = joblib.load(model_path)
            processor = DataProcessor()
            feature_engineer = FeatureEngineer()
            print("Modèle chargé avec succès")
        else:
            raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
    
    return model, processor, feature_engineer

def lambda_handler(event, context):
    """
    Handler principal pour AWS Lambda.
    
    Args:
        event: Données de la requête (dict ou API Gateway event)
        context: Contexte Lambda (métadonnées)
    
    Returns:
        Réponse JSON avec la prédiction
    """
    try:
        # Charger le modèle (une seule fois)
        model, processor, feature_engineer = load_model()
        
        # Extraire les données de la requête
        if 'body' in event:
            # API Gateway envoie le body comme string JSON
            body = json.loads(event['body'])
        else:
            # Appel direct Lambda
            body = event
        
        # Extraire les features
        features = body.get('features', body)
        
        # Convertir en DataFrame
        house_df = pd.DataFrame([features])
        
        # Preprocessing
        house_df = processor.handle_missing_values(house_df, is_train=False)
        house_df = feature_engineer.create_features(house_df)
        
        # Prédiction
        prediction = model.predict(house_df)[0]
        
        # Réponse
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Pour CORS
            },
            'body': json.dumps({
                'predicted_price': float(prediction),
                'confidence': 0.85,  # Placeholder
                'message': 'Prédiction réussie'
            })
        }
    
    except Exception as e:
        # Gestion d'erreur
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Erreur lors de la prédiction'
            })
        }
```

### Déploiement avec AWS CLI

```bash
# 1. Créer un package de déploiement
cd lambda
zip -r lambda_function.zip . -x "*.pyc" "__pycache__/*"

# 2. Créer la fonction Lambda
aws lambda create-function \
    --function-name house-price-predictor \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_function.zip \
    --timeout 60 \
    --memory-size 1024

# 3. Mettre à jour le code
aws lambda update-function-code \
    --function-name house-price-predictor \
    --zip-file fileb://lambda_function.zip
```

### Déploiement avec Serverless Framework

```yaml
# serverless.yml
service: house-price-predictor

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 1024
  timeout: 60
  environment:
    MODEL_BUCKET: my-models-bucket

functions:
  predict:
    handler: lambda_function.lambda_handler
    events:
      - http:
          path: predict
          method: post
          cors: true
    layers:
      - arn:aws:lambda:region:account:layer:python-deps:1

package:
  patterns:
    - '!**'
    - 'lambda_function.py'
    - 'model/**'
    - 'src/**'
```

Déploiement :
```bash
npm install -g serverless
serverless deploy
```

## Implémentation Azure Functions

### Structure

```
azure_function/
├── function_app.py         # Code principal
├── requirements.txt
├── host.json              # Configuration
└── model/
    └── final_model.pkl
```

### Code Azure Function

```python
# function_app.py
import azure.functions as func
import json
import joblib
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer

# Variables globales
model = None
processor = None
feature_engineer = None

def load_model():
    global model, processor, feature_engineer
    if model is None:
        model_path = Path(__file__).parent / "model" / "final_model.pkl"
        model = joblib.load(model_path)
        processor = DataProcessor()
        feature_engineer = FeatureEngineer()
    return model, processor, feature_engineer

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function HTTP trigger."""
    try:
        model, processor, feature_engineer = load_model()
        
        # Lire les données de la requête
        req_body = req.get_json()
        features = req_body.get('features', req_body)
        
        # Preprocessing et prédiction
        house_df = pd.DataFrame([features])
        house_df = processor.handle_missing_values(house_df, is_train=False)
        house_df = feature_engineer.create_features(house_df)
        prediction = model.predict(house_df)[0]
        
        return func.HttpResponse(
            json.dumps({
                'predicted_price': float(prediction),
                'confidence': 0.85
            }),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )
```

## Optimisations pour Serverless

### 1. Lambda Layers (AWS)
Créer un layer avec les dépendances pour réduire la taille du package :

```bash
# Créer un layer
mkdir python
pip install -r requirements.txt -t python/
zip -r layer.zip python/

# Uploader le layer
aws lambda publish-layer-version \
    --layer-name python-deps \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.11
```

### 2. Modèle dans S3/Blob Storage
Pour les gros modèles, stocker dans S3 et télécharger au runtime :

```python
import boto3
import os

def load_model_from_s3():
    s3 = boto3.client('s3')
    model_path = '/tmp/model.pkl'
    
    # Télécharger seulement si pas déjà présent
    if not os.path.exists(model_path):
        s3.download_file('my-bucket', 'model/final_model.pkl', model_path)
    
    return joblib.load(model_path)
```

### 3. Provisioned Concurrency (AWS)
Éviter le cold start en gardant des instances chaudes :

```bash
aws lambda put-provisioned-concurrency-config \
    --function-name house-price-predictor \
    --qualifier $LATEST \
    --provisioned-concurrent-executions 2
```

## Coûts Estimés

### AWS Lambda
- **1 million de requêtes/mois** : ~$0.20
- **Temps d'exécution** : $0.0000166667 par GB-seconde
- **Exemple** : 1M requêtes × 1s × 1GB = ~$16.67/mois

### Azure Functions
- **1 million d'exécutions** : ~$0.16
- **Temps d'exécution** : $0.000016/GB-seconde
- **Exemple** : Similaire à AWS

## Comparaison avec HTTP API

| Critère | HTTP API (FastAPI) | Serverless (Lambda) |
|---------|-------------------|---------------------|
| **Coût** | Serveur toujours actif | Pay-per-use |
| **Scaling** | Manuel | Automatique |
| **Maintenance** | Vous gérez | Géré par AWS |
| **Latence** | Faible (toujours chaud) | Variable (cold start) |
| **Complexité** | Simple | Moyenne |
| **Idéal pour** | Usage constant | Usage sporadique |

## Quand Utiliser Serverless ?

### ✅ Utilisez Serverless si :
- Charge variable (pics et creux)
- Budget limité (pay-per-use)
- Pas d'infrastructure à gérer
- Besoin de scaling automatique
- Usage sporadique

### ❌ N'utilisez PAS Serverless si :
- Charge constante et élevée (plus cher)
- Besoin de latence très faible
- Modèle très gros (>500MB)
- Besoin de connexions persistantes

## Exemple d'Intégration

### Depuis Python
```python
import boto3
import json

lambda_client = boto3.client('lambda')

response = lambda_client.invoke(
    FunctionName='house-price-predictor',
    Payload=json.dumps({
        'features': {
            'OverallQual': 7,
            'GrLivArea': 1710,
            'Neighborhood': 'CollgCr'
        }
    })
)

result = json.loads(response['Payload'].read())
print(f"Prix prédit: ${result['predicted_price']:,.2f}")
```

### Depuis JavaScript/Node.js
```javascript
const AWS = require('aws-sdk');
const lambda = new AWS.Lambda();

const params = {
  FunctionName: 'house-price-predictor',
  Payload: JSON.stringify({
    features: {
      OverallQual: 7,
      GrLivArea: 1710,
      Neighborhood: 'CollgCr'
    }
  })
};

lambda.invoke(params, (err, data) => {
  if (err) console.error(err);
  else {
    const result = JSON.parse(data.Payload);
    console.log(`Prix prédit: $${result.predicted_price.toLocaleString()}`);
  }
});
```

## Conclusion

Les Serverless Functions sont excellentes pour :
- **Déploiement rapide** sans gestion d'infrastructure
- **Coûts optimisés** pour usage sporadique
- **Scaling automatique** selon la demande

Pour ce projet académique, une **API HTTP classique** reste plus simple, mais les Serverless Functions sont une excellente option pour la production avec une charge variable.

