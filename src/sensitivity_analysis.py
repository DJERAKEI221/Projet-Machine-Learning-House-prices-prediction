"""
Module d'analyse de sensibilité.
Permet d'analyser l'impact des variables sur les prédictions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SensitivityAnalyzer:
    """Classe pour analyser la sensibilité des prédictions aux variables."""
    
    def __init__(self, model: Any):
        """
        Initialize SensitivityAnalyzer.
        
        Args:
            model: Modèle entraîné
        """
        self.model = model
    
    def analyze_feature_impact(self, X_base: pd.DataFrame, 
                               feature_name: str,
                               variation_range: Optional[tuple] = None,
                               steps: int = 20) -> pd.DataFrame:
        """
        Analyser l'impact d'une variable sur la prédiction.
        
        Args:
            X_base: Données de base (une ligne)
            feature_name: Nom de la variable à analyser
            variation_range: Plage de variation (min, max). Si None, utilise les valeurs du dataset
            steps: Nombre de points à tester
            
        Returns:
            DataFrame avec les variations et prédictions
        """
        if feature_name not in X_base.columns:
            raise ValueError(f"Variable {feature_name} non trouvée dans les données")
        
        # Déterminer la plage de variation
        if variation_range is None:
            # Utiliser les valeurs min/max du dataset comme référence
            feature_min = X_base[feature_name].min() * 0.5
            feature_max = X_base[feature_name].max() * 1.5
        else:
            feature_min, feature_max = variation_range
        
        # Créer les valeurs de test
        if X_base[feature_name].dtype in ['int64', 'float64']:
            test_values = np.linspace(feature_min, feature_max, steps)
        else:
            # Pour les variables catégorielles, tester toutes les valeurs uniques
            test_values = X_base[feature_name].unique()
        
        # Créer les données de test
        results = []
        base_prediction = self.model.predict(X_base)[0]
        
        for val in test_values:
            X_test = X_base.copy()
            X_test[feature_name] = val
            
            prediction = self.model.predict(X_test)[0]
            impact = prediction - base_prediction
            impact_pct = (impact / base_prediction) * 100 if base_prediction != 0 else 0
            
            results.append({
                'feature_value': val,
                'prediction': prediction,
                'impact': impact,
                'impact_percentage': impact_pct
            })
        
        return pd.DataFrame(results)
    
    def plot_sensitivity(self, X_base: pd.DataFrame, 
                        feature_name: str,
                        variation_range: Optional[tuple] = None,
                        output_path: Optional[str] = None):
        """
        Visualiser la sensibilité d'une variable.
        
        Args:
            X_base: Données de base
            feature_name: Nom de la variable
            variation_range: Plage de variation
            output_path: Chemin pour sauvegarder le plot
        """
        results_df = self.analyze_feature_impact(X_base, feature_name, variation_range)
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Prédiction vs Valeur de la variable
        axes[0].plot(results_df['feature_value'], results_df['prediction'], 
                    marker='o', linewidth=2, markersize=4)
        axes[0].axhline(y=results_df['prediction'].iloc[len(results_df)//2], 
                       color='r', linestyle='--', alpha=0.5, label='Prédiction de base')
        axes[0].set_xlabel(feature_name)
        axes[0].set_ylabel('Prix Prédit ($)')
        axes[0].set_title(f'Impact de {feature_name} sur le Prix')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Impact en pourcentage
        axes[1].plot(results_df['feature_value'], results_df['impact_percentage'], 
                    marker='o', linewidth=2, markersize=4, color='coral')
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1].set_xlabel(feature_name)
        axes[1].set_ylabel('Impact sur le Prix (%)')
        axes[1].set_title(f'Impact Relatif de {feature_name}')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot sauvegardé dans {output_path}")
        
        plt.show()
    
    def simulate_renovation(self, X_base: pd.DataFrame, 
                           renovations: Dict[str, Any]) -> Dict:
        """
        Simuler l'impact de rénovations sur le prix.
        
        Args:
            X_base: Données de base (une ligne)
            renovations: Dictionnaire {variable: nouvelle_valeur}
            
        Returns:
            Dictionnaire avec les résultats de la simulation
        """
        base_prediction = self.model.predict(X_base)[0]
        
        X_renovated = X_base.copy()
        for feature, new_value in renovations.items():
            if feature in X_renovated.columns:
                X_renovated[feature] = new_value
        
        new_prediction = self.model.predict(X_renovated)[0]
        price_increase = new_prediction - base_prediction
        price_increase_pct = (price_increase / base_prediction) * 100 if base_prediction != 0 else 0
        
        return {
            'base_price': float(base_prediction),
            'new_price': float(new_prediction),
            'price_increase': float(price_increase),
            'price_increase_percentage': float(price_increase_pct),
            'renovations': renovations
        }
    
    def recommend_improvements(self, X_base: pd.DataFrame, 
                              max_recommendations: int = 5) -> List[Dict]:
        """
        Recommander des améliorations pour maximiser la valeur.
        
        Args:
            X_base: Données de base (une ligne)
            max_recommendations: Nombre maximum de recommandations
            
        Returns:
            Liste de recommandations avec impact estimé
        """
        recommendations = []
        base_prediction = self.model.predict(X_base)[0]
        
        # Analyser l'impact de différentes améliorations possibles
        improvements = {
            'OverallQual': min(10, X_base['OverallQual'].iloc[0] + 1) if 'OverallQual' in X_base.columns else None,
            'GrLivArea': X_base['GrLivArea'].iloc[0] * 1.1 if 'GrLivArea' in X_base.columns else None,
            'GarageCars': min(4, X_base['GarageCars'].iloc[0] + 1) if 'GarageCars' in X_base.columns else None,
            'FullBath': X_base['FullBath'].iloc[0] + 1 if 'FullBath' in X_base.columns else None,
        }
        
        for feature, new_value in improvements.items():
            if feature in X_base.columns and new_value is not None:
                if new_value != X_base[feature].iloc[0]:  # Seulement si changement
                    result = self.simulate_renovation(X_base, {feature: new_value})
                    recommendations.append({
                        'feature': feature,
                        'current_value': float(X_base[feature].iloc[0]),
                        'recommended_value': float(new_value),
                        'price_increase': result['price_increase'],
                        'price_increase_percentage': result['price_increase_percentage']
                    })
        
        # Trier par impact décroissant
        recommendations.sort(key=lambda x: x['price_increase'], reverse=True)
        
        return recommendations[:max_recommendations]

