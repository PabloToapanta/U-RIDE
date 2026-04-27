# cuentas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroEstudianteForm(UserCreationForm):
    class Meta:
        model = Usuario
        # Definimos qué campos aparecerán en el formulario HTML
        # Nota: 'email' es nuestro USERNAME_FIELD
        fields = ('email', 'first_name', 'last_name', 'carrera', 'zona_referencial', 'foto')

