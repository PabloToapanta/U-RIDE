# Create your views here.
# vehiculos/views.py
from cuentas.models import Usuario
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.utils import timezone

from .forms import VehiculoForm,ViajeForm
from .models import Vehiculo,Viaje


@login_required
def registrar_vehiculo(request):
    # Verificar si el usuario ya tiene un vehículo registrado
    if hasattr(request.user, "vehiculo"):
        messages.warning(
            request, "Ya tienes un vehículo registrado. Solo puedes tener uno."
        )
        return redirect("home")  # VIsta home aun por implementar

    if request.method == "POST":
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
            messages.success(
                request, "¡Vehículo registrado exitosamente! Ahora eres conductor."
            )

            # 6. Redirigir a donde quieras (perfil, crear viaje, etc.)
            return redirect("perfil")  # O 'crear_viaje', 'dashboard_conductor', etc.
    else:
        form = VehiculoForm()

    return render(request, "registrar_vehiculo.html", {"form": form})


def home(request):
    # 2. Obtenemos la fecha y hora exacta de este mismo instante
    ahora = timezone.now()
    
    # 3. Añadimos el filtro fecha_hora_salida__gte (Greater Than or Equal -> Mayor o igual que)
    viajes_disponibles = Viaje.objects.filter(
        asientos_disponibles__gt=0,
        fecha_hora_salida__gte=ahora  # <--- LA NUEVA REGLA DE TIEMPO
    ).order_by('fecha_hora_salida')
    
    contexto = {
        'viajes': viajes_disponibles
    }
    
    return render(request, 'home.html', contexto)

@login_required
def crear_viaje(request):
    if not request.user.es_conductor:
        messages.error(request, 'Acceso denegado: Debes registrar un vehículo para publicar viajes.')
        return redirect("home")
    
    if request.method == 'POST':
        form = ViajeForm(request.POST, usuario=request.user)
        if form.is_valid():
            nuevo_viaje=form.save(commit=False)
            nuevo_viaje.auto=request.user.vehiculo
            #Aqui no puse el estado viaje porque en el modelo esta como default NO_INICIADO

            nuevo_viaje.save()

            messages.success(request,'Viaje creado con exito')
            return redirect('home')
    else:
        form = ViajeForm(usuario=request.user)
    
    return render(request,'crear_viaje.html',{'form':form})