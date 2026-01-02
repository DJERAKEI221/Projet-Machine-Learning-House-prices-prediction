"""
Tests unitaires pour le module feature_engineering.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from feature_engineering import FeatureEngineer


class TestFeatureEngineer:
    """Tests pour la classe FeatureEngineer."""
    
    def setup_method(self):
        """Setup pour chaque test."""
        self.fe = FeatureEngineer()
    
    def test_initialization(self):
        """Test de l'initialisation du FeatureEngineer."""
        assert self.fe is not None
    
    def test_create_features(self):
        """Test de la création de nouvelles features."""
        test_data = pd.DataFrame({
            'TotalBsmtSF': [1000, 1200, 800],
            '1stFlrSF': [1500, 1600, 1400],
            '2ndFlrSF': [500, 600, 400],
            'FullBath': [2, 3, 2],
            'HalfBath': [1, 0, 1],
            'BsmtFullBath': [1, 1, 0],
            'BsmtHalfBath': [0, 0, 0],
            'YrSold': [2010, 2011, 2012],
            'YearBuilt': [2000, 2005, 1995],
            'YearRemodAdd': [2000, 2005, 1995],
            'GarageYrBlt': [2000, 2005, 1995],
            'OverallQual': [7, 8, 6],
            'OverallCond': [5, 6, 5],
            'GarageArea': [500, 600, 400],
            'Fireplaces': [1, 2, 0],
            'PoolArea': [0, 100, 0],
            'LotFrontage': [65, 80, 60],
            'LotArea': [8450, 9600, 8000],
            'GrLivArea': [2000, 2200, 1800],
            'TotRmsAbvGrd': [8, 9, 7]
        })
        
        result = self.fe.create_features(test_data)
        
        # Vérifier que de nouvelles colonnes ont été créées
        assert 'TotalSF' in result.columns
        assert 'TotalBathrooms' in result.columns
        assert 'HouseAge' in result.columns
        assert 'RemodAge' in result.columns
    
    def test_encode_categorical_ordinal(self):
        """Test de l'encodage ordinal."""
        test_data = pd.DataFrame({
            'ExterQual': ['Ex', 'Gd', 'TA', 'Fa'],
            'BsmtQual': ['Gd', 'TA', None, 'Ex'],
            'GarageQual': ['TA', 'Gd', 'Ex', 'TA']
        })
        
        categorical_cols = ['ExterQual', 'BsmtQual', 'GarageQual']
        result = self.fe.encode_categorical(test_data, categorical_cols, encoding_type='ordinal')
        
        # Vérifier que les valeurs sont encodées
        assert result['ExterQual'].dtype in [np.int64, np.float64, int, float]
        assert result['BsmtQual'].dtype in [np.int64, np.float64, int, float]
    
    def test_transform_skewed_features(self):
        """Test de la transformation des features asymétriques."""
        # Créer des données avec skewness élevée
        skewed_data = np.random.lognormal(mean=5, sigma=1, size=1000)
        test_data = pd.DataFrame({
            'skewed_col': skewed_data,
            'normal_col': np.random.normal(100, 10, 1000),
            'Id': range(1000)
        })
        
        numeric_cols = ['skewed_col', 'normal_col']
        result = self.fe.transform_skewed_features(test_data, numeric_cols, threshold=0.75)
        
        # Vérifier que la transformation a été appliquée
        assert 'skewed_col' in result.columns
        # La skewness devrait être réduite après transformation
        assert abs(result['skewed_col'].skew()) < abs(test_data['skewed_col'].skew())


if __name__ == "__main__":
    pytest.main([__file__])

