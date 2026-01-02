"""
AWS Lambda Function pour prédire les prix immobiliers.
Déployable sur AWS Lambda pour un service serverless.
"""

import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Ajouter les modules au path
# Pour Lambda Layers, les dépendances sont dans /opt/python
sys.path.insert(0, '/opt/python')
sys.path.insert(0, str(Path(__file__).parent))

try:
    from data_processing import DataProcessor
    from feature_engineering import FeatureEngineer
except ImportError:
    # Fallback si les modules ne sont pas dans le layer
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from data_processing import DataProcessor
    from feature_engineering import FeatureEngineer

# Variables globales (chargées une seule fois au cold start)
model = None
processor = None
feature_engineer = None
MODEL_LOADED = False


def load_model():
    """
    Charger le modèle et les processeurs.
    Cette fonction est appelée une seule fois au cold start.
    """
    global model, processor, feature_engineer, MODEL_LOADED
    
    if MODEL_LOADED:
        return model, processor, feature_engineer
    
    try:
        # Option 1: Modèle dans le package Lambda
        model_path = Path(__file__).parent / "model" / "final_model.pkl"
        
        # Option 2: Modèle dans S3 (recommandé pour gros modèles)
        # Décommenter si vous stockez le modèle dans S3
        # import boto3
        # s3 = boto3.client('s3')
        # bucket_name = os.environ.get('MODEL_BUCKET', 'my-models-bucket')
        # model_path = '/tmp/final_model.pkl'
        # if not os.path.exists(model_path):
        #     s3.download_file(bucket_name, 'model/final_model.pkl', model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Modèle non trouvé: {model_path}\n"
                "Assurez-vous que le modèle est dans lambda/model/final_model.pkl"
            )
        
        model = joblib.load(model_path)
        processor = DataProcessor()
        feature_engineer = FeatureEngineer()
        MODEL_LOADED = True
        
        print(f"Modèle chargé avec succès depuis {model_path}")
        print(f"Modèle type: {type(model)}")
        
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {e}")
        raise
    
    return model, processor, feature_engineer


def lambda_handler(event, context):
    """
    Handler principal pour AWS Lambda.
    
    Args:
        event: Données de la requête
            - Si appelé via API Gateway: event contient 'body' (string JSON)
            - Si appelé directement: event est un dict
        context: Contexte Lambda (métadonnées de l'exécution)
    
    Returns:
        dict: Réponse au format API Gateway
            {
                'statusCode': int,
                'headers': dict,
                'body': str (JSON)
            }
    """
    try:
        # Charger le modèle (une seule fois, réutilisé pour les appels suivants)
        model, processor, feature_engineer = load_model()
        
        # Extraire les données de la requête
        if 'body' in event:
            # API Gateway envoie le body comme string JSON
            try:
                body = json.loads(event['body'])
            except (TypeError, json.JSONDecodeError):
                body = event['body'] if isinstance(event['body'], dict) else {}
        else:
            # Appel direct Lambda ou autre trigger
            body = event
        
        # Extraire les features
        # Supporte deux formats:
        # 1. {"features": {...}} 
        # 2. {"OverallQual": 7, "GrLivArea": 1710, ...}
        features = body.get('features', body)
        
        if not features:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Aucune caractéristique fournie',
                    'message': 'Fournissez les caractéristiques de la maison dans le body'
                })
            }
        
        # Convertir en DataFrame
        house_df = pd.DataFrame([features])
        
        # Preprocessing
        house_df = processor.handle_missing_values(house_df, is_train=False)
        house_df = feature_engineer.create_features(house_df)
        
        # Prédiction
        prediction = model.predict(house_df)[0]
        
        # Si le modèle prédit en log, convertir
        # (dépend de comment le modèle a été entraîné)
        if prediction < 1000:  # Heuristique: si très petit, c'est probablement en log
            prediction = np.expm1(prediction)
        
        # Réponse réussie
        response_body = {
            'predicted_price': float(prediction),
            'confidence': 0.85,  # Placeholder - à améliorer avec l'incertitude du modèle
            'message': 'Prédiction réussie',
            'features_used': len(house_df.columns)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Pour CORS
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_body)
        }
    
    except FileNotFoundError as e:
        # Modèle non trouvé
        return {
            'statusCode': 503,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Modèle non disponible',
                'message': str(e),
                'suggestion': 'Vérifiez que le modèle est déployé avec la fonction'
            })
        }
    
    except Exception as e:
        # Erreur générale
        error_message = str(e)
        print(f"Erreur lors de la prédiction: {error_message}")
        print(f"Type d'erreur: {type(e).__name__}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Erreur lors de la prédiction',
                'message': error_message,
                'type': type(e).__name__
            })
        }


# Pour tester localement
if __name__ == "__main__":
    # Simuler un événement API Gateway
    test_event = {
        'body': json.dumps({
            'features': {
                'OverallQual': 7,
                'GrLivArea': 1710,
                'Neighborhood': 'CollgCr',
                'YearBuilt': 2003,
                'LotArea': 8450,
                'GarageCars': 2
            }
        })
    }
    
    class MockContext:
        function_name = "house-price-predictor"
        function_version = "$LATEST"
        memory_limit_in_mb = 1024
    
    result = lambda_handler(test_event, MockContext())
    print("\n" + "="*60)
    print("Résultat du test:")
    print("="*60)
    print(json.dumps(json.loads(result['body']), indent=2))
    print("="*60)

