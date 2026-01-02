"""
Composant Navigation en onglets horizontaux.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_nav_tabs():
    """
    Créer la navigation en onglets horizontaux.
    
    Returns:
        dbc.Tabs: Onglets de navigation
    """
    return dbc.Tabs(
        [
            dbc.Tab(
                label=[
                    html.I(className="fas fa-calculator me-2"),
                    "Prédiction"
                ],
                tab_id="prediction",
                id="nav-prediction",
                className="nav-tab-item"
            ),
            dbc.Tab(
                label=[
                    html.I(className="fas fa-chart-bar me-2"),
                    "Analyse de Sensibilité"
                ],
                tab_id="sensitivity",
                id="nav-sensitivity",
                className="nav-tab-item"
            ),
            dbc.Tab(
                label=[
                    html.I(className="fas fa-lightbulb me-2"),
                    "Explicabilité (SHAP)"
                ],
                tab_id="explainability",
                id="nav-explainability",
                className="nav-tab-item"
            ),
            dbc.Tab(
                label=[
                    html.I(className="fas fa-star me-2"),
                    "Recommandations"
                ],
                tab_id="recommendations",
                id="nav-recommendations",
                className="nav-tab-item"
            )
        ],
        id="nav-tabs",
        active_tab="prediction",
        className="mb-3",
        style={
            "borderBottom": "2px solid #e0e0e0"
        }
    )
