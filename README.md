

# U-Ride

Sistema web de viajes compartidos (carpooling) diseñado para la comunidad universitaria. Construido con Django y PostgreSQL, permite a los estudiantes con vehículo publicar sus rutas y a los pasajeros reservar asientos, gestionando la disponibilidad, estados de viaje y un sistema de reputación.

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrese de tener instalado el siguiente software en su entorno Windows 11:

* **Python 3.10 o superior:** Asegúrese de marcar la opción "Add Python to PATH" durante la instalación.
* **PostgreSQL 14 o superior:** Incluyendo la herramienta pgAdmin para la gestión de bases de datos.
* **Git:** Para clonar el repositorio.

## Configuración del Entorno de Desarrollo (Windows 11)

Siga estos pasos de manera secuencial para levantar el proyecto en su máquina local.

### 1. Clonar el repositorio

Abra la terminal (PowerShell o CMD) y ejecute:

```bash
git clone <URL_DEL_REPOSITORIO>
cd URide

```

*(Nota: Reemplace `<URL_DEL_REPOSITORIO>` con la URL real de GitHub).*

### 2. Configuración de la Base de Datos

Antes de ejecutar la aplicación, debe crear la base de datos en PostgreSQL:

1. Abra **pgAdmin** o la consola de `psql`.
2. Cree una nueva base de datos llamada `uride_db`.
3. Tenga a la mano su usuario (generalmente `postgres`) y contraseña locales.

### 3. Crear y activar el entorno virtual

En la raíz del proyecto, ejecute el siguiente comando para aislar las dependencias:

```bash
python -m venv venv

```

Para activar el entorno virtual en **PowerShell** (Windows 11), ejecute:

```powershell
.\venv\Scripts\activate

```

**Nota de resolución de problemas en Windows:** Si PowerShell arroja un error indicando que "la ejecución de scripts está deshabilitada en este sistema", ejecute el siguiente comando como Administrador para otorgar permisos locales y vuelva a intentar la activación:

```powershell
Set-ExecutionPolicy Unrestricted -Scope CurrentUser

```

### 4. Instalación de dependencias

Con el entorno virtual activado (notará un `(venv)` al inicio de su línea de comandos), instale los paquetes requeridos:

```bash
pip install -r requirements.txt

```

### 5. Configuración de Variables de Entorno

El proyecto requiere variables de entorno para proteger credenciales.

1. En la raíz del proyecto, localice el archivo `.env.example`.
2. Haga una copia de este archivo y renómbrela exactamente a `.env`.
3. Abra el archivo `.env` en su editor de código y modifique las variables de la base de datos con sus credenciales locales de PostgreSQL.

Ejemplo de configuración en `.env`:

```env
DB_NAME=uride_db
DB_USER=postgres
DB_PASSWORD=su_contraseña_local
DB_HOST=localhost
DB_PORT=5432

```

### 6. Aplicar Migraciones

Una vez conectada la base de datos, construya la estructura de tablas necesaria ejecutando:

```bash
python manage.py makemigrations
python manage.py migrate

```

### 7. Crear el superusuario (Administrador)

Para acceder al panel de administración de Django, cree una cuenta con privilegios elevados:

```bash
python manage.py createsuperuser

```

Siga las instrucciones en consola para definir correo y contraseña.

### 8. Ejecutar el servidor de desarrollo

Finalmente, inicie el servidor local:

```bash
python manage.py runserver

```

El proyecto estará disponible en su navegador ingresando a: `http://localhost:8000/`. Para acceder al panel de administración, diríjase a `http://localhost:8000/admin/`.

## Estructura Principal del Proyecto

* `comunidad/`: Gestión de reportes, evaluaciones y reputación de usuarios.
* `cuentas/`: Modelo de usuario personalizado, perfiles, registro de vehículos y autenticación.
* `viajes/`: Lógica principal de publicación de rutas, reservas de asientos y control de estados.
* `templates/`: Archivos HTML base y vistas renderizadas con Bootstrap.

## Notas Adicionales para el Equipo

* **Correos Electrónicos:** En el entorno de desarrollo local, el sistema está configurado para imprimir los correos electrónicos (como advertencias o recuperaciones de contraseña) directamente en la consola de la terminal. No se enviarán correos reales a menos que se modifique el `EMAIL_BACKEND` en el archivo `.env`.
* **Archivos Estáticos y Multimedia:** Las imágenes subidas en entorno local se almacenarán en el directorio `/media/`, el cual está excluido del control de versiones.
