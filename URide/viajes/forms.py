from django import forms
from .models import Vehiculo

class VehiculoForm(forms.ModelForm):
    class Meta:
        model=Vehiculo
        fields=['marca','modelo','anio','color','placa','max_capacidad']
            # Widgets para aplicar clases de Bootstrap
        widgets = {
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Toyota, Chevrolet, Kia'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Corolla, Spark, Cerato'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Rojo, Azul, Blanco'
            }),
            'placa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ABC-1234',
                'style': 'text-transform: uppercase'  # Convertir a mayúsculas
            }),
            'max_capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 6
            }),
        }
    
    # Limpiar y formatear la placa a mayúsculas
    def clean_placa(self):
        placa = self.cleaned_data['placa']
        return placa.upper().strip()