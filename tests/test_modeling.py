"""
Tests unitaires pour le module modeling.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modeling import ModelTrainer


class TestModelTrainer:
    """Tests pour la classe ModelTrainer."""
    
    def setup_method(self):
        """Setup pour chaque test."""
        self.trainer = ModelTrainer(experiment_name="test_experiment")
        
        # Créer des données de test
        np.random.seed(42)
        n_samples = 100
        n_features = 10
        
        self.X_train = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        self.y_train = pd.Series(np.random.randn(n_samples) * 10000 + 180000)
        
        self.X_val = pd.DataFrame(
            np.random.randn(20, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        self.y_val = pd.Series(np.random.randn(20) * 10000 + 180000)
    
    def test_initialization(self):
        """Test de l'initialisation du ModelTrainer."""
        assert self.trainer.experiment_name == "test_experiment"
        assert self.trainer.models == {}
        assert self.trainer.best_model is None
    
    def test_train_model(self):
        """Test de l'entraînement d'un modèle."""
        model = LinearRegression()
        
        metrics = self.trainer.train_model(
            model, self.X_train, self.y_train,
            self.X_val, self.y_val,
            model_name="test_model",
            params={'test_param': 1},
            use_mlflow=False  # Désactiver MLFlow pour les tests
        )
        
        assert 'train_rmse' in metrics
        assert 'val_rmse' in metrics
        assert 'train_r2' in metrics
        assert 'val_r2' in metrics
        assert metrics['train_rmse'] >= 0
        assert metrics['val_rmse'] >= 0
        assert 'test_model' in self.trainer.models
    
    def test_get_best_model(self):
        """Test de la récupération du meilleur modèle."""
        # Entraîner plusieurs modèles
        model1 = LinearRegression()
        self.trainer.train_model(
            model1, self.X_train, self.y_train,
            self.X_val, self.y_val,
            model_name="model1",
            use_mlflow=False
        )
        
        model2 = RandomForestRegressor(n_estimators=10, random_state=42)
        self.trainer.train_model(
            model2, self.X_train, self.y_train,
            self.X_val, self.y_val,
            model_name="model2",
            use_mlflow=False
        )
        
        best_model = self.trainer.get_best_model()
        assert best_model is not None
    
    def test_save_and_load_model(self):
        """Test de la sauvegarde et du chargement d'un modèle."""
        model = LinearRegression()
        model.fit(self.X_train, self.y_train)
        
        # Sauvegarder
        model_path = "tests/test_model.pkl"
        self.trainer.save_model(model, model_path)
        
        # Vérifier que le fichier existe
        assert Path(model_path).exists()
        
        # Charger
        loaded_model = self.trainer.load_model(model_path)
        assert loaded_model is not None
        
        # Vérifier que les prédictions sont similaires
        pred_original = model.predict(self.X_val[:5])
        pred_loaded = loaded_model.predict(self.X_val[:5])
        np.testing.assert_array_almost_equal(pred_original, pred_loaded)
        
        # Nettoyer
        Path(model_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__])


