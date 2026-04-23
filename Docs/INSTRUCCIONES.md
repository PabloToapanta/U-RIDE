# Proyecto U-Ride - Guía de Configuración Local

¡Bienvenidos al equipo de desarrollo de U-Ride! 
Para que el proyecto funcione en sus computadoras locales, por favor sigan estos pasos **exactamente en orden**. Si tienen algún error, lean la sección de "Solución de Problemas" al final.

---

##  Paso 1: Prerrequisitos e Instalación

### Para usuarios de Linux (Fedora)
Abre tu terminal y ejecuta:
`sudo dnf install python3 git postgresql-server postgresql-contrib`
*(Nota: Asegúrate de inicializar y arrancar el servicio de PostgreSQL).*

### Para usuarios de Windows 11
Descarga e instala manualmente:
1. **Python:** Descárgalo de `python.org`. **IMPORTANTE:** Durante la instalación, marca la casilla que dice *"Add Python to PATH"*.
2. **Git:** Descárgalo de `git-scm.com`. Esto instalará "Git Bash", que es la terminal que usaremos.
3. **PostgreSQL:** Descárgalo de `postgresql.org` (el instalador de EnterpriseDB). Anota la contraseña maestra del usuario `postgres` que te pedirá al instalar.

---

##  Paso 2: Clonar el Repositorio y Entorno Virtual

Abre tu terminal (En Windows usa **Git Bash** o **PowerShell**).

1. Clona este repositorio:
   `git clone <AQUÍ_PONES_LA_URL_DE_TU_REPOSITORIO_GITHUB>`
2. Entra a la carpeta del proyecto:
   `cd uride_project` *(Cambia esto por el nombre real de tu carpeta)*
3. Crea un entorno virtual aislado:
   * **Linux / Windows:** `python -m venv venv`  *(Si en Windows falla, intenta `py -m venv venv`)*
4. Activa el entorno virtual (Asegúrate de ver `(venv)` al inicio de tu terminal):
   * **Linux:** `source venv/bin/activate`
   * **Windows (Git Bash):** `source venv/Scripts/activate`
   * **Windows (PowerShell):** `venv\Scripts\activate`

---

##  Paso 3: Instalar Dependencias

Con el entorno virtual activado, instala las herramientas del proyecto:
`pip install -r requirements.txt`

> ** ATENCIÓN USUARIOS DE WINDOWS (Error de psycopg2):**
> Si el comando anterior lanza un error rojo gigante al intentar instalar `psycopg2`, se debe a que Windows necesita compilarlo. Para solucionarlo, ejecuta esto:
> `pip install psycopg2-binary`
> Luego, vuelve a ejecutar `pip install -r requirements.txt` para instalar el resto.

---

## Paso 4: Preparar la Base de Datos (PostgreSQL)

Necesitamos crear la base de datos donde se guardarán los usuarios y viajes.

**En Linux:**
`sudo -i -u postgres psql`

**En Windows:**
Abre tu terminal y ejecuta `psql -U postgres` (Te pedirá la contraseña que creaste al instalar).
*(Alternativamente, puedes hacer esto usando la interfaz gráfica **pgAdmin 4**).*

**Comandos SQL (Para ambos sistemas):**
Ejecuta uno por uno dentro de la consola de Postgres:
```sql
CREATE DATABASE uride_db;
CREATE USER uride_admin WITH PASSWORD 'pon_tu_propia_contraseña_aqui';
ALTER ROLE uride_admin SET client_encoding TO 'utf8';
ALTER ROLE uride_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE uride_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE uride_db TO uride_admin;
\q