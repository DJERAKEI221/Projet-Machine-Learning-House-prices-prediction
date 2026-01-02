#!/bin/bash
# Script pour lancer l'interface MLFlow

echo "Démarrage de MLFlow UI..."
echo "Ouvrez http://localhost:5000 dans votre navigateur"

mlflow ui --backend-store-uri file:./mlruns --port 5000


