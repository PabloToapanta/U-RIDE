# Coneccion con base de datos PostgreSQL
Para esta coneccion segun la documentacion, se debe ir a settings.py en django y modificar la tupla DATABASES que sigue el siguiente esquema 
``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'masteruser',
        'PASSWORD': '12345678',
        'HOST': 'w3-django-project.cdxmgq9zqqlr.us-east-1.rds.amazonaws.com',
        'PORT': '5432'
    }
}
```
Nositrs debemos cambiar el nombre, usuario, contrasenia, host y el port para nuestro caso especifico, pero antes de esto hay que hace algunas otras cosas.

Primero debemos crear la base de datos:
``` SQL
CREATE DATABASE uride_db;
```
Creamos superusuario especifico para acceder a esta base de datos.
``` SQL
CREATE USER uride_admin WITH PASSWORD 'tu_contraseña_segura';
```
Configuramos los permisos de ese usuario en nuestra base de datos
``` SQL
GRANT ALL PRIVILEGES ON DATABASE uride_db TO uride_admin;

```

## Configurar Librerias
Para el proyecto necesitamos un entorno virtual e instalar la libreria psycopg2 que es un adaptador de la base de datos PostgreSQL con el lenguaje de python.

Crear entorno virtual
``` bash
python3 -m venv venv
```

Instalar psycopg
``` bash
pip install psycopg
```

Instalar django

``` bash
pip install django
```

Con todo esto, nuestra tupla DATABASE quedaria de la siguiente forma:

``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uride_db',
        'USER': 'uride_admin',
        'PASSWORD': '*****',
        'HOST': 'lolcalhost',
        'PORT': '5432'
    }
}
```
Con esto simplemente inicializamos el proyecto en django y reemplazamos los ajustes

Despues de esto ocurrio un error dado el sistema operativo usado (FEDORA 43), y se debio modificar el archivo ubicado en `/var/lib/pgsql/data/pg_hba.conf` y cambiar el cifrado al usado por PosrgreSQL

``` bash
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
# IPv6 local connections:
host    all             all             ::1/128                 scram-sha-256
```
Despues de esto reiniciamos el servicio con el comando 
``` bash
sudo systemctl restart postgresql
```

Obtuvimos otro problema relacionado a los permisos de los usuarios, los comandos utilizados fueron:
Convertir a usuario `uride_admin` en duenio de la base de datos
``` bash
ALTER DATABASE uride_db OWNER TO uride_admin;
```

Dar todos los permisos sobre el esquema publico
``` bash
GRANT ALL ON SCHEMA public TO uride_admin;
```
