"""
Tests unitaires pour le module utils.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import prepare_data, calculate_rmse, create_submission


class TestUtils:
    """Tests pour les fonctions utilitaires."""
    
    def test_prepare_data(self):
        """Test de la préparation des données."""
        train_df = pd.DataFrame({
            'Id': [1, 2, 3],
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6],
            'SalePrice': [100000, 200000, 300000]
        })
        
        test_df = pd.DataFrame({
            'Id': [4, 5],
            'feature1': [7, 8],
            'feature2': [9, 10]
        })
        
        X_train, y_train, X_test = prepare_data(train_df, test_df, target_col='SalePrice')
        
        assert 'SalePrice' not in X_train.columns
        assert 'Id' not in X_train.columns
        assert len(y_train) == 3
        assert X_test.shape[0] == 2
        assert list(X_train.columns) == list(X_test.columns)
    
    def test_calculate_rmse(self):
        """Test du calcul du RMSE."""
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])
        
        rmse = calculate_rmse(y_true, y_pred)
        
        # RMSE = sqrt(mean((100-110)^2 + (200-190)^2 + (300-310)^2))
        # RMSE = sqrt(mean(100 + 100 + 100)) = sqrt(100) = 10
        expected_rmse = 10.0
        assert abs(rmse - expected_rmse) < 0.01
    
    def test_create_submission(self):
        """Test de la création du fichier de soumission."""
        predictions = np.array([150000, 250000, 350000])
        test_ids = pd.Series([1, 2, 3])
        output_path = "tests/test_submission.csv"
        
        create_submission(predictions, test_ids, output_path)
        
        # Vérifier que le fichier existe
        assert Path(output_path).exists()
        
        # Vérifier le contenu
        submission = pd.read_csv(output_path)
        assert 'Id' in submission.columns
        assert 'SalePrice' in submission.columns
        assert len(submission) == 3
        
        # Nettoyer
        Path(output_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__])


