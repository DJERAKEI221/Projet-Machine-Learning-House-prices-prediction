"""
Feature engineering module for house price prediction.
Creates new features and transforms existing ones.
"""

import pandas as pd
import numpy as np
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Class for feature engineering operations."""
    
    def __init__(self):
        """Initialize FeatureEngineer."""
        pass
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features from existing ones.
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with new features added
        """
        df = df.copy()
        
        logger.info("Creating new features...")
        
        # Total square footage
        if all(col in df.columns for col in ['TotalBsmtSF', '1stFlrSF', '2ndFlrSF']):
            df['TotalSF'] = df['TotalBsmtSF'] + df['1stFlrSF'] + df['2ndFlrSF']
        
        # Total bathrooms
        if all(col in df.columns for col in ['FullBath', 'HalfBath', 'BsmtFullBath', 'BsmtHalfBath']):
            df['TotalBathrooms'] = df['FullBath'] + 0.5 * df['HalfBath'] + \
                                   df['BsmtFullBath'] + 0.5 * df['BsmtHalfBath']
        
        # Total porch area
        porch_cols = ['WoodDeckSF', 'OpenPorchSF', 'EnclosedPorch', 
                     '3SsnPorch', 'ScreenPorch']
        existing_porch = [col for col in porch_cols if col in df.columns]
        if existing_porch:
            df['TotalPorchSF'] = df[existing_porch].sum(axis=1)
        
        # House age and renovation
        if 'YrSold' in df.columns and 'YearBuilt' in df.columns:
            df['HouseAge'] = df['YrSold'] - df['YearBuilt']
            df['HouseAge'] = df['HouseAge'].apply(lambda x: 0 if x < 0 else x)
        
        if 'YrSold' in df.columns and 'YearRemodAdd' in df.columns:
            df['RemodAge'] = df['YrSold'] - df['YearRemodAdd']
            df['RemodAge'] = df['RemodAge'].apply(lambda x: 0 if x < 0 else x)
            df['IsRemod'] = (df['YearRemodAdd'] != df['YearBuilt']).astype(int)
        
        # Garage age
        if 'YrSold' in df.columns and 'GarageYrBlt' in df.columns:
            df['GarageAge'] = df['YrSold'] - df['GarageYrBlt']
            df['GarageAge'] = df['GarageAge'].apply(lambda x: 0 if x < 0 or pd.isna(x) else x)
        
        # Quality and condition scores
        if 'OverallQual' in df.columns and 'OverallCond' in df.columns:
            df['QualityScore'] = df['OverallQual'] * df['OverallCond']
        
        # Has basement
        if 'TotalBsmtSF' in df.columns:
            df['HasBasement'] = (df['TotalBsmtSF'] > 0).astype(int)
        
        # Has garage
        if 'GarageArea' in df.columns:
            df['HasGarage'] = (df['GarageArea'] > 0).astype(int)
        
        # Has fireplace
        if 'Fireplaces' in df.columns:
            df['HasFireplace'] = (df['Fireplaces'] > 0).astype(int)
        
        # Has pool
        if 'PoolArea' in df.columns:
            df['HasPool'] = (df['PoolArea'] > 0).astype(int)
        
        # Lot features
        if 'LotFrontage' in df.columns and 'LotArea' in df.columns:
            df['LotRatio'] = df['LotFrontage'] / df['LotArea']
            df['LotRatio'] = df['LotRatio'].fillna(0)
        
        # Living area ratio
        if 'GrLivArea' in df.columns and 'LotArea' in df.columns:
            df['LivAreaRatio'] = df['GrLivArea'] / df['LotArea']
            df['LivAreaRatio'] = df['LivAreaRatio'].replace([np.inf, -np.inf], 0)
        
        # Room density
        if 'TotRmsAbvGrd' in df.columns and 'GrLivArea' in df.columns:
            df['RoomDensity'] = df['TotRmsAbvGrd'] / df['GrLivArea']
            df['RoomDensity'] = df['RoomDensity'].replace([np.inf, -np.inf], 0)
        
        logger.info(f"Created {len([col for col in df.columns if col not in df.columns])} new features")
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame, categorical_cols: List[str], 
                          encoding_type: str = 'ordinal') -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Args:
            df: DataFrame to process
            categorical_cols: List of categorical column names
            encoding_type: Type of encoding ('ordinal', 'onehot', 'target')
            
        Returns:
            DataFrame with encoded categorical variables
        """
        df = df.copy()
        
        logger.info(f"Encoding {len(categorical_cols)} categorical variables using {encoding_type} encoding")
        
        if encoding_type == 'ordinal':
            # Ordinal encoding for quality/condition variables
            quality_map = {'None': 0, 'Po': 1, 'Fa': 2, 'TA': 3, 'Gd': 4, 'Ex': 5}
            quality_cols = ['ExterQual', 'ExterCond', 'BsmtQual', 'BsmtCond',
                           'HeatingQC', 'KitchenQual', 'FireplaceQu', 'GarageQual', 'GarageCond', 'PoolQC']
            
            for col in quality_cols:
                if col in df.columns and col in categorical_cols:
                    df[col] = df[col].map(quality_map).fillna(0)
            
            # Other ordinal mappings
            if 'BsmtExposure' in df.columns and 'BsmtExposure' in categorical_cols:
                exposure_map = {'None': 0, 'No': 1, 'Mn': 2, 'Av': 3, 'Gd': 4}
                df['BsmtExposure'] = df['BsmtExposure'].map(exposure_map).fillna(0)
            
            if 'BsmtFinType1' in df.columns and 'BsmtFinType1' in categorical_cols:
                fin_type_map = {'None': 0, 'Unf': 1, 'LwQ': 2, 'Rec': 3, 'BLQ': 4, 'ALQ': 5, 'GLQ': 6}
                df['BsmtFinType1'] = df['BsmtFinType1'].map(fin_type_map).fillna(0)
                if 'BsmtFinType2' in df.columns:
                    df['BsmtFinType2'] = df['BsmtFinType2'].map(fin_type_map).fillna(0)
            
            if 'GarageFinish' in df.columns and 'GarageFinish' in categorical_cols:
                garage_finish_map = {'None': 0, 'Unf': 1, 'RFn': 2, 'Fin': 3}
                df['GarageFinish'] = df['GarageFinish'].map(garage_finish_map).fillna(0)
            
            if 'Fence' in df.columns and 'Fence' in categorical_cols:
                fence_map = {'None': 0, 'MnWw': 1, 'GdWo': 2, 'MnPrv': 3, 'GdPrv': 4}
                df['Fence'] = df['Fence'].map(fence_map).fillna(0)
            
            if 'PavedDrive' in df.columns and 'PavedDrive' in categorical_cols:
                paved_map = {'N': 0, 'P': 1, 'Y': 2}
                df['PavedDrive'] = df['PavedDrive'].map(paved_map).fillna(0)
            
            if 'Functional' in df.columns and 'Functional' in categorical_cols:
                functional_map = {'Sal': 0, 'Sev': 1, 'Maj2': 2, 'Maj1': 3, 
                                'Mod': 4, 'Min2': 5, 'Min1': 6, 'Typ': 7}
                df['Functional'] = df['Functional'].map(functional_map).fillna(7)
        
        elif encoding_type == 'onehot':
            # One-hot encoding for remaining categorical variables
            remaining_cats = [col for col in categorical_cols 
                            if col in df.columns and df[col].dtype == 'object']
            df = pd.get_dummies(df, columns=remaining_cats, prefix=remaining_cats)
        
        logger.info("Categorical encoding completed")
        
        return df
    
    def transform_skewed_features(self, df: pd.DataFrame, numeric_cols: List[str], 
                                  threshold: float = 0.75) -> pd.DataFrame:
        """
        Apply log transformation to skewed numeric features.
        
        Args:
            df: DataFrame to process
            numeric_cols: List of numeric column names
            threshold: Skewness threshold for transformation
            
        Returns:
            DataFrame with transformed features
        """
        df = df.copy()
        
        logger.info("Transforming skewed features...")
        
        # Exclude target and ID columns
        exclude_cols = ['Id', 'SalePrice']
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        skewed_cols = []
        for col in numeric_cols:
            if col in df.columns:
                skewness = df[col].skew()
                if abs(skewness) > threshold:
                    skewed_cols.append(col)
                    # Add 1 to handle zeros
                    df[col] = np.log1p(df[col])
        
        logger.info(f"Transformed {len(skewed_cols)} skewed features")
        
        return df


