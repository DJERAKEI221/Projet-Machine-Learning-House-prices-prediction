"""
Page d'explicabilité avec SHAP.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import sys
from pathlib import Path

# Ajouter la racine au path pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dashboard.utils.data_loader import load_train_data


def create_explainability_page():
    """
    Créer la page d'explicabilité.
    
    Returns:
        dbc.Container: Page d'explicabilité
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(className="fas fa-lightbulb me-2"),
                                    "Explicabilité des Prédictions (SHAP)"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            ),
                            html.P(
                                "Comprenez pourquoi le modèle prédit un certain prix grâce à SHAP (SHapley Additive exPlanations).",
                                className="text-muted mb-4"
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-info-circle me-2"),
                                    "Cette fonctionnalité utilise SHAP pour expliquer chaque prédiction. "
                                    "Les visualisations montrent la contribution de chaque variable au prix prédit."
                                ],
                                color="info",
                                className="mb-4"
                            ),
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-chart-pie me-2"),
                                            "Visualisations SHAP"
                                        ],
                                        className="bg-primary text-white"
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [
                                                    html.H5("Waterfall Plot", className="mb-3"),
                                                    html.P(
                                                        "Le waterfall plot montre comment chaque variable contribue "
                                                        "à la prédiction finale, en partant de la valeur de base.",
                                                        className="text-muted"
                                                    ),
                                                    dcc.Graph(id="shap-waterfall-chart")
                                                ],
                                                className="mb-4"
                                            ),
                                            html.Hr(),
                                            html.Div(
                                                [
                                                    html.H5("Summary Plot", className="mb-3"),
                                                    html.P(
                                                        "Le summary plot montre l'importance globale des variables "
                                                        "et leur impact sur les prédictions.",
                                                        className="text-muted"
                                                    ),
                                                    dcc.Graph(id="shap-summary-chart")
                                                ]
                                            )
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


def register_explainability_callbacks(app):
    """Enregistrer les callbacks pour la page d'explicabilité."""
    # Les callbacks SHAP seront implémentés ici
    pass

