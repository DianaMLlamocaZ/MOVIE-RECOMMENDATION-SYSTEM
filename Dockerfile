FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

#Instalo dos2unix para limpiar archivos
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY data/ ./data
COPY templates/ ./templates

COPY apis.py .
COPY connect_database.py .
COPY custom_dataset.py .
COPY dataset_to_db.py .
COPY model.py .
COPY utils.py .

COPY entrypoint.sh .

#Se convierte el formato de Windows a Linux y se da permisos de ejecución
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]
