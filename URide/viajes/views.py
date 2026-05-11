# Create your views here.
# vehiculos/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import VehiculoForm
from .models import Vehiculo
from cuentas.models import Usuario

@login_required
def registrar_vehiculo(request):
    # Verificar si el usuario ya tiene un vehículo registrado
    if hasattr(request.user, 'vehiculo'):
        messages.warning(request, 'Ya tienes un vehículo registrado. Solo puedes tener uno.')
        return redirect('home')  # VIsta home aun por implementar
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            # 1. Guardar temporalmente usando commit=False
            vehiculo = form.save(commit=False)
            
            # 2. Asignar el dueño (usuario logueado)
            vehiculo.duenio = request.user  
            
            # 3. Guardar el vehículo en la base de datos
            vehiculo.save()
            
            # 4. ACTUALIZAR el atributo es_conductor del usuario a True
            request.user.es_conductor = True
            request.user.save()  # Importante: guardar los cambios
            
            # 5. Mensaje de éxito
            messages.success(request, '¡Vehículo registrado exitosamente! Ahora eres conductor.')
            
            # 6. Redirigir a donde quieras (perfil, crear viaje, etc.)
            return redirect('perfil')  # O 'crear_viaje', 'dashboard_conductor', etc.
    else:
        form = VehiculoForm()
    
    return render(request, 'registrar_vehiculo.html', {'form': form})