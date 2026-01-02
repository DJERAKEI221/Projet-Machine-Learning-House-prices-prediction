"""
Module d'explicabilité du modèle utilisant SHAP.
Permet d'expliquer les prédictions du modèle.
"""

import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from typing import Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelExplainer:
    """Classe pour expliquer les prédictions du modèle."""
    
    def __init__(self, model: Any, X_train: pd.DataFrame):
        """
        Initialize ModelExplainer.
        
        Args:
            model: Modèle entraîné
            X_train: Données d'entraînement pour calculer les valeurs SHAP
        """
        self.model = model
        self.X_train = X_train
        self.explainer = None
        self.shap_values = None
        
    def create_explainer(self, explainer_type: str = 'tree'):
        """
        Créer l'explainer SHAP.
        
        Args:
            explainer_type: Type d'explainer ('tree', 'kernel', 'linear')
        """
        logger.info(f"Création de l'explainer SHAP de type {explainer_type}...")
        
        if explainer_type == 'tree':
            self.explainer = shap.TreeExplainer(self.model)
        elif explainer_type == 'kernel':
            # Utiliser un échantillon pour la vitesse
            sample_size = min(100, len(self.X_train))
            X_sample = self.X_train.sample(n=sample_size, random_state=42)
            self.explainer = shap.KernelExplainer(self.model.predict, X_sample)
        else:
            raise ValueError(f"Type d'explainer non supporté: {explainer_type}")
        
        logger.info("Explainer créé avec succès")
    
    def explain_prediction(self, X_instance: pd.DataFrame, 
                         max_display: int = 10) -> dict:
        """
        Expliquer une prédiction spécifique.
        
        Args:
            X_instance: Instance à expliquer (une ou plusieurs lignes)
            max_display: Nombre maximum de features à afficher
            
        Returns:
            Dictionnaire avec les explications
        """
        if self.explainer is None:
            self.create_explainer()
        
        shap_values = self.explainer.shap_values(X_instance)
        
        # Pour les modèles d'ensemble, shap_values peut être une liste
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Calculer la contribution de chaque feature
        feature_contributions = {}
        for i, feature in enumerate(X_instance.columns):
            feature_contributions[feature] = {
                'shap_value': float(shap_values[0, i]) if len(shap_values.shape) > 1 else float(shap_values[i]),
                'feature_value': float(X_instance.iloc[0, i])
            }
        
        # Trier par valeur absolue de SHAP
        sorted_contributions = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]['shap_value']),
            reverse=True
        )
        
        return {
            'base_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else None,
            'prediction': float(self.model.predict(X_instance)[0]),
            'top_features': dict(sorted_contributions[:max_display])
        }
    
    def plot_summary(self, X_sample: Optional[pd.DataFrame] = None, 
                    max_display: int = 20, output_path: Optional[str] = None):
        """
        Créer un plot de résumé SHAP.
        
        Args:
            X_sample: Échantillon de données (si None, utilise X_train)
            max_display: Nombre maximum de features à afficher
            output_path: Chemin pour sauvegarder le plot
        """
        if self.explainer is None:
            self.create_explainer()
        
        if X_sample is None:
            # Utiliser un échantillon pour la vitesse
            sample_size = min(100, len(self.X_train))
            X_sample = self.X_train.sample(n=sample_size, random_state=42)
        
        shap_values = self.explainer.shap_values(X_sample)
        
        # Pour les modèles d'ensemble
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_sample, max_display=max_display, show=False)
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot sauvegardé dans {output_path}")
        
        plt.show()
    
    def plot_waterfall(self, X_instance: pd.DataFrame, 
                      output_path: Optional[str] = None):
        """
        Créer un waterfall plot pour une instance spécifique.
        
        Args:
            X_instance: Instance à expliquer
            output_path: Chemin pour sauvegarder le plot
        """
        if self.explainer is None:
            self.create_explainer()
        
        shap_values = self.explainer.shap_values(X_instance)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0] if len(shap_values.shape) > 1 else shap_values,
                base_values=self.explainer.expected_value if hasattr(self.explainer, 'expected_value') else 0,
                data=X_instance.iloc[0].values,
                feature_names=X_instance.columns.tolist()
            ),
            show=False
        )
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Waterfall plot sauvegardé dans {output_path}")
        
        plt.show()

