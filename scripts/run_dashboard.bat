@echo off
REM Script pour lancer le dashboard Dash sur Windows

echo ============================================================
echo Demarrage du Dashboard Dash
echo ============================================================
echo Dashboard disponible sur http://localhost:8050
echo ============================================================
echo.

cd /d "%~dp0\.."

REM Essayer d'utiliser l'interpréteur Python de Spyder si disponible
if exist "D:\Spyder\Python\python.exe" (
    echo Utilisation de l'interpréteur Python de Spyder...
    "D:\Spyder\Python\python.exe" app_dash.py
) else (
    echo Utilisation de l'interpréteur Python par défaut...
    python app_dash.py
)

pause

