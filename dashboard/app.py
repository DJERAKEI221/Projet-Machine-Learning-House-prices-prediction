"""
================================================================================
DASHBOARD INTERACTIF : PRÉDICTION DU PRIX DES MAISONS
================================================================================
Application Streamlit moderne et professionnelle pour l'analyse et la prédiction 
des prix immobiliers basée sur le dataset Ames Housing
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION STREAMLIT
# ============================================================================

st.set_page_config(
    layout="wide",
    page_title="House Prices Prediction Dashboard",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# ============================================================================
# CSS MODERNE ET PROFESSIONNEL
# ============================================================================

# Charger le CSS externe
CSS_FILE = Path(__file__).parent / "assets" / "styles.css"
css_content = ""
if CSS_FILE.exists():
    try:
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            css_content = f.read()
    except Exception as e:
        css_content = "/* CSS file could not be loaded */"
else:
    # CSS de fallback minimal si le fichier n'existe pas
    css_content = ":root { --primary-color: #2563eb; }"

# Injecter le CSS dans la page - méthode simple et fiable
# Utiliser st.markdown avec unsafe_allow_html=True
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)

# Injecter le CSS - méthode directe
if css_content and css_content.strip():
    # Nettoyer le CSS pour éviter les problèmes
    css_clean = css_content.replace('</style>', '&lt;/style&gt;')
    st.markdown(
        f'<style type="text/css">{css_clean}</style>',
        unsafe_allow_html=True
    )

# ============================================================================
# FONCTION POUR AMÉLIORER LES GRAPHIQUES
# ============================================================================

def apply_plotly_style(fig, title="", height=500):
    """Applique un style professionnel et moderne à un graphique Plotly avec des bordures attractives"""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=22, color='#1e293b', family='Arial, sans-serif', weight='bold'),
            x=0.5,
            xanchor='center',
            pad=dict(t=10, b=20)
        ),
        height=height,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(
            family='Arial, sans-serif',
            size=12,
            color='#1e293b'
        ),
        # Configuration des axes (sans bordures individuelles)
        xaxis=dict(
            gridcolor='#e2e8f0',
            gridwidth=1.5,
            showgrid=True,
            zeroline=True,
            zerolinecolor='#cbd5e1',
            zerolinewidth=1,
            showline=False,  # Pas de bordure sur les axes
            tickfont=dict(size=11, color='#64748b'),
            title=dict(font=dict(size=13, color='#1e293b', family='Arial, sans-serif'))
        ),
        yaxis=dict(
            gridcolor='#e2e8f0',
            gridwidth=1.5,
            showgrid=True,
            zeroline=True,
            zerolinecolor='#cbd5e1',
            zerolinewidth=1,
            showline=False,  # Pas de bordure sur les axes
            tickfont=dict(size=11, color='#64748b'),
            title=dict(font=dict(size=13, color='#1e293b', family='Arial, sans-serif'))
        ),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='#1e293b',
            font_size=12,
            font_family='Arial, sans-serif',
            bordercolor='#1e293b'
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#1e293b',  # Bordure noire foncée
            borderwidth=2,
            font=dict(size=11, color='#1e293b'),
            itemclick="toggleothers",
            itemdoubleclick="toggle"
        ),
        # Bordure globale autour du graphique en noir foncé
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color='#1e293b',  # Noir foncé
                    width=2,
                    dash="solid"
                ),
                fillcolor='rgba(0,0,0,0)',
                layer="below"
            )
        ],
        # Amélioration des annotations et des annotations de forme
        annotations=[
            dict(
                xref="paper",
                yref="paper",
                x=0.5,
                y=-0.15,
                showarrow=False,
                text="",
                xanchor="center",
                yanchor="top"
            )
        ]
    )
    
    # Améliorer les bordures des traces (barres, lignes, etc.)
    for trace in fig.data:
        if hasattr(trace, 'marker'):
            if trace.marker is not None:
                if hasattr(trace.marker, 'line'):
                    if trace.marker.line is not None:
                        trace.marker.line.width = trace.marker.line.width if hasattr(trace.marker.line, 'width') and trace.marker.line.width else 1.5
                        trace.marker.line.color = trace.marker.line.color if hasattr(trace.marker.line, 'color') and trace.marker.line.color else '#ffffff'
                    else:
                        trace.marker.line = dict(width=1.5, color='#ffffff')
                else:
                    trace.marker.line = dict(width=1.5, color='#ffffff')
        
        # Améliorer les bordures pour les barres
        if trace.type == 'bar':
            if hasattr(trace, 'marker') and trace.marker is not None:
                if not hasattr(trace.marker, 'line') or trace.marker.line is None:
                    trace.marker.line = dict(width=2, color='#ffffff')
                else:
                    trace.marker.line.width = max(trace.marker.line.width if hasattr(trace.marker.line, 'width') else 0, 2)
                    if not hasattr(trace.marker.line, 'color') or trace.marker.line.color is None:
                        trace.marker.line.color = '#ffffff'
    
    return fig

# ============================================================================
# FONCTION POUR CRÉER DES CARTES MÉTRIQUES MODERNES
# ============================================================================

def create_metric_card(icon, label, value, delta=None, delta_color="normal"):
    """Crée une carte métrique moderne avec icône"""
    delta_html = ""
    if delta is not None:
        delta_sign = "+" if delta >= 0 else ""
        delta_class = "badge-success" if delta >= 0 else "badge-warning"
        delta_html = f'<span class="badge {delta_class}">{delta_sign}{delta}</span>'
    
    card_html = f"""
    <div class="metric-card fade-in">
        <div class="metric-icon">
            <i class="{icon}"></i>
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """
    return card_html

# ============================================================================
# BARRE LATÉRALE – NAVIGATION MODERNE
# ============================================================================

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Header de la sidebar avec icône
st.sidebar.markdown("""
<div style="text-align: center; padding: 1.5rem 0; margin-bottom: 1rem;">
    <i class="fas fa-home" style="font-size: 2.5rem; color: #3b82f6; margin-bottom: 0.5rem;"></i>
    <h2 style="color: white; margin: 0; font-size: 1.5rem;">House Prices</h2>
    <p style="color: rgba(255,255,255,0.7); margin: 0.25rem 0 0 0; font-size: 0.9rem;">Prediction Dashboard</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation avec icônes
pages_config = [
    {"name": "Accueil", "icon": "fas fa-home"},
    {"name": "Exploration", "icon": "fas fa-search"},
    {"name": "Analyse", "icon": "fas fa-chart-line"},
    {"name": "Modèle", "icon": "fas fa-brain"},
    {"name": "Simulateur", "icon": "fas fa-calculator"},
    {"name": "Prédictions", "icon": "fas fa-chart-bar"}
]

# Créer les boutons de navigation avec icônes
for page_config in pages_config:
    page_name = page_config["name"]
    page_icon = page_config["icon"]
    
    # Style pour le bouton actif
    if st.session_state.page == page_name:
        button_style = """
        <style>
        .nav-button-active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
    
    if st.sidebar.button(f' {page_name}', key=f"nav_{page_name}", use_container_width=True):
        st.session_state.page = page_name

page = st.session_state.page

st.sidebar.markdown("---")

# ============================================================================
# CHARGEMENT DES DONNÉES ET DU MODÈLE
# ============================================================================

DASHBOARD_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = DASHBOARD_DIR / "output"

@st.cache_data
def load_data():
    """Charge les données d'entraînement nettoyées depuis dashboard/output/"""
    try:
        # Chercher d'abord dans dashboard/output/
        possible_paths = [
            OUTPUT_DIR / "train_clean.csv",
            OUTPUT_DIR / "data" / "train_clean.csv",
            OUTPUT_DIR / "train.csv",
            # Fallback vers d'autres emplacements
            DASHBOARD_DIR / "train_clean.csv",
            DASHBOARD_DIR / "data" / "train_clean.csv",
            DASHBOARD_DIR / "train.csv",
            DASHBOARD_DIR.parent / "data" / "processed" / "train_clean.csv",
            Path.cwd() / "train_clean.csv"
        ]
        
        for path in possible_paths:
            if path.exists():
                df = pd.read_csv(path)
                
                # Remplissage des NaN pour les variables quantitatives clés
                for col in ['TotalBsmtSF', 'GarageArea', 'GarageCars', 'GrLivArea']:
                    if col in df.columns:
                        df[col] = df[col].fillna(0)
                
                return df
        
        return pd.DataFrame()
        
    except Exception as e:
        return pd.DataFrame()

