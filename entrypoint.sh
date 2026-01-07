#!/bin/bash

echo "Esperando a que la BD encienda"
sleep 8

echo "Ejecutando el script dataset_to_db para insertar las películas a la BD"
python dataset_to_db.py

echo "Lanzamiento de la aplicación"
python apis.py
