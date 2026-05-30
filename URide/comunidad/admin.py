from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Reporte, EvaluacionViaje
# Registramos el modelo de Reportes


# Registramos el modelo de Evaluaciones (opcional pero útil)
@admin.register(EvaluacionViaje)
class EvaluacionViajeAdmin(admin.ModelAdmin):
    list_display = ('evaluador', 'evaluado', 'viaje', 'calificacion', 'fecha')
    list_filter = ('calificacion', 'fecha')
    search_fields = ('evaluador__email', 'evaluado__email')




@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    # Columnas que verá el administrador en la tabla
    list_display = ('id', 'viaje', 'reportador', 'reportado', 'estado_reporte', 'fecha')
    
    # Filtros laterales
    list_filter = ('estado_reporte', 'fecha')
    
    # Buscador superior
    search_fields = ('reportador__email', 'reportado__email', 'motivo')

    readonly_fields = ('fecha', 'reportador', 'reportado', 'viaje', 'motivo', 'prueba')

    
    # NUEVO: Registramos nuestra acción personalizada
    actions = ['enviar_advertencia']

    @admin.action(description=' Enviar correo de ADVERTENCIA al usuario reportado')
    def enviar_advertencia(self, request, queryset):
        """
        Esta función se ejecuta cuando el admin selecciona uno o varios reportes
        y elige la acción de enviar advertencia.
        """
        correos_enviados = 0
        
        for reporte in queryset:
            # 1. Armamos el correo
            asunto = f" ADVERTENCIA OFICIAL U-RIDE: Reporte de conducta en viaje {reporte.viaje.id}"
            mensaje = (
                f"Hola {reporte.reportado.get_full_name() or reporte.reportado.email},\n\n"
                f"La administración de U-Ride ha revisado un reporte en tu contra respecto a tu "
                f"conducta en el viaje de {reporte.viaje.zona_origen} a {reporte.viaje.zona_destino}.\n\n"
                f"Motivo del reporte: {reporte.motivo}\n\n"
                f"Te recordamos que el incumplimiento continuo de las reglas de seguridad y convivencia "
                f"resultará en la suspensión temporal o definitiva de tu cuenta en la plataforma.\n\n"
                f"Atentamente,\nEl equipo de Administración de U-Ride"
            )
            
            # 2. Enviamos el correo usando el motor de Django
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reporte.reportado.email],
                fail_silently=False,
            )
            
            # 3. Cambiamos el estado del reporte a resuelto en PostgreSQL
            reporte.estado_reporte = Reporte.EstadoReporte.RESUELTO
            reporte.save()
            
            correos_enviados += 1
        
        # 4. Mostramos mensaje de éxito verde en el panel admin
        self.message_user(request, f"Se enviaron {correos_enviados} advertencias por correo y los reportes pasaron a estado RESUELTO.")