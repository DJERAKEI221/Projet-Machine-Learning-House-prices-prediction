@echo off
REM Script pour lancer l'API REST sur Windows

echo Demarrage de l'API REST...
echo API disponible sur http://localhost:8000
echo Documentation disponible sur http://localhost:8000/docs

cd /d "%~dp0\.."
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

pause

