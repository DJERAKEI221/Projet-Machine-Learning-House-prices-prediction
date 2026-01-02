"""
Page d'analyse de sensibilité.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import sys
from pathlib import Path

# Ajouter la racine au path pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dashboard.components.charts import create_sensitivity_chart
from dashboard.utils.data_loader import load_train_data, get_numeric_columns
from dashboard.utils.model_loader import load_model, get_processors, predict_price


def create_sensitivity_page():
    """
    Créer la page d'analyse de sensibilité.
    
    Returns:
        dbc.Container: Page d'analyse de sensibilité
    """
    train_df = load_train_data()
    numeric_cols = get_numeric_columns(train_df)
    
    # Filtrer les colonnes pertinentes
    relevant_cols = [col for col in numeric_cols if col not in ['Id', 'SalePrice']][:15]
    
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(className="fas fa-chart-bar me-2"),
                                    "Analyse de Sensibilité"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            ),
                            html.P(
                                "Analysez l'impact de chaque variable sur le prix prédit. "
                                "Modifiez une variable et observez son effet sur la prédiction.",
                                className="text-muted mb-4"
                            ),
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-sliders-h me-2"),
                                            "Paramètres de Base"
                                        ],
                                        className="bg-primary text-white"
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Label("Variable à Analyser", className="fw-bold"),
                                                            dcc.Dropdown(
                                                                id="sensitivity-variable",
                                                                options=[{"label": col, "value": col} for col in relevant_cols],
                                                                value=relevant_cols[0] if relevant_cols else None,
                                                                className="mb-3"
                                                            )
                                                        ],
                                                        width=6
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Label("Variation (%)", className="fw-bold"),
                                                            dcc.Slider(
                                                                id="sensitivity-variation",
                                                                min=-50,
                                                                max=50,
                                                                step=5,
                                                                value=10,
                                                                marks={-50: "-50%", 0: "0%", 50: "+50%"},
                                                                tooltip={"placement": "bottom", "always_visible": True}
                                                            )
                                                        ],
                                                        width=6
                                                    )
                                                ]
                                            ),
                                            dbc.Button(
                                                [
                                                    html.I(className="fas fa-chart-line me-2"),
                                                    "Analyser l'Impact"
                                                ],
                                                id="btn-analyze-sensitivity",
                                                color="primary",
                                                className="mt-3",
                                                n_clicks=0
                                            )
                                        ]
                                    )
                                ],
                                className="mb-4 shadow-sm"
                            ),
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-chart-bar me-2"),
                                            "Résultats de l'Analyse"
                                        ],
                                        className="bg-success text-white"
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(id="sensitivity-chart")
                                        ]
                                    )
                                ],
                                className="shadow-sm"
                            )
                        ],
                        width=12
                    )
                ]
            )
        ],
        fluid=True,
        className="mt-4"
    )


def register_sensitivity_callbacks(app):
    """Enregistrer les callbacks pour la page de sensibilité."""
    
    @app.callback(
        Output("sensitivity-chart", "figure"),
        [Input("btn-analyze-sensitivity", "n_clicks")],
        [
            Input("sensitivity-variable", "value"),
            Input("sensitivity-variation", "value")
        ]
    )
    def update_sensitivity_analysis(n_clicks, variable, variation):
        """Mettre à jour l'analyse de sensibilité."""
        if n_clicks == 0 or variable is None:
            return create_sensitivity_chart({})
        
        # Valeurs de base (exemple)
        base_features = {
            'OverallQual': 7,
            'GrLivArea': 1500,
            'GarageCars': 2,
            'TotalBsmtSF': 1000,
            'YearBuilt': 2000
        }
        
        # Prédiction de base
        model = load_model()
        processor, feature_engineer = get_processors()
        
        base_result = predict_price(model, processor, feature_engineer, base_features)
        if not base_result['success']:
            return create_sensitivity_chart({})
        
        base_price = base_result['predicted_price']
        
        # Analyser l'impact de la variable
        sensitivity_data = {}
        
        if variable in base_features:
            # Varier la variable
            base_value = base_features[variable]
            new_value = base_value * (1 + variation / 100)
            
            new_features = base_features.copy()
            new_features[variable] = new_value
            
            new_result = predict_price(model, processor, feature_engineer, new_features)
            if new_result['success']:
                impact = new_result['predicted_price'] - base_price
                sensitivity_data[variable] = impact
        
        # Analyser d'autres variables importantes
        important_vars = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt']
        for var in important_vars:
            if var != variable and var in base_features:
                test_features = base_features.copy()
                test_features[var] = test_features[var] * 1.1  # +10%
                
                test_result = predict_price(model, processor, feature_engineer, test_features)
                if test_result['success']:
                    impact = test_result['predicted_price'] - base_price
                    sensitivity_data[var] = impact
        
        return create_sensitivity_chart(sensitivity_data)

