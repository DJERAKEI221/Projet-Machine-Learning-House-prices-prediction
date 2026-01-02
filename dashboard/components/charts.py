"""
Composants de graphiques pour le dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def create_prediction_card(predicted_price, confidence=None):
    """
    Créer une carte de prédiction avec design moderne.
    
    Args:
        predicted_price: Prix prédit
        confidence: Score de confiance (optionnel)
        
    Returns:
        dict: Figure Plotly
    """
    fig = go.Figure()
    
    # Cercle avec le prix
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode='markers+text',
        marker=dict(
            size=200,
            color='#2E86AB',
            line=dict(width=5, color='#A23B72')
        ),
        text=[f"${predicted_price:,.0f}"],
        textfont=dict(size=32, color='white', family="Arial Black"),
        textposition="middle center",
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title={
            'text': 'Prix Prédit',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2E86AB'}
        },
        xaxis=dict(visible=False, range=[-1, 1]),
        yaxis=dict(visible=False, range=[-1, 1]),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_sensitivity_chart(sensitivity_data):
    """
    Créer un graphique d'analyse de sensibilité.
    
    Args:
        sensitivity_data: Dict avec les données de sensibilité
        
    Returns:
        dict: Figure Plotly
    """
    if not sensitivity_data:
        return go.Figure()
    
    features = list(sensitivity_data.keys())
    impacts = list(sensitivity_data.values())
    
    # Trier par impact
    sorted_data = sorted(zip(features, impacts), key=lambda x: abs(x[1]), reverse=True)
    features, impacts = zip(*sorted_data)
    
    colors = ['#2E86AB' if x > 0 else '#A23B72' for x in impacts]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=impacts,
        y=features,
        orientation='h',
        marker=dict(color=colors),
        text=[f"${x:,.0f}" for x in impacts],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Impact: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Impact des Variables sur le Prix',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E86AB'}
        },
        xaxis=dict(title='Impact sur le Prix ($)'),
        yaxis=dict(title='Variables'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=150, r=20, t=60, b=40)
    )
    
    return fig


def create_price_distribution_chart(train_df):
    """
    Créer un graphique de distribution des prix.
    
    Args:
        train_df: DataFrame avec les données d'entraînement
        
    Returns:
        dict: Figure Plotly
    """
    if train_df is None or 'SalePrice' not in train_df.columns:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=train_df['SalePrice'],
        nbinsx=50,
        marker=dict(
            color='#2E86AB',
            line=dict(color='white', width=1)
        ),
        name='Distribution des Prix'
    ))
    
    fig.update_layout(
        title={
            'text': 'Distribution des Prix de Vente',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2E86AB'}
        },
        xaxis=dict(title='Prix ($)'),
        yaxis=dict(title='Fréquence'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=300,
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    return fig

