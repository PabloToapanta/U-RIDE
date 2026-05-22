from django import forms
from .models import Vehiculo,Viaje

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
    
class ViajeForm(forms.ModelForm):
    class Meta:
        model=Viaje
        fields=['zona_origen','zona_destino','fecha_hora_salida','asientos_disponibles']
        # Añadimos los widgets para Bootstrap y el selector de fecha
        widgets = {
            'zona_origen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ficoa, Huachi, Izamba'
            }),
            'zona_destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Campus Huachi, Campus Ingahurco'
            }),
            'fecha_hora_salida': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'  # ¡Esto invoca el calendario interactivo del navegador!
            }),
            'asientos_disponibles': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 6
            }),
        }
    # 1. Interceptamos la creación del formulario para recibir al usuario
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None) # Extraemos el usuario
        super().__init__(*args, **kwargs)

    # 2. Validación exclusiva para este campo
    def clean_asientos_disponibles(self):
        asientos = self.cleaned_data.get('asientos_disponibles')
        
        # Revisamos la capacidad del auto del usuario que recibimos
        if self.usuario and hasattr(self.usuario, 'vehiculo'):
            capacidad_maxima = self.usuario.vehiculo.max_capacidad
            
            if asientos > capacidad_maxima:
                # Esto es lo que hará que el texto rojo aparezca en HTML
                raise forms.ValidationError(f"Error: Tu vehículo (placa {self.usuario.vehiculo.placa}) solo tiene capacidad para {capacidad_maxima} pasajeros.")
                
        return asientos