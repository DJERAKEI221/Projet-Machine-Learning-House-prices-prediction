"""
Composant formulaire de prédiction avec design amélioré.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ajouter la racine au path pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dashboard.utils.data_loader import load_train_data, get_unique_values, get_column_statistics


def format_number(value, unit=""):
    """Formater un nombre avec des séparateurs de milliers."""
    if value >= 1000:
        return f"{value:,.0f}{unit}".replace(",", " ")
    return f"{value:.0f}{unit}"


def create_slider_with_value(label_text, slider_id, min_val, max_val, step, default_val, 
                            icon_class, marks=None, unit=""):
    """Créer un slider avec label et valeur affichée."""
    return html.Div(
        [
            html.Div(
                [
                    html.I(className=f"{icon_class} me-2", style={"color": "#2E86AB"}),
                    html.Label(label_text, className="form-label fw-bold mb-2", style={"fontSize": "0.95rem"}),
                ],
                className="d-flex align-items-center mb-2"
            ),
            html.Div(
                [
                    dcc.Slider(
                        id=slider_id,
                        min=min_val,
                        max=max_val,
                        step=step,
                        value=default_val,
                        marks=marks,
                        tooltip={"placement": "bottom", "always_visible": False},
                        className="slider-custom"
                    ),
                    html.Div(
                        id=f"{slider_id}-value",
                        className="slider-value-display",
                        children=[
                            html.Span(format_number(default_val, unit), className="badge bg-primary")
                        ]
                    )
                ],
                className="slider-container"
            )
        ],
        className="form-group-custom mb-4"
    )


def create_prediction_form():
    """
    Créer le formulaire de prédiction avec design amélioré.
    
    Returns:
        dbc.Card: Formulaire de prédiction
    """
    train_df = load_train_data()
    
    # Valeurs par défaut
    default_values = {
        'OverallQual': 7,
        'GrLivArea': 1500,
        'GarageCars': 2,
        'TotalBsmtSF': 1000,
        'YearBuilt': 2000,
        'FullBath': 2,
        'TotRmsAbvGrd': 6,
        'LotArea': 8000
    }
    
    # Obtenir les statistiques pour les sliders
    stats = {}
    if train_df is not None:
        for col in default_values.keys():
            if col in train_df.columns:
                stats[col] = get_column_statistics(train_df, col)
    
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-home me-2"),
                    "Caractéristiques de la Maison"
                ],
                className="bg-primary text-white",
                style={"fontSize": "1.1rem", "fontWeight": "600"}
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    create_slider_with_value(
                                        "Qualité Globale",
                                        "input-overall-qual",
                                        min_val=1,
                                        max_val=10,
                                        step=1,
                                        default_val=default_values['OverallQual'],
                                        icon_class="fas fa-star",
                                        marks={1: "1", 5: "5", 10: "10"}
                                    ),
                                    
                                    create_slider_with_value(
                                        "Surface Habitable",
                                        "input-gr-liv-area",
                                        min_val=0,
                                        max_val=5000,
                                        step=50,
                                        default_val=default_values['GrLivArea'],
                                        icon_class="fas fa-ruler-combined",
                                        marks={0: "0", 1500: "1500", 3000: "3000", 5000: "5000"},
                                        unit=" sqft"
                                    ),
                                    
                                    create_slider_with_value(
                                        "Capacité du Garage",
                                        "input-garage-cars",
                                        min_val=0,
                                        max_val=4,
                                        step=1,
                                        default_val=default_values['GarageCars'],
                                        icon_class="fas fa-car",
                                        marks={i: str(i) for i in range(5)}
                                    ),
                                    
                                    create_slider_with_value(
                                        "Surface du Sous-sol",
                                        "input-total-bsmt-sf",
                                        min_val=0,
                                        max_val=3000,
                                        step=50,
                                        default_val=default_values['TotalBsmtSF'],
                                        icon_class="fas fa-layer-group",
                                        marks={0: "0", 1000: "1000", 2000: "2000", 3000: "3000"},
                                        unit=" sqft"
                                    ),
                                    
                                    create_slider_with_value(
                                        "Année de Construction",
                                        "input-year-built",
                                        min_val=1800,
                                        max_val=2024,
                                        step=1,
                                        default_val=default_values['YearBuilt'],
                                        icon_class="fas fa-calendar-alt",
                                        marks={1800: "1800", 1900: "1900", 2000: "2000", 2024: "2024"}
                                    )
                                ],
                                width=6,
                                className="pe-4"
                            ),
                            dbc.Col(
                                [
                                    create_slider_with_value(
                                        "Salles de bain complètes",
                                        "input-full-bath",
                                        min_val=0,
                                        max_val=4,
                                        step=1,
                                        default_val=default_values['FullBath'],
                                        icon_class="fas fa-bath",
                                        marks={i: str(i) for i in range(5)}
                                    ),
                                    
                                    create_slider_with_value(
                                        "Nombre total de pièces",
                                        "input-tot-rms-abv-grd",
                                        min_val=2,
                                        max_val=15,
                                        step=1,
                                        default_val=default_values['TotRmsAbvGrd'],
                                        icon_class="fas fa-door-open",
                                        marks={2: "2", 5: "5", 10: "10", 15: "15"}
                                    ),
                                    
                                    create_slider_with_value(
                                        "Superficie du terrain",
                                        "input-lot-area",
                                        min_val=0,
                                        max_val=20000,
                                        step=100,
                                        default_val=default_values['LotArea'],
                                        icon_class="fas fa-map-marked-alt",
                                        marks={0: "0", 5000: "5k", 10000: "10k", 15000: "15k", 20000: "20k"},
                                        unit=" sqft"
                                    ),
                                    
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.I(className="fas fa-map-marker-alt me-2", style={"color": "#2E86AB"}),
                                                    html.Label("Quartier", className="form-label fw-bold mb-2", style={"fontSize": "0.95rem"}),
                                                ],
                                                className="d-flex align-items-center mb-2"
                                            ),
                                            dcc.Dropdown(
                                                id="input-neighborhood",
                                                options=[
                                                    {"label": val, "value": val} 
                                                    for val in (get_unique_values(train_df, 'Neighborhood') if train_df is not None else [])
                                                ],
                                                value=get_unique_values(train_df, 'Neighborhood')[0] if train_df is not None and len(get_unique_values(train_df, 'Neighborhood')) > 0 else None,
                                                placeholder="Sélectionner un quartier",
                                                className="dropdown-custom"
                                            )
                                        ],
                                        className="form-group-custom mb-4"
                                    ),
                                    
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.I(className="fas fa-building me-2", style={"color": "#2E86AB"}),
                                                    html.Label("Style de maison", className="form-label fw-bold mb-2", style={"fontSize": "0.95rem"}),
                                                ],
                                                className="d-flex align-items-center mb-2"
                                            ),
                                            dcc.Dropdown(
                                                id="input-house-style",
                                                options=[
                                                    {"label": val, "value": val} 
                                                    for val in (get_unique_values(train_df, 'HouseStyle') if train_df is not None else [])
                                                ],
                                                value=get_unique_values(train_df, 'HouseStyle')[0] if train_df is not None and len(get_unique_values(train_df, 'HouseStyle')) > 0 else None,
                                                placeholder="Sélectionner un style",
                                                className="dropdown-custom"
                                            )
                                        ],
                                        className="form-group-custom mb-4"
                                    )
                                ],
                                width=6,
                                className="ps-4"
                            )
                        ]
                    ),
                    html.Hr(className="my-4"),
                    dbc.Button(
                        [
                            html.I(className="fas fa-calculator me-2"),
                            "Prédire le Prix"
                        ],
                        id="btn-predict",
                        color="primary",
                        size="lg",
                        className="w-100 mt-2 btn-predict-custom",
                        n_clicks=0
                    )
                ],
                style={"padding": "2rem"}
            )
        ],
        className="shadow-lg border-0 form-card-custom"
    )
