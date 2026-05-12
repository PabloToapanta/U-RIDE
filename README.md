Entendido. He reestructurado la documentación utilizando un lenguaje técnico formal acorde al nivel académico del proyecto, pero manteniendo una redacción clara que facilite la comprensión de la arquitectura para el resto del equipo.

Aquí tienes el contenido en formato Markdown crudo:

```markdown
# U-Ride: Documentación Técnica de la Plataforma de Movilidad Estudiantil

## 1. Introducción
U-Ride es una solución tecnológica desarrollada para optimizar el transporte de la comunidad universitaria de la Universidad Técnica de Ambato (UTA). El sistema permite el intercambio de rutas de transporte entre estudiantes, fomentando la seguridad y la eficiencia económica mediante un modelo de economía colaborativa.

## 2. Especificaciones Tecnológicas
La arquitectura del sistema se fundamenta en las siguientes tecnologías:
* **Lenguaje de Programación:** Python 3.12 o superior.
* **Framework Web:** Django 5.x.
* **Sistema de Gestión de Base de Datos:** PostgreSQL.
* **Procesamiento de Imágenes:** Biblioteca Pillow.
* **Frontend:** Framework Bootstrap 5.3 mediante red de entrega de contenidos (CDN).

## 3. Arquitectura del Proyecto
El proyecto sigue el patrón arquitectónico de Django, organizando la lógica de negocio en aplicaciones modulares:

* **Aplicación 'cuentas':** Gestiona la identidad digital de los usuarios. Incluye la extensión del modelo de usuario base, validaciones de dominio institucional y flujos de seguridad (registro, activación y recuperación de credenciales).
* **Aplicación 'viajes':** Administra los recursos vehiculares y la lógica de publicación de rutas. Controla la transición de estados de un estudiante a conductor una vez validado su vehículo.
* **Templates:** Directorio centralizado que almacena la interfaz de usuario, garantizando la consistencia visual mediante el uso de plantillas base.

## 4. Guía de Despliegue en Entorno de Desarrollo

### 4.1. Configuración del Entorno Virtual
Es obligatorio aislar las dependencias del proyecto para evitar conflictos de versiones.

1. Clonar el repositorio institucional.
2. Ejecutar la creación del entorno: `python -m venv venv`.
3. Activar el entorno según el sistema operativo:
   - Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Instalar las dependencias requeridas: `pip install -r requirements.txt`.

### 4.2. Configuración de la Base de Datos (PostgreSQL)
Se debe garantizar que el servicio de PostgreSQL esté operativo antes de ejecutar los siguientes comandos en la consola de psql o pgAdmin:

```sql
CREATE DATABASE uride_db;
CREATE USER uride_admin WITH PASSWORD 'clave_de_seguridad';
GRANT ALL PRIVILEGES ON DATABASE uride_db TO uride_admin;
ALTER DATABASE uride_db OWNER TO uride_admin;

```

## 5. Fundamentos Técnicos del Desarrollo

### 5.1. Modelo de Usuario Personalizado

Para cumplir con los Requerimientos Funcionales (RF1), se optó por extender la clase `AbstractUser`. La modificación principal radica en el desplazamiento del atributo `username` por el `email` como identificador único de acceso (USERNAME_FIELD).

Se implementó un validador de dominio estricto que asegura que solo direcciones terminadas en `@uta.edu.ec` puedan persistir en la base de datos. Asimismo, fue necesario sobrescribir el `BaseUserManager` para alinear los métodos de creación de usuarios (CLI) con la nueva estructura de credenciales.

### 5.2. Gestión de la Capa de Datos (Modelos)

* **Usuario:** Extiende los campos base para incluir carrera, zona referencial, fotografía y estado de suspensión.
* **Vehículo:** Establece una relación uno a uno (OneToOneField) con el usuario, asegurando la integridad referencial donde cada conductor solo puede tener un vehículo asociado en el sistema.

### 5.3. Flujo de Comunicación (Request/Response)

El sistema opera bajo el protocolo HTTP, donde Django procesa los objetos `request`.

* Las peticiones **GET** se destinan a la recuperación de interfaces (ej. carga del formulario de perfil).
* Las peticiones **POST** se utilizan para la transmisión de datos sensibles y archivos multimedia (ej. actualización de datos o registro de vehículos), requiriendo siempre la validación del token CSRF por seguridad.

## 6. Seguridad y Validación

El sistema incorpora un flujo de activación mediante tokens criptográficos de un solo uso. Tras el registro, la cuenta permanece en estado inactivo hasta que el usuario valida su identidad a través de un enlace enviado a su correo institucional. Este mismo mecanismo se emplea para el módulo de recuperación de contraseñas, garantizando que el acceso al sistema sea exclusivo y seguro.


