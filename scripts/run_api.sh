#!/bin/bash
# Script pour lancer l'API REST

echo "Démarrage de l'API REST..."
echo "API disponible sur http://localhost:8000"
echo "Documentation disponible sur http://localhost:8000/docs"

cd "$(dirname "$0")/.."
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

