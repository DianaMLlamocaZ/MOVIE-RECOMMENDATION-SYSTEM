import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2


class DataBase():
    def __init__(self,env_path):
        #Conexión a la BD
        self.path=Path(env_path)
        load_dotenv(self.path)
    
    
    def __get_credentials_conection(self):
        username,database,host,puerto_db,password=os.getenv("user_nm"),os.getenv("database"),os.getenv("host"),os.getenv("puerto_db_int"),os.getenv("password")
        return username,database,host,puerto_db,password
    

    def connection(self):
        username,database,host,puerto_db,password=self.__get_credentials_conection()
        
        connection_obj=psycopg2.connect(database=database,user=username,host=host,password=password,port=int(puerto_db))
        print(f"Conexión establecida!")
        return connection_obj
