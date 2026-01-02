"""
Page de prédiction.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback_context
import sys
from pathlib import Path

# Ajouter la racine au path pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dashboard.components.prediction_form import create_prediction_form
from dashboard.components.charts import create_prediction_card, create_price_distribution_chart
from dashboard.utils.model_loader import load_model, get_processors, predict_price
from dashboard.utils.data_loader import load_train_data


def create_prediction_page():
    """
    Créer la page de prédiction avec résultat en bas.
    
    Returns:
        dbc.Container: Page de prédiction
    """
    train_df = load_train_data()
    
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(className="fas fa-calculator me-2"),
                                    "Prédiction de Prix"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            ),
                            create_prediction_form()
                        ],
                        width=12
                    )
                ],
                className="mb-5"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.Div(
                                                [
                                                    html.I(className="fas fa-chart-line me-3"),
                                                    html.H4("Résultat de la Prédiction", className="mb-0")
                                                ],
                                                className="d-flex align-items-center"
                                            )
                                        ],
                                        className="prediction-result-header"
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.Span("Prix Estimé", className="prediction-label"),
                                                                            html.Div(
                                                                                id="prediction-price-display",
                                                                                className="prediction-price-display",
                                                                                children=[
                                                                                    html.Span("$0", className="prediction-price-large")
                                                                                ]
                                                                            ),
                                                                            html.Div(
                                                                                id="prediction-confidence-display",
                                                                                className="prediction-confidence-display",
                                                                                children=""
                                                                            )
                                                                        ],
                                                                        className="prediction-main-display"
                                                                    ),
                                                                    dcc.Graph(
                                                                        id="prediction-chart",
                                                                        figure=create_prediction_card(0),
                                                                        config={"displayModeBar": False},
                                                                        className="prediction-chart-wrapper"
                                                                    )
                                                                ],
                                                                className="prediction-left-section"
                                                            )
                                                        ],
                                                        width=6,
                                                        className="d-flex align-items-center justify-content-center"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                id="prediction-details",
                                                                className="prediction-details-wrapper"
                                                            )
                                                        ],
                                                        width=6
                                                    )
                                                ]
                                            )
                                        ],
                                        className="prediction-result-body"
                                    )
                                ],
                                className="prediction-result-card shadow-lg"
                            )
                        ],
                        width=12,
                        className="mb-4"
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-chart-bar me-2"),
                                            "Distribution des Prix sur le Marché"
                                        ],
                                        className="bg-light",
                                        style={"fontWeight": "600", "color": "#2E86AB"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="price-distribution-chart",
                                                figure=create_price_distribution_chart(train_df),
                                                config={"displayModeBar": False}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm border-0"
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


def register_prediction_callbacks(app):
    """Enregistrer les callbacks pour la page de prédiction."""
    
    # Callbacks pour mettre à jour les valeurs affichées des sliders
    @app.callback(Output("input-overall-qual-value", "children"), Input("input-overall-qual", "value"))
    def update_overall_qual(value):
        if value is None: value = 0
        return html.Span(str(int(value)), className="badge bg-primary")
    
    @app.callback(Output("input-gr-liv-area-value", "children"), Input("input-gr-liv-area", "value"))
    def update_gr_liv_area(value):
        if value is None: value = 0
        formatted = f"{value:,.0f} sqft".replace(",", " ") if value >= 1000 else f"{value:.0f} sqft"
        return html.Span(formatted, className="badge bg-primary")
    
    @app.callback(Output("input-garage-cars-value", "children"), Input("input-garage-cars", "value"))
    def update_garage_cars(value):
        if value is None: value = 0
        return html.Span(str(int(value)), className="badge bg-primary")
    
    @app.callback(Output("input-total-bsmt-sf-value", "children"), Input("input-total-bsmt-sf", "value"))
    def update_total_bsmt_sf(value):
        if value is None: value = 0
        formatted = f"{value:,.0f} sqft".replace(",", " ") if value >= 1000 else f"{value:.0f} sqft"
        return html.Span(formatted, className="badge bg-primary")
    
    @app.callback(Output("input-year-built-value", "children"), Input("input-year-built", "value"))
    def update_year_built(value):
        if value is None: value = 0
        return html.Span(str(int(value)), className="badge bg-primary")
    
    @app.callback(Output("input-full-bath-value", "children"), Input("input-full-bath", "value"))
    def update_full_bath(value):
        if value is None: value = 0
        return html.Span(str(int(value)), className="badge bg-primary")
    
    @app.callback(Output("input-tot-rms-abv-grd-value", "children"), Input("input-tot-rms-abv-grd", "value"))
    def update_tot_rms(value):
        if value is None: value = 0
        return html.Span(str(int(value)), className="badge bg-primary")
    
    @app.callback(Output("input-lot-area-value", "children"), Input("input-lot-area", "value"))
    def update_lot_area(value):
        if value is None: value = 0
        formatted = f"{value:,.0f} sqft".replace(",", " ") if value >= 1000 else f"{value:.0f} sqft"
        return html.Span(formatted, className="badge bg-primary")
    
    @app.callback(
        [
            Output("prediction-chart", "figure"),
            Output("prediction-details", "children"),
            Output("prediction-price-display", "children"),
            Output("prediction-confidence-display", "children")
        ],
        [Input("btn-predict", "n_clicks")],
        [
            State("input-overall-qual", "value"),
            State("input-gr-liv-area", "value"),
            State("input-garage-cars", "value"),
            State("input-total-bsmt-sf", "value"),
            State("input-year-built", "value"),
            State("input-full-bath", "value"),
            State("input-tot-rms-abv-grd", "value"),
            State("input-lot-area", "value"),
            State("input-neighborhood", "value"),
            State("input-house-style", "value")
        ]
    )
    def update_prediction(n_clicks, overall_qual, gr_liv_area, garage_cars, 
                         total_bsmt_sf, year_built, full_bath, tot_rms_abv_grd,
                         lot_area, neighborhood, house_style):
        """Mettre à jour la prédiction."""
        from dashboard.components.charts import create_prediction_card
        
        if n_clicks == 0:
            return create_prediction_card(0), "", html.Span("$0", className="prediction-price-large"), ""
        
        # Préparer les features
        features = {
            'OverallQual': overall_qual,
            'GrLivArea': gr_liv_area,
            'GarageCars': garage_cars,
            'TotalBsmtSF': total_bsmt_sf,
            'YearBuilt': year_built,
            'FullBath': full_bath,
            'TotRmsAbvGrd': tot_rms_abv_grd,
            'LotArea': lot_area,
            'Neighborhood': neighborhood,
            'HouseStyle': house_style
        }
        
        # Charger le modèle et faire la prédiction
        model = load_model()
        processor, feature_engineer = get_processors()
        
        result = predict_price(model, processor, feature_engineer, features)
        
        if result['success']:
            predicted_price = result['predicted_price']
            confidence = result.get('confidence', 0.85)
            
            # Créer la carte de prédiction
            fig = create_prediction_card(predicted_price, confidence)
            
            # Formater le prix
            formatted_price = f"${predicted_price:,.0f}".replace(",", " ")
            
            # Créer l'affichage du prix
            price_display = html.Span(formatted_price, className="prediction-price-large")
            
            # Créer l'affichage de la confiance
            confidence_display = html.Div(
                [
                    html.I(className="fas fa-check-circle me-2"),
                    html.Span(f"Confiance: {confidence*100:.1f}%", className="confidence-text")
                ],
                className="confidence-badge-display"
            )
            
            # Créer les détails améliorés
            details = dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(
                                [
                                    html.I(className="fas fa-info-circle me-2"),
                                    "Informations de la Prédiction"
                                ],
                                className="text-primary mb-4",
                                style={"fontWeight": "600"}
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="fas fa-dollar-sign detail-icon"),
                                                            html.Div(
                                                                [
                                                                    html.Span("Prix Prédit", className="detail-label"),
                                                                    html.Div(formatted_price, className="detail-value-text")
                                                                ],
                                                                className="detail-content"
                                                            )
                                                        ],
                                                        className="detail-card-item"
                                                    )
                                                ],
                                                className="mb-3"
                                            )
                                        ],
                                        width=12,
                                        className="mb-3"
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(className="fas fa-chart-line detail-icon"),
                                                            html.Div(
                                                                [
                                                                    html.Span("Score de Confiance", className="detail-label"),
                                                                    html.Div(
                                                                        f"{confidence*100:.1f}%",
                                                                        className="detail-value-text confidence-value-text"
                                                                    )
                                                                ],
                                                                className="detail-content"
                                                            )
                                                        ],
                                                        className="detail-card-item"
                                                    )
                                                ]
                                            )
                                        ],
                                        width=12
                                    )
                                ]
                            ),
                            html.Hr(className="my-4"),
                            html.Div(
                                [
                                    html.I(className="fas fa-lightbulb text-warning me-2"),
                                    html.Span(
                                        "Cette estimation est générée par notre modèle LightGBM, entraîné sur un large ensemble de données immobilières. Les résultats sont indicatifs et peuvent varier selon les conditions du marché.",
                                        className="text-muted small"
                                    )
                                ],
                                className="prediction-info-note"
                            )
                        ],
                        style={"padding": "2rem"}
                    )
                ],
                className="shadow-sm border-0 detail-card-wrapper",
                style={"borderRadius": "12px", "backgroundColor": "#f8f9fa"}
            )
            
            return fig, details, price_display, confidence_display
        else:
            # Erreur
            error_msg = dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Erreur: {result.get('error', 'Erreur inconnue')}"
                ],
                color="danger",
                className="mt-3"
            )
            return create_prediction_card(0), error_msg, html.Span("$0", className="prediction-price-large"), ""
