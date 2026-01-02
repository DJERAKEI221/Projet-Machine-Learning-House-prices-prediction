@echo off
REM Script de déploiement AWS Lambda pour Windows
REM Usage: deploy.bat [method]
REM Methods: manual, layer

setlocal enabledelayedexpansion

set METHOD=%1
if "%METHOD%"=="" set METHOD=manual

set FUNCTION_NAME=house-price-predictor
set REGION=%AWS_REGION%
if "%REGION%"=="" set REGION=us-east-1
set RUNTIME=python3.11
set TIMEOUT=60
set MEMORY=1024

echo ==========================================
echo Déploiement AWS Lambda - House Price Predictor
echo ==========================================
echo Méthode: %METHOD%
echo Fonction: %FUNCTION_NAME%
echo Région: %REGION%
echo ==========================================
echo.

echo Vérification des prérequis...
where aws >nul 2>&1
if errorlevel 1 (
    echo ERREUR: AWS CLI non installé. Installez-le d'abord.
    exit /b 1
)

echo Vérification de la configuration AWS...
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ERREUR: AWS CLI non configuré. Exécutez 'aws configure'.
    exit /b 1
)

for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo Compte AWS: %ACCOUNT_ID%

if not exist "model\final_model.pkl" (
    echo ERREUR: Modèle non trouvé dans model\final_model.pkl
    echo Entraînez d'abord le modèle avec: python train.py
    exit /b 1
)

echo Prérequis OK
echo.

if "%METHOD%"=="manual" goto :manual
if "%METHOD%"=="layer" goto :layer
goto :error

:manual
echo === Déploiement Manuel ===
echo.

echo Création du package ZIP...
if exist lambda_function.zip del lambda_function.zip
powershell -Command "Compress-Archive -Path lambda_function.py,requirements.txt,model,src -DestinationPath lambda_function.zip -Force"

for %%A in (lambda_function.zip) do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1048576
echo Taille du package: %SIZE_MB% MB

if %SIZE_MB% gtr 50 (
    echo ATTENTION: Package ^> 50 MB. Utilisez Lambda Layers.
)
echo.

echo Vérification du rôle IAM...
aws iam get-role --role-name lambda-house-price-role >nul 2>&1
if errorlevel 1 (
    echo Création du rôle IAM...
    
    echo { > %TEMP%\trust-policy.json
    echo   "Version": "2012-10-17", >> %TEMP%\trust-policy.json
    echo   "Statement": [ >> %TEMP%\trust-policy.json
    echo     { >> %TEMP%\trust-policy.json
    echo       "Effect": "Allow", >> %TEMP%\trust-policy.json
    echo       "Principal": { >> %TEMP%\trust-policy.json
    echo         "Service": "lambda.amazonaws.com" >> %TEMP%\trust-policy.json
    echo       }, >> %TEMP%\trust-policy.json
    echo       "Action": "sts:AssumeRole" >> %TEMP%\trust-policy.json
    echo     } >> %TEMP%\trust-policy.json
    echo   ] >> %TEMP%\trust-policy.json
    echo } >> %TEMP%\trust-policy.json
    
    aws iam create-role --role-name lambda-house-price-role --assume-role-policy-document file://%TEMP%\trust-policy.json
    aws iam attach-role-policy --role-name lambda-house-price-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    echo Rôle créé
) else (
    echo Rôle existe déjà
)

set ROLE_ARN=arn:aws:iam::%ACCOUNT_ID%:role/lambda-house-price-role
echo.

aws lambda get-function --function-name %FUNCTION_NAME% --region %REGION% >nul 2>&1
if errorlevel 1 (
    echo Création de la fonction...
    aws lambda create-function --function-name %FUNCTION_NAME% --runtime %RUNTIME% --role %ROLE_ARN% --handler lambda_function.lambda_handler --zip-file fileb://lambda_function.zip --timeout %TIMEOUT% --memory-size %MEMORY% --description "Prédiction des prix immobiliers - Projet Laplace Immo" --region %REGION%
) else (
    echo Mise à jour de la fonction existante...
    aws lambda update-function-code --function-name %FUNCTION_NAME% --zip-file fileb://lambda_function.zip --region %REGION%
)

echo.
echo Déploiement terminé!
echo.
echo Pour tester:
echo   aws lambda invoke --function-name %FUNCTION_NAME% --payload "{\"body\":\"{\\\"features\\\":{\\\"OverallQual\\\":7,\\\"GrLivArea\\\":1710}}\"}" response.json
goto :end

:layer
echo === Déploiement avec Lambda Layers ===
echo.
echo Cette méthode nécessite des commandes supplémentaires.
echo Consultez le guide: docs\GUIDE_DEPLOIEMENT_AWS_LAMBDA.md
goto :end

:error
echo Méthode inconnue: %METHOD%
echo Méthodes disponibles: manual, layer
exit /b 1

:end
echo.
echo ==========================================
echo Déploiement terminé!
echo ==========================================
echo.
echo Fonction Lambda: %FUNCTION_NAME%
echo Région: %REGION%
echo.
echo Pour voir les logs:
echo   aws logs tail /aws/lambda/%FUNCTION_NAME% --follow
echo.

