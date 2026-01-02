# Guide Complet : Déploiement sur AWS Lambda

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Préparation](#préparation)
3. [Méthode 1 : Déploiement Manuel](#méthode-1--déploiement-manuel)
4. [Méthode 2 : Avec Lambda Layers](#méthode-2--avec-lambda-layers)
5. [Méthode 3 : Avec Serverless Framework](#méthode-3--avec-serverless-framework)
6. [Configuration API Gateway](#configuration-api-gateway)
7. [Test et Validation](#test-et-validation)
8. [Monitoring et Logs](#monitoring-et-logs)
9. [Optimisation](#optimisation)
10. [Dépannage](#dépannage)

---

## 🔧 Prérequis

### 1. Compte AWS

- Créer un compte AWS : https://aws.amazon.com/
- Accès à la console AWS
- Compte avec permissions pour Lambda, IAM, S3 (optionnel)

### 2. AWS CLI Installé

**Windows (PowerShell) :**
```powershell
# Télécharger depuis https://aws.amazon.com/cli/
# Ou installer via MSI
# Vérifier l'installation
aws --version
```

**Linux/Mac :**
```bash
# Installer AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Vérifier
aws --version
```

### 3. Configuration AWS CLI

```bash
aws configure
```

Vous devrez fournir :
- **AWS Access Key ID** : Créer dans IAM → Users → Security credentials
- **AWS Secret Access Key** : Généré avec la clé
- **Default region** : `us-east-1` (ou votre région préférée)
- **Default output format** : `json`

### 4. Modèle Entraîné

```bash
# Entraîner le modèle si pas déjà fait
python train.py

# Vérifier que le modèle existe
ls output/models/final_model.pkl
```

### 5. Permissions IAM

Créer un rôle IAM pour Lambda avec les permissions suivantes :
- `AWSLambdaBasicExecutionRole` (logs CloudWatch)
- `AmazonS3ReadOnlyAccess` (si modèle dans S3)

---

## 📦 Préparation

### Étape 1 : Préparer la Structure

```bash
# Depuis la racine du projet
cd lambda

# Créer les dossiers nécessaires
mkdir -p model src

# Copier le modèle
cp ../output/models/final_model.pkl model/

# Copier les modules source
cp -r ../src/* src/
```

### Étape 2 : Vérifier les Fichiers

Votre structure `lambda/` devrait ressembler à :

```
lambda/
├── lambda_function.py      ✅ Code principal
├── requirements.txt         ✅ Dépendances
├── README.md               ✅ Documentation
├── model/
│   └── final_model.pkl     ✅ Modèle entraîné
└── src/                    ✅ Modules (optionnel si dans layer)
    ├── data_processing.py
    ├── feature_engineering.py
    └── ...
```

---

## 🚀 Méthode 1 : Déploiement Manuel

### Étape 1 : Créer le Package ZIP

**Windows (PowerShell) :**
```powershell
cd lambda

# Créer le ZIP (exclure les fichiers inutiles)
Compress-Archive -Path lambda_function.py,requirements.txt,model,src -DestinationPath lambda_function.zip -Force

# Vérifier la taille (doit être < 50 MB pour upload direct)
(Get-Item lambda_function.zip).Length / 1MB
```

**Linux/Mac :**
```bash
cd lambda

# Créer le ZIP
zip -r lambda_function.zip . \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*.git*" \
    -x "*.DS_Store" \
    -x "README.md"

# Vérifier la taille
ls -lh lambda_function.zip
```

### Étape 2 : Créer le Rôle IAM

```bash
# Créer un fichier de politique de confiance
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Créer le rôle
aws iam create-role \
    --role-name lambda-house-price-role \
    --assume-role-policy-document file://trust-policy.json

# Attacher la politique d'exécution de base
aws iam attach-role-policy \
    --role-name lambda-house-price-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Obtenir l'ARN du rôle (notez-le pour l'étape suivante)
aws iam get-role --role-name lambda-house-price-role --query 'Role.Arn' --output text
```

### Étape 3 : Créer la Fonction Lambda

```bash
# Remplacer YOUR_ACCOUNT_ID et YOUR_REGION
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"  # Changez selon votre région
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lambda-house-price-role"

# Créer la fonction
aws lambda create-function \
    --function-name house-price-predictor \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_function.zip \
    --timeout 60 \
    --memory-size 1024 \
    --description "Prédiction des prix immobiliers - Projet Laplace Immo" \
    --environment Variables="{ENVIRONMENT=production}" \
    --region ${REGION}
```

**Résultat attendu :**
```json
{
    "FunctionName": "house-price-predictor",
    "FunctionArn": "arn:aws:lambda:us-east-1:ACCOUNT:function:house-price-predictor",
    "Runtime": "python3.11",
    "Role": "arn:aws:iam::ACCOUNT:role/lambda-house-price-role",
    "State": "Active"
}
```

### Étape 4 : Mettre à Jour le Code

Si vous modifiez le code plus tard :

```bash
# Recréer le ZIP
zip -r lambda_function.zip . -x "*.pyc" "__pycache__/*"

# Mettre à jour la fonction
aws lambda update-function-code \
    --function-name house-price-predictor \
    --zip-file fileb://lambda_function.zip \
    --region ${REGION}
```

---

## 🎯 Méthode 2 : Avec Lambda Layers (Recommandé)

Cette méthode réduit la taille du package principal en externalisant les dépendances.

### Étape 1 : Créer le Layer

```bash
# Créer un dossier pour le layer
mkdir -p layer/python
cd layer/python

# Installer les dépendances dans ce dossier
pip install -r ../../requirements.txt -t .

# Retourner au dossier layer
cd ..

# Créer le ZIP du layer
zip -r python-deps-layer.zip python/

# Vérifier la taille (doit être < 50 MB)
ls -lh python-deps-layer.zip
```

### Étape 2 : Publier le Layer

```bash
# Publier le layer
LAYER_ARN=$(aws lambda publish-layer-version \
    --layer-name python-deps \
    --zip-file fileb://python-deps-layer.zip \
    --compatible-runtimes python3.11 python3.10 \
    --query 'LayerVersionArn' \
    --output text)

echo "Layer ARN: ${LAYER_ARN}"
```

### Étape 3 : Créer le Package Principal (Sans Dépendances)

```bash
cd ../lambda

# Créer un ZIP minimal (sans les dépendances)
zip -r lambda_function.zip lambda_function.py model/ src/ \
    -x "*.pyc" "__pycache__/*" "requirements.txt"
```

### Étape 4 : Créer la Fonction avec le Layer

```bash
# Créer la fonction avec le layer attaché
aws lambda create-function \
    --function-name house-price-predictor \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_function.zip \
    --layers ${LAYER_ARN} \
    --timeout 60 \
    --memory-size 1024 \
    --region ${REGION}
```

### Étape 5 : Mettre à Jour le Layer

Si vous modifiez les dépendances :

```bash
# Recréer le layer
cd layer
zip -r python-deps-layer.zip python/

# Publier une nouvelle version
aws lambda publish-layer-version \
    --layer-name python-deps \
    --zip-file fileb://python-deps-layer.zip \
    --compatible-runtimes python3.11

# Mettre à jour la fonction avec le nouveau layer
aws lambda update-function-configuration \
    --function-name house-price-predictor \
    --layers ${NEW_LAYER_ARN}
```

---

## 🛠️ Méthode 3 : Avec Serverless Framework

Cette méthode automatise tout le processus.

### Étape 1 : Installer Serverless Framework

```bash
# Installer Node.js si pas déjà installé
# Puis installer Serverless
npm install -g serverless

# Vérifier
serverless --version
```

### Étape 2 : Créer serverless.yml

Créer `serverless.yml` à la racine du projet :

```yaml
service: house-price-predictor

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 1024
  timeout: 60
  environment:
    ENVIRONMENT: production
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: "arn:aws:logs:*:*:*"

functions:
  predict:
    handler: lambda/lambda_function.lambda_handler
    description: Prédiction des prix immobiliers
    events:
      - http:
          path: predict
          method: post
          cors: true
      - http:
          path: predict
          method: options
          cors: true

package:
  patterns:
    - '!**'
    - 'lambda/**'
    - '!lambda/README.md'
    - 'output/models/**'
    - 'src/**'
    - '!**/*.pyc'
    - '!**/__pycache__'

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    layer: true
```

### Étape 3 : Installer le Plugin

```bash
npm install --save-dev serverless-python-requirements
```

### Étape 4 : Déployer

```bash
# Déployer (créera tout automatiquement)
serverless deploy

# Ou en mode verbose
serverless deploy --verbose
```

### Étape 5 : Obtenir l'URL de l'API

```bash
# Lister les endpoints
serverless info

# Vous obtiendrez quelque chose comme :
# POST - https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/predict
```

### Étape 6 : Supprimer (si besoin)

```bash
serverless remove
```

---

## 🌐 Configuration API Gateway

### Option A : Via Console AWS

1. **Aller dans API Gateway** → Créer une API REST
2. **Créer une ressource** `/predict`
3. **Créer une méthode POST**
4. **Intégrer avec Lambda** → Sélectionner `house-price-predictor`
5. **Activer CORS** si nécessaire
6. **Déployer l'API** → Créer un stage (ex: `prod`)

### Option B : Via AWS CLI

```bash
# Créer l'API
API_ID=$(aws apigateway create-rest-api \
    --name house-price-api \
    --query 'id' \
    --output text)

# Obtenir la racine
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id ${API_ID} \
    --query 'items[0].id' \
    --output text)

# Créer la ressource /predict
RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id ${API_ID} \
    --parent-id ${ROOT_ID} \
    --path-part predict \
    --query 'id' \
    --output text)

# Créer la méthode POST
aws apigateway put-method \
    --rest-api-id ${API_ID} \
    --resource-id ${RESOURCE_ID} \
    --http-method POST \
    --authorization-type NONE

# Intégrer avec Lambda
LAMBDA_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:house-price-predictor"

aws apigateway put-integration \
    --rest-api-id ${API_ID} \
    --resource-id ${RESOURCE_ID} \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations

# Donner la permission à API Gateway d'appeler Lambda
aws lambda add-permission \
    --function-name house-price-predictor \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*"

# Déployer
aws apigateway create-deployment \
    --rest-api-id ${API_ID} \
    --stage-name prod
```

---

## 🧪 Test et Validation

### Test 1 : Test Local

```bash
# Tester localement
cd lambda
python lambda_function.py
```

### Test 2 : Test Direct Lambda

```bash
# Créer un fichier de test
cat > test_event.json << EOF
{
  "body": "{\"features\": {\"OverallQual\": 7, \"GrLivArea\": 1710, \"Neighborhood\": \"CollgCr\", \"YearBuilt\": 2003, \"LotArea\": 8450, \"GarageCars\": 2}}"
}
EOF

# Tester la fonction
aws lambda invoke \
    --function-name house-price-predictor \
    --payload file://test_event.json \
    --region ${REGION} \
    response.json

# Voir la réponse
cat response.json | python -m json.tool
```

**Résultat attendu :**
```json
{
  "statusCode": 200,
  "body": "{\"predicted_price\": 180000.0, \"confidence\": 0.85, \"message\": \"Prédiction réussie\"}"
}
```

### Test 3 : Test via API Gateway

```bash
# Obtenir l'URL de l'API
API_URL=$(aws apigateway get-rest-apis \
    --query "items[?name=='house-price-api'].id" \
    --output text)

# Tester
curl -X POST https://${API_URL}.execute-api.${REGION}.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "OverallQual": 7,
      "GrLivArea": 1710,
      "Neighborhood": "CollgCr",
      "YearBuilt": 2003,
      "LotArea": 8450,
      "GarageCars": 2
    }
  }'
```

### Test 4 : Test depuis Python

```python
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

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
print(json.dumps(json.loads(result['body']), indent=2))
```

---

## 📊 Monitoring et Logs

### Voir les Logs en Temps Réel

```bash
# Suivre les logs
aws logs tail /aws/lambda/house-price-predictor --follow

# Voir les dernières lignes
aws logs tail /aws/lambda/house-price-predictor --since 1h
```

### Métriques CloudWatch

```bash
# Voir les métriques
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=house-price-predictor \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum
```

### Console AWS

1. **Lambda Console** → Sélectionner la fonction → Onglet "Monitoring"
2. **CloudWatch** → Logs → `/aws/lambda/house-price-predictor`
3. **CloudWatch** → Metrics → AWS/Lambda

---

## ⚡ Optimisation

### 1. Réduire le Cold Start

```bash
# Provisioned Concurrency (garder des instances chaudes)
aws lambda put-provisioned-concurrency-config \
    --function-name house-price-predictor \
    --qualifier \$LATEST \
    --provisioned-concurrent-executions 2
```

**Coût supplémentaire** : ~$0.015/heure par instance

### 2. Modèle dans S3 (Pour gros modèles)

Si le modèle est > 50 MB, le stocker dans S3 :

```bash
# Uploader le modèle dans S3
aws s3 cp output/models/final_model.pkl s3://my-models-bucket/model/final_model.pkl

# Modifier lambda_function.py pour télécharger depuis S3
# (voir code dans lambda_function.py)
```

### 3. Augmenter la Mémoire

```bash
# Plus de mémoire = plus de CPU = plus rapide
aws lambda update-function-configuration \
    --function-name house-price-predictor \
    --memory-size 2048
```

### 4. Variables d'Environnement

```bash
aws lambda update-function-configuration \
    --function-name house-price-predictor \
    --environment Variables="{MODEL_BUCKET=my-bucket,ENVIRONMENT=prod}"
```

---

## 🔧 Dépannage

### Problème 1 : "Module not found"

**Solution :**
```bash
# Vérifier que les dépendances sont dans le layer ou le package
# Vérifier le PYTHONPATH dans lambda_function.py
# Utiliser Lambda Layers pour les dépendances
```

### Problème 2 : "Model not found"

**Solution :**
```bash
# Vérifier que model/final_model.pkl est dans le ZIP
unzip -l lambda_function.zip | grep final_model.pkl

# Ou utiliser S3
aws s3 cp output/models/final_model.pkl s3://bucket/model.pkl
```

### Problème 3 : Timeout

**Solution :**
```bash
# Augmenter le timeout
aws lambda update-function-configuration \
    --function-name house-price-predictor \
    --timeout 120
```

### Problème 4 : Cold Start Lent

**Solution :**
- Utiliser Provisioned Concurrency
- Réduire la taille du modèle
- Optimiser le code de chargement

### Problème 5 : Erreur de Permissions

**Solution :**
```bash
# Vérifier le rôle IAM
aws iam get-role --role-name lambda-house-price-role

# Ajouter des permissions si nécessaire
aws iam attach-role-policy \
    --role-name lambda-house-price-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

---

## 📝 Checklist de Déploiement

- [ ] AWS CLI installé et configuré
- [ ] Modèle entraîné (`output/models/final_model.pkl`)
- [ ] Rôle IAM créé avec les bonnes permissions
- [ ] Package ZIP créé avec tous les fichiers nécessaires
- [ ] Fonction Lambda créée
- [ ] Test local réussi
- [ ] Test Lambda réussi
- [ ] API Gateway configuré (si nécessaire)
- [ ] CORS activé (si nécessaire)
- [ ] Monitoring configuré
- [ ] Documentation mise à jour

---

## 💰 Estimation des Coûts

### Pour 1000 prédictions/jour (30,000/mois)

- **Invocations** : 30,000 × $0.20/1M = **$0.006/mois**
- **Temps d'exécution** : 30,000 × 1s × 1GB × $0.0000166667 = **$0.50/mois**
- **Total** : **~$0.51/mois**

### Avec Provisioned Concurrency (2 instances)

- **Invocations** : $0.006/mois
- **Temps d'exécution** : $0.50/mois
- **Provisioned Concurrency** : 2 × $0.015/heure × 730h = **$21.90/mois**
- **Total** : **~$22.41/mois**

---

## 🎓 Ressources Supplémentaires

- [Documentation AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Guide Serverless Functions](docs/SERVERLESS_FUNCTIONS.md)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Serverless Framework Docs](https://www.serverless.com/framework/docs)

---

## ✅ Conclusion

Vous avez maintenant votre modèle déployé sur AWS Lambda ! 

**Prochaines étapes :**
1. Tester l'API
2. Configurer le monitoring
3. Optimiser les performances
4. Documenter l'API pour les utilisateurs

**Besoin d'aide ?** Consultez la section [Dépannage](#dépannage) ou les logs CloudWatch.

