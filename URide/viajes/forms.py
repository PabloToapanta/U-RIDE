from django import forms
from .models import Vehiculo,Viaje
from django.utils import timezone
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
        model = Viaje
        fields = ['zona_origen', 'zona_destino', 'fecha_hora_salida','precio','asientos_disponibles','notas']
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
                'type': 'datetime-local' 
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',  # Permite subir/bajar de a 1 centavo
                'min': '0.00',   # No hay precios negativos
                'placeholder': 'Ej: 1.50'
            }),
            'asientos_disponibles': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 6
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  # Define la altura inicial del cuadro
                'placeholder': 'Ej: Máximo 5 min de espera, no comer en el vehículo, llevar suelto para el aporte...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None) 
        super().__init__(*args, **kwargs)

    # NUEVO: Escudo contra viajes en el tiempo
    def clean_fecha_hora_salida(self):
        fecha = self.cleaned_data.get('fecha_hora_salida')
        
        # timezone.now() obtiene la fecha y hora exacta del sistema en este instante
        if fecha and fecha < timezone.now():
            raise forms.ValidationError("Error: No puedes programar un viaje en el pasado. Por favor, selecciona una fecha y hora futura.")
            
        return fecha

    def clean_asientos_disponibles(self):
        asientos = self.cleaned_data.get('asientos_disponibles')
        if self.usuario and hasattr(self.usuario, 'vehiculo'):
            capacidad_maxima = self.usuario.vehiculo.max_capacidad
            if asientos > capacidad_maxima:
                raise forms.ValidationError(f"Error: Tu vehículo (placa {self.usuario.vehiculo.placa}) solo tiene capacidad para {capacidad_maxima} pasajeros.")
        return asientos