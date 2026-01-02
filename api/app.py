"""
API REST pour les prédictions de prix immobiliers.
Utilise FastAPI pour créer une API moderne et documentée.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
import logging

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Laplace Immo - API de Prédiction des Prix",
    description="API REST pour prédire les prix des maisons",
    version="1.0.0"
)

# Charger le modèle au démarrage
MODEL_PATH = Path("output/models/final_model.pkl")
model = None
processor = None
feature_engineer = None

@app.on_event("startup")
async def load_model_on_startup():
    """Charger le modèle au démarrage de l'API."""
    global model, processor, feature_engineer
    
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        processor = DataProcessor()
        feature_engineer = FeatureEngineer()
        logger.info("Modèle chargé avec succès")
    else:
        logger.warning("Modèle non trouvé. L'API fonctionnera en mode limité.")

# Modèles Pydantic pour la validation
class HouseFeatures(BaseModel):
    """Modèle pour les caractéristiques d'une maison."""
    MSSubClass: Optional[int] = None
    MSZoning: Optional[str] = None
    LotFrontage: Optional[float] = None
    LotArea: Optional[float] = None
    Street: Optional[str] = None
    Alley: Optional[str] = None
    LotShape: Optional[str] = None
    LandContour: Optional[str] = None
    Utilities: Optional[str] = None
    LotConfig: Optional[str] = None
    LandSlope: Optional[str] = None
    Neighborhood: Optional[str] = None
    OverallQual: Optional[int] = Field(None, ge=1, le=10)
    OverallCond: Optional[int] = Field(None, ge=1, le=10)
    YearBuilt: Optional[int] = None
    GrLivArea: Optional[float] = None
    # Ajouter d'autres champs selon les besoins
    
    class Config:
        schema_extra = {
            "example": {
                "MSSubClass": 60,
                "MSZoning": "RL",
                "LotArea": 8450,
                "Neighborhood": "CollgCr",
                "OverallQual": 7,
                "OverallCond": 5,
                "YearBuilt": 2003,
                "GrLivArea": 1710
            }
        }

class PredictionResponse(BaseModel):
    """Réponse de prédiction."""
    predicted_price: float = Field(..., description="Prix prédit en dollars")
    confidence_score: Optional[float] = Field(None, description="Score de confiance (0-1)")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Importance des features")

class BatchPredictionRequest(BaseModel):
    """Requête pour prédictions en batch."""
    houses: List[HouseFeatures]

class BatchPredictionResponse(BaseModel):
    """Réponse pour prédictions en batch."""
    predictions: List[float]
    total_houses: int

@app.get("/")
async def root():
    """Endpoint racine."""
    return {
        "message": "API Laplace Immo - Prédiction des Prix Immobiliers",
        "version": "1.0.0",
        "status": "running",
        "note": "Utilisez http://localhost:8000 (et non 0.0.0.0:8000) dans votre navigateur",
        "endpoints": {
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "health": "/health",
            "docs": "/docs (documentation Swagger UI)",
            "redoc": "/redoc (documentation ReDoc)"
        },
        "access_urls": {
            "api": "http://localhost:8000",
            "swagger_docs": "http://localhost:8000/docs",
            "redoc_docs": "http://localhost:8000/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Vérifier l'état de l'API."""
    return {
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_price(house: HouseFeatures):
    """
    Prédire le prix d'une maison.
    
    Args:
        house: Caractéristiques de la maison
        
    Returns:
        Prédiction du prix
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    try:
        # Convertir en DataFrame
        house_dict = house.dict(exclude_none=True)
        house_df = pd.DataFrame([house_dict])
        
        # Appliquer le preprocessing complet
        if processor is not None:
            # Traiter les valeurs manquantes
            house_df = processor.handle_missing_values(house_df, is_train=False)
            
            # Feature engineering
            if feature_engineer is not None:
                house_df = feature_engineer.create_features(house_df)
        
        # Prédiction
        # Note: Le modèle doit avoir été entraîné avec les mêmes features
        # Si erreur, vérifier que toutes les colonnes attendues sont présentes
        try:
            prediction = model.predict(house_df)[0]
        except Exception as pred_error:
            logger.error(f"Erreur de prédiction (colonnes manquantes?): {pred_error}")
            # Essayer avec seulement les colonnes disponibles
            if hasattr(model, 'feature_names_in_'):
                # Si le modèle a des noms de features, aligner les colonnes
                missing_cols = set(model.feature_names_in_) - set(house_df.columns)
                if missing_cols:
                    # Remplir les colonnes manquantes avec des valeurs par défaut
                    for col in missing_cols:
                        house_df[col] = 0
                house_df = house_df[model.feature_names_in_]
            prediction = model.predict(house_df)[0]
        
        # Calculer un score de confiance basique
        # (simplifié - en production, utiliser l'incertitude du modèle)
        confidence = 0.85  # Placeholder
        
        return PredictionResponse(
            predicted_price=float(prediction),
            confidence_score=confidence
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/batch_predict", response_model=BatchPredictionResponse)
async def batch_predict(houses: BatchPredictionRequest):
    """
    Prédire les prix de plusieurs maisons en une fois.
    
    Args:
        houses: Liste de caractéristiques de maisons
        
    Returns:
        Liste des prédictions
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    try:
        # Convertir en DataFrame
        houses_list = [house.dict(exclude_none=True) for house in houses.houses]
        houses_df = pd.DataFrame(houses_list)
        
        # Prédictions
        predictions = model.predict(houses_df).tolist()
        
        return BatchPredictionResponse(
            predictions=[float(p) for p in predictions],
            total_houses=len(predictions)
        )
    
    except Exception as e:
        logger.error(f"Erreur lors des prédictions batch: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("API Laplace Immo - Démarrage")
    print("=" * 60)
    print("IMPORTANT: Utilisez http://localhost:8000 dans votre navigateur")
    print("(et non http://0.0.0.0:8000)")
    print("=" * 60)
    print("Documentation disponible à:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)

