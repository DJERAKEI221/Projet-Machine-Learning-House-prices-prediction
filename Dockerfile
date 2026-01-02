# Dockerfile pour containeriser l'application
FROM python:3.10-slim

WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .
COPY requirements_api.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_api.txt

# Copier le code
COPY . .

# Exposer les ports
EXPOSE 8000 8501

# Commande par défaut (peut être overridée)
CMD ["python", "train.py"]

