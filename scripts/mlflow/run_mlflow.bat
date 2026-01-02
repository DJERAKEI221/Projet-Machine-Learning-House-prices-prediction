@echo off
REM Script pour lancer l'interface MLFlow sur Windows

echo Démarrage de MLFlow UI...
echo Ouvrez http://localhost:5000 dans votre navigateur

mlflow ui --backend-store-uri file:./mlruns --port 5000

pause


