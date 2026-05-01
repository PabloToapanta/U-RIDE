from django.urls import path
from . import views

urlpatterns = [
    path('registrar/',views.registrar_vehiculo,name='registro_vehiculo'),
]
