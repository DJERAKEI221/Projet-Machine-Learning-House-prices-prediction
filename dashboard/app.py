"""
Application Dash principale pour le dashboard de prédiction des prix immobiliers.
Architecture modulaire avec séparation des composants, pages et callbacks.
Tous les chemins sont gérés via le module config à la racine du projet.
"""

import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Ajouter la racine du projet au path pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importer config pour initialiser les chemins
try:
    import config
except ImportError:
    print("⚠️  Module config non trouvé, utilisation des chemins par défaut")

# Imports des composants
from dashboard.components.header import create_header

# Imports des pages
from dashboard.pages.prediction import create_prediction_page, register_prediction_callbacks
from dashboard.pages.sensitivity import create_sensitivity_page, register_sensitivity_callbacks
from dashboard.pages.explainability import create_explainability_page, register_explainability_callbacks
from dashboard.pages.recommendations import create_recommendations_page

# Imports des utilitaires
from dashboard.utils.data_loader import load_train_data
from dashboard.utils.model_loader import load_model


# Configuration de l'application
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
]

# Créer l'application Dash
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

# Configurer le dossier assets avec chemins relatifs depuis la racine
try:
    from config import DASHBOARD_ASSETS, DASHBOARD_IMAGES
    assets_path = DASHBOARD_ASSETS
    images_path = DASHBOARD_IMAGES
except ImportError:
    assets_path = Path(__file__).parent / "assets"
    images_path = Path(__file__).parent / "images"

if assets_path.exists():
    app.assets_folder = str(assets_path)

# Titre de l'application
app.title = "La Place Immo - Dashboard de Prédiction Immobilière"

# Layout principal
app.layout = dbc.Container(
    [
        create_header(),
        html.Div(id="page-content", className="mt-4")
    ],
    fluid=True,
    className="px-4"
)


# Callback pour la navigation avec NavLinks
@app.callback(
    Output("page-content", "children"),
    [
        Input("nav-prediction", "n_clicks"),
        Input("nav-sensitivity", "n_clicks"),
        Input("nav-explainability", "n_clicks"),
        Input("nav-recommendations", "n_clicks")
    ],
    prevent_initial_call=False
)
def display_page(n_pred, n_sens, n_expl, n_rec):
    """Afficher la page sélectionnée selon le lien cliqué."""
    from dash import callback_context
    
    ctx = callback_context
    
    if not ctx.triggered:
        return create_prediction_page()
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "nav-prediction":
        return create_prediction_page()
    elif button_id == "nav-sensitivity":
        return create_sensitivity_page()
    elif button_id == "nav-explainability":
        return create_explainability_page()
    elif button_id == "nav-recommendations":
        return create_recommendations_page()
    
    return create_prediction_page()


# Callback pour mettre à jour l'état actif des liens de navigation
@app.callback(
    [
        Output("nav-prediction", "active"),
        Output("nav-sensitivity", "active"),
        Output("nav-explainability", "active"),
        Output("nav-recommendations", "active")
    ],
    [
        Input("nav-prediction", "n_clicks"),
        Input("nav-sensitivity", "n_clicks"),
        Input("nav-explainability", "n_clicks"),
        Input("nav-recommendations", "n_clicks")
    ],
    prevent_initial_call=False
)
def update_active_nav(n_pred, n_sens, n_expl, n_rec):
    """Mettre à jour l'état actif des liens de navigation."""
    from dash import callback_context
    
    ctx = callback_context
    
    if not ctx.triggered:
        return True, False, False, False
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    return (
        button_id == "nav-prediction",
        button_id == "nav-sensitivity",
        button_id == "nav-explainability",
        button_id == "nav-recommendations"
    )


# Enregistrer les callbacks des pages
register_prediction_callbacks(app)
register_sensitivity_callbacks(app)
register_explainability_callbacks(app)


if __name__ == "__main__":
    # Afficher les chemins utilisés depuis config
    try:
        from config import MODEL_PATH, TRAIN_DATA_PATH, PROJECT_ROOT
        print(f"📁 Racine du projet: {PROJECT_ROOT}")
        print(f"📁 Chemin du modèle: {MODEL_PATH} (existe: {MODEL_PATH.exists()})")
        print(f"📁 Chemin des données: {TRAIN_DATA_PATH} (existe: {TRAIN_DATA_PATH.exists()})")
    except ImportError:
        print("⚠️  Module config non trouvé, utilisation des chemins par défaut")
    
    # Vérifier que le modèle et les données sont disponibles
    model = load_model()
    train_df = load_train_data()
    
    if model is None:
        print("⚠️  ATTENTION: Modèle non trouvé. Certaines fonctionnalités ne fonctionneront pas.")
        print("   Entraînez d'abord le modèle avec: python train.py")
    
    if train_df is None:
        print("⚠️  ATTENTION: Données non trouvées. Certaines fonctionnalités ne fonctionneront pas.")
    
    print("=" * 60)
    print("🚀 Démarrage du Dashboard Dash")
    print("=" * 60)
    print("📊 Dashboard disponible sur: http://localhost:8050")
    print("=" * 60)
    
    app.run_server(debug=True, host="127.0.0.1", port=8050)
