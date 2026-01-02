"""
Interface en ligne de commande (CLI) pour les prédictions de prix immobiliers.
Alternative à l'API HTTP pour des utilisations en ligne de commande.
"""

import argparse
import pandas as pd
import numpy as np
import joblib
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Chemins par défaut
MODEL_PATH = Path("output/models/final_model.pkl")
DEFAULT_DATA_DIR = Path("data/raw")


def load_model(model_path: Path = MODEL_PATH):
    """Charger le modèle entraîné."""
    if not model_path.exists():
        logger.error(f"Modèle non trouvé à {model_path}")
        logger.info("Entraînez d'abord le modèle avec: python train.py")
        return None
    return joblib.load(model_path)


def predict_single(model, processor: DataProcessor, feature_engineer: FeatureEngineer, 
                   features: Dict[str, Any]) -> float:
    """Faire une prédiction pour une seule maison."""
    try:
        # Convertir en DataFrame
        house_df = pd.DataFrame([features])
        
        # Preprocessing
        house_df = processor.handle_missing_values(house_df, is_train=False)
        house_df = feature_engineer.create_features(house_df)
        
        # Prédiction
        prediction = model.predict(house_df)[0]
        return float(prediction)
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise


def predict_batch(model, processor: DataProcessor, feature_engineer: FeatureEngineer,
                  input_file: Path, output_file: Optional[Path] = None) -> pd.DataFrame:
    """Faire des prédictions pour plusieurs maisons depuis un fichier CSV."""
    try:
        # Charger les données
        df = pd.read_csv(input_file)
        logger.info(f"Chargé {len(df)} maisons depuis {input_file}")
        
        # Preprocessing
        df_processed = processor.handle_missing_values(df.copy(), is_train=False)
        df_processed = feature_engineer.create_features(df_processed)
        
        # Prédictions
        predictions = model.predict(df_processed)
        df['PredictedPrice'] = predictions
        
        # Sauvegarder si un fichier de sortie est spécifié
        if output_file:
            df.to_csv(output_file, index=False)
            logger.info(f"Prédictions sauvegardées dans {output_file}")
        
        return df
    except Exception as e:
        logger.error(f"Erreur lors du traitement batch: {e}")
        raise


def interactive_mode(model, processor: DataProcessor, feature_engineer: FeatureEngineer):
    """Mode interactif pour entrer les caractéristiques d'une maison."""
    print("\n" + "="*60)
    print("Mode Interactif - Prédiction de Prix Immobilier")
    print("="*60)
    print("Entrez les caractéristiques de la maison (appuyez sur Entrée pour passer)")
    print("="*60 + "\n")
    
    features = {}
    
    # Caractéristiques principales
    print("Caractéristiques principales:")
    overall_qual = input("Qualité globale (1-10) [7]: ").strip()
    if overall_qual:
        features['OverallQual'] = int(overall_qual)
    else:
        features['OverallQual'] = 7
    
    gr_liv_area = input("Surface habitable (sqft) [1710]: ").strip()
    if gr_liv_area:
        features['GrLivArea'] = float(gr_liv_area)
    else:
        features['GrLivArea'] = 1710
    
    neighborhood = input("Quartier [CollgCr]: ").strip()
    if neighborhood:
        features['Neighborhood'] = neighborhood
    else:
        features['Neighborhood'] = "CollgCr"
    
    year_built = input("Année de construction [2003]: ").strip()
    if year_built:
        features['YearBuilt'] = int(year_built)
    else:
        features['YearBuilt'] = 2003
    
    lot_area = input("Surface du terrain (sqft) [8450]: ").strip()
    if lot_area:
        features['LotArea'] = float(lot_area)
    else:
        features['LotArea'] = 8450
    
    garage_cars = input("Nombre de places de garage [2]: ").strip()
    if garage_cars:
        features['GarageCars'] = int(garage_cars)
    else:
        features['GarageCars'] = 2
    
    # Faire la prédiction
    try:
        prediction = predict_single(model, processor, feature_engineer, features)
        print("\n" + "="*60)
        print(f"Prix prédit: ${prediction:,.2f}")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\nErreur: {e}\n")


