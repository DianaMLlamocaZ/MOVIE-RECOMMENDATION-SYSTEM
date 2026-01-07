#Script para insertar el dataset a la base de datos
import os
from dotenv import load_dotenv
import torch
from pathlib import Path
from connect_database import DataBase
from custom_dataset import Dataset
from model import get_model_and_tokz


#DB conexión
database=DataBase("./.env")
database_con=database.connection()


#Dataset
dataset=Dataset("./data/netflix_titles.csv")


#Obtener el modelo y el tokenizador
modelo,tokenizer=get_model_and_tokz()


#SQL query
sql_query="INSERT INTO movies (title_movie,desc_movie,emb_desc) VALUES (%s,%s,%s)"


#Insertando los embeddings a la BD
with database_con as con:
    cursor=con.cursor()

    #Verificación de existencia de datos en la BD (para evitar duplicados al iniciar los contenedores)
    cursor.execute("SELECT COUNT(*) FROM movies")
    count=cursor.fetchone()[0]

    #Consistencia de datos
    if count>0:
        print(f"Ya hay datos en la BD")
    
    else:
        for i,(t,d) in enumerate(dataset):
            title,desc=t,d
            tokens_desc=tokenizer(text=desc,return_tensors="pt")["input_ids"]
            

            with torch.no_grad():
                emb_desc=modelo.get_text_features(tokens_desc).squeeze(0)


            cursor.execute(query=sql_query,vars=(title,desc,emb_desc.numpy().tolist()))

            if (i%1000==0) and i!=0:
                print(f"1000 embeddings insertados a la BD!")

        print(f"Embeddings insertados a la BD!")
