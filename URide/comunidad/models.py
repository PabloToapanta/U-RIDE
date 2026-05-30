from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from viajes.models import Viaje

class EvaluacionViaje(models.Model):
    # Relaciones
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='evaluaciones')
    evaluador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluaciones_dadas')
    evaluado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluaciones_recibidas')
    
    # Datos de la evaluación
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación del 1 al 5"
    )
    resenia = models.TextField(blank=True, null=True, help_text="Comentario opcional sobre el viaje")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        # REGLA DE NEGOCIO: Un usuario solo puede evaluar a otra persona UNA vez por el mismo viaje
        constraints = [
            models.UniqueConstraint(fields=['viaje', 'evaluador', 'evaluado'], name='unica_evaluacion_por_viaje')
        ]

    def __str__(self):
        return f"{self.evaluador.email} calificó a {self.evaluado.email} con {self.calificacion}"


class Reporte(models.Model):
    class EstadoReporte(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de revisión'
        EN_REVISION = 'EN_REVISION', 'En revisión por administrador'
        RESUELTO = 'RESUELTO', 'Caso resuelto'

    # Relaciones
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='reportes_generados')
    reportador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportes_enviados')
    reportado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportes_recibidos')
    
    # Datos del reporte
    fecha = models.DateTimeField(auto_now_add=True)
    estado_reporte = models.CharField(max_length=20, choices=EstadoReporte.choices, default=EstadoReporte.PENDIENTE)
    motivo = models.TextField(help_text="Descripción detallada de la infracción o problema")
    
    # Evidencia (Opcional, porque a veces es un reporte verbal)
    prueba = models.ImageField(upload_to='evidencias_reportes/', blank=True, null=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['viaje', 'reportador', 'reportado'], 
                name='unico_reporte_por_viaje'
            )
        ]
    def __str__(self):
        return f"Reporte de {self.reportador.email} a {self.reportado.email} - {self.get_estado_reporte_display()}"