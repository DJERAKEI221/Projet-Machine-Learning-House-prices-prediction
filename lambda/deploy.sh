#!/bin/bash
# Script d'aide pour déployer sur AWS Lambda
# Usage: ./deploy.sh [method]
# Methods: manual, layer, serverless

set -e

METHOD=${1:-manual}
FUNCTION_NAME="house-price-predictor"
REGION=${AWS_REGION:-us-east-1}
RUNTIME="python3.11"
TIMEOUT=60
MEMORY=1024

echo "=========================================="
echo "Déploiement AWS Lambda - House Price Predictor"
echo "=========================================="
echo "Méthode: $METHOD"
echo "Fonction: $FUNCTION_NAME"
echo "Région: $REGION"
echo "=========================================="

# Vérifier les prérequis
echo ""
echo "Vérification des prérequis..."
command -v aws >/dev/null 2>&1 || { echo "AWS CLI non installé. Installez-le d'abord."; exit 1; }
command -v zip >/dev/null 2>&1 || { echo "zip non installé. Installez-le d'abord."; exit 1; }

# Vérifier la configuration AWS
echo "Vérification de la configuration AWS..."
aws sts get-caller-identity > /dev/null || { echo "AWS CLI non configuré. Exécutez 'aws configure'."; exit 1; }

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Compte AWS: $ACCOUNT_ID"

# Vérifier que le modèle existe
if [ ! -f "model/final_model.pkl" ]; then
    echo "ERREUR: Modèle non trouvé dans model/final_model.pkl"
    echo "Entraînez d'abord le modèle avec: python train.py"
    exit 1
fi

echo "✅ Prérequis OK"
echo ""

