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

class Viaje(models.Model):
    class EstadoViaje(models.TextChoices):
        NO_INICIADO="NO_INICIADO",'No iniciado'
        EN_CURSO='EN_CURSO','En curso'
        FINALIZADO='FINALIZADO','Finalizado'
        CANCELADO='CANCELADO','Cancelado'
    estado_viaje=models.CharField(max_length=20,choices=EstadoViaje.choices,default=EstadoViaje.NO_INICIADO)
    auto=models.ForeignKey(Vehiculo,on_delete=models.CASCADE)
    zona_origen=models.CharField( max_length=50)
    zona_destino=models.CharField( max_length=50)
    fecha_hora_salida=models.DateTimeField(verbose_name="Fecha y hora de salida",help_text="Formato: DD/MM/YYYY HH:MM")
    asientos_disponibles=models.PositiveSmallIntegerField(validators=[MinValueValidator(2),MaxValueValidator(6)])
    def __str__(self):
        return f"Viaje {self.id} - {self.zona_origen} -> {self.zona_destino} - {self.fecha_hora_salida}"
