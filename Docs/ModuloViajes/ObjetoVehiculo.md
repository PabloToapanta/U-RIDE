# Objeto Vehiculo

Para crear primero creamos nuestra aplicacion donde vamos a contener toda la logica de negocio

``` bash
python manage.py startapp viajes
```

Despues de esto la registramos en nuestros settings:
``` python
INSTALLED_APPS = [
    'viajes.apps.ViajesConfig', #<---Aqui la anidadimos
    'cuentas.apps.CuentasConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

## Creacion del modelo
La creacion de nuestro modelo vienen dada por

``` python
class Vehiculo(models.Model):
    #Relacion uno a uno
    duenio=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)  
    # En settings AUTH_USER_MODEL='cuentas.Usuario'  
    marca=models.CharField(max_length=50)
    modelo=models.CharField( max_length=50)
    anio=models.PositiveSmallIntegerField(validators=[MinValueValidator(1800),MaxValueValidator(3000)])
    color=models.CharField( max_length=50)
    placa=models.CharField( max_length=50, unique=True)
    max_capacidad=models.PositiveSmallIntegerField(validators=[MinValueValidator(2),MaxValueValidator(6)])
```

Una vez hecho esto, procedi a realizar laz migraciones y migrarlo a la base de datos

Bug a arreglar: ¿Qué pasa si un conductor registra un vehículo tipo sedán pequeño con max_capacidad=3, y luego intenta publicar un viaje diciendo que tiene asientos_disponibles=6?
A nivel de tu tabla actual en PostgreSQL, el sistema se lo va a permitir, ¡porque 6 está dentro del límite de MinValueValidator(2) y MaxValueValidator(6)!