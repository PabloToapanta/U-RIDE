from django.contrib import admin
from .models import EvaluacionViaje, Reporte

# Registramos el modelo de Reportes
@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    # Columnas que se verán en la tabla principal
    list_display = ('reportador', 'reportado', 'viaje', 'fecha', 'estado_reporte')
    # Filtros laterales para buscar rápidamente
    list_filter = ('estado_reporte', 'fecha')
    # Barra de búsqueda
    search_fields = ('reportador__email', 'reportado__email', 'motivo')
    # Campos que el admin no debería poder modificar (solo leer)
    readonly_fields = ('fecha', 'reportador', 'reportado', 'viaje', 'motivo', 'prueba')

# Registramos el modelo de Evaluaciones (opcional pero útil)
@admin.register(EvaluacionViaje)
class EvaluacionViajeAdmin(admin.ModelAdmin):
    list_display = ('evaluador', 'evaluado', 'viaje', 'calificacion', 'fecha')
    list_filter = ('calificacion', 'fecha')
    search_fields = ('evaluador__email', 'evaluado__email')