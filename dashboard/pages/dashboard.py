"""
Page Dashboard pour visualiser la base de données train.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, dash_table
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ajouter la racine au path pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dashboard.utils.data_loader import load_train_data


def normalize_id(text):
    """
    Normaliser un texte pour créer un ID valide sans accents.
    
    Args:
        text: Texte à normaliser
        
    Returns:
        str: ID normalisé
    """
    import unicodedata
    # Normaliser les caractères Unicode (NFD = décomposition)
    text = unicodedata.normalize('NFD', text.lower())
    # Supprimer les accents
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Remplacer les espaces par des tirets
    text = text.replace(' ', '-')
    # Supprimer les caractères non alphanumériques sauf tirets
    text = ''.join(char if char.isalnum() or char == '-' else '' for char in text)
    return text


def create_stat_card(title, value, icon, color="#2E86AB"):
    """
    Créer une carte de statistique élégante.
    
    Args:
        title: Titre de la carte
        value: Valeur à afficher
        icon: Classe d'icône Font Awesome
        color: Couleur principale
        
    Returns:
        dbc.Card: Carte de statistique
    """
    stat_id = f"stat-{normalize_id(title)}"
    
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className=f"{icon} fa-3x", style={"color": color}),
                        ],
                        className="text-center mb-3"
                    ),
                    html.H3(
                        value,
                        id=stat_id,
                        className="text-center mb-2",
                        style={"color": color, "fontWeight": "700", "fontSize": "2rem"}
                    ),
                    html.P(
                        title,
                        className="text-center mb-0",
                        style={"color": "#6c757d", "fontSize": "0.9rem", "textTransform": "uppercase", "letterSpacing": "1px"}
                    )
                ],
                className="p-4"
            )
        ],
        className="shadow-sm h-100",
        style={
            "border": "none",
            "borderRadius": "15px",
            "transition": "all 0.3s ease",
            "borderTop": f"4px solid {color}"
        }
    )


def create_price_distribution_chart(df):
    """
    Créer un graphique de distribution des prix.
    
    Args:
        df: DataFrame avec colonne SalePrice
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or 'SalePrice' not in df.columns:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Distribution des Prix', 'Distribution Log des Prix'),
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5]
    )
    
    # Distribution normale
    fig.add_trace(
        go.Histogram(
            x=df['SalePrice'],
            nbinsx=50,
            marker_color='#2E86AB',
            name='Prix',
            hovertemplate='Prix: $%{x:,.0f}<br>Nombre: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Distribution log
    log_prices = np.log1p(df['SalePrice'])
    fig.add_trace(
        go.Histogram(
            x=log_prices,
            nbinsx=50,
            marker_color='#A23B72',
            name='Log Prix',
            hovertemplate='Log Prix: %{x:.2f}<br>Nombre: %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Prix ($)", row=1, col=1)
    fig.update_xaxes(title_text="Log(Prix)", row=2, col=1)
    fig.update_yaxes(title_text="Fréquence", row=1, col=1)
    fig.update_yaxes(title_text="Fréquence", row=2, col=1)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Segoe UI", size=12),
        title={
            'text': 'Analyse de la Distribution des Prix',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2E86AB'}
        }
    )
    
    return fig


def create_correlation_heatmap(df):
    """
    Créer une heatmap de corrélation pour les variables numériques principales.
    
    Args:
        df: DataFrame
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0:
        return go.Figure()
    
    # Sélectionner les colonnes numériques principales
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Limiter aux colonnes les plus importantes (top 15 + SalePrice)
    if 'SalePrice' in numeric_cols:
        numeric_cols.remove('SalePrice')
    
    # Prendre les top 15 corrélées avec SalePrice si disponible
    if 'SalePrice' in df.columns:
        try:
            correlations = df[numeric_cols + ['SalePrice']].corr()['SalePrice'].abs().sort_values(ascending=False)
            top_cols = correlations.head(15).index.tolist()
            if 'SalePrice' not in top_cols:
                top_cols.append('SalePrice')
        except:
            top_cols = numeric_cols[:15] if len(numeric_cols) > 15 else numeric_cols
            if 'SalePrice' in df.columns and 'SalePrice' not in top_cols:
                top_cols.append('SalePrice')
    else:
        top_cols = numeric_cols[:15] if len(numeric_cols) > 15 else numeric_cols
    
    if len(top_cols) == 0:
        return go.Figure()
    
    try:
        corr_matrix = df[top_cols].corr()
    except:
        return go.Figure()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='<b>%{y} vs %{x}</b><br>Corrélation: %{z:.2f}<extra></extra>',
        colorbar=dict(title="Corrélation")
    ))
    
    fig.update_layout(
        title={
            'text': 'Matrice de Corrélation des Variables Numériques',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E86AB'}
        },
        height=700,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(side="bottom"),
        font=dict(family="Segoe UI", size=11)
    )
    
    return fig


def create_feature_vs_price_chart(df, feature_col):
    """
    Créer un graphique montrant la relation entre une feature et le prix.
    
    Args:
        df: DataFrame
        feature_col: Nom de la colonne feature
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0:
        return go.Figure()
    
    if feature_col is None or feature_col not in df.columns:
        return go.Figure()
    
    if 'SalePrice' not in df.columns:
        return go.Figure()
    
    try:
        # Filtrer les valeurs nulles
        df_clean = df[[feature_col, 'SalePrice']].dropna()
        
        if len(df_clean) == 0:
            return go.Figure()
        
        # Vérifier si la colonne est numérique
        if df_clean[feature_col].dtype in ['int64', 'float64']:
            fig = px.scatter(
                df_clean,
                x=feature_col,
                y='SalePrice',
                trendline="ols",
                color_discrete_sequence=['#2E86AB'],
                labels={feature_col: feature_col, 'SalePrice': 'Prix de Vente ($)'},
                hover_data=[feature_col, 'SalePrice']
            )
        else:
            # Si c'est catégoriel, créer un box plot
            fig = px.box(
                df_clean,
                x=feature_col,
                y='SalePrice',
                labels={feature_col: feature_col, 'SalePrice': 'Prix de Vente ($)'}
            )
        
        fig.update_traces(
            marker=dict(size=5, opacity=0.6) if df_clean[feature_col].dtype in ['int64', 'float64'] else {},
            hovertemplate=f'<b>{feature_col}</b>: %{{x}}<br>Prix: $%{{y:,.0f}}<extra></extra>'
        )
        
        fig.update_layout(
            title={
                'text': f'Relation entre {feature_col} et Prix de Vente',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2E86AB'}
            },
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=13),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_feature_vs_price_chart: {e}")
        import traceback
        traceback.print_exc()
        return go.Figure()


def create_top_correlations_chart(df):
    """
    Créer un graphique des top corrélations avec le prix.
    
    Args:
        df: DataFrame
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or 'SalePrice' not in df.columns:
        return go.Figure()
    
    try:
        # Sélectionner les colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if 'SalePrice' not in numeric_cols or len(numeric_cols) < 2:
            return go.Figure()
        
        # Calculer les corrélations
        correlations = df[numeric_cols].corr()['SalePrice'].abs().sort_values(ascending=False)
        correlations = correlations[correlations.index != 'SalePrice'].head(10)
        
        if len(correlations) == 0:
            return go.Figure()
        
        # Créer le graphique en barres horizontales
        fig = go.Figure()
        
        colors = ['#2E86AB' if x > 0.5 else '#A23B72' for x in correlations.values]
        
        fig.add_trace(go.Bar(
            x=correlations.values,
            y=correlations.index,
            orientation='h',
            marker_color=colors,
            text=[f"{x:.3f}" for x in correlations.values],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Corrélation: %{x:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Top 10 Variables les Plus Corrélées avec le Prix',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2E86AB'}
            },
            xaxis_title='Corrélation Absolue',
            yaxis_title='Variable',
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=13),
            margin=dict(l=100, r=50, t=80, b=50)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_top_correlations_chart: {e}")
        return go.Figure()


def create_categorical_analysis_chart(df, cat_col):
    """
    Créer un graphique d'analyse catégorielle avec box plot.
    
    Args:
        df: DataFrame
        cat_col: Nom de la colonne catégorielle
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or cat_col is None or cat_col not in df.columns or 'SalePrice' not in df.columns:
        return go.Figure()
    
    try:
        # Créer un box plot pour voir la distribution
        df_clean = df[[cat_col, 'SalePrice']].dropna()
        if len(df_clean) == 0:
            return go.Figure()
        
        # Limiter aux top 15 catégories par nombre d'observations
        top_cats = df_clean[cat_col].value_counts().head(15).index.tolist()
        df_clean = df_clean[df_clean[cat_col].isin(top_cats)]
        
        fig = px.box(
            df_clean,
            x=cat_col,
            y='SalePrice',
            title=f'Distribution des Prix par {cat_col}',
            labels={'SalePrice': 'Prix de Vente ($)', cat_col: cat_col}
        )
        
        fig.update_traces(
            marker_color='#2E86AB',
            line_color='#1E5F7A'
        )
        
        fig.update_layout(
            title={
                'text': f'Distribution des Prix par {cat_col}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2E86AB'}
            },
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=12),
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_categorical_analysis_chart: {e}")
        return go.Figure()


def create_temporal_analysis_chart(df):
    """
    Créer un graphique d'analyse temporelle (YearBuilt, YrSold).
    
    Args:
        df: DataFrame
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or 'SalePrice' not in df.columns:
        return go.Figure()
    
    try:
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Prix par Année de Construction', 'Prix par Année de Vente'),
            vertical_spacing=0.15
        )
        
        # YearBuilt vs SalePrice
        if 'YearBuilt' in df.columns:
            df_year = df[['YearBuilt', 'SalePrice']].dropna()
            if len(df_year) > 0:
                year_stats = df_year.groupby('YearBuilt')['SalePrice'].agg(['mean', 'count']).reset_index()
                year_stats = year_stats[year_stats['count'] >= 3]  # Au moins 3 observations
                
                fig.add_trace(
                    go.Scatter(
                        x=year_stats['YearBuilt'],
                        y=year_stats['mean'],
                        mode='lines+markers',
                        name='Prix Moyen',
                        marker=dict(size=year_stats['count']/5, color='#2E86AB'),
                        hovertemplate='Année: %{x}<br>Prix moyen: $%{y:,.0f}<br>Nombre: %{customdata}<extra></extra>',
                        customdata=year_stats['count'].tolist()
                    ),
                    row=1, col=1
                )
        
        # YrSold vs SalePrice
        if 'YrSold' in df.columns:
            df_sold = df[['YrSold', 'SalePrice']].dropna()
            if len(df_sold) > 0:
                sold_stats = df_sold.groupby('YrSold')['SalePrice'].agg(['mean', 'count']).reset_index()
                
                fig.add_trace(
                    go.Bar(
                        x=sold_stats['YrSold'],
                        y=sold_stats['mean'],
                        name='Prix Moyen',
                        marker_color='#A23B72',
                        hovertemplate='Année: %{x}<br>Prix moyen: $%{y:,.0f}<br>Nombre: %{customdata}<extra></extra>',
                        customdata=sold_stats['count'].tolist()
                    ),
                    row=2, col=1
                )
        
        fig.update_xaxes(title_text="Année de Construction", row=1, col=1)
        fig.update_xaxes(title_text="Année de Vente", row=2, col=1)
        fig.update_yaxes(title_text="Prix Moyen ($)", row=1, col=1)
        fig.update_yaxes(title_text="Prix Moyen ($)", row=2, col=1)
        
        fig.update_layout(
            height=700,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=13),
            title={
                'text': 'Analyse Temporelle des Prix',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2E86AB'}
            },
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_temporal_analysis_chart: {e}")
        return go.Figure()


def create_neighborhood_analysis_chart(df):
    """
    Créer un graphique d'analyse par quartier (Neighborhood).
    
    Args:
        df: DataFrame
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or 'Neighborhood' not in df.columns or 'SalePrice' not in df.columns:
        return go.Figure()
    
    try:
        df_clean = df[['Neighborhood', 'SalePrice']].dropna()
        if len(df_clean) == 0:
            return go.Figure()
        
        # Calculer les statistiques par quartier
        neighborhood_stats = df_clean.groupby('Neighborhood')['SalePrice'].agg(['mean', 'count', 'median']).reset_index()
        neighborhood_stats = neighborhood_stats.sort_values('mean', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=neighborhood_stats['Neighborhood'],
            y=neighborhood_stats['mean'],
            marker_color='#2E86AB',
            text=[f"${x:,.0f}" for x in neighborhood_stats['mean']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Prix moyen: $%{y:,.0f}<br>Prix médian: $%{customdata[0]:,.0f}<br>Nombre: %{customdata[1]}<extra></extra>',
            customdata=neighborhood_stats[['median', 'count']].values
        ))
        
        fig.update_layout(
            title={
                'text': 'Prix Moyen par Quartier (Neighborhood)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2E86AB'}
            },
            xaxis_title='Quartier',
            yaxis_title='Prix Moyen ($)',
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=12),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            margin=dict(l=50, r=50, t=80, b=120)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_neighborhood_analysis_chart: {e}")
        return go.Figure()


def create_cross_analysis_chart(df, x_col, y_col, color_col=None):
    """
    Créer un graphique de croisement entre variables.
    
    Args:
        df: DataFrame
        x_col: Colonne X
        y_col: Colonne Y (généralement SalePrice)
        color_col: Colonne pour la couleur (optionnel)
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or x_col not in df.columns or y_col not in df.columns:
        return go.Figure()
    
    try:
        if color_col and color_col in df.columns:
            df_clean = df[[x_col, y_col, color_col]].dropna()
            fig = px.scatter(
                df_clean,
                x=x_col,
                y=y_col,
                color=color_col,
                size_max=10,
                hover_data=[x_col, y_col, color_col],
                labels={x_col: x_col, y_col: y_col, color_col: color_col}
            )
        else:
            df_clean = df[[x_col, y_col]].dropna()
            fig = px.scatter(
                df_clean,
                x=x_col,
                y=y_col,
                trendline="ols",
                color_discrete_sequence=['#2E86AB'],
                labels={x_col: x_col, y_col: y_col}
            )
        
        fig.update_traces(
            marker=dict(size=5, opacity=0.6)
        )
        
        fig.update_layout(
            title={
                'text': f'Croisement: {x_col} vs {y_col}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2E86AB'}
            },
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=13),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_cross_analysis_chart: {e}")
        return go.Figure()


def create_quality_analysis_chart(df):
    """
    Créer un graphique d'analyse par qualité (OverallQual, OverallCond).
    
    Args:
        df: DataFrame
        
    Returns:
        dict: Figure Plotly
    """
    if df is None or len(df) == 0 or 'SalePrice' not in df.columns:
        return go.Figure()
    
    try:
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Prix par Qualité Globale (OverallQual)', 'Prix par Condition Globale (OverallCond)'),
            horizontal_spacing=0.15
        )
        
        # OverallQual
        if 'OverallQual' in df.columns:
            df_qual = df[['OverallQual', 'SalePrice']].dropna()
            if len(df_qual) > 0:
                qual_stats = df_qual.groupby('OverallQual')['SalePrice'].agg(['mean', 'median', 'count']).reset_index()
                
                fig.add_trace(
                    go.Bar(
                        x=qual_stats['OverallQual'],
                        y=qual_stats['mean'],
                        name='Prix Moyen',
                        marker_color='#2E86AB',
                        hovertemplate='Qualité: %{x}<br>Prix moyen: $%{y:,.0f}<br>Prix médian: $%{customdata[0]:,.0f}<br>Nombre: %{customdata[1]}<extra></extra>',
                        customdata=qual_stats[['median', 'count']].values
                    ),
                    row=1, col=1
                )
        
        # OverallCond
        if 'OverallCond' in df.columns:
            df_cond = df[['OverallCond', 'SalePrice']].dropna()
            if len(df_cond) > 0:
                cond_stats = df_cond.groupby('OverallCond')['SalePrice'].agg(['mean', 'median', 'count']).reset_index()
                
                fig.add_trace(
                    go.Bar(
                        x=cond_stats['OverallCond'],
                        y=cond_stats['mean'],
                        name='Prix Moyen',
                        marker_color='#A23B72',
                        hovertemplate='Condition: %{x}<br>Prix moyen: $%{y:,.0f}<br>Prix médian: $%{customdata[0]:,.0f}<br>Nombre: %{customdata[1]}<extra></extra>',
                        customdata=cond_stats[['median', 'count']].values
                    ),
                    row=1, col=2
                )
        
        fig.update_xaxes(title_text="Qualité Globale", row=1, col=1)
        fig.update_xaxes(title_text="Condition Globale", row=1, col=2)
        fig.update_yaxes(title_text="Prix Moyen ($)", row=1, col=1)
        fig.update_yaxes(title_text="Prix Moyen ($)", row=1, col=2)
        
        fig.update_layout(
            height=500,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI", size=13),
            title={
                'text': 'Analyse par Qualité et Condition',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2E86AB'}
            },
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    except Exception as e:
        print(f"Erreur dans create_quality_analysis_chart: {e}")
        return go.Figure()


def create_data_table(df, max_rows=100):
    """
    Créer un tableau interactif avec les données.
    
    Args:
        df: DataFrame
        max_rows: Nombre maximum de lignes à afficher
        
    Returns:
        html.Div: Tableau Dash DataTable
    """
    if df is None or len(df) == 0:
        return html.Div("Aucune donnée disponible", className="text-center p-4")
    
    # Limiter le nombre de colonnes pour l'affichage
    display_cols = df.columns.tolist()[:20]  # Afficher les 20 premières colonnes
    df_display = df[display_cols].head(max_rows)
    
    return html.Div(
        [
            html.Div(
                [
                    html.I(className="fas fa-info-circle me-2", style={"color": "#2E86AB"}),
                    html.Span(
                        f"Aperçu: {len(df_display)} lignes sur {len(df)} totales | Les données sont filtrées selon les critères sélectionnés",
                        style={"fontSize": "0.9rem", "color": "#6c757d"}
                    )
                ],
                className="mb-3 p-2",
                style={"backgroundColor": "#f8f9fa", "borderRadius": "5px"}
            ),
            dash_table.DataTable(
                data=df_display.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df_display.columns],
                page_size=20,
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '10px',
                    'overflowY': 'auto',
                    'minHeight': '500px',
                    'width': '100%'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Segoe UI',
                    'fontSize': '13px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '120px'
                },
                style_header={
                    'backgroundColor': '#2E86AB',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid #1E5F7A',
                    'padding': '15px',
                    'fontSize': '14px'
                },
                style_data={
                    'border': '1px solid #e0e0e0',
                    'padding': '12px'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    },
                    {
                        'if': {'row_index': 'even'},
                        'backgroundColor': 'white'
                    },
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': 'rgba(46, 134, 171, 0.1)',
                        'border': '1px solid #2E86AB'
                    }
                ],
                filter_action="native",
                sort_action="native",
                export_format="csv",
                export_headers="display",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df_display.to_dict('records')
                ],
                tooltip_duration=None,
                fixed_rows={'headers': True}
            )
        ],
        className="mb-4"
    )


def create_dashboard_page():
    """
    Créer la page Dashboard principale avec visualisations de la base de données train.
    
    Returns:
        dbc.Container: Page Dashboard complète
    """
    try:
        train_df = load_train_data()
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        train_df = None
    
    if train_df is None or len(train_df) == 0:
        return dbc.Container(
            [
                dbc.Alert(
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        "Impossible de charger les données train. Vérifiez que le fichier existe."
                    ],
                    color="warning",
                    className="mt-4"
                )
            ]
        )
    
    try:
        # Identifier les colonnes numériques et catégorielles
        numeric_cols = train_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = train_df.select_dtypes(include=['object']).columns.tolist()
        
        # Top features corrélées avec SalePrice
        top_features = []
        if 'SalePrice' in numeric_cols and len(numeric_cols) > 1:
            try:
                correlations = train_df[numeric_cols].corr()['SalePrice'].abs().sort_values(ascending=False)
                top_features = correlations.head(10).index.tolist()
                top_features = [f for f in top_features if f != 'SalePrice']
            except Exception as e:
                print(f"Erreur lors du calcul des corrélations: {e}")
                top_features = []
        
        # Valeurs par défaut pour les dropdowns
        default_numeric_feature = None
        if top_features and len(top_features) > 0:
            default_numeric_feature = top_features[0]
        elif numeric_cols:
            numeric_without_target = [col for col in numeric_cols if col != 'SalePrice']
            if numeric_without_target:
                default_numeric_feature = numeric_without_target[0]
        
        default_cat_feature = categorical_cols[0] if categorical_cols and len(categorical_cols) > 0 else None
        
        # Valeurs min/max pour les filtres de prix
        min_price_val = float(train_df['SalePrice'].min()) if 'SalePrice' in train_df.columns else 0
        max_price_val = float(train_df['SalePrice'].max()) if 'SalePrice' in train_df.columns else 1000000
        
    except Exception as e:
        print(f"Erreur lors de la préparation des données: {e}")
        import traceback
        traceback.print_exc()
        return dbc.Container(
            [
                dbc.Alert(
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Erreur lors de la création de la page: {str(e)}"
                    ],
                    color="danger",
                    className="mt-4"
                )
            ]
        )
    
    return dbc.Container(
        [
            # En-tête de la page
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(className="fas fa-chart-line me-3", style={"color": "#2E86AB"}),
                                    "Dashboard - Base de Données Train"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB", "fontWeight": "700"}
                            ),
                            html.P(
                                "Visualisation interactive et analyse de la base de données d'entraînement",
                                className="text-muted mb-4",
                                style={"fontSize": "1.1rem"}
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-4"
            ),
            
            # Zone de navigation avec filtres regroupés
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-sliders-h me-2"),
                                            "Filtres et Navigation"
                                        ],
                                        style={"backgroundColor": "#2E86AB", "color": "white", "fontWeight": "600", "fontSize": "1.1rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Accordion(
                                                [
                                                    dbc.AccordionItem(
                                                        [
                                                            html.Label("Prix Minimum ($):", className="mb-2", style={"fontWeight": "600"}),
                                                            dcc.Slider(
                                                                id="price-min-filter",
                                                                min=min_price_val,
                                                                max=max_price_val,
                                                                value=min_price_val,
                                                                marks={int(min_price_val): f"${int(min_price_val):,}", 
                                                                       int(max_price_val): f"${int(max_price_val):,}"},
                                                                tooltip={"placement": "bottom", "always_visible": True}
                                                            ),
                                                            html.Br(),
                                                            html.Label("Prix Maximum ($):", className="mb-2 mt-3", style={"fontWeight": "600"}),
                                                            dcc.Slider(
                                                                id="price-max-filter",
                                                                min=min_price_val,
                                                                max=max_price_val,
                                                                value=max_price_val,
                                                                marks={int(min_price_val): f"${int(min_price_val):,}", 
                                                                       int(max_price_val): f"${int(max_price_val):,}"},
                                                                tooltip={"placement": "bottom", "always_visible": True}
                                                            ),
                                                        ],
                                                        title="Filtres par Prix",
                                                        item_id="price-filters"
                                                    ),
                                                    dbc.AccordionItem(
                                                        [
                                                            html.Label("Filtrer par catégorie:", className="mb-2", style={"fontWeight": "600"}),
                                                            dcc.Dropdown(
                                                                id="category-filter-col",
                                                                options=[{"label": col, "value": col} for col in categorical_cols] if categorical_cols else [],
                                                                placeholder="Sélectionner une catégorie...",
                                                                clearable=True,
                                                                className="mb-3"
                                                            ),
                                                            dcc.Dropdown(
                                                                id="category-filter-value",
                                                                placeholder="Sélectionner une valeur...",
                                                                clearable=True,
                                                                disabled=True,
                                                                value=None
                                                            ),
                                                        ],
                                                        title="Filtres par Catégorie",
                                                        item_id="category-filters"
                                                    ),
                                                    dbc.AccordionItem(
                                                        [
                                                            html.P(
                                                                [
                                                                    html.I(className="fas fa-info-circle me-2", style={"color": "#2E86AB"}),
                                                                    "Tous les graphiques et statistiques se mettent à jour automatiquement lorsque vous modifiez les filtres."
                                                                ],
                                                                className="mb-0",
                                                                style={"fontSize": "0.9rem", "color": "#6c757d"}
                                                            )
                                                        ],
                                                        title="Information",
                                                        item_id="info"
                                                    )
                                                ],
                                                id="filters-accordion",
                                                always_open=True,
                                                active_item=["price-filters"]
                                            )
                                        ],
                                        style={"padding": "1.5rem"}
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12,
                        className="mb-4"
                    )
                ],
                className="mb-4"
            ),
            
            # Tableau de données avec plus d'espace
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-table me-2"),
                                            "Aperçu des Données"
                                        ],
                                        style={"backgroundColor": "#2E86AB", "color": "white", "fontWeight": "600", "fontSize": "1.1rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="data-table-container")
                                        ],
                                        style={"padding": "2rem"}
                                    )
                                ],
                                className="shadow-sm mb-5",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12,
                        className="mb-5"
                    )
                ]
            ),
            
            # Cards de statistiques dynamiques
            dbc.Row(
                [
                    dbc.Col(
                        create_stat_card(
                            "Nombre de Maisons",
                            "0",
                            "fas fa-home",
                            "#2E86AB"
                        ),
                        width=12, md=6, lg=2, className="mb-3"
                    ),
                    dbc.Col(
                        create_stat_card(
                            "Prix Moyen",
                            "$0",
                            "fas fa-dollar-sign",
                            "#06A77D"
                        ),
                        width=12, md=6, lg=2, className="mb-3"
                    ),
                    dbc.Col(
                        create_stat_card(
                            "Prix Médian",
                            "$0",
                            "fas fa-chart-line",
                            "#A23B72"
                        ),
                        width=12, md=6, lg=2, className="mb-3"
                    ),
                    dbc.Col(
                        create_stat_card(
                            "Prix Minimum",
                            "$0",
                            "fas fa-arrow-down",
                            "#F18F01"
                        ),
                        width=12, md=6, lg=2, className="mb-3"
                    ),
                    dbc.Col(
                        create_stat_card(
                            "Prix Maximum",
                            "$0",
                            "fas fa-arrow-up",
                            "#D00000"
                        ),
                        width=12, md=6, lg=2, className="mb-3"
                    ),
                    dbc.Col(
                        create_stat_card(
                            "Écart-type",
                            "$0",
                            "fas fa-chart-bar",
                            "#6c757d"
                        ),
                        width=12, md=6, lg=2, className="mb-3"
                    )
                ],
                className="mb-5",
                id="stats-cards-row"
            ),
            
            # Graphiques principaux avec plus d'espace
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-chart-bar me-2"),
                                            "Distribution des Prix"
                                        ],
                                        style={"backgroundColor": "#2E86AB", "color": "white", "fontWeight": "600"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="price-distribution-chart",
                                                config={'displayModeBar': True, 'displaylogo': False}
                                            )
                                        ],
                                        style={"padding": "1.5rem"}
                                    )
                                ],
                                className="shadow-sm mb-5",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12,
                        className="mb-5"
                    )
                ]
            ),
            
            # Analyse des variables les plus importantes avec plus d'espace
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-star me-2"),
                                            "Top 10 Variables les Plus Corrélées avec le Prix"
                                        ],
                                        style={"backgroundColor": "#2E86AB", "color": "white", "fontWeight": "600"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="top-correlations-chart",
                                                config={'displayModeBar': True, 'displaylogo': False}
                                            )
                                        ],
                                        style={"padding": "1.5rem"}
                                    )
                                ],
                                className="shadow-sm mb-5",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12,
                        className="mb-5"
                    )
                ]
            ),
            
            # Graphiques de features vs prix
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(
                                [
                                    html.I(className="fas fa-chart-scatter me-2"),
                                    "Relations Features vs Prix"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-3"
            ),
            
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Label(
                                                "Sélectionner une variable numérique:",
                                                className="mb-2",
                                                style={"fontWeight": "600"}
                                            ),
                                            dcc.Dropdown(
                                                id="feature-selector",
                                                options=[
                                                    {"label": col, "value": col}
                                                    for col in (top_features[:10] if top_features else ([col for col in numeric_cols if col != 'SalePrice'][:10] if numeric_cols else []))
                                                ] if (top_features or numeric_cols) else [],
                                                value=default_numeric_feature,
                                                className="mb-3",
                                                disabled=default_numeric_feature is None or len(top_features if top_features else ([col for col in numeric_cols if col != 'SalePrice'] if numeric_cols else [])) == 0
                                            ),
                                            dcc.Graph(
                                                id="feature-vs-price-chart",
                                                config={'displayModeBar': True, 'displaylogo': False},
                                                style={"height": "500px"}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12, lg=6,
                        className="mb-4"
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Label(
                                                "Sélectionner une variable catégorielle:",
                                                className="mb-2",
                                                style={"fontWeight": "600"}
                                            ),
                                            dcc.Dropdown(
                                                id="cat-selector",
                                                options=[
                                                    {"label": col, "value": col}
                                                    for col in (categorical_cols[:10] if categorical_cols else [])
                                                ],
                                                value=default_cat_feature,
                                                className="mb-3",
                                                disabled=default_cat_feature is None or len(categorical_cols) == 0
                                            ),
                                            dcc.Graph(
                                                id="categorical-chart",
                                                config={'displayModeBar': True, 'displaylogo': False},
                                                style={"height": "500px"}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12, lg=6,
                        className="mb-4"
                    )
                ],
                className="mb-5"
            ),
            
            # Analyses approfondies
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(
                                [
                                    html.I(className="fas fa-chart-area me-2"),
                                    "Analyses Approfondies"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-3"
            ),
            
            # Analyse temporelle
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="temporal-analysis-chart",
                                                config={'displayModeBar': True, 'displaylogo': False}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12,
                        className="mb-4"
                    )
                ]
            ),
            
            # Analyse par quartier et qualité
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="neighborhood-analysis-chart",
                                                config={'displayModeBar': True, 'displaylogo': False}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12, lg=6,
                        className="mb-4"
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="quality-analysis-chart",
                                                config={'displayModeBar': True, 'displaylogo': False}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12, lg=6,
                        className="mb-4"
                    )
                ],
                className="mb-5"
            ),
            
            # Croisements intéressants
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(
                                [
                                    html.I(className="fas fa-project-diagram me-2"),
                                    "Croisements et Relations Multiples"
                                ],
                                className="mb-4",
                                style={"color": "#2E86AB"}
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-3"
            ),
            
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Label(
                                                "Variable X:",
                                                className="mb-2",
                                                style={"fontWeight": "600"}
                                            ),
                                            dcc.Dropdown(
                                                id="cross-x-selector",
                                                options=[
                                                    {"label": col, "value": col}
                                                    for col in numeric_cols
                                                    if col != 'SalePrice'
                                                ][:15],
                                                value=numeric_cols[0] if numeric_cols and numeric_cols[0] != 'SalePrice' else None,
                                                className="mb-3"
                                            ),
                                            html.Label(
                                                "Variable de couleur (optionnel):",
                                                className="mb-2",
                                                style={"fontWeight": "600"}
                                            ),
                                            dcc.Dropdown(
                                                id="cross-color-selector",
                                                options=[
                                                    {"label": col, "value": col}
                                                    for col in categorical_cols[:10]
                                                ] if categorical_cols else [],
                                                placeholder="Aucune",
                                                clearable=True,
                                                className="mb-3"
                                            ),
                                            dcc.Graph(
                                                id="cross-analysis-chart",
                                                config={'displayModeBar': True, 'displaylogo': False},
                                                style={"height": "500px"}
                                            )
                                        ]
                                    )
                                ],
                                className="shadow-sm mb-4",
                                style={"border": "none", "borderRadius": "15px"}
                            )
                        ],
                        width=12,
                        className="mb-4"
                    )
                ],
                className="mb-5"
            )
        ],
        fluid=True,
        className="px-4"
    )


def register_dashboard_callbacks(app):
    """
    Enregistrer les callbacks pour la page Dashboard.
    
    Args:
        app: Application Dash
    """
    @app.callback(
        [
            Output("stat-nombre-de-maisons", "children"),
            Output("stat-prix-moyen", "children"),
            Output("stat-prix-median", "children"),
            Output("stat-prix-minimum", "children"),
            Output("stat-prix-maximum", "children"),
            Output("stat-ecart-type", "children"),
            Output("price-distribution-chart", "figure"),
            Output("top-correlations-chart", "figure"),
            Output("data-table-container", "children"),
            Output("feature-vs-price-chart", "figure"),
            Output("categorical-chart", "figure"),
            Output("temporal-analysis-chart", "figure"),
            Output("neighborhood-analysis-chart", "figure"),
            Output("quality-analysis-chart", "figure"),
            Output("cross-analysis-chart", "figure")
        ],
        [
            Input("price-min-filter", "value"),
            Input("price-max-filter", "value"),
            Input("category-filter-col", "value"),
            Input("category-filter-value", "value"),
            Input("feature-selector", "value"),
            Input("cat-selector", "value"),
            Input("cross-x-selector", "value"),
            Input("cross-color-selector", "value")
        ],
        prevent_initial_call=False
    )
    def update_all_components(price_min, price_max, cat_filter_col, cat_filter_value, selected_feature, selected_cat, cross_x, cross_color):
        """Mettre à jour tous les composants en fonction des filtres."""
        try:
            train_df = load_train_data()
            if train_df is None or len(train_df) == 0:
                empty_table = html.Div("Aucune donnée disponible", className="text-center p-4")
                return ["0"] * 6 + [go.Figure(), go.Figure(), empty_table] + [go.Figure()] * 6
            
            # Appliquer les filtres
            filtered_df = train_df.copy()
            
            # Filtre par prix
            if 'SalePrice' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['SalePrice'] >= price_min) & 
                    (filtered_df['SalePrice'] <= price_max)
                ]
            
            # Filtre par catégorie
            if cat_filter_col and cat_filter_value and cat_filter_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[cat_filter_col] == cat_filter_value]
            
            if len(filtered_df) == 0:
                empty_table = html.Div("Aucune donnée ne correspond aux filtres sélectionnés", className="text-center p-4")
                return ["0"] * 6 + [go.Figure(), go.Figure(), empty_table] + [go.Figure()] * 6
            
            # Calculer les statistiques
            if 'SalePrice' in filtered_df.columns:
                n_houses = len(filtered_df)
                avg_price = filtered_df['SalePrice'].mean()
                median_price = filtered_df['SalePrice'].median()
                min_price = filtered_df['SalePrice'].min()
                max_price = filtered_df['SalePrice'].max()
                std_price = filtered_df['SalePrice'].std()
            else:
                n_houses = len(filtered_df)
                avg_price = median_price = min_price = max_price = std_price = 0
            
            stats = [
                f"{n_houses:,}",
                f"${avg_price:,.0f}",
                f"${median_price:,.0f}",
                f"${min_price:,.0f}",
                f"${max_price:,.0f}",
                f"${std_price:,.0f}"
            ]
            
            # Créer les graphiques
            price_dist_fig = create_price_distribution_chart(filtered_df)
            top_corr_fig = create_top_correlations_chart(filtered_df)
            
            # Tableau de données - créer le composant avec les données filtrées
            table_component = create_data_table(filtered_df, max_rows=100)
            
            # Graphiques de features
            feature_fig = create_feature_vs_price_chart(filtered_df, selected_feature)
            cat_fig = create_categorical_analysis_chart(filtered_df, selected_cat)
            
            # Nouvelles analyses approfondies
            temporal_fig = create_temporal_analysis_chart(filtered_df)
            neighborhood_fig = create_neighborhood_analysis_chart(filtered_df)
            quality_fig = create_quality_analysis_chart(filtered_df)
            cross_fig = create_cross_analysis_chart(filtered_df, cross_x, 'SalePrice', cross_color if cross_color else None)
            
            return stats + [price_dist_fig, top_corr_fig, table_component, feature_fig, cat_fig, 
                          temporal_fig, neighborhood_fig, quality_fig, cross_fig]
            
        except Exception as e:
            print(f"Erreur dans update_all_components: {e}")
            import traceback
            traceback.print_exc()
            empty_table = html.Div("Erreur lors du chargement des données", className="text-center p-4")
            return ["0"] * 6 + [go.Figure(), go.Figure(), empty_table] + [go.Figure()] * 6
    
    @app.callback(
        [Output("category-filter-value", "options"),
         Output("category-filter-value", "disabled"),
         Output("category-filter-value", "value")],
        [Input("category-filter-col", "value")]
    )
    def update_category_filter_values(selected_col):
        """Mettre à jour les valeurs disponibles pour le filtre de catégorie."""
        try:
            train_df = load_train_data()
            if train_df is None or selected_col is None or selected_col not in train_df.columns:
                return [], True, None
            
            unique_values = sorted(train_df[selected_col].dropna().unique().tolist())
            options = [{"label": str(val), "value": val} for val in unique_values]
            # Réinitialiser la valeur quand on change de colonne
            return options, False, None
        except Exception as e:
            print(f"Erreur dans update_category_filter_values: {e}")
            return [], True, None
