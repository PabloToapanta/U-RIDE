# Autenticacion
En el presente arhcivo se desarrollara el requisito funcional 1 que dicta:
>RF1. Registro e inicio de sesión de estudiantes usando correo institucional (verificación por
>código o enlace).
Pero en principio solo se realizara la autenticacion sin el codigo de verificacion.
Se usara esta [informacion](https://www.geeksforgeeks.org/python/custom-user-models-in-django/)

Los campos de un usuario son los siguientes:
* ID (clave primaria)
* Correo Institucional
* Contrasenia
* Nombre
* Apellido
* Carrera
* Foto
* Telefono
* Zona_Referencia
* es_Conductor
* FECHA_FIN_SUSPENSION

Para la definicion de un usuario se usara la clase [AbstractUser](https://github.com/django/django/blob/017d7f6f12e597e6179de7ffdf330a52c2b22053/django/contrib/auth/models.py#L451) que tiene por defecto los siguientes campos:
* Username
* first_name
* last_name
* email
* password
* is_active
* ID

Los nuevos campos a agregar son:
1. Carrera
2. Foto
3. Zona_Referencia
4. es_Conductor
5. Fecha_fin_suspension

Debemos hacer un pequenio y sobreescribir la clase padre con el fin de cambiar el atributo `USERNAME_FIELD = "username"` a `USERNAME_FIELD = "email"` para que el usuario ingrese con su correo institucional.
El codigo queda de la siguiente forma:

``` python
class Usuario(AbstractUser):

    #Funcion validador de correo
    def validate_email(correo:str):
        if not correo.endswith("@uta.edu.ec"):
            raise ValidationError(
                f"El correo {correo} no termina en @uta.edu.ec",
                params={"correo":correo}
            )
    #Sobreescribimos el atributo email
    email=models.EmailField(validators=[validate_email],unique=True) #Para que no se repitan
    # DEfinimos que el campo para registro sera el email del usuario
    USERNAME_FIELD='email' 
    #Definicion de campos carrera,foto,zona_referencial,es_conductor,fecha_fin_suspension
    carrera=models.CharField(max_length=50)
    foto=models.ImageField(upload_to='perfiles/',null=True,blank=True)
    zona_referencial=models.CharField(max_length=50)
    es_conductor=models.BooleanField(default=False)
    fecha_fin_suspension=models.DateField(null=True,blank=True) #SOLO FECHA, NO HORA

    #QUITAMOS ATRIBUTO USERNAME
    username=None
    #Evitar error de sobreescritura
    REQUIRED_FIELDS = []
```
Para procesar imagenes, se usa el campo ImageField, pero debemos hacer algunos [pasos](https://mjoghenemaega.hashnode.dev/django-imagefield-easy-steps-to-use-it-in-your-model?__cf_chl_tk=9lRIHHIh27B5ZpIEPs1ig6MWH6Y28fQZTczFwzubHKY-1777150510-1.0.1.1-37eFX1N1ZEFFis_Rsyr1EqhntW7kM01zItYcW6vPvkU
)

1. Instalar pillow para procesar imagenes con `pip install pillow`
2. Confugurar el modelo 
3. Configurar settings.py y agrega lo siguiente
``` python
# 1. MEDIA_URL: Es el link público. Si alguien quiere ver la foto, la URL empezará así.
MEDIA_URL = '/media/'

# 2. MEDIA_ROOT: Es la ruta física real 
# Le dice: "Crea una carpeta llamada 'media' justo al lado del archivo manage.py"
MEDIA_ROOT = BASE_DIR / 'media'
```
3. Asignar una url a cada imagen y que se muestre cuando se este en modo desarollo
``` python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Creacion de usuarios
Sobrescritura del Gestor de Usuarios (BaseUserManager)

La necesidad de implementar un gestor de usuarios personalizado en el marco de trabajo de Django radica en la disociación estructural entre la capa del modelo de datos y la capa de instanciación de objetos. Al extender la clase `AbstractUser` para reemplazar el identificador clásico por defecto (`username`) y establecer el correo electrónico institucional como la credencial principal de acceso (`USERNAME_FIELD = 'email'`), se modifica exitosamente la representación de la entidad en la base de datos. No obstante, el manejador de base de datos predeterminado (`UserManager`), el cual orquesta las operaciones de creación mediante la interfaz de línea de comandos (CLI), conserva en su código base la exigencia del atributo `username` como argumento posicional estricto. Por consiguiente, para garantizar la cohesión arquitectónica y evitar excepciones de tipo `TypeError` durante el despliegue y administración del sistema, resulta un requerimiento técnico imperativo sobrescribir los métodos `create_user` y `create_superuser`. Esta reestructuración asegura que la lógica de persistencia se alinee íntegramente con las restricciones del dominio del negocio de *U-Ride*, eliminando dependencias obsoletas y validando el correo electrónico como identificador único y absoluto desde el momento de la instanciación.

## INTERFAZ GRAFICA

Para iniciar con la vista, creamos una carpeta llamada `templates` y le avisamos a django que en esa carpeta van a estar las plantillas

``` python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Seguido esto, creamos el arhcivo `base.html` la cual funcionara como plantilla generica para todo el proyecto.

### Base.html
Para la elaboracion, utilizamos BootStrap via CDN y aplicamos una (navbar)[https://getbootstrap.com/docs/4.0/components/navbar/]

#### Login.html
Primero configuramos la url de un login en urls.py
``` python
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/'),auth_views.LoginView.as_view(template_name='login.html',name='login'),
]
```

Despues aniadimos el codigo a login.html

Seguido de esto aniadimos estos ajustes a settings.py para que cuando un usuario ingrese, se lo redirija a la URL correcta

``` python
# URide/settings.py
LOGIN_REDIRECT_URL = '/'  # Después del login, llévalo al Home
LOGOUT_REDIRECT_URL = '/login/' # Después de cerrar sesión, llévalo al login
```

Con esto ya tenemos el modulo para iniciar secion

##### Cerrar Sesion
Para cerrar secion, las versiones modernas de django exigen  que se hagan con los metodos POST, por ello primero aniadimos la ruta de salida
``` python
path('logout/', auth_views.LogoutView.as_view(), name='logout'),
```
Y cambiamos el enlace simbolico de cerrar secion con un formulario:
``` python 
<form action="{% url 'logout' %}" method="post" class="d-inline">
    {% csrf_token %}
    <button type="submit" class="nav-link text-danger border-0 bg-transparent">Cerrar Sesión</button>
</form>
```