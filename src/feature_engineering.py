"""
Module de feature engineering pour le projet de prédiction des prix immobiliers.
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Classe pour effectuer le feature engineering sur les données immobilières.
    """
    
    def __init__(self):
        """Initialiser le FeatureEngineer."""
        self.label_encoders = {}
        self.skewed_features = []
    
    def create_features(self, df):
        """
        Créer de nouvelles features à partir des features existantes.
        
        Args:
            df: DataFrame avec les données
            
        Returns:
            DataFrame avec les nouvelles features ajoutées
        """
        df = df.copy()
        
        # Features de surface totale
        if 'TotalBsmtSF' in df.columns and '1stFlrSF' in df.columns and '2ndFlrSF' in df.columns:
            df['TotalSF'] = df['TotalBsmtSF'] + df['1stFlrSF'] + df.get('2ndFlrSF', 0)
        
        # Features de salles de bain totales
        bath_cols = ['FullBath', 'HalfBath', 'BsmtFullBath', 'BsmtHalfBath']
        existing_bath_cols = [col for col in bath_cols if col in df.columns]
        if existing_bath_cols:
            df['TotalBathrooms'] = df[existing_bath_cols].sum(axis=1)
        
        # Features d'âge
        if 'YrSold' in df.columns and 'YearBuilt' in df.columns:
            df['HouseAge'] = df['YrSold'] - df['YearBuilt']
        
        if 'YrSold' in df.columns and 'YearRemodAdd' in df.columns:
            df['RemodAge'] = df['YrSold'] - df['YearRemodAdd']
            df['RemodAge'] = df['RemodAge'].apply(lambda x: 0 if x < 0 else x)
        
        if 'YrSold' in df.columns and 'GarageYrBlt' in df.columns:
            df['GarageAge'] = df['YrSold'] - df['GarageYrBlt']
            df['GarageAge'] = df['GarageAge'].apply(lambda x: 0 if x < 0 or pd.isna(x) else x)
        
        # Features de qualité totale
        if 'OverallQual' in df.columns and 'OverallCond' in df.columns:
            df['OverallScore'] = df['OverallQual'] + df['OverallCond']
        
        # Features de surface par pièce
        if 'GrLivArea' in df.columns and 'TotRmsAbvGrd' in df.columns:
            df['SFPerRoom'] = df['GrLivArea'] / df['TotRmsAbvGrd'].replace(0, 1)
        
        # Features de garage
        if 'GarageArea' in df.columns and 'GarageCars' in df.columns:
            df['GarageAreaPerCar'] = df['GarageArea'] / df['GarageCars'].replace(0, 1)
        
        # Features de lot
        if 'LotArea' in df.columns and 'GrLivArea' in df.columns:
            df['LotAreaPerSF'] = df['LotArea'] / df['GrLivArea'].replace(0, 1)
        
        # Features de porche total
        porch_cols = ['WoodDeckSF', 'OpenPorchSF', 'EnclosedPorch', '3SsnPorch', 'ScreenPorch']
        existing_porch_cols = [col for col in porch_cols if col in df.columns]
        if existing_porch_cols:
            df['TotalPorchSF'] = df[existing_porch_cols].sum(axis=1)
        
        # Features booléennes
        if 'PoolArea' in df.columns:
            df['HasPool'] = (df['PoolArea'] > 0).astype(int)
        
        if 'Fireplaces' in df.columns:
            df['HasFireplace'] = (df['Fireplaces'] > 0).astype(int)
        
        if 'TotalBsmtSF' in df.columns:
            df['HasBsmt'] = (df['TotalBsmtSF'] > 0).astype(int)
        
        if 'GarageArea' in df.columns:
            df['HasGarage'] = (df['GarageArea'] > 0).astype(int)
        
        if 'MasVnrArea' in df.columns:
            df['HasMasVnr'] = (df['MasVnrArea'] > 0).astype(int)
        
        logger.info(f"Features créées. Nouveau nombre de colonnes: {df.shape[1]}")
        
        return df
    
    def encode_categorical(self, df, categorical_cols, encoding_type='ordinal'):
        """
        Encoder les variables catégorielles.
        
        Args:
            df: DataFrame avec les données
            categorical_cols: Liste des colonnes catégorielles à encoder
            encoding_type: Type d'encodage ('ordinal' ou 'label')
            
        Returns:
            DataFrame avec les colonnes catégorielles encodées
        """
        df = df.copy()
        
        # Mapping pour l'encodage ordinal des variables de qualité
        quality_mapping = {
            'Ex': 5, 'Gd': 4, 'TA': 3, 'Fa': 2, 'Po': 1, 'None': 0
        }
        
        # Variables de qualité
        quality_vars = ['ExterQual', 'ExterCond', 'BsmtQual', 'BsmtCond', 
                       'HeatingQC', 'KitchenQual', 'FireplaceQu', 
                       'GarageQual', 'GarageCond', 'PoolQC']
        
        for col in categorical_cols:
            if col not in df.columns:
                continue
            
            if encoding_type == 'ordinal' and col in quality_vars:
                # Encodage ordinal pour les variables de qualité
                df[col] = df[col].map(quality_mapping).fillna(0)
            else:
                # Encodage label pour les autres variables catégorielles
                if col not in self.label_encoders:
                    le = LabelEncoder()
                    # Gérer les valeurs manquantes et nouvelles
                    unique_values = df[col].dropna().unique()
                    le.fit(unique_values)
                    self.label_encoders[col] = le
                else:
                    le = self.label_encoders[col]
                
                # Encoder, en gérant les nouvelles valeurs
                mask = df[col].notna()
                df.loc[mask, col] = le.transform(df.loc[mask, col])
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(-1)
        
        logger.info(f"Variables catégorielles encodées: {len(categorical_cols)}")
        
        return df
    
    def transform_skewed_features(self, df, numeric_cols, threshold=0.75):
        """
        Transformer les features numériques asymétriques avec log1p.
        
        Args:
            df: DataFrame avec les données
            numeric_cols: Liste des colonnes numériques à vérifier
            threshold: Seuil de skewness pour appliquer la transformation
            
        Returns:
            DataFrame avec les features transformées
        """
        df = df.copy()
        
        # Exclure certaines colonnes de la transformation
        exclude_cols = ['Id', 'SalePrice', 'YrSold', 'YearBuilt', 'YearRemodAdd', 'GarageYrBlt', 'MoSold']
        
        for col in numeric_cols:
            if col not in df.columns or col in exclude_cols:
                continue
            
            # Vérifier si la colonne a des valeurs négatives ou nulles
            if df[col].min() <= 0:
                # Utiliser log1p pour gérer les zéros
                if abs(df[col].skew()) > threshold:
                    df[col] = np.log1p(df[col])
                    self.skewed_features.append(col)
                    logger.debug(f"Feature {col} transformée (skewness: {df[col].skew():.3f})")
            else:
                # Utiliser log pour les valeurs strictement positives
                if abs(df[col].skew()) > threshold:
                    df[col] = np.log(df[col])
                    self.skewed_features.append(col)
                    logger.debug(f"Feature {col} transformée (skewness: {df[col].skew():.3f})")
        
        logger.info(f"Features transformées: {len(self.skewed_features)}")
        
        return df

