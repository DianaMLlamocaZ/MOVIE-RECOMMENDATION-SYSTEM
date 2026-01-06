# dIAnaMovieCLIP - Sistema de recomendación de películas

### Índice
{anclas}

---

## Descripción del proyecto:
El presente proyecto que desarrollé se basa en la creación de un sistema de recomendación de películas (por búsqueda y preferencias de usuario) End-to-End, utilizando el modelo multimodal CLIP de OpenAI, que permite convertir la descripción textual, que ingresa el usuario, a un 'embedding' (vector numérico de 512 dimensiones) en un espacio latente aprendido por el modelo, donde 'oraciones' con 'contexto' similar están más cerca, permitiendo así la recomendación textual.
Asimismo, el usuario tiene recomendaciones personalizadas en base a lo que añada en su historial de películas favoritas.
Para permitir la interacción del usuario con la interfaz, la recomendación textual y la recomendación personalizada en tiempo real, utilicé la base de datos PostgreSQL con la extensión 'pgvector', y Flask para conectar los endpoints y renderizar los HTML.
La extensión 'pgvector' genera un nuevo tipo de datos 'vector', que permite almacenar las descripciones de las películas y búsquedas textuales del usuario en formato *'embedding*' (vector). 

---

## ¿Cómo funciona la recomendación?
El sistema ofrece dos niveles de interacción:
1. *Búsqueda semántica:*
     - El usuario ingresa una descripción textual (descripción de la película) y el modelo CLIP la vectoriza para encontrar películas, almacenadas en la base de datos, cuyas descripciones estén más cerca en el espacio latente (espacio vectorial).

2. *Personalización basada en el perfil del usuario (**promedio vectorial**):*
	- Para que la recomendación personalizada sea adecuada en base a las preferencias del usuario, se calcula un 'embedding promedio' de todas las películas presentes en la lista de 'favoritas' del usuario actual.
			- Este 'embedding promedio' representa el 'resumen numérico' de las preferencias del usuario.
			- La métrica utilizada para comparar el 'embedding promedio' respecto al catálogo en la base de datos es 'cosine distance'.
			- Se ordenan las películas de menor a mayor distancia, mostrando solo las cinco coincidencias más cercanas respecto al 'embedding promedio'.

---

## Herramientas utilizadas:
- Dataset: Netflix Movies and TV Shows - Kaggle
- Backend: Flask
- AI: OpenAI CLIP (multimodal)
- Base de datos: PostgreSQL + pgvector para el almacenamiento y consulta de '*embeddings*' (vectores)
- Frontend: HTML + CSS
- Docker Compose: Creación de imágenes y despliegue conjunto local

---

## Scripts:
- custom_dataset.py:
  	- Con el objetivo de evitar cargar el dataset en memoria, se lee el csv, película por película, para tener en memoria únicamente ese dato durante la inserción --> lazy load.


- connect_database.py:
	- Se crea una clase 'DataBase' que contiene las configuraciones necesarias para conectarse a la base de datos local:
		- El método .connection (luego de instanciar el objeto a la clase 'DataBase') es el encargado de realizar la conexión automáticamente y devuelve otra instancia con la conexión directa.
		- **NOTA:** El archivo **.env** debes configurarlo con **variables propias**, necesario para crear y conectarse a la base de datos local.


- model.py:
	- Este archivo usa la librería 'transformers' con el objetivo de descargar el modelo CLIP y el tokenizer. Este último es muy importante, ya que convierte el texto plano en un tensor de tokens que el modelo CLIP usará para convertir dicho tensor en un embedding (vector de 512 dimensiones) dentro del espacio latente de CLIP, dando como resultado un vector de contexto.
		

- dataset_to_db.py:
	- Primero verifica si hay datos insertados en la base de datos, para evitar la duplicados de películas cada vez que se ejecutan los contenedores.
	- Inserta las películas (título, descripción y embedding) a la base de datos, añadiéndole un ID único (primary key) necesario para relacionar la tabla con otras y permitir la recomendación personalizada por usuario.
	- **NOTA:** Este *script* se ejecuta al inicio, justo luego de crear las tablas en la base de datos, pues la tabla 'movies' debe contener la información de las películas del dataset, crucial para la recomendación personalizada.


