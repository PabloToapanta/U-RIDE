# cuentas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroEstudianteForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Definimos qué campos aparecerán en el formulario HTML
        # Nota: 'email' es nuestro USERNAME_FIELD
        fields = (
            "email",
            "first_name",
            "last_name",
            "carrera",
            "zona_referencial",
            "foto",
        )


class PerfilEstudianteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            "first_name",
            "last_name",
            "carrera",
            "zona_referencial",
            "numero_contacto",
            "foto",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
