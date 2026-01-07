--Primero, se crea la extensión para vectores al usar pgvector--
CREATE EXTENSION IF NOT EXISTS vector;

--Tabla movies (tabla de películas)--
CREATE TABLE movies(id_movie BIGSERIAL PRIMARY KEY, title_movie VARCHAR(500), desc_movie VARCHAR(500), emb_desc vector(512));

--Tabla users_movies (tabla de usuarios)--
CREATE TABLE users_movies (id_user BIGSERIAL PRIMARY KEY, username VARCHAR(100), correo VARCHAR(100), password VARCHAR(200));

--Tabla tabla de user_likes (tabla de usuarios con sus movies favoritas)--
CREATE TABLE user_likes (user_likes_id BIGSERIAL PRIMARY KEY, user_id INT references users_movies(id_user), movie_id INT references movies(id_movie));
