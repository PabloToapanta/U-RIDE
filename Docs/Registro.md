# Pasos

Creamos un archivo form.py  utilizando la importacion UserCreationForm

Creamos la vista en views.py   

Aniadimos la url a urls.py

Configuramos el sistema de correo por la terminal, por ello aniadimos esto al archivo settings.py
``` python
# URide/settings.py
# Simulador de correos para entorno de desarrollo local
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin@uride.uta.edu.ec'
```

Modificamos la view registrar para crear el token y la url que se va a enviar al usuario por consola

Aniadimos una funcion de activar cuenta que desencripte el id, verifique el token y si todo es valido, active la cuenta

Actualizamos las urls

``` python
# URide/urls.py
from cuentas import views as cuentas_views

urlpatterns = [
    # ... tus otras rutas (admin, login, logout) ...
    
    path('registro/', cuentas_views.registro, name='registro'),
    
    # Esta es la ruta que atrapa el enlace mágico del correo
    path('activar/<uidb64>/<token>/', cuentas_views.activar_cuenta, name='activar'),
]
```