- apis.py:
	- Se conecta a la base de datos.
	- Obtiene el modelo CLIP y el tokenizer.
	- Crea una instancia de la clase 'Flask' y configura los *endpoints* para permitir que el flujo de acciones en el frontend (la interfaz), generado por el usuario, interactúe con el backend (base de datos local):
		- **app.route("/")**:
			- Endpoint que muestra el HTML correspondiente al menú principal, dando la posibilidad a que el usuario se registre o inicie sesión.

		- **app.route("/register_user")**:
			- Endpoint que permite la creación de usuario (si es nuevo), interactuando con la base de datos directamente para que se añada dicha información nueva a la tabla que almacena a los usuarios.

		- **app.route("/login_user")**:
			- Endpoint que valida el inicio de sesión, permitiendo el ingreso solo si el usuario coloca sus credenciales correctamente en base a su registro inicial. Si el usuario inicia sesión correctamente, este será redirigido al menú principal de la aplicación; caso contrario, permanecerá en la interfaz de *login*.
			- Se usa 'session', objeto de flask (similar a un diccionario) que permite almacenar variables para su uso posterior durante el flujo de eventos en la interfaz.  
			- **NOTA:** Se hashean las credenciales.
		
		- **app.route("/logout")**:
			- Permite al usuario cerrar sesión, eliminándolo, momentámeante, del 'session' object y redireccionándolo al 'main'.
			- **NOTA:** Si el usuario decide iniciar sesión nuevamente, el 'session' object se restablecerá.

		- **app.route("/buscar_movie")**:
			- Este endpoint contiene la lógica 'principal':
				- 1: Si el usuario decide escribir la descripción de una película, se mostrarán, en la interfaz, las películas recomendadas que más se acercan a lo que el usuario escribió.
				- 2: Si el usuario está *'logeado'* en la aplicación y, además, tiene películas añadidas en 'favoritas', se genera la recomendación personalizada.
					- **NOTA:**
						- Para que la recomendación personalizada funcione, se promedian los 'embeddings' que el usuario actual tiene en su lista de películas favoritas. Dicho 'embedding promedio' se compara, utilizando la métrica *cosine distance*, con las películas en la tabla 'movies' para calcular la distancia entre el 'embedding promedio' y los 'embeddings' de las películas en la base de datos ordenándolos de menor a mayor distancia y mostrando solo las primeras cinco coincidencias.
						- En resumen, la recomendación personalizada muestra las cinco películas cercanas (en distancia) al 'embedding promedio'. El 'embedding promedio' puede verse como el 'resumen' (numérico) de las películas favoritas del usuario actual.
		
		- **app.route("/add_movie")**:
			- Permite al usuario seleccionar una película como favorita dándole click al botón 'Favorita'
			- Los cambios se realizan directamente en la base de datos local, añadiéndole a la tabla, que almacena la información de preferencias de usuario, el ID de la película añadida.
			- También se maneja el caso en que el usuario intenta agregar una película como 'favorita' que ya ha sido añadida previamente:
				- Para evitar estos casos, primero se realiza una consulta SQL con el ID de la película que el usuario intenta añadir. Dicho ID se busca en la tabla de preferencias de usuario. Si la respuesta a dicha consulta es 'None', entonces esa película no está duplicada y se permite la consulta INSERT SQL; en caso contrario, se le muestra al usuario un mensaje (durante tres segundos) de que la película ya está añadida.
 
		- **app.route("/list_movies")**:
			- Permite al usuario, a través de la interfaz, ver las películas que añadió como favoritas.

		- **app.route("/delete_movie")**:
			- Permite al usuario eliminar una película de su lista de favoritas.
			- **NOTA:** El cambio es directo, la consulta DELETE se realiza en ese preciso instante, permitiendo un flujo de recomendación de películas personalizadas, en tiempo real, en base a lo que el usuario tiene en su lista de preferencias.


- utils.py:
	- Este archivo contiene la función que permite convertir la descripción textual en embedding.
