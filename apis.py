from connect_database import DataBase
from flask import render_template,Flask,request,session,redirect,url_for,flash
from model import get_model_and_tokz
from utils import get_embedding
import os
from werkzeug.security import generate_password_hash,check_password_hash

#Conexión a BD
db=DataBase("./.env") #Asegúrate de que el nombre del archivo .env sea exactamente '.env'
db_con=db.connection()

#Cursor
cursor=db_con.cursor()

#Modelo y tokenizer
model,tokenizer=get_model_and_tokz()


#Flask
app=Flask(__name__)
app.secret_key=os.getenv("app_secret")


#Página principal
@app.route("/")
def main():
    print(f"dIAnaMovieCLIP - Creado por DianaLlamoca")
    return render_template("main.html")


#Registro
@app.route("/register_user",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["uname"]
        correo=request.form["email"]
        password=generate_password_hash(request.form["psw"])
        
        
        sql_query="INSERT INTO users_movies(username,correo,password) VALUES (%s,%s,%s)"
        cursor.execute(query=sql_query,vars=(username,correo,password))
        db_con.commit()

        return redirect(url_for("login"))

    #HTML por default en la ruta register_user
    return render_template("register.html")


#Login
@app.route("/login_user",methods=["GET","POST"])
def login():
    if request.method=="POST":
         email,password=request.form["uemail"],request.form["psw"]

         query=f"SELECT id_user,password,username FROM users_movies WHERE correo='{email}'"
         cursor.execute(query)
         res=cursor.fetchall()
         
         #Si el resultados es distinto de [], lista vacía --> el correo existe
         if res!=[]:
            user_id,pwd_real,usnm=res[0][0],res[0][1],res[0][2]
            
            #Verificar hashes para comprobación
            if check_password_hash(pwhash=pwd_real,password=password):
                #Almaceno el id_user y username en 'session' object
                session["id_user"]=user_id
                session["username"]=usnm
                
                return redirect(url_for("buscar_clip"))
         
         else:
             return render_template("login.html")

    return render_template("login.html")


#LogOut
@app.route("/logout")
def logout():
    session.pop("id_user") #Elimino el id user de la sesión actual
    return redirect(url_for("main"))



#Ver películas en base a descripción
@app.route("/buscar_movie")
def buscar_clip():
        movies_rec_busqueda=None #Inicialmente, para evitar errores en la muestra de interfaz
        movies_rec_favs=None #Inicialmente, para evitar errores en la muestra de interfaz

        #Para evitar errores de muestra de interfaz
        if request.args:
            
            desc_user=request.args["query"]
            #Búsqueda por CLIP y retornar las 5 pelis más parecidas
            emb_desc=get_embedding(description=desc_user,tokenizer=tokenizer,modelo=model)

            #Query
            query=f"SELECT id_movie,title_movie,desc_movie FROM movies ORDER BY emb_desc <=> '{emb_desc}' LIMIT 5"
            cursor.execute(query)
            movies_rec_busqueda=cursor.fetchall()
            
        

        #Recomendación personalizada en base a lo que el usuario logeado tiene como favoritos (si los tiene) cuando este no escribe una descripción en el buscador
        if session["id_user"]:
            
            #Esta query se encargar de verificar que el usuario SÍ tiene películas AÑADIDAS como favoritas, y en base a eso RECOMIENDA.
            query=f"SELECT id_movie,title_movie FROM movies INNER JOIN user_likes ON movies.id_movie=user_likes.movie_id WHERE user_likes.user_id={session['id_user']}"
            cursor.execute(query)
            res=cursor.fetchall()

            #Esta query es la que se encarga de recomendar movies promediando los embeddings de películas favoritas del usuario            
            if res:
                query_avg_emb = f"""
                SELECT m.id_movie, m.title_movie, m.desc_movie
                FROM movies m
                WHERE m.id_movie NOT IN (SELECT movie_id FROM user_likes WHERE user_id = {session['id_user']})
                ORDER BY m.emb_desc <=> (
                    SELECT AVG(m2.emb_desc) 
                    FROM movies m2
                    INNER JOIN user_likes ul ON ul.movie_id = m2.id_movie
                    WHERE ul.user_id = {session['id_user']}
                )
                LIMIT 5
                """
                cursor.execute(query_avg_emb)
                movies_rec_favs=cursor.fetchall()
                
                
            
        return render_template("busqueda.html",movies=movies_rec_busqueda,movies_favs=movies_rec_favs, username=session["username"]) #busqueda.html
    

#Agregar películas al perfil del usuario: necesito el id del usuario
@app.route("/add_movie",methods=["GET","POST"])
def add_movie():
    #El usuario agrega una película
    if request.method=="POST":
        user_id_act=session["id_user"]
        movie_id_act=request.form["id_movie"]

        #Para evitar duplicados, en caso el usuario intente añadir una película que ya tiene
        query_dup=f"SELECT movie_id FROM user_likes ul INNER JOIN users_movies um ON ul.user_id=um.id_user WHERE ul.movie_id={movie_id_act} AND ul.user_id={user_id_act}"
        cursor.execute(query_dup)
        res=cursor.fetchone()
        

        if res==None:
            query="INSERT INTO user_likes(user_id,movie_id) VALUES(%s,%s)"
            cursor.execute(query,vars=(user_id_act,movie_id_act))
            db_con.commit()

            flash("¡Película añadida correctamente!","success")
        
        else:
            flash("La película que intentas añadir, ya está presente en tu lista de favoritos","error")

    return redirect(url_for("buscar_clip"))
    

#Ver favoritos
@app.route("/list_movies")
def ver_favs():
    query=f"SELECT id_movie,title_movie FROM movies INNER JOIN user_likes ON user_likes.movie_id=movies.id_movie WHERE user_likes.user_id={session['id_user']}"
    cursor.execute(query)
    movies_favs=cursor.fetchall() #lista de tuplas
    
    return render_template("favoritos.html",favoritas=movies_favs)


#Eliminar favorito
@app.route("/delete_movie",methods=["GET","POST"])
def delete_movie():
    movie_id_delete=request.form["movie_id"]

    query=f"DELETE FROM user_likes WHERE movie_id={movie_id_delete} and user_likes.user_id={session['id_user']}"
    cursor.execute(query)
    db_con.commit()

    return redirect(url_for("ver_favs"))


if __name__=="__main__":
    app.run(host="0.0.0.0",port=os.getenv("puerto_app_int")) #Puerto del contenedor donde se tendrá que mapear del puerto host al puerto del contenedor