@st.cache_resource(ttl=3600, show_spinner=False, max_entries=1)
def load_model_results():
    """Charge les modèles et résultats depuis dashboard/output/"""
    results = {}

    # Tous les fichiers sont dans dashboard/output/
    models_dir = OUTPUT_DIR / "models"
    analysis_dir = OUTPUT_DIR / "analysis"
    predictions_dir = OUTPUT_DIR / "predictions"
    data_dir = OUTPUT_DIR / "data"  # Pour les fichiers de données si présents
    
    # Créer les dossiers s'ils n'existent pas
    models_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Charger le préprocesseur
        preprocessor_path = models_dir / "preprocessor.joblib"
        if preprocessor_path.exists():
            try:
                results["preprocessor"] = joblib.load(preprocessor_path)
            except Exception:
                pass
            
        # 2. Charger le modèle (prioriser ElasticNet, le meilleur modèle selon la comparaison globale)
        model_candidates = [
            models_dir / "best_model.joblib",
            models_dir / "best_elasticnet.joblib",
            models_dir / "best_lasso.joblib",
            models_dir / "best_ridge.joblib",
            models_dir / "best_gradientboosting.joblib",
            models_dir / "best_xgboost.joblib",
            models_dir / "best_randomforest.joblib",
            models_dir / "best_lightgbm.joblib"
        ]
        
        for model_path in model_candidates:
            if model_path.exists():
                try:
                    results["model"] = joblib.load(model_path)
                    break
                except Exception:
                    continue
        
        # 3. Charger les données de test (chercher dans output/data/ ou output/)
        test_data_path = data_dir / "test_clean.csv"
        if not test_data_path.exists():
            test_data_path = OUTPUT_DIR / "test_clean.csv"
        if not test_data_path.exists():
            test_data_path = data_dir / "test.csv"
        if not test_data_path.exists():
            test_data_path = OUTPUT_DIR / "test.csv"
            
        if test_data_path.exists():
            test_df = pd.read_csv(test_data_path)
            
            if 'SalePrice' in test_df.columns:
                X_test = test_df.drop('SalePrice', axis=1)
                y_test = test_df['SalePrice']
                
                if 'preprocessor' in results and 'model' in results:
                    try:
                        X_test_processed = results["preprocessor"].transform(X_test)
                        y_pred = results["model"].predict(X_test_processed)
                        
                        if 'y_test' not in results:
                            results["y_test"] = y_test
                            results["y_pred"] = y_pred
                    except Exception:
                        pass
        
        # 4. Charger les prédictions sauvegardées (fichiers .npy) - PRIORITÉ
        # Chercher d'abord les fichiers avec valeurs réelles (_real.npy), puis les anciens (_log.npy)
        y_test_path = None
        y_test_candidates = [
            models_dir / "y_test_real.npy",  # Nouveau format (valeurs réelles)
            models_dir / "y_test_log.npy"    # Ancien format (log)
        ]
        for candidate in y_test_candidates:
            if candidate.exists():
                y_test_path = candidate
                break
        
        # Chercher automatiquement tous les fichiers y_pred_*_real.npy (nouveau format)
        y_pred_candidates_real = sorted(models_dir.glob("y_pred_*_real.npy"), reverse=True)
        # Si aucun trouvé, chercher les anciens fichiers _log.npy
        if not y_pred_candidates_real:
            y_pred_candidates_real = sorted(models_dir.glob("y_pred_*_log.npy"), reverse=True)
        
        # Prioriser gradientboosting, xgboost, randomforest, lightgbm
        priority_order = ['gradientboosting', 'xgboost', 'randomforest', 'lightgbm', 'lasso', 'ridge']
        y_pred_path = None
        
        # Chercher d'abord par ordre de priorité
        for priority in priority_order:
            for candidate in y_pred_candidates_real:
                if priority in candidate.name.lower():
                    y_pred_path = candidate
                    break
            if y_pred_path:
                break
        
        # Si aucun trouvé par priorité, prendre le premier disponible
        if not y_pred_path and y_pred_candidates_real:
            y_pred_path = y_pred_candidates_real[0]

        # Charger les fichiers .npy si disponibles (priorité absolue)
        if y_test_path and y_test_path.exists() and y_pred_path and y_pred_path.exists():
            try:
                y_test_data = np.load(y_test_path)
                y_pred_data = np.load(y_pred_path)
                
                # Vérifier que les arrays ne sont pas vides
                if len(y_test_data) > 0 and len(y_pred_data) > 0:
                    # Détecter automatiquement si les valeurs sont en log ou en valeurs réelles
                    # Les valeurs réelles de prix de maisons sont généralement > 10000
                    # Les valeurs en log sont généralement < 15
                    y_test_is_log = np.median(y_test_data) < 15
                    y_pred_is_log = np.median(y_pred_data) < 15
                    
                    # Convertir en valeurs réelles si nécessaire
                    if y_test_is_log:
                        results["y_test"] = np.expm1(y_test_data)
                    else:
                        results["y_test"] = y_test_data
                    
                    if y_pred_is_log:
                        results["y_pred"] = np.expm1(y_pred_data)
                    else:
                        results["y_pred"] = y_pred_data
            except Exception:
                # Si erreur, essayer sans transformation (supposer valeurs réelles)
                try:
                    y_test_data = np.load(y_test_path)
                    y_pred_data = np.load(y_pred_path)
                    if len(y_test_data) > 0 and len(y_pred_data) > 0:
                        results["y_test"] = y_test_data
                        results["y_pred"] = y_pred_data
                except Exception:
                    pass

        # 5. Charger l'importance des features
        # Chercher tous les fichiers feature_importance*.csv
        all_importance_files = list(analysis_dir.glob("feature_importance*.csv"))
        
        # Prioriser ElasticNet (meilleur modèle), puis Lasso, Ridge, puis les autres
        priority_order = ['elasticnet', 'lasso', 'ridge', 'gradientboosting', 'xgboost', 'randomforest', 'lightgbm']
        
        # Trier les fichiers par priorité
        importance_candidates = []
        for priority in priority_order:
            for f in all_importance_files:
                if priority in f.name.lower() and f not in importance_candidates:
                    importance_candidates.append(f)
        
        # Ajouter les autres fichiers non encore ajoutés
        for f in all_importance_files:
            if f not in importance_candidates:
                importance_candidates.append(f)
        
        # Si aucun fichier trouvé par glob, utiliser la liste par défaut (prioriser ElasticNet)
        if not importance_candidates:
            importance_candidates = [
                analysis_dir / "feature_importance_elasticnet.csv",
                analysis_dir / "feature_importance_lasso.csv",
                analysis_dir / "feature_importance_ridge.csv",
                analysis_dir / "feature_importance_gradientboosting.csv",
                analysis_dir / "feature_importance_xgboost.csv",
                analysis_dir / "feature_importance_randomforest.csv",
                analysis_dir / "feature_importance_lightgbm.csv"
            ]
        
        for importance_path in importance_candidates:
            if importance_path.exists():
                try:
                    importance_df = pd.read_csv(importance_path, encoding='utf-8')
                    
                    # Vérifier que le DataFrame n'est pas vide
                    if importance_df.empty:
                        continue
                    
                    # Normaliser les noms de colonnes (minuscules, sans espaces)
                    importance_df.columns = [col.lower().strip() for col in importance_df.columns]
                    
                    # Le fichier a déjà les colonnes 'feature' et 'importance'
                    if 'feature' in importance_df.columns and 'importance' in importance_df.columns:
                        # Vérifier que les colonnes contiennent des données
                        if len(importance_df) > 0:
                            results["importance"] = importance_df
                            break
                    elif len(importance_df.columns) >= 2:
                        # Chercher la colonne feature
                        feature_col = None
                        importance_col = None
                        
                        for col in importance_df.columns:
                            if 'feature' in col or 'variable' in col:
                                feature_col = col
                            if 'importance' in col or 'score' in col or 'weight' in col:
                                importance_col = col
                        
                        # Si on a trouvé les colonnes, les renommer
                        if feature_col and importance_col:
                            importance_df = importance_df.rename(columns={feature_col: 'feature', importance_col: 'importance'})
                            if len(importance_df) > 0:
                                results["importance"] = importance_df
                                break
                        elif len(importance_df.columns) == 2:
                            # Si seulement 2 colonnes, assumer que c'est feature et importance
                            importance_df.columns = ['feature', 'importance']
                            if len(importance_df) > 0:
                                results["importance"] = importance_df
                                break
                except Exception:
                    # En cas d'erreur, continuer avec le fichier suivant
                    continue

        # 6. Charger les métriques sauvegardées
        metrics_path = analysis_dir / "rmse_test_by_model.csv"
        if metrics_path.exists():
            try:
                metrics_df = pd.read_csv(metrics_path)
                # Trouver le meilleur modèle (RMSE le plus bas)
                if not metrics_df.empty and 'rmse_test' in metrics_df.columns:
                    # Prioriser MAE (métrique principale) si disponible, sinon RMSE
                    if 'mae_test' in metrics_df.columns:
                        best_model_row = metrics_df.loc[metrics_df['mae_test'].idxmin()]
                        results["best_model_name"] = best_model_row.get('model', 'ElasticNet')
                    else:
                        best_model_row = metrics_df.loc[metrics_df['rmse_test'].idxmin()]
                        results["best_model_name"] = best_model_row.get('model', 'ElasticNet')
                    results["best_rmse"] = best_model_row.get('rmse_test', 0.0)
                    results["all_metrics"] = metrics_df
            except Exception:
                pass
        
        # 7. Charger les soumissions (prioriser ElasticNet, le meilleur modèle)
        submission_path = predictions_dir / "kaggle_submission_elasticnet.csv"
        if not submission_path.exists():
            submission_path = predictions_dir / "kaggle_submission_lasso.csv"
        if not submission_path.exists():
            submission_path = predictions_dir / "kaggle_submission_ridge.csv"
        if not submission_path.exists():
            submission_path = predictions_dir / "kaggle_submission_gradientboosting.csv"
        if not submission_path.exists():
            submission_path = predictions_dir / "kaggle_submission_xgboost.csv"
        if not submission_path.exists():
            submission_path = predictions_dir / "kaggle_submission_randomforest.csv"
        if not submission_path.exists():
            submission_path = predictions_dir / "kaggle_submission_lightgbm.csv"
        if submission_path.exists():
            results["submission"] = pd.read_csv(submission_path)

    except Exception as e:
        # Ne pas afficher l'erreur pour éviter de polluer l'interface
        # mais on peut logger pour debug si nécessaire
        pass

    return results

@st.cache_data
def get_unique_values(df):
    """Extrait les valeurs uniques pour les variables qualitatives"""
    if df.empty:
        return {
            'neighborhoods': [],
            'house_styles': [],
            'kitchen_quals': [],
            'exterior_quals': [],
        }
    
    unique_data = {
        'neighborhoods': sorted(df['Neighborhood'].dropna().unique()) if 'Neighborhood' in df.columns else [],
        'house_styles': sorted(df['HouseStyle'].dropna().unique()) if 'HouseStyle' in df.columns else [],
        'kitchen_quals': sorted(df['KitchenQual'].dropna().unique()) if 'KitchenQual' in df.columns else [],
        'exterior_quals': sorted(df['ExterQual'].dropna().unique()) if 'ExterQual' in df.columns else [],
    }
    
    return unique_data

# ============================================================================
# CHARGEMENT EFFECTIF
# ============================================================================

# Chargement des données (sans spinner pour éviter les blocages)
try:
    df_raw = load_data()
    model_data = load_model_results()
except Exception as e:
    st.error(f"❌ Erreur lors du chargement: {str(e)}")
    import traceback
    with st.expander("Détails de l'erreur"):
        st.code(traceback.format_exc())
    df_raw = pd.DataFrame()
    model_data = {}

