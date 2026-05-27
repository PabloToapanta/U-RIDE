from django.urls import path
from . import views

urlpatterns = [
    path('registrar_vehiculo/',views.registrar_vehiculo,name='registro_vehiculo'),
    path('crear_viaje/',views.crear_viaje,name='registro_viaje'),
    path('solicitar/<int:viaje_id>/', views.solicitar_viaje, name='solicitar_viaje'),
    path('mis-viajes/', views.mis_viajes, name='mis_viajes'),
    
    # 1. PRIMERO la ruta específica de cancelar
    path('solicitud/<int:solicitud_id>/cancelar/', views.cancelar_solicitud, name='cancelar_solicitud'), 
    
    # 2. DESPUÉS la ruta con la variable dinámica <str:accion>
    path('solicitud/<int:solicitud_id>/<str:accion>/', views.responder_solicitud, name='responder_solicitud'),
    
    path('viaje/<int:viaje_id>/estado/<str:nuevo_estado>/', views.cambiar_estado_viaje, name='cambiar_estado_viaje'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    
    # Ruta de la Fase 2 (Vista detallada)
    path('viaje/<int:viaje_id>/detalles/', views.detalle_viaje, name='detalle_viaje'),
]