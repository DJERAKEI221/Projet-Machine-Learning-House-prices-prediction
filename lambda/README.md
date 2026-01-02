# Déploiement AWS Lambda

Ce dossier contient le code pour déployer le modèle de prédiction sur AWS Lambda.

## Structure

```
lambda/
├── lambda_function.py      # Code principal de la fonction
├── requirements.txt        # Dépendances Python
├── model/                  # Modèle (à ajouter)
│   └── final_model.pkl
└── README.md              # Ce fichier
```

## Prérequis

1. **AWS CLI installé et configuré**
   ```bash
   aws configure
   ```

2. **Modèle entraîné**
   ```bash
   python train.py
   # Le modèle sera dans output/models/final_model.pkl
   ```

3. **IAM Role avec permissions Lambda**
   - Créer un rôle IAM avec la politique `AWSLambdaBasicExecutionRole`

## Déploiement

### Option 1: Déploiement Manuel

#### 1. Préparer le package

```bash
# Depuis la racine du projet
cd lambda

# Copier le modèle
mkdir -p model
cp ../output/models/final_model.pkl model/

# Copier les modules src (ou utiliser Lambda Layers)
mkdir -p src
cp -r ../src/* src/

# Créer le package
zip -r lambda_function.zip . -x "*.pyc" "__pycache__/*" "*.git*"
```

#### 2. Créer la fonction Lambda

```bash
aws lambda create-function \
    --function-name house-price-predictor \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_function.zip \
    --timeout 60 \
    --memory-size 1024 \
    --description "Prédiction des prix immobiliers"
```

#### 3. Mettre à jour le code

```bash
aws lambda update-function-code \
    --function-name house-price-predictor \
    --zip-file fileb://lambda_function.zip
```

### Option 2: Utiliser Lambda Layers (Recommandé)

Pour réduire la taille du package, créer un layer avec les dépendances :

```bash
# Créer un layer avec les dépendances
mkdir -p layer/python
pip install -r requirements.txt -t layer/python/
cd layer
zip -r ../python-deps-layer.zip python/
cd ..

# Publier le layer
aws lambda publish-layer-version \
    --layer-name python-deps \
    --zip-file fileb://python-deps-layer.zip \
    --compatible-runtimes python3.11

# Noter l'ARN du layer (ex: arn:aws:lambda:region:account:layer:python-deps:1)
```

Puis attacher le layer à la fonction :
```bash
aws lambda update-function-configuration \
    --function-name house-price-predictor \
    --layers arn:aws:lambda:region:account:layer:python-deps:1
```

### Option 3: Utiliser Serverless Framework

1. Installer Serverless Framework :
```bash
npm install -g serverless
```

2. Créer `serverless.yml` :
```yaml
service: house-price-predictor

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 1024
  timeout: 60

functions:
  predict:
    handler: lambda/lambda_function.lambda_handler
    events:
      - http:
          path: predict
          method: post
          cors: true

package:
  patterns:
    - 'lambda/**'
    - 'src/**'
    - 'output/models/**'
```

3. Déployer :
```bash
serverless deploy
```

## Tester la Fonction

### Test Local

```bash
python lambda/lambda_function.py
```

### Test sur AWS Lambda

```bash
# Créer un fichier de test
cat > test_event.json << EOF
{
  "body": "{\"features\": {\"OverallQual\": 7, \"GrLivArea\": 1710, \"Neighborhood\": \"CollgCr\"}}"
}
EOF

# Tester
aws lambda invoke \
    --function-name house-price-predictor \
    --payload file://test_event.json \
    response.json

# Voir la réponse
cat response.json | jq
```

### Test via API Gateway

Si vous avez configuré API Gateway :

```bash
curl -X POST https://YOUR_API_ID.execute-api.REGION.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "OverallQual": 7,
      "GrLivArea": 1710,
      "Neighborhood": "CollgCr"
    }
  }'
```

## Configuration API Gateway (Optionnel)

Pour exposer la fonction via HTTP :

1. Créer une API REST dans API Gateway
2. Créer une ressource `/predict`
3. Créer une méthode POST
4. Intégrer avec la fonction Lambda
5. Déployer l'API

## Optimisations

### 1. Provisioned Concurrency (Éviter Cold Start)

```bash
aws lambda put-provisioned-concurrency-config \
    --function-name house-price-predictor \
    --qualifier $LATEST \
    --provisioned-concurrent-executions 2
```

### 2. Modèle dans S3 (Pour gros modèles)

Modifier `lambda_function.py` pour télécharger depuis S3 :

```python
import boto3

def load_model_from_s3():
    s3 = boto3.client('s3')
    model_path = '/tmp/final_model.pkl'
    
    if not os.path.exists(model_path):
        s3.download_file('my-models-bucket', 'model/final_model.pkl', model_path)
    
    return joblib.load(model_path)
```

### 3. Environment Variables

```bash
aws lambda update-function-configuration \
    --function-name house-price-predictor \
    --environment Variables="{MODEL_BUCKET=my-bucket,MODEL_KEY=model/final_model.pkl}"
```

## Monitoring

### CloudWatch Logs

Les logs sont automatiquement envoyés à CloudWatch :
```bash
aws logs tail /aws/lambda/house-price-predictor --follow
```

### Métriques

Voir les métriques dans la console AWS :
- Nombre d'invocations
- Durée d'exécution
- Erreurs
- Coûts

## Coûts

### Estimation pour 1000 prédictions/jour

- **Invocations** : 30,000/mois × $0.20/1M = $0.006/mois
- **Temps d'exécution** : 30,000 × 1s × 1GB × $0.0000166667 = $0.50/mois
- **Total** : ~$0.51/mois

Très économique pour un usage modéré !

## Dépannage

### Erreur "Module not found"
- Vérifier que les dépendances sont dans le layer ou le package
- Vérifier le PYTHONPATH dans la fonction

### Erreur "Model not found"
- Vérifier que `model/final_model.pkl` est dans le package
- Ou configurer S3 et télécharger depuis S3

### Timeout
- Augmenter le timeout : `--timeout 120`
- Optimiser le code de chargement du modèle

### Cold Start lent
- Utiliser Provisioned Concurrency
- Réduire la taille du modèle
- Utiliser Lambda Layers

## Ressources

- [Documentation AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Serverless Framework](https://www.serverless.com/)
- [Guide complet Serverless](docs/SERVERLESS_FUNCTIONS.md)

