from django import forms
from .models import EvaluacionViaje
from .models import Reporte


class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = EvaluacionViaje
        fields = ['calificacion', 'resenia']
        labels = {
            'calificacion': 'Puntuación (1 al 5 Estrellas)',
            'resenia': 'Escribe una breve reseña (Opcional)'
        }
        widgets = {
            'calificacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'resenia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '¿Cómo fue tu experiencia en este viaje?'}),
        }



class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['motivo', 'prueba']
        labels = {
            'motivo': 'Motivo del reporte (Descripción detallada)',
            'prueba': 'Evidencia (Captura o foto opcional)'
        }
        widgets = {
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe qué sucedió durante la coordinación o el viaje...'}),
            'prueba': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }