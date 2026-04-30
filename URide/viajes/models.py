from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

# Create your models here.
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