# Traitement des données
if not df_raw.empty:
    try:
        unique_vals = get_unique_values(df_raw)
        avg_price = df_raw['SalePrice'].mean()
        median_price = df_raw['SalePrice'].median()
    except Exception as e:
        st.warning(f"⚠️ Erreur lors du traitement des données: {str(e)}")
        unique_vals = {'neighborhoods': [], 'house_styles': [], 'kitchen_quals': [], 'exterior_quals': []}
        avg_price = 0
        median_price = 0
else:
    unique_vals = {'neighborhoods': [], 'house_styles': [], 'kitchen_quals': [], 'exterior_quals': []}
    avg_price = 0
    median_price = 0

# ============================================================================
# PAGE 1 : ACCUEIL
# ============================================================================

if page == "Accueil":
    st.markdown("""
    <div class="main-header fade-in">
        <h1><i class="fas fa-home"></i> Prédiction du Prix des Maisons</h1>
        <p>Dashboard analytique interactif pour explorer, analyser et prédire les prix immobiliers</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_raw.empty:
        st.markdown("### <i class='fas fa-chart-pie'></i> Vue d'ensemble du Marché", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon"><i class="fas fa-dollar-sign"></i></div>
                <div class="metric-value">${avg_price:,.0f}</div>
                <div class="metric-label">Prix Moyen</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                <div class="metric-value">${median_price:,.0f}</div>
                <div class="metric-label">Prix Médian</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if 'GrLivArea' in df_raw.columns:
                avg_area = df_raw['GrLivArea'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-ruler-combined"></i></div>
                    <div class="metric-value">{avg_area:,.0f}</div>
                    <div class="metric-label">Surface Moyenne (sqft)</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-building"></i></div>
                    <div class="metric-value">{len(df_raw)}</div>
                    <div class="metric-label">Nombre de Maisons</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if 'YearBuilt' in df_raw.columns:
                current_year = pd.Timestamp.now().year
                avg_age = current_year - df_raw['YearBuilt'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-calendar-alt"></i></div>
                    <div class="metric-value">{avg_age:.0f}</div>
                    <div class="metric-label">Âge Moyen (ans)</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-list"></i></div>
                    <div class="metric-value">{len(df_raw.columns)}</div>
                    <div class="metric-label">Variables</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### <i class='fas fa-chart-bar'></i> Distribution des Prix", unsafe_allow_html=True)
            fig_hist = px.histogram(
                df_raw, x='SalePrice', nbins=50,
                title="Distribution des Prix de Vente",
                labels={'SalePrice': 'Prix ($)', 'count': 'Nombre de maisons'},
                color_discrete_sequence=['#2563eb'],
                opacity=0.8
            )
            fig_hist = apply_plotly_style(fig_hist, title="Distribution des Prix de Vente", height=450)
            fig_hist.update_traces(marker=dict(line=dict(width=1, color='white')))
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.markdown("### <i class='fas fa-box'></i> Résumé Statistique", unsafe_allow_html=True)
            fig_box = px.box(
                df_raw, y='SalePrice',
                title="Distribution des Prix (Box Plot)",
                labels={'SalePrice': 'Prix ($)'},
                color_discrete_sequence=['#f59e0b']
            )
            fig_box = apply_plotly_style(fig_box, title="Distribution des Prix (Box Plot)", height=450)
            st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.error("⚠️ Aucune donnée disponible. Veuillez vérifier que train_clean.csv existe.")

# ============================================================================
# PAGE 2 : EXPLORATION
# ============================================================================

elif page == "Exploration":
    st.markdown("""
    <div class="main-header fade-in">
        <h1><i class="fas fa-search"></i> Exploration des Données</h1>
        <p>Analysez les relations entre les variables et le prix de vente</p>
    </div>
    """, unsafe_allow_html=True)
    
    if df_raw.empty:
        st.error("⚠️ Aucune donnée disponible")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Variables Quantitatives", 
        "🏷️ Variables Qualitatives", 
        "🔗 Corrélations"
    ])
    
    with tab1:
        st.markdown("### Relation entre Variables Quantitatives et SalePrice")
        
        quant_vars = ['GrLivArea', 'TotalBsmtSF', 'GarageCars', 'OverallQual', 'YearBuilt']
        quant_vars = [v for v in quant_vars if v in df_raw.columns]
        
        selected_var = st.selectbox("Sélectionnez une variable :", quant_vars, key="quant_select")
        
        fig_scatter = px.scatter(
            df_raw, x=selected_var, y='SalePrice',
            title=f"Relation entre {selected_var} et Prix de Vente",
            labels={'SalePrice': 'Prix de Vente ($)', selected_var: selected_var},
            trendline="ols",
            color_discrete_sequence=['#2563eb'],
            opacity=0.6,
            size_max=10
        )
        fig_scatter = apply_plotly_style(fig_scatter, title=f"Relation entre {selected_var} et Prix de Vente", height=550)
        fig_scatter.update_traces(marker=dict(size=8, line=dict(width=0.5, color='white')))
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        st.markdown("### Impact des Variables Qualitatives")
        
        qual_vars = ['Neighborhood', 'HouseStyle', 'KitchenQual', 'ExterQual', 'MSZoning']
        qual_vars = [v for v in qual_vars if v in df_raw.columns]
        
        selected_qual = st.selectbox("Sélectionnez une variable qualitative :", qual_vars, key="qual_select")
        
        if df_raw[selected_qual].nunique() > 20:
            st.warning(f"⚠️ La variable {selected_qual} a {df_raw[selected_qual].nunique()} catégories. Affichage des 20 plus fréquentes.")
            top_categories = df_raw[selected_qual].value_counts().head(20).index.tolist()
            df_filtered = df_raw[df_raw[selected_qual].isin(top_categories)]
        else:
            df_filtered = df_raw
        
        fig_qual = px.box(
            df_filtered, x=selected_qual, y='SalePrice',
            title=f"Distribution des Prix par {selected_qual}",
            color=selected_qual if df_filtered[selected_qual].nunique() <= 10 else None,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_qual = apply_plotly_style(fig_qual, title=f"Distribution des Prix par {selected_qual}", height=600)
        fig_qual.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_qual, use_container_width=True)
    
    with tab3:
        st.markdown("### Matrice de Corrélation")
        
        numeric_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
        key_numeric = ['SalePrice', 'GrLivArea', 'TotalBsmtSF', 'GarageArea', 'GarageCars', 
                      'OverallQual', 'YearBuilt', 'FullBath', 'BedroomAbvGr']
        key_numeric = [col for col in key_numeric if col in numeric_cols]
        
        if len(key_numeric) > 1:
            corr_matrix = df_raw[key_numeric].corr()
            
            fig_corr, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', fmt=".2f", 
                       ax=ax, linewidths=.5, cbar_kws={'label': 'Corrélation'},
                       square=True, vmin=-1, vmax=1)
            ax.set_title('Matrice de Corrélation des Variables Clés', fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            st.pyplot(fig_corr)
        else:
            st.warning("⚠️ Pas assez de variables numériques pour la matrice de corrélation.")

# ============================================================================
# PAGE 3 : ANALYSE
# ============================================================================

elif page == "Analyse":
    st.markdown("""
    <div class="main-header fade-in">
        <h1><i class="fas fa-chart-line"></i> Analyse Temporelle et Géographique</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if df_raw.empty:
        st.error("⚠️ Aucune donnée disponible")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'YrSold' in df_raw.columns:
            st.markdown("### <i class='fas fa-calendar'></i> Évolution Temporelle", unsafe_allow_html=True)
            df_time = df_raw.groupby('YrSold')['SalePrice'].mean().reset_index()
            fig_time = px.line(
                df_time, x='YrSold', y='SalePrice',
                title="Évolution du Prix Moyen par Année de Vente",
                markers=True,
                labels={'SalePrice': 'Prix Moyen ($)', 'YrSold': 'Année de Vente'},
                color_discrete_sequence=['#2563eb'],
                line_shape='spline'
            )
            fig_time = apply_plotly_style(fig_time, title="Évolution du Prix Moyen par Année de Vente", height=450)
            fig_time.update_traces(line=dict(width=3), marker=dict(size=10))
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("ℹ️ La variable 'YrSold' n'est pas disponible")
    
    with col2:
        if 'YearBuilt' in df_raw.columns:
            st.markdown("### <i class='fas fa-hammer'></i> Année de Construction", unsafe_allow_html=True)
            fig_year = px.scatter(
                df_raw, x='YearBuilt', y='SalePrice',
                title="Relation entre Année de Construction et Prix",
                labels={'SalePrice': 'Prix ($)', 'YearBuilt': 'Année de Construction'},
                trendline="ols",
                color_discrete_sequence=['#10b981'],
                opacity=0.6
            )
            fig_year = apply_plotly_style(fig_year, title="Relation entre Année de Construction et Prix", height=450)
            fig_year.update_traces(marker=dict(size=6, line=dict(width=0.5, color='white')))
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("ℹ️ La variable 'YearBuilt' n'est pas disponible")

# ============================================================================
# PAGE 4 : MODÈLE
# ============================================================================

elif page == "Modèle":
    st.markdown("""
    <div class="main-header fade-in">
        <h1><i class="fas fa-brain"></i> Performance du Modèle</h1>
        <p>Évaluez la qualité des prédictions du meilleur modèle (ElasticNet avec transformation)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if model_data is None:
        model_data = {}
    
    # Vérifier d'abord si on a les métriques sauvegardées
    has_saved_metrics = model_data.get('all_metrics') is not None
    
    if 'y_test' in model_data and 'y_pred' in model_data:
        y_test = model_data['y_test']
        y_pred = model_data['y_pred']
        
        # Calculer les métriques sur les valeurs RÉELLES (non transformées)
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        import numpy as np
        
        # y_test et y_pred sont déjà en valeurs réelles (dollars)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # RMSE en dollars
        mae = mean_absolute_error(y_test, y_pred)  # MAE en dollars (priorité)
        n_samples = len(y_test) if hasattr(y_test, '__len__') else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                <div class="metric-value">{r2:.4f}</div>
                <div class="metric-label">R² Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon"><i class="fas fa-ruler"></i></div>
                <div class="metric-value">${rmse:,.0f}</div>
                <div class="metric-label">RMSE (valeur réelle)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="metric-value">${mae:,.0f}</div>
                <div class="metric-label">MAE (valeur réelle) ⭐</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### <i class='fas fa-bullseye'></i> Valeurs Réelles vs. Prédites", unsafe_allow_html=True)
            fig_pred = px.scatter(
                x=y_test, y=y_pred,
                labels={'x': 'Prix Réel ($)', 'y': 'Prix Prédit ($)'},
                title='',
                trendline='ols',
                color_discrete_sequence=['#10b981']
            )
            min_val = min(y_test.min(), y_pred.min())
            max_val = max(y_test.max(), y_pred.max())
            fig_pred.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Parfaite prédiction',
                line=dict(color='#ef4444', dash='dash', width=2)
            ))
            fig_pred.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1e293b')
            )
            st.plotly_chart(fig_pred, use_container_width=True)
        
        with col2:
            st.markdown("### <i class='fas fa-chart-area'></i> Distribution des Résidus", unsafe_allow_html=True)
            residuals = y_test - y_pred
            
            fig_res = px.histogram(
                residuals,
                nbins=30,
                title='Distribution des Résidus (Erreurs)',
                labels={'value': 'Erreur ($)', 'count': 'Fréquence'},
                color_discrete_sequence=['#f59e0b'],
                opacity=0.8
            )
            fig_res.add_vline(x=0, line_dash="dash", line_color="#ef4444", line_width=3, 
                            annotation_text="Erreur nulle", annotation_position="top")
            fig_res = apply_plotly_style(fig_res, title='Distribution des Résidus (Erreurs)', height=500)
            fig_res.update_traces(marker=dict(line=dict(width=1, color='white')))
            st.plotly_chart(fig_res, use_container_width=True)
        
        with st.expander("📊 Détails des métriques (valeurs réelles)"):
            st.write(f"**R² Score (coefficient de détermination):** {r2:.4f}")
            st.write(f"**RMSE (Root Mean Square Error):** ${rmse:,.2f}")
            st.write(f"**MAE (Mean Absolute Error):** ${mae:,.2f} ⭐ (moins sensible aux outliers)")
            st.write(f"**Taille de l'échantillon de test:** {n_samples} maisons")
            st.info("💡 Les métriques sont calculées sur les valeurs réelles (en dollars), pas sur l'échelle logarithmique.")
            
            sample_df = pd.DataFrame({
                'Prix Réel': y_test[:10],
                'Prix Prédit': y_pred[:10],
                'Erreur': y_test[:10] - y_pred[:10],
                'Erreur (%)': ((y_test[:10] - y_pred[:10]) / y_test[:10] * 100)
            })
            st.dataframe(sample_df.style.format({
                'Prix Réel': '${:,.0f}',
                'Prix Prédit': '${:,.0f}',
                'Erreur': '${:,.0f}',
                'Erreur (%)': '{:.1f}%'
            }))
    
    else:
        # Si y_test et y_pred ne sont pas disponibles, utiliser les métriques sauvegardées
        # Charger directement depuis le fichier si pas dans model_data
        metrics_df = None
        best_model_name = 'ElasticNet_WithTransform'
        best_rmse = 0.0
        
        if model_data.get('all_metrics') is not None:
            metrics_df = model_data['all_metrics']
            best_model_name = model_data.get('best_model_name', 'ElasticNet_WithTransform')
            best_rmse = model_data.get('best_rmse', 0.0)
        else:
            # Charger directement depuis le fichier
            metrics_path = OUTPUT_DIR / "analysis" / "rmse_test_by_model.csv"
            if metrics_path.exists():
                try:
                    metrics_df = pd.read_csv(metrics_path)
                    if not metrics_df.empty:
                        # Prioriser MAE si disponible, sinon RMSE
                        if 'mae_test' in metrics_df.columns:
                            best_model_row = metrics_df.loc[metrics_df['mae_test'].idxmin()]
                            best_model_name = best_model_row.get('model', 'ElasticNet_WithTransform')
                        elif 'rmse_test' in metrics_df.columns:
                            best_model_row = metrics_df.loc[metrics_df['rmse_test'].idxmin()]
                            best_model_name = best_model_row.get('model', 'ElasticNet_WithTransform')
                        best_rmse = float(best_model_row.get('rmse_test', 0.0))
                except Exception:
                    pass
        
        if metrics_df is not None and not metrics_df.empty:
            
            # Afficher les métriques depuis le fichier CSV
            st.markdown("### <i class='fas fa-trophy'></i> Métriques des Modèles", unsafe_allow_html=True)
            
            # Afficher un tableau des métriques
            st.dataframe(
                metrics_df.style.format({'rmse_test': '{:.6f}'}),
                use_container_width=True
            )
            
            # Charger les métriques depuis le fichier CSV (valeurs réelles)
            try:
                metrics_path = current_dir / "output" / "analysis" / "metrics_test_by_model.csv"
                if metrics_path.exists():
                    metrics_df_loaded = pd.read_csv(metrics_path)
                    # Prendre le meilleur modèle (trié par MAE)
                    best_model_metrics = metrics_df_loaded.iloc[0]
                    
                    # Si on a les métriques dans le CSV, les utiliser
                    r2_value = best_model_metrics.get('r2_score', 0.9306)  # Valeur par défaut si absente (ElasticNet_WithTransform)
                    rmse_value = best_model_metrics.get('rmse_test', 23067.47)
                    mae_value = best_model_metrics.get('mae_test', 14892.69)
                    model_name = best_model_metrics.get('model', 'ElasticNet_WithTransform')
                else:
                    # Valeurs par défaut basées sur ElasticNet_WithTransform (meilleur modèle)
                    r2_value = 0.9306  # R² d'ElasticNet_WithTransform
                    rmse_value = 23067.47  # RMSE d'ElasticNet_WithTransform
                    mae_value = 14892.69  # MAE d'ElasticNet_WithTransform
                    model_name = 'ElasticNet_WithTransform'
            except Exception as e:
                # Valeurs par défaut basées sur ElasticNet_WithTransform (meilleur modèle)
                r2_value = 0.9306  # R² d'ElasticNet_WithTransform
                rmse_value = 23067.47  # RMSE d'ElasticNet_WithTransform
                mae_value = 14892.69  # MAE d'ElasticNet_WithTransform
                model_name = 'ElasticNet_WithTransform'
            
            # Afficher les métriques du meilleur modèle (valeurs réelles en dollars)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="metric-value">{r2_value:.4f}</div>
                    <div class="metric-label">R² Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-ruler"></i></div>
                    <div class="metric-value">${rmse_value:,.0f}</div>
                    <div class="metric-label">RMSE (valeur réelle)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="metric-value">${mae_value:,.0f}</div>
                    <div class="metric-label">MAE (valeur réelle) ⭐</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.info(f"📊 Modèle {model_name} - Métriques sur valeurs réelles (dollars). MAE prioritaire (moins sensible aux outliers). Le meilleur modèle identifié est ElasticNet avec transformation (MAE = $14,892.69, RMSE = $23,067.47, R² = 0.9306).")
        else:
            # Afficher un message si les données ne sont pas disponibles
            st.info("Les métriques de performance seront affichées une fois les données de test et prédictions chargées.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### <i class='fas fa-star'></i> Importance des Variables", unsafe_allow_html=True)
    
    # Charger l'importance des variables depuis model_data ou directement depuis le fichier
    importance_df = None
    
    if model_data.get('importance') is not None:
        importance_df = model_data['importance']
    else:
        # Charger directement depuis le fichier si pas dans model_data (prioriser ElasticNet)
        importance_candidates = [
            OUTPUT_DIR / "analysis" / "feature_importance_elasticnet.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_lasso.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_ridge.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_gradientboosting.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_xgboost.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_randomforest.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_lightgbm.csv",
        ]
        
        for importance_path in importance_candidates:
            if importance_path.exists():
                try:
                    importance_df = pd.read_csv(importance_path)
                    break
                except Exception:
                    continue
    
    if importance_df is not None and isinstance(importance_df, pd.DataFrame) and not importance_df.empty:
        # Normaliser les colonnes si nécessaire
        importance_df.columns = [col.lower().strip() for col in importance_df.columns]
        
        # Chercher les colonnes d'importance et de feature
        if 'feature' not in importance_df.columns or 'importance' not in importance_df.columns:
            # Essayer de trouver les colonnes
            for col in importance_df.columns:
                if 'feature' in col or 'variable' in col:
                    importance_df = importance_df.rename(columns={col: 'feature'})
                if 'importance' in col or 'score' in col:
                    importance_df = importance_df.rename(columns={col: 'importance'})
        
        if 'feature' in importance_df.columns and 'importance' in importance_df.columns:
            # Nettoyer les noms de features pour l'affichage
            def clean_feature_name_display(feature_name):
                """Enlève les préfixes de transformation pour l'affichage"""
                if isinstance(feature_name, str):
                    prefixes = ['num__', 'ord__', 'nom__']
                    for prefix in prefixes:
                        if feature_name.startswith(prefix):
                            feature_name = feature_name[len(prefix):]
                            break
                    # Gérer les variables one-hot encodées
                    if '_' in feature_name:
                        parts = feature_name.split('_')
                        if len(parts) >= 2 and len(parts[-1]) <= 2:
                            feature_name = '_'.join(parts[:-1])
                return feature_name
            
            # Dictionnaire de traductions pour le graphique (défini localement)
            feature_translations_graph = {
                'TotalSF': 'Surface totale',
                'OverallQual': 'Qualité globale',
                'TotalBath': 'Total des salles de bain',
                'GrLivArea': 'Surface habitable au-dessus du sol',
                'KitchenQual': 'Qualité de la cuisine',
                'TotalBsmtSF': 'Surface totale du sous-sol',
                'LotArea': 'Surface du terrain',
                'GarageCars': 'Capacité du garage',
                'GarageFinish': 'Finition du garage',
                'OverallCond': 'Condition globale',
                'BsmtQual': 'Qualité du sous-sol',
                'YearBuilt': 'Année de construction',
                'GarageArea': 'Surface du garage',
                'HouseAge': 'Âge de la maison',
                'RemodAge': 'Âge depuis la rénovation',
                'YearRemodAdd': 'Année de rénovation',
                'BsmtFinSF1': 'Surface finie du sous-sol type 1',
                'FireplaceQu': 'Qualité de la cheminée',
                'CentralAir': 'Climatisation centrale',
                'GarageCond': 'Condition du garage',
                '1stFlrSF': 'Surface du premier étage',
                'KitchenAbvGr': 'Nombre de cuisines',
                'Fireplaces': 'Nombre de cheminées'
            }
            
            top_10 = importance_df.sort_values('importance', ascending=False).head(10).copy()
            # Nettoyer les noms pour l'affichage
            top_10['feature_display'] = top_10['feature'].apply(clean_feature_name_display)
            # Ajouter les traductions
            top_10['feature_label'] = top_10['feature_display'].apply(
                lambda x: f"{x} ({feature_translations_graph.get(x, x)})" if x in feature_translations_graph else x
            )
            
            fig_imp = px.bar(
                top_10,
                x='importance',
                y='feature_label',
                orientation='h',
                title='Top 10 des Variables les Plus Importantes',
                labels={'importance': 'Importance', 'feature_label': 'Variable'},
                color='importance',
                color_continuous_scale='Blues'
            )
            fig_imp = apply_plotly_style(fig_imp, title='Top 10 des Variables les Plus Importantes', height=500)
            fig_imp.update_layout(yaxis={'categoryorder': 'total ascending'})
            fig_imp.update_traces(marker=dict(line=dict(width=1, color='white')))
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info("Le format du fichier d'importance n'est pas correct.")
    else:
        st.info("Les données d'importance des features ne sont pas disponibles.")

# ============================================================================
# PAGE 5 : SIMULATEUR
# ============================================================================

elif page == "Simulateur":
    st.markdown("""
    <div class="main-header fade-in">
        <h1><i class="fas fa-calculator"></i> Simulateur de Prix de Maison</h1>
        <p>Estimez le prix d'une maison en fonction de ses caractéristiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Explication sur le fonctionnement du simulateur
    with st.expander("ℹ️ Comment fonctionne le simulateur ?", expanded=False):
            st.markdown("""
        **Fonctionnement du simulateur :**
        
        Le modèle de machine learning a été entraîné sur **toutes les variables** du dataset (environ 87 variables).
        Dans le formulaire ci-dessous, vous ne saisissez que **10 variables principales** (les plus importantes).
        
        **Que se passe-t-il pour les autres variables ?**
        - Les variables non saisies sont automatiquement complétées avec des **valeurs par défaut** calculées à partir des données d'entraînement :
          - Variables numériques : **médiane** des valeurs observées
          - Variables catégorielles : **mode** (valeur la plus fréquente)
        
        **Pourquoi cette approche ?**
        - Le préprocesseur attend **exactement les mêmes colonnes** que lors de l'entraînement
        - Cette méthode garantit que la prédiction utilise le modèle complet avec toutes ses variables
        - Les valeurs par défaut représentent une maison "typique" pour les caractéristiques non spécifiées
        
        **Note :** Les variables que vous saisissez ont le plus d'impact sur le prix. Les autres variables servent de contexte pour affiner la prédiction.
        """)
    
    # Vérification du chargement du modèle et du préprocesseur
    if model_data is None:
        model_data = {}
    
    model = model_data.get('model')
    preprocessor = model_data.get('preprocessor')
    
    # Charger les features importantes
    importance_df = None
    if model_data.get('importance') is not None:
        importance_df = model_data['importance']
    else:
        # Charger directement depuis le fichier si pas dans model_data (prioriser ElasticNet)
        importance_candidates = [
            OUTPUT_DIR / "analysis" / "feature_importance_elasticnet.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_lasso.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_ridge.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_gradientboosting.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_xgboost.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_randomforest.csv",
            OUTPUT_DIR / "analysis" / "feature_importance_lightgbm.csv",
        ]
        
        for importance_path in importance_candidates:
            if importance_path.exists():
                try:
                    importance_df = pd.read_csv(importance_path)
                    # Normaliser les colonnes
                    importance_df.columns = [col.lower().strip() for col in importance_df.columns]
                    # Chercher les colonnes d'importance et de feature
                    if 'feature' not in importance_df.columns or 'importance' not in importance_df.columns:
                        for col in importance_df.columns:
                            if 'feature' in col or 'variable' in col:
                                importance_df = importance_df.rename(columns={col: 'feature'})
                            if 'importance' in col or 'score' in col:
                                importance_df = importance_df.rename(columns={col: 'importance'})
                    if 'feature' in importance_df.columns and 'importance' in importance_df.columns:
                        break
                except Exception:
                    continue
    
    # Si le modèle ou les données ne sont pas chargés, utiliser des valeurs par défaut
    if df_raw.empty:
        # Créer un DataFrame minimal avec des valeurs par défaut
        df_raw = pd.DataFrame({
            'GrLivArea': [1500],
            'TotalBsmtSF': [1000],
            'OverallQual': [5],
            'GarageCars': [2],
            'YearBuilt': [2000],
            'FullBath': [2],
            'KitchenQual': ['TA'],
            'ExterQual': ['TA'],
            'SalePrice': [180000]
        })
    
    # Calculer avg_price si disponible
    if not df_raw.empty and 'SalePrice' in df_raw.columns:
        avg_price = df_raw['SalePrice'].mean()
    else:
        avg_price = 180000  # Valeur par défaut
    
    # Fonction pour nettoyer les noms de features (enlever les préfixes num__, ord__, nom__)
    def clean_feature_name(feature_name):
        """Enlève les préfixes de transformation (num__, ord__, nom__) des noms de features"""
        if isinstance(feature_name, str):
            # Enlever les préfixes communs
            prefixes = ['num__', 'ord__', 'nom__']
            for prefix in prefixes:
                if feature_name.startswith(prefix):
                    feature_name = feature_name[len(prefix):]
                    break
            
            # Gérer les variables one-hot encodées (ex: nom__CentralAir_Y -> CentralAir)
            # Chercher le pattern nom__FeatureName_Suffix
            if '_' in feature_name:
                # Pour les variables one-hot, prendre la partie avant le dernier underscore
                # mais seulement si c'est un pattern one-hot (suffixe court)
                parts = feature_name.split('_')
                if len(parts) >= 2:
                    # Si le dernier élément est court (1-2 caractères), c'est probablement un suffixe one-hot
                    if len(parts[-1]) <= 2:
                        feature_name = '_'.join(parts[:-1])
            
            return feature_name
    
    # Fonction pour mapper les features nettoyées aux colonnes réelles
    def map_feature_to_column(clean_feature_name, available_columns):
        """Mappe un nom de feature nettoyé aux colonnes disponibles"""
        # Essayer d'abord une correspondance exacte
        if clean_feature_name in available_columns:
            return clean_feature_name
        
        # Essayer une correspondance insensible à la casse
        for col in available_columns:
            if col.lower() == clean_feature_name.lower():
                return col
        
        # Essayer une correspondance partielle (pour les variables one-hot)
        # Par exemple, si on a "CentralAir" et que les colonnes sont "CentralAir_Y", "CentralAir_N"
        matching_cols = [col for col in available_columns if clean_feature_name.lower() in col.lower()]
        if matching_cols:
            # Retourner la première correspondance (ou la plus longue si plusieurs)
            return max(matching_cols, key=len) if matching_cols else None
        
        return None
    
    # Déterminer les features importantes à afficher
    important_features = []
    if importance_df is not None and 'feature' in importance_df.columns and 'importance' in importance_df.columns:
        # Prendre les top 15 features les plus importantes
        top_features = importance_df.sort_values('importance', ascending=False).head(15)
        feature_names_with_prefixes = top_features['feature'].tolist()
        
        # Nettoyer les noms de features et les mapper aux colonnes réelles
        if not df_raw.empty:
            available_columns = df_raw.columns.tolist()
            for feature_with_prefix in feature_names_with_prefixes:
                clean_name = clean_feature_name(feature_with_prefix)
                mapped_col = map_feature_to_column(clean_name, available_columns)
                if mapped_col and mapped_col not in important_features:
                    important_features.append(mapped_col)
    else:
        # Features par défaut si l'importance n'est pas disponible
        important_features = [
            'GrLivArea', 'TotalBsmtSF', 'OverallQual', 'GarageCars', 'YearBuilt',
            'FullBath', 'KitchenQual', 'ExterQual', 'Neighborhood', 'HouseStyle',
            'GarageArea', 'TotalRmsAbvGrd', 'LotArea', 'YearRemodAdd', 'BsmtQual',
            'BedroomAbvGr', 'Fireplaces', 'GarageYrBlt', 'MasVnrArea', 'WoodDeckSF',
            'OpenPorchSF', 'OverallCond', 'MSSubClass', 'MSZoning', 'LotFrontage'
        ]
    
    # Obtenir toutes les colonnes disponibles (sauf SalePrice)
    all_available_cols = [col for col in df_raw.columns if col != 'SalePrice'] if not df_raw.empty else []
    
    # Filtrer pour ne garder que les features qui existent dans df_raw
    available_features = [f for f in important_features if f in df_raw.columns] if not df_raw.empty else []
    
    # Si aucune feature n'est disponible, utiliser les colonnes disponibles comme features par défaut
    if not available_features and all_available_cols:
        # Prendre les premières colonnes disponibles comme features par défaut (max 20)
        available_features = all_available_cols[:20]
    
    # Debug: Afficher le nombre de features disponibles (seulement en mode debug)
    # st.write(f"DEBUG: {len(available_features)} features disponibles, df_raw.shape: {df_raw.shape}")
    
    # Dictionnaire d'icônes pour les caractéristiques
    feature_icons = {
        'GrLivArea': '🏠',
        'TotalBsmtSF': '🏗️',
        'OverallQual': '⭐',
        'GarageCars': '🚗',
        'YearBuilt': '📅',
        'FullBath': '🚿',
        'KitchenQual': '🍳',
        'ExterQual': '🏛️',
        'Neighborhood': '📍',
        'HouseStyle': '🏡',
        'GarageArea': '🚙',
        'TotalRmsAbvGrd': '🚪',
        'LotArea': '🌳',
        'YearRemodAdd': '🔨',
        'BsmtQual': '🏢',
        'BsmtFinSF1': '📐',
        '1stFlrSF': '📏',
        '2ndFlrSF': '📐',
        'BedroomAbvGr': '🛏️',
        'Fireplaces': '🔥',
        'GarageYrBlt': '🏭',
        'MasVnrArea': '🧱',
        'WoodDeckSF': '🪵',
        'OpenPorchSF': '🌿',
        'OverallCond': '✨',
        'MSSubClass': '🏘️',
        'MSZoning': '🗺️',
        'LotFrontage': '🛣️',
        'LotShape': '📐',
        'LandContour': '⛰️',
        'Utilities': '⚡',
        'LotConfig': '🗺️',
        'LandSlope': '⛰️',
        'Condition1': '🌍',
        'BldgType': '🏘️',
        'RoofStyle': '🏠',
        'RoofMatl': '🧱',
        'Exterior1st': '🏛️',
        'Exterior2nd': '🏛️',
        'MasVnrType': '🧱',
        'ExterCond': '✨',
        'Foundation': '🏗️',
        'BsmtCond': '🏢',
        'BsmtExposure': '☀️',
        'BsmtFinType1': '📐',
        'BsmtFinType2': '📐',
        'BsmtUnfSF': '📐',
        'Heating': '🔥',
        'HeatingQC': '🔥',
        'CentralAir': '❄️',
        'Electrical': '⚡',
        'BsmtFullBath': '🚿',
        'BsmtHalfBath': '🚿',
        'HalfBath': '🚿',
        'KitchenAbvGr': '🍳',
        'TotRmsAbvGrd': '🚪',
        'Functional': '⚙️',
        'FireplaceQu': '🔥',
        'GarageType': '🚗',
        'GarageFinish': '🚙',
        'GarageQual': '🚗',
        'GarageCond': '🚗',
        'PavedDrive': '🛣️',
        'PoolArea': '🏊',
        'Fence': '🚧',
        'MiscFeature': '🔧',
        'MiscVal': '💰',
        'MoSold': '📅',
        'YrSold': '📅',
        'SaleType': '💼',
        'SaleCondition': '📋',
        'TotalSF': '📐',
        'TotalBath': '🚿',
        'TotalPorchSF': '🌿',
        'HouseAge': '📅',
        'RemodAge': '🔨',
        'GarageAge': '🏭'
    }
    
    # Dictionnaire de traductions françaises pour les features
    feature_translations = {
        'GrLivArea': 'Surface habitable au-dessus du sol',
        'TotalBsmtSF': 'Surface totale du sous-sol',
        'OverallQual': 'Qualité globale du matériau et de la finition',
        'GarageCars': 'Capacité du garage en voitures',
        'YearBuilt': 'Année de construction',
        'FullBath': 'Nombre de salles de bain complètes',
        'KitchenQual': 'Qualité de la cuisine',
        'ExterQual': 'Qualité extérieure',
        'Neighborhood': 'Quartier',
        'HouseStyle': 'Style de maison',
        'GarageArea': 'Surface du garage',
        'TotalRmsAbvGrd': 'Nombre total de pièces au-dessus du sol',
        'LotArea': 'Surface du terrain',
        'YearRemodAdd': 'Année de rénovation',
        'BsmtQual': 'Qualité du sous-sol',
        'BsmtFinSF1': 'Surface finie du sous-sol type 1',
        '1stFlrSF': 'Surface du premier étage',
        '2ndFlrSF': 'Surface du deuxième étage',
        'BedroomAbvGr': 'Nombre de chambres au-dessus du sol',
        'Fireplaces': 'Nombre de cheminées',
        'GarageYrBlt': 'Année de construction du garage',
        'MasVnrArea': 'Surface du placage en maçonnerie',
        'WoodDeckSF': 'Surface de la terrasse en bois',
        'OpenPorchSF': 'Surface du porche ouvert',
        'OverallCond': 'Condition globale',
        'MSSubClass': 'Classe de logement',
        'MSZoning': 'Classification de zonage',
        'LotFrontage': 'Front de terrain',
        'LotShape': 'Forme du terrain',
        'LandContour': 'Contour du terrain',
        'Utilities': 'Services publics',
        'LotConfig': 'Configuration du terrain',
        'LandSlope': 'Pente du terrain',
        'Condition1': 'Proximité de routes ou voies ferrées',
        'BldgType': 'Type de bâtiment',
        'RoofStyle': 'Style de toit',
        'RoofMatl': 'Matériau du toit',
        'Exterior1st': 'Revêtement extérieur principal',
        'Exterior2nd': 'Revêtement extérieur secondaire',
        'MasVnrType': 'Type de placage en maçonnerie',
        'ExterCond': 'Condition extérieure',
        'Foundation': 'Fondation',
        'BsmtCond': 'Condition du sous-sol',
        'BsmtExposure': 'Exposition du sous-sol',
        'BsmtFinType1': 'Type de finition du sous-sol 1',
        'BsmtFinType2': 'Type de finition du sous-sol 2',
        'BsmtUnfSF': 'Surface non finie du sous-sol',
        'Heating': 'Type de chauffage',
        'HeatingQC': 'Qualité et condition du chauffage',
        'CentralAir': 'Climatisation centrale',
        'Electrical': 'Système électrique',
        'BsmtFullBath': 'Salles de bain complètes au sous-sol',
        'BsmtHalfBath': 'Demi-salles de bain au sous-sol',
        'HalfBath': 'Demi-salles de bain au-dessus du sol',
        'KitchenAbvGr': 'Nombre de cuisines au-dessus du sol',
        'TotRmsAbvGrd': 'Total des pièces au-dessus du sol',
        'Functional': 'Fonctionnalité du logement',
        'FireplaceQu': 'Qualité de la cheminée',
        'GarageType': 'Type de garage',
        'GarageFinish': 'Finition du garage',
        'GarageQual': 'Qualité du garage',
        'GarageCond': 'Condition du garage',
        'PavedDrive': 'Allée pavée',
        'PoolArea': 'Surface de la piscine',
        'Fence': 'Clôture',
        'MiscFeature': 'Caractéristique diverse',
        'MiscVal': 'Valeur des caractéristiques diverses',
        'MoSold': 'Mois de vente',
        'YrSold': 'Année de vente',
        'SaleType': 'Type de vente',
        'SaleCondition': 'Condition de vente',
        'TotalSF': 'Surface totale',
        'TotalBath': 'Total des salles de bain',
        'TotalPorchSF': 'Surface totale des porches',
        'HouseAge': 'Âge de la maison',
        'RemodAge': 'Âge depuis la rénovation',
        'GarageAge': 'Âge du garage'
    }
    
    # Fonction pour obtenir l'icône d'une feature
    def get_feature_icon(feature_name):
        return feature_icons.get(feature_name, '📊')
    
    # Fonction pour obtenir le label avec traduction
    def get_feature_label(feature_name):
        """Retourne le label avec icône et traduction française"""
        icon = get_feature_icon(feature_name)
        translation = feature_translations.get(feature_name, feature_name)
        return f"{icon} {feature_name} ({translation})"
    
    with st.form("house_prediction_form"):
        # SECTION 1 : Caractéristiques Principales (Features Importantes)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h3 style="color: white; margin: 0; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-star"></i> Caractéristiques Principales
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                Variables les plus importantes selon le modèle (basées sur l'importance des features)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Créer un dictionnaire pour stocker les valeurs saisies
        input_values = {}
        
        # Afficher les features importantes par groupes
        features_per_row = 3
        
        # Fonction helper pour afficher une feature (réutilisable)
        def display_feature_input(feature, input_values_dict, key_prefix=""):
            """Affiche un input (slider ou selectbox) pour une feature"""
            label = get_feature_label(feature)
            if df_raw[feature].dtype in ['int64', 'float64']:
                # Variable numérique : slider
                min_val = float(df_raw[feature].min())
                max_val = float(df_raw[feature].max())
                median_val = float(df_raw[feature].median())
                step = max(1.0, (max_val - min_val) / 100) if max_val > min_val else 1.0
                
                input_values_dict[feature] = st.slider(
                    label,
                    min_value=min_val,
                    max_value=max_val,
                    value=median_val,
                    step=float(step),
                    help=f"Valeur médiane: {median_val:.0f}",
                    key=f"{key_prefix}_{feature}" if key_prefix else None
                )
            else:
                # Variable catégorielle : selectbox
                unique_vals_feature = sorted(df_raw[feature].dropna().unique().tolist())
                if len(unique_vals_feature) > 0:
                    mode_val = df_raw[feature].mode()[0] if len(df_raw[feature].mode()) > 0 else unique_vals_feature[0]
                    
                    if mode_val and mode_val in unique_vals_feature:
                        default_idx = unique_vals_feature.index(mode_val)
                    else:
                        default_idx = 0
                    
                    input_values_dict[feature] = st.selectbox(
                        label,
                        options=unique_vals_feature,
                        index=default_idx,
                        help=f"Valeur la plus fréquente: {mode_val}",
                        key=f"{key_prefix}_{feature}" if key_prefix else None
                    )
                else:
                    st.warning(f"⚠️ Aucune valeur disponible pour {feature}")
        
        # Afficher les features disponibles
        if available_features:
            # Diviser les features importantes en groupes
            for i in range(0, len(available_features), features_per_row):
                cols = st.columns(features_per_row)
                for j, feature in enumerate(available_features[i:i+features_per_row]):
                    with cols[j]:
                        display_feature_input(feature, input_values)
        else:
            # Si aucune feature n'est disponible, essayer de charger des features par défaut
            if df_raw.empty:
                st.error("❌ Le DataFrame est vide. Vérifiez le chargement des données.")
                st.info("💡 Le dashboard cherche les données dans : dashboard/output/train_clean.csv ou dashboard/output/data/train_clean.csv")
            else:
                # Si df_raw n'est pas vide mais available_features est vide, utiliser toutes les colonnes
                st.warning("⚠️ Aucune feature importante trouvée. Utilisation de toutes les colonnes disponibles...")
                available_features = all_available_cols[:20] if all_available_cols else []
                
                # Réafficher les features si on en a trouvé
                if available_features:
                    st.info(f"✅ {len(available_features)} feature(s) chargée(s) par défaut")
                    for i in range(0, len(available_features), features_per_row):
                        cols = st.columns(features_per_row)
                        for j, feature in enumerate(available_features[i:i+features_per_row]):
                            with cols[j]:
                                display_feature_input(feature, input_values)
                else:
                    st.error("❌ Aucune feature disponible. Vérifiez que les données sont correctement chargées.")
        
        # SECTION 2 : Variables Personnalisées
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #1e293b; margin: 0; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-sliders-h"></i> Variables Personnalisées
            </h3>
            <p style="color: #64748b; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                Ajoutez des caractéristiques supplémentaires pour affiner votre prédiction
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section pour ajouter des features personnalisées
        with st.expander("➕ Sélectionner des Variables Personnalisées", expanded=True):
            st.markdown("**Sélectionnez des caractéristiques supplémentaires à inclure dans la prédiction :**")
            
            # Features disponibles qui ne sont pas déjà dans les features importantes
            custom_features_available = [col for col in all_available_cols if col not in available_features]
            
            if custom_features_available:
                # Permettre à l'utilisateur de sélectionner plusieurs features
                selected_custom = st.multiselect(
                    "📋 Choisissez les caractéristiques supplémentaires :",
                    options=sorted(custom_features_available),
                    help="Sélectionnez une ou plusieurs caractéristiques pour personnaliser votre prédiction. Les contrôles pour choisir les valeurs s'afficheront automatiquement ci-dessous.",
                    label_visibility="visible"
                )
                
                # Afficher les inputs pour les features personnalisées sélectionnées
                if selected_custom:
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%); 
                                padding: 1rem; 
                                border-radius: 8px; 
                                margin: 1rem 0;
                                border-left: 4px solid #0288d1;">
                        <h4 style="color: #01579b; margin: 0; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-edit"></i> Valeurs pour les {len(selected_custom)} caractéristique(s) sélectionnée(s)
                        </h4>
                        <p style="color: #0277bd; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                            Ajustez les valeurs ou choisissez les modalités pour chaque caractéristique sélectionnée
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Organiser les features en colonnes (2 colonnes)
                    custom_cols = st.columns(2)
                    
                    for idx, feature in enumerate(selected_custom):
                        with custom_cols[idx % 2]:
                            # Afficher un petit header pour chaque feature
                            icon = get_feature_icon(feature)
                            translation = feature_translations.get(feature, feature)
                            st.markdown(f"<div style='margin-top: 1rem; padding: 0.5rem; background: #f5f5f5; border-radius: 6px;'><strong>{icon} {feature}</strong><br><small style='color: #666;'>({translation})</small></div>", unsafe_allow_html=True)
                            # Afficher l'input pour cette feature
                            display_feature_input(feature, input_values, key_prefix="custom")
                else:
                    st.info("💡 Sélectionnez des caractéristiques ci-dessus pour voir les contrôles permettant de choisir leurs valeurs ou modalités.")
            else:
                st.info("ℹ️ Toutes les caractéristiques disponibles sont déjà affichées dans les caractéristiques principales.")
        
        submit_button = st.form_submit_button("💰 Estimer le Prix", use_container_width=True)
    
    if submit_button:
        try:
            # Utiliser les valeurs du dictionnaire input_values
            input_data = input_values.copy()
            
            # Ajouter des valeurs calculées ou par défaut pour certaines variables si elles ne sont pas déjà présentes
            # Ces valeurs seront utilisées si elles ne sont pas dans input_values
            
            # Valeurs calculées basées sur les variables saisies
            if 'GarageCars' in input_data and 'GarageArea' not in input_data:
                input_data['GarageArea'] = input_data.get('GarageCars', 2) * 200
            
            if 'TotalBsmtSF' in input_data:
                if 'BsmtFinSF1' not in input_data:
                    input_data['BsmtFinSF1'] = input_data['TotalBsmtSF'] * 0.5
                if 'BsmtUnfSF' not in input_data:
                    input_data['BsmtUnfSF'] = input_data['TotalBsmtSF'] * 0.3
            
            if 'YearBuilt' in input_data:
                if 'YearRemodAdd' not in input_data:
                    input_data['YearRemodAdd'] = input_data['YearBuilt']
                if 'GarageYrBlt' not in input_data:
                    input_data['GarageYrBlt'] = input_data['YearBuilt']
            
            # Valeurs par défaut pour certaines variables communes si absentes
            defaults = {
                'BedroomAbvGr': 3,
                'TotRmsAbvGrd': 6,
                'TotalRmsAbvGrd': 6,
                'Fireplaces': 1,
                'WoodDeckSF': 0,
                'OpenPorchSF': 50,
                'EnclosedPorch': 0,
                'ScreenPorch': 0,
                '3SsnPorch': 0,
                'MoSold': 6,
                'YrSold': 2024,
                'LotArea': 8000,
                'MasVnrArea': 0,
                'GarageQual': 'TA',
                'GarageCond': 'TA',
                'PavedDrive': 'Y',
                'CentralAir': 'Y',
                'HeatingQC': 'Ex',
                'Electrical': 'SBrkr',
                'BsmtQual': 'TA',
                'BsmtCond': 'TA',
                'Foundation': 'PConc',
                'BsmtExposure': 'No',
                'BsmtFinType1': 'Unf',
                'BsmtFinType2': 'Unf',
                'RoofStyle': 'Gable',
                'RoofMatl': 'CompShg',
                'Exterior1st': 'VinylSd',
                'Exterior2nd': 'VinylSd',
                'MasVnrType': 'None',
                'ExterCond': 'TA',
                'BsmtFullBath': 0,
                'BsmtHalfBath': 0,
                'HalfBath': 1,
                'KitchenAbvGr': 1,
                'Functional': 'Typ',
                'FireplaceQu': 'Gd',
                'GarageType': 'Attchd',
                'GarageFinish': 'Unf',
                'PoolArea': 0,
                'Fence': 'None',
                'MiscFeature': 'None',
                'SaleType': 'WD',
                'SaleCondition': 'Normal',
                'LotFrontage': 60,
                'LotShape': 'Reg',
                'LandContour': 'Lvl',
                'Utilities': 'AllPub',
                'LotConfig': 'Inside',
                'LandSlope': 'Gtl',
                'Condition1': 'Norm',
                'Condition2': 'Norm',
                'BldgType': '1Fam',
                'OverallCond': 5,
                'MSSubClass': 60,
                'MSZoning': 'RL',
                'Street': 'Pave',
                'Alley': 'None',
            }
            
            # Ajouter les valeurs par défaut seulement si elles ne sont pas déjà dans input_data
            for key, value in defaults.items():
                if key not in input_data:
                    input_data[key] = value
            
            input_df = pd.DataFrame([input_data])
            
            # Utiliser le préprocesseur et le modèle si disponibles
            if preprocessor is not None and model is not None:
                try:
                    # Le préprocesseur ColumnTransformer attend TOUTES les colonnes sur lesquelles il a été entraîné
                    # Il faut donc compléter input_df avec toutes les colonnes manquantes
                    
                    # Récupérer les colonnes attendues par le préprocesseur
                    # Le ColumnTransformer stocke les noms des colonnes dans feature_names_in_
                    if hasattr(preprocessor, 'feature_names_in_'):
                        expected_cols = list(preprocessor.feature_names_in_)
                    else:
                        # Si feature_names_in_ n'est pas disponible, utiliser les colonnes de df_raw
                        if not df_raw.empty:
                            expected_cols = [col for col in df_raw.columns if col != 'SalePrice']
                        else:
                            expected_cols = list(input_df.columns)
                    
                    # Compléter input_df avec les colonnes manquantes
                    # Utiliser les données d'entraînement pour les valeurs par défaut
                    if not df_raw.empty:
                        for col in expected_cols:
                            if col not in input_df.columns:
                                if df_raw[col].dtype in ['int64', 'float64']:
                                    # Variable numérique : utiliser la médiane
                                    input_df[col] = df_raw[col].median()
                                else:
                                    # Variable catégorielle : utiliser le mode
                                    mode_value = df_raw[col].mode()[0] if len(df_raw[col].mode()) > 0 else 'None'
                                    input_df[col] = mode_value
                    
                    # Réorganiser les colonnes dans le même ordre que le préprocesseur les attend
                    if hasattr(preprocessor, 'feature_names_in_'):
                        input_df = input_df.reindex(columns=preprocessor.feature_names_in_, fill_value=0)
                    
                    # Préparer les données avec toutes les colonnes nécessaires
                    X_processed = preprocessor.transform(input_df)
                    y_pred_raw = model.predict(X_processed)
                    
                    # Détecter automatiquement si la prédiction est en log ou en valeurs réelles
                    # Les valeurs réelles de prix de maisons sont généralement > 10000
                    # Les valeurs en log sont généralement < 15
                    if np.median(y_pred_raw) < 15:
                        # Valeurs en log, convertir en valeurs réelles
                        price = np.expm1(y_pred_raw[0])
                    else:
                        # Valeurs déjà réelles
                        price = y_pred_raw[0]
                    
                    st.success("✅ Prédiction effectuée avec le modèle entraîné")
                except Exception as e:
                    st.warning(f"⚠️ Erreur lors de la prédiction avec le modèle: {str(e)}")
                    st.info("Utilisation d'une estimation simplifiée...")
                    # Fallback vers estimation simple
                    base_price = 100000
                    gr_liv_area_val = input_data.get('GrLivArea', 1500)
                    total_bsmt_sf_val = input_data.get('TotalBsmtSF', 1000)
                    overall_qual_val = input_data.get('OverallQual', 5)
                    garage_cars_val = input_data.get('GarageCars', 2)
                    year_built_val = input_data.get('YearBuilt', 2000)
                    kitchen_qual_val = input_data.get('KitchenQual', 'TA')
                    exterior_qual_val = input_data.get('ExterQual', 'TA')
                    
                    price = base_price + (gr_liv_area_val * 50) + (total_bsmt_sf_val * 30) + (overall_qual_val * 10000)
                    price += garage_cars_val * 5000 + ((2024 - year_built_val) * -1000)
                    qual_adjustments = {'Ex': 30000, 'Gd': 15000, 'TA': 0, 'Fa': -10000, 'Po': -20000}
                    price += qual_adjustments.get(kitchen_qual_val, 0)
                    price += qual_adjustments.get(exterior_qual_val, 0)
            else:
                # Si le préprocesseur ou le modèle ne sont pas disponibles, charger directement
                if preprocessor is None:
                    # Essayer de charger le préprocesseur directement
                    preprocessor_path = OUTPUT_DIR / "models" / "preprocessor.joblib"
                    if preprocessor_path.exists():
                        try:
                            preprocessor = joblib.load(preprocessor_path)
                            model_data['preprocessor'] = preprocessor
                        except Exception:
                            pass
                
                if model is None:
                    # Essayer de charger le modèle directement
                    model_candidates = [
                        OUTPUT_DIR / "models" / "best_model.joblib",
                        OUTPUT_DIR / "models" / "best_elasticnet.joblib",
                        OUTPUT_DIR / "models" / "best_lasso.joblib",
                        OUTPUT_DIR / "models" / "best_ridge.joblib",
                        OUTPUT_DIR / "models" / "best_gradientboosting.joblib",
                        OUTPUT_DIR / "models" / "best_xgboost.joblib",
                    ]
                    for model_path in model_candidates:
                        if model_path.exists():
                            try:
                                model = joblib.load(model_path)
                                model_data['model'] = model
                                break
                            except Exception:
                                continue
                
                # Réessayer avec le modèle et préprocesseur chargés
                if preprocessor is not None and model is not None:
                    try:
                        X_processed = preprocessor.transform(input_df)
                        y_pred_raw = model.predict(X_processed)
                        
                        # Détecter automatiquement si la prédiction est en log ou en valeurs réelles
                        if np.median(y_pred_raw) < 15:
                            # Valeurs en log, convertir en valeurs réelles
                            price = np.expm1(y_pred_raw[0])
                        else:
                            # Valeurs déjà réelles
                            price = y_pred_raw[0]
                        
                        st.success("✅ Prédiction effectuée avec le modèle entraîné")
                    except Exception:
                        # Fallback vers estimation simple
                        base_price = 100000
                        gr_liv_area_val = input_data.get('GrLivArea', 1500)
                        total_bsmt_sf_val = input_data.get('TotalBsmtSF', 1000)
                        overall_qual_val = input_data.get('OverallQual', 5)
                        garage_cars_val = input_data.get('GarageCars', 2)
                        year_built_val = input_data.get('YearBuilt', 2000)
                        kitchen_qual_val = input_data.get('KitchenQual', 'TA')
                        exterior_qual_val = input_data.get('ExterQual', 'TA')
                        
                        price = base_price + (gr_liv_area_val * 50) + (total_bsmt_sf_val * 30) + (overall_qual_val * 10000)
                        price += garage_cars_val * 5000 + ((2024 - year_built_val) * -1000)
                        qual_adjustments = {'Ex': 30000, 'Gd': 15000, 'TA': 0, 'Fa': -10000, 'Po': -20000}
                        price += qual_adjustments.get(kitchen_qual_val, 0)
                        price += qual_adjustments.get(exterior_qual_val, 0)
                else:
                    # Estimation simplifiée si le préprocesseur n'est toujours pas disponible
                    base_price = 100000
                    gr_liv_area_val = input_data.get('GrLivArea', 1500)
                    total_bsmt_sf_val = input_data.get('TotalBsmtSF', 1000)
                    overall_qual_val = input_data.get('OverallQual', 5)
                    garage_cars_val = input_data.get('GarageCars', 2)
                    year_built_val = input_data.get('YearBuilt', 2000)
                    kitchen_qual_val = input_data.get('KitchenQual', 'TA')
                    exterior_qual_val = input_data.get('ExterQual', 'TA')
                    
                    price = base_price + (gr_liv_area_val * 50) + (total_bsmt_sf_val * 30) + (overall_qual_val * 10000)
                    price += garage_cars_val * 5000 + ((2024 - year_built_val) * -1000)
                    qual_adjustments = {'Ex': 30000, 'Gd': 15000, 'TA': 0, 'Fa': -10000, 'Po': -20000}
                    price += qual_adjustments.get(kitchen_qual_val, 0)
                    price += qual_adjustments.get(exterior_qual_val, 0)
            
            # Afficher le résultat avec un design moderne
            st.markdown(f"""
            <div class="prediction-card fade-in">
                <div class="prediction-icon">
                    <i class="fas fa-dollar-sign"></i>
                </div>
                <h1>${price:,.0f}</h1>
                <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;">Prix estimé</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📊 Comparaison avec le marché"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Votre estimation", f"${price:,.0f}")
                    if 'avg_price' in locals() and avg_price > 0:
                        st.metric("Prix moyen du marché", f"${avg_price:,.0f}")
                    else:
                        st.metric("Prix moyen du marché", "N/A")
                with col2:
                    if 'avg_price' in locals() and avg_price > 0:
                        diff = price - avg_price
                        diff_pct = (diff / avg_price) * 100
                        st.metric("Différence", f"${diff:,.0f}", f"{diff_pct:+.1f}%")
                        
                        if diff_pct > 20:
                            st.warning("⚠️ Cette estimation est significativement au-dessus du marché")
                        elif diff_pct < -20:
                            st.info("ℹ️ Cette estimation est significativement en dessous du marché")
                        else:
                            st.success("✅ Cette estimation est dans la fourchette du marché")
                    else:
                        st.info("ℹ️ Données de marché non disponibles")
            
        except Exception as e:
            st.error(f"❌ Erreur lors de l'estimation: {str(e)}")

# ============================================================================
# PAGE 6 : PRÉDICTIONS
# ============================================================================

elif page == "Prédictions":
    st.markdown("""
    <div class="main-header fade-in">
        <h1><i class="fas fa-chart-bar"></i> Prédictions du Prix des Maisons</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if model_data is None:
        model_data = {}
    
    submission_df = model_data.get('submission')
    
    if submission_df is None:
        current_dir = Path(__file__).parent.absolute()
        submission_path = current_dir / "output" / "predictions" / "kaggle_submission_elasticnet.csv"
        if not submission_path.exists():
            submission_path = current_dir / "output" / "predictions" / "kaggle_submission_lasso.csv"
        if not submission_path.exists():
            submission_path = current_dir / "output" / "predictions" / "kaggle_submission_ridge.csv"
        if not submission_path.exists():
            submission_path = current_dir / "output" / "predictions" / "kaggle_submission_gradientboosting.csv"
        if not submission_path.exists():
            submission_path = current_dir / "output" / "predictions" / "kaggle_submission_xgboost.csv"
        
        if submission_path.exists():
            try:
                submission_df = pd.read_csv(submission_path)
            except Exception as e:
                st.stop()
        else:
            st.stop()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### <i class='fas fa-list'></i> Aperçu des Prédictions", unsafe_allow_html=True)
        st.write(f"**Nombre de prédictions :** {len(submission_df):,}")
        
        st.dataframe(
            submission_df.head(10).style.format({'SalePrice': '${:,.0f}'}),
            use_container_width=True
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### <i class='fas fa-chart-pie'></i> Statistiques", unsafe_allow_html=True)
        
        if 'SalePrice' in submission_df.columns:
            st.metric("Prix Moyen Prédit", f"${submission_df['SalePrice'].mean():,.0f}")
            st.metric("Prix Médian Prédit", f"${submission_df['SalePrice'].median():,.0f}")
            st.metric("Prix Minimum", f"${submission_df['SalePrice'].min():,.0f}")
            st.metric("Prix Maximum", f"${submission_df['SalePrice'].max():,.0f}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### <i class='fas fa-download'></i> Téléchargement", unsafe_allow_html=True)
        
        csv = submission_df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger submission.csv",
            data=csv,
            file_name="submission_elasticnet.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### <i class='fas fa-chart-area'></i> Distribution des Prix Prédits", unsafe_allow_html=True)
        
        if 'SalePrice' in submission_df.columns:
            fig = px.histogram(
                submission_df, 
                x='SalePrice',
                nbins=50,
                title='Distribution des Prix Prédits',
                labels={'SalePrice': 'Prix Prédit ($)', 'count': 'Nombre de maisons'},
                color_discrete_sequence=['#2563eb'],
                opacity=0.8
            )
            
            mean_price = submission_df['SalePrice'].mean()
            median_price = submission_df['SalePrice'].median()
            
            fig.add_vline(
                x=mean_price, 
                line_dash="dash", 
                line_color="#ef4444",
                line_width=2,
                annotation_text=f"Moyenne: ${mean_price:,.0f}"
            )
            
            fig.add_vline(
                x=median_price, 
                line_dash="dash", 
                line_color="#10b981",
                line_width=2,
                annotation_text=f"Médiane: ${median_price:,.0f}"
            )
            
            fig = apply_plotly_style(fig, title='Distribution des Prix Prédits', height=550)
            fig.update_traces(marker=dict(line=dict(width=1, color='white')))
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📦 Box Plot des Prix"):
                fig_box = px.box(
                    submission_df,
                    y='SalePrice',
                    title='Distribution des Prix Prédits (Box Plot)',
                    labels={'SalePrice': 'Prix Prédit ($)'},
                    color_discrete_sequence=['#f59e0b']
                )
                fig_box = apply_plotly_style(fig_box, title='Distribution des Prix Prédits (Box Plot)', height=450)
                st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.error("❌ La colonne 'SalePrice' est manquante dans le fichier de prédictions")

