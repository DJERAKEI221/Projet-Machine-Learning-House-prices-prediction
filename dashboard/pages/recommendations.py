"""
Page de recommandations d'amélioration.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_recommendations_page():
    """
    Créer la page de recommandations.
    
    Returns:
        dbc.Container: Page de recommandations
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(className="fas fa-star me-2"),
                                    "Recommandations d'Amélioration"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            ),
                            html.P(
                                "Obtenez des recommandations personnalisées pour maximiser la valeur de votre propriété.",
                                className="text-muted mb-4"
                            ),
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-magic me-2"),
                                            "Recommandations Intelligentes"
                                        ],
                                        className="bg-primary text-white"
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [
                                                    html.H5("Types de Recommandations", className="mb-3"),
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(className="fas fa-home me-2 text-primary"),
                                                                    html.Strong("Amélioration de la Qualité Globale"),
                                                                    html.P(
                                                                        "Augmenter la qualité globale peut significativement "
                                                                        "augmenter la valeur de la propriété.",
                                                                        className="mb-0 text-muted small"
                                                                    )
                                                                ],
                                                                className="mb-2"
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(className="fas fa-expand me-2 text-success"),
                                                                    html.Strong("Ajout d'Espace"),
                                                                    html.P(
                                                                        "Ajouter des chambres, salles de bain ou surface habitable "
                                                                        "peut augmenter la valeur.",
                                                                        className="mb-0 text-muted small"
                                                                    )
                                                                ],
                                                                className="mb-2"
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(className="fas fa-car me-2 text-info"),
                                                                    html.Strong("Rénovation du Garage"),
                                                                    html.P(
                                                                        "Améliorer ou agrandir le garage peut être rentable.",
                                                                        className="mb-0 text-muted small"
                                                                    )
                                                                ],
                                                                className="mb-2"
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(className="fas fa-layer-group me-2 text-warning"),
                                                                    html.Strong("Améliorations du Sous-sol"),
                                                                    html.P(
                                                                        "Finir ou améliorer le sous-sol peut ajouter de la valeur.",
                                                                        className="mb-0 text-muted small"
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                        flush=True
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                className="mb-4 shadow-sm"
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-lightbulb me-2"),
                                    html.Strong("Note: "),
                                    "Les recommandations sont basées sur l'analyse de sensibilité du modèle. "
                                    "Chaque amélioration est évaluée selon son impact sur le prix prédit et son ROI estimé."
                                ],
                                color="info"
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