case $METHOD in
    manual)
        echo "=== Déploiement Manuel ==="
        
        # Créer le package
        echo "Création du package ZIP..."
        zip -r lambda_function.zip . \
            -x "*.pyc" \
            -x "__pycache__/*" \
            -x "*.git*" \
            -x "*.DS_Store" \
            -x "README.md" \
            -x "deploy.sh" \
            -x "*.zip"
        
        SIZE=$(ls -lh lambda_function.zip | awk '{print $5}')
        echo "Taille du package: $SIZE"
        
        # Vérifier la taille (doit être < 50 MB)
        SIZE_MB=$(du -m lambda_function.zip | cut -f1)
        if [ $SIZE_MB -gt 50 ]; then
            echo "⚠️  ATTENTION: Package > 50 MB. Utilisez Lambda Layers."
        fi
        
        # Créer le rôle IAM si nécessaire
        echo ""
        echo "Vérification du rôle IAM..."
        if ! aws iam get-role --role-name lambda-house-price-role > /dev/null 2>&1; then
            echo "Création du rôle IAM..."
            cat > /tmp/trust-policy.json << EOF
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
            
            aws iam create-role \
                --role-name lambda-house-price-role \
                --assume-role-policy-document file:///tmp/trust-policy.json
            
            aws iam attach-role-policy \
                --role-name lambda-house-price-role \
                --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
            
            echo "✅ Rôle créé"
        else
            echo "✅ Rôle existe déjà"
        fi
        
        ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lambda-house-price-role"
        
        # Créer ou mettre à jour la fonction
        echo ""
        if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION > /dev/null 2>&1; then
            echo "Mise à jour de la fonction existante..."
            aws lambda update-function-code \
                --function-name $FUNCTION_NAME \
                --zip-file fileb://lambda_function.zip \
                --region $REGION
        else
            echo "Création de la fonction..."
            aws lambda create-function \
                --function-name $FUNCTION_NAME \
                --runtime $RUNTIME \
                --role $ROLE_ARN \
                --handler lambda_function.lambda_handler \
                --zip-file fileb://lambda_function.zip \
                --timeout $TIMEOUT \
                --memory-size $MEMORY \
                --description "Prédiction des prix immobiliers - Projet Laplace Immo" \
                --region $REGION
        fi
        
        echo ""
        echo "✅ Déploiement terminé!"
        echo ""
        echo "Pour tester:"
        echo "  aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"body\":\"{\\\"features\\\":{\\\"OverallQual\\\":7,\\\"GrLivArea\\\":1710}}\"}' response.json"
        ;;
    
    layer)
        echo "=== Déploiement avec Lambda Layers ==="
        
        # Créer le layer
        echo "Création du Lambda Layer..."
        mkdir -p ../layer/python
        cd ../layer/python
        
        if [ -f "../../lambda/requirements.txt" ]; then
            pip install -r ../../lambda/requirements.txt -t . --quiet
        else
            echo "Installation des dépendances de base..."
            pip install pandas numpy scikit-learn lightgbm joblib -t . --quiet
        fi
        
        cd ..
        zip -r python-deps-layer.zip python/ > /dev/null
        LAYER_SIZE=$(ls -lh python-deps-layer.zip | awk '{print $5}')
        echo "Taille du layer: $LAYER_SIZE"
        
        # Publier le layer
        echo "Publication du layer..."
        LAYER_ARN=$(aws lambda publish-layer-version \
            --layer-name python-deps \
            --zip-file fileb://python-deps-layer.zip \
            --compatible-runtimes python3.11 python3.10 \
            --query 'LayerVersionArn' \
            --output text)
        
        echo "✅ Layer publié: $LAYER_ARN"
        
        # Créer le package principal (sans dépendances)
        cd ../lambda
        echo ""
        echo "Création du package principal..."
        zip -r lambda_function.zip lambda_function.py model/ src/ \
            -x "*.pyc" "__pycache__/*" "requirements.txt" "README.md" "deploy.sh" "*.zip"
        
        # Créer ou mettre à jour la fonction
        ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lambda-house-price-role"
        
        if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION > /dev/null 2>&1; then
            echo "Mise à jour de la fonction..."
            aws lambda update-function-code \
                --function-name $FUNCTION_NAME \
                --zip-file fileb://lambda_function.zip \
                --region $REGION
            
            aws lambda update-function-configuration \
                --function-name $FUNCTION_NAME \
                --layers $LAYER_ARN \
                --region $REGION
        else
            echo "Création de la fonction..."
            aws lambda create-function \
                --function-name $FUNCTION_NAME \
                --runtime $RUNTIME \
                --role $ROLE_ARN \
                --handler lambda_function.lambda_handler \
                --zip-file fileb://lambda_function.zip \
                --layers $LAYER_ARN \
                --timeout $TIMEOUT \
                --memory-size $MEMORY \
                --region $REGION
        fi
        
        echo ""
        echo "✅ Déploiement terminé avec Lambda Layer!"
        ;;
    
    serverless)
        echo "=== Déploiement avec Serverless Framework ==="
        
        command -v serverless >/dev/null 2>&1 || { 
            echo "Serverless Framework non installé."
            echo "Installez-le avec: npm install -g serverless"
            exit 1
        }
        
        cd ..
        if [ ! -f "serverless.yml" ]; then
            echo "Création de serverless.yml..."
            # Le fichier devrait être créé manuellement
            echo "ERREUR: serverless.yml non trouvé. Créez-le d'abord."
            exit 1
        fi
        
        echo "Déploiement avec Serverless Framework..."
        serverless deploy
        
        echo ""
        echo "✅ Déploiement terminé!"
        echo ""
        echo "Pour obtenir l'URL:"
        echo "  serverless info"
        ;;
    
    *)
        echo "Méthode inconnue: $METHOD"
        echo "Méthodes disponibles: manual, layer, serverless"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Déploiement terminé!"
echo "=========================================="
echo ""
echo "Fonction Lambda: $FUNCTION_NAME"
echo "Région: $REGION"
echo ""
echo "Pour voir les logs:"
echo "  aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo ""