def main():
    """Point d'entrée principal de la CLI."""
    parser = argparse.ArgumentParser(
        description="CLI pour prédire les prix immobiliers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Prédiction simple
  python cli.py predict --OverallQual 7 --GrLivArea 1710 --Neighborhood "CollgCr"
  
  # Prédiction depuis un fichier CSV
  python cli.py batch --input houses.csv --output predictions.csv
  
  # Mode interactif
  python cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande: predict (prédiction simple)
    predict_parser = subparsers.add_parser('predict', help='Prédire le prix d\'une maison')
    predict_parser.add_argument('--OverallQual', type=int, help='Qualité globale (1-10)')
    predict_parser.add_argument('--GrLivArea', type=float, help='Surface habitable (sqft)')
    predict_parser.add_argument('--Neighborhood', type=str, help='Quartier')
    predict_parser.add_argument('--YearBuilt', type=int, help='Année de construction')
    predict_parser.add_argument('--LotArea', type=float, help='Surface du terrain (sqft)')
    predict_parser.add_argument('--GarageCars', type=int, help='Nombre de places de garage')
    predict_parser.add_argument('--OverallCond', type=int, help='Condition globale (1-10)')
    predict_parser.add_argument('--MSZoning', type=str, help='Zone')
    predict_parser.add_argument('--json', type=str, help='Fichier JSON avec toutes les caractéristiques')
    predict_parser.add_argument('--model', type=Path, default=MODEL_PATH, help='Chemin vers le modèle')
    
    # Commande: batch (prédictions multiples)
    batch_parser = subparsers.add_parser('batch', help='Prédictions depuis un fichier CSV')
    batch_parser.add_argument('--input', type=Path, required=True, help='Fichier CSV d\'entrée')
    batch_parser.add_argument('--output', type=Path, help='Fichier CSV de sortie')
    batch_parser.add_argument('--model', type=Path, default=MODEL_PATH, help='Chemin vers le modèle')
    
    # Commande: interactive
    interactive_parser = subparsers.add_parser('interactive', help='Mode interactif')
    interactive_parser.add_argument('--model', type=Path, default=MODEL_PATH, help='Chemin vers le modèle')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Charger le modèle
    model = load_model(args.model)
    if model is None:
        sys.exit(1)
    
    # Initialiser les processeurs
    processor = DataProcessor()
    feature_engineer = FeatureEngineer()
    
    # Exécuter la commande
    if args.command == 'predict':
        # Construire le dictionnaire de features
        if args.json:
            # Charger depuis un fichier JSON
            with open(args.json, 'r') as f:
                features = json.load(f)
        else:
            # Construire depuis les arguments
            features = {}
            if args.OverallQual:
                features['OverallQual'] = args.OverallQual
            if args.GrLivArea:
                features['GrLivArea'] = args.GrLivArea
            if args.Neighborhood:
                features['Neighborhood'] = args.Neighborhood
            if args.YearBuilt:
                features['YearBuilt'] = args.YearBuilt
            if args.LotArea:
                features['LotArea'] = args.LotArea
            if args.GarageCars:
                features['GarageCars'] = args.GarageCars
            if args.OverallCond:
                features['OverallCond'] = args.OverallCond
            if args.MSZoning:
                features['MSZoning'] = args.MSZoning
        
        if not features:
            logger.error("Aucune caractéristique fournie. Utilisez --help pour voir les options.")
            sys.exit(1)
        
        try:
            prediction = predict_single(model, processor, feature_engineer, features)
            print(f"\nPrix prédit: ${prediction:,.2f}\n")
        except Exception as e:
            logger.error(f"Erreur: {e}")
            sys.exit(1)
    
    elif args.command == 'batch':
        try:
            df = predict_batch(model, processor, feature_engineer, args.input, args.output)
            print(f"\n{len(df)} prédictions effectuées avec succès!")
            if args.output:
                print(f"Résultats sauvegardés dans {args.output}")
            else:
                print("\nPremières prédictions:")
                print(df[['PredictedPrice']].head(10))
        except Exception as e:
            logger.error(f"Erreur: {e}")
            sys.exit(1)
    
    elif args.command == 'interactive':
        interactive_mode(model, processor, feature_engineer)


if __name__ == "__main__":
    main()

