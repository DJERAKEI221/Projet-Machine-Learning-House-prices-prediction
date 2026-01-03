"""
Composant Header pour le dashboard avec navigation intégrée.
"""

import dash_bootstrap_components as dbc
from dash import html
from pathlib import Path
import sys
import base64

# Ajouter la racine au path pour importer config
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config import DASHBOARD_IMAGES
    LOGO_PATH = DASHBOARD_IMAGES / "logo_immo.png"
except ImportError:
    LOGO_PATH = Path(__file__).parent.parent / "images" / "logo_immo.png"


def get_logo_base64():
    """
    Encoder le logo en base64 pour l'afficher dans Dash.
    
    Returns:
        str: URL base64 du logo ou None
    """
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
                return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            return None
    return None


def create_header():
    """
    Créer le header du dashboard avec logo et navigation horizontale élégante.
    
    Returns:
        dbc.Navbar: Header du dashboard avec navigation
    """
    # Obtenir le logo en base64
    logo_base64 = get_logo_base64()
    
    # Créer l'élément logo ou icône de fallback
    if logo_base64:
        logo_element = html.Img(
            src=logo_base64,
            alt="La Place Immo",
            style={
                "height": "50px",
                "width": "auto",
                "objectFit": "contain"
            }
        )
    else:
        # Fallback vers l'icône si le logo n'existe pas
        logo_element = html.I(
            className="fas fa-home fa-2x",
            style={"color": "#2E86AB"}
        )
    
    # Créer les éléments de navigation avec des NavLinks
    nav_items = dbc.Nav(
        [
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-chart-line me-2"),
                        html.Span("Dashboard")
                    ],
                    id="nav-dashboard",
                    n_clicks=0,
                    href="#",
                    className="nav-link-custom"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-calculator me-2"),
                        html.Span("Prédiction")
                    ],
                    id="nav-prediction",
                    n_clicks=0,
                    href="#",
                    className="nav-link-custom"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-chart-bar me-2"),
                        html.Span("Sensibilité")
                    ],
                    id="nav-sensitivity",
                    n_clicks=0,
                    href="#",
                    className="nav-link-custom"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-lightbulb me-2"),
                        html.Span("Explicabilité")
                    ],
                    id="nav-explainability",
                    n_clicks=0,
                    href="#",
                    className="nav-link-custom"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-star me-2"),
                        html.Span("Recommandations")
                    ],
                    id="nav-recommendations",
                    n_clicks=0,
                    href="#",
                    className="nav-link-custom"
                )
            )
        ],
        className="ms-auto d-flex align-items-center",
        navbar=True,
        pills=False,
        style={"flexWrap": "nowrap"}
    )
    
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    logo_element,
                                    className="d-flex align-items-center"
                                )
                            ],
                            width="auto",
                            className="pe-5"
                        ),
                        dbc.Col(
                            [
                                nav_items
                            ],
                            width="auto",
                            className="flex-grow-1"
                        )
                    ],
                    className="w-100 align-items-center",
                    style={"flexWrap": "nowrap"}
                )
            ],
            fluid=True
        ),
        dark=False,
        color="light",
        className="mb-0 shadow-sm navbar-custom",
        style={
            "borderBottom": "3px solid #2E86AB",
            "padding": "1.25rem 0",
            "backgroundColor": "#ffffff",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
        }
    )
