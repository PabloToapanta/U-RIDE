from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

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
        NO_INICIADO = "NO_INICIADO", 'No iniciado'
        EN_CURSO = 'EN_CURSO', 'En curso'
        FINALIZADO = 'FINALIZADO', 'Finalizado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        
    estado_viaje = models.CharField(
        max_length=20,
        choices=EstadoViaje.choices,
        default=EstadoViaje.NO_INICIADO
    )
    auto = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    zona_origen = models.CharField(max_length=50)
    zona_destino = models.CharField(max_length=50)
    fecha_hora_salida = models.DateTimeField(
        verbose_name="Fecha y hora de salida",
        help_text="Formato: DD/MM/YYYY HH:MM"
    )
    
    # Ajustamos el validador mínimo a 1
    asientos_disponibles = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    
    @property
    def puede_iniciarse(self):
        """Devuelve True solo si estamos en la ventana de tiempo permitida."""
        ahora = timezone.now()
        inicio_ventana = self.fecha_hora_salida - timedelta(minutes=15) # 15 min antes
        fin_ventana = self.fecha_hora_salida + timedelta(minutes=30)    # 30 min después (tolerancia)
        
        return inicio_ventana <= ahora <= fin_ventana and self.estado_viaje == self.EstadoViaje.NO_INICIADO

    @property
    def esta_expirado(self):
        """Expira únicamente cuando se acaba la ventana de tolerancia y no se inició."""
        fin_ventana = self.fecha_hora_salida + timedelta(minutes=30)
        return timezone.now() > fin_ventana and self.estado_viaje == self.EstadoViaje.NO_INICIADO

    def __str__(self):
        return f"Viaje {self.id} - {self.zona_origen} -> {self.zona_destino} - {self.fecha_hora_salida}"


class Solicitud(models.Model):
    # Definimos el ENUM de estados que tenías en tu DBML
    class EstadoSolicitud(models.TextChoices):
        EN_ESPERA = 'EN_ESPERA', 'En espera'
        CANCELADA = 'CANCELADA', 'Cancelada' # Si el pasajero se arrepiente
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada' # Añadí este para que el conductor pueda decir "No"

    # Relaciones (Foreign Keys)
    viaje = models.ForeignKey(
        Viaje, 
        on_delete=models.CASCADE, 
        related_name='solicitudes'
    )
    pasajero = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='solicitudes_enviadas'
    )
    
    # Atributos
    estado_solicitud = models.CharField(
        max_length=20,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.EN_ESPERA
    )
    # auto_now_add=True captura la fecha y hora exacta en la que se crea el registro
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Esta regla de la base de datos garantiza que 
        # un pasajero NO pueda enviar más de una solicitud al mismo viaje.
        unique_together = ('viaje', 'pasajero')

    def __str__(self):
        return f"Solicitud: {self.pasajero.email} -> Viaje {self.viaje.id} ({self.estado_solicitud})"
    