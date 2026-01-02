#!/bin/bash
# Script pour lancer le dashboard Dash

echo "============================================================"
echo "Démarrage du Dashboard Dash"
echo "============================================================"
echo "Dashboard disponible sur http://localhost:8050"
echo "============================================================"
echo ""

cd "$(dirname "$0")/.."
python app_dash.py

