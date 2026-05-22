from django.urls import path
from . import views

urlpatterns = [
    path('registrar_vehiculo/',views.registrar_vehiculo,name='registro_vehiculo'),
    path('crear_viaje/',views.crear_viaje,name='registro_viaje'),
]
