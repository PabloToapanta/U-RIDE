from django.urls import path
from . import views

urlpatterns = [
    # ... tus otras rutas ...
    path('perfil/<int:usuario_id>/', views.perfil_publico, name='perfil_publico'),
]