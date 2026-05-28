# Create your views here.
# vehiculos/views.py
from cuentas.models import Usuario
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
import logging

from .forms import VehiculoForm,ViajeForm
from .models import Vehiculo,Viaje,Solicitud

# Invocamos el logger para cumplir con el RNF4 (Trazabilidad)
logger = logging.getLogger('trazabilidad')

@login_required
def registrar_vehiculo(request):
    # Verificar si el usuario ya tiene un vehículo registrado
    if hasattr(request.user, "vehiculo"):
        messages.warning(
            request, "Ya tienes un vehículo registrado. Solo puedes tener uno."
        )
        return redirect("home") 

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
            return redirect("perfil")
    else:
        form = VehiculoForm()

    return render(request, "registrar_vehiculo.html", {"form": form})


def home(request):
    ahora = timezone.now()
    
    # 1. Obtenemos TODOS los viajes disponibles
    viajes_disponibles = Viaje.objects.filter(
        asientos_disponibles__gt=0,
        fecha_hora_salida__gte=ahora
    ).order_by('fecha_hora_salida')
    
    # 2. Capturamos los parámetros
    origen_buscado = request.GET.get('origen')
    destino_buscado = request.GET.get('destino')
    fecha_buscada = request.GET.get('fecha')
    asientos_buscados = request.GET.get('asientos') 
    
    # 3. Aplicamos filtros
    if origen_buscado:
        viajes_disponibles = viajes_disponibles.filter(zona_origen__icontains=origen_buscado)
        
    if destino_buscado:
        viajes_disponibles = viajes_disponibles.filter(zona_destino__icontains=destino_buscado)
        
    if fecha_buscada:
        viajes_disponibles = viajes_disponibles.filter(fecha_hora_salida__date=fecha_buscada)

    # 4. NUEVO FILTRO: ASIENTOS (Mayor o igual que)
    if asientos_buscados:
        try:
            asientos_num = int(asientos_buscados)
            # __gte significa Greater Than or Equal (Mayor o igual a)
            viajes_disponibles = viajes_disponibles.filter(asientos_disponibles__gte=asientos_num)
        except ValueError:
            pass
    
    # 5. Empacamos los viajes y los filtros usados
    contexto = {
        'viajes': viajes_disponibles,
        'filtros': {
            'origen': origen_buscado,
            'destino': destino_buscado,
            'fecha': fecha_buscada,
            'asientos': asientos_buscados, 
        }
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
            nuevo_viaje.save()

            # RNF4: Registro de publicación de un nuevo viaje
            logger.info(f"[NUEVO VIAJE] El conductor {request.user.email} publicó el Viaje #{nuevo_viaje.id} de {nuevo_viaje.zona_origen} a {nuevo_viaje.zona_destino}.")

            messages.success(request,'Viaje creado con exito')
            return redirect('home')
    else:
        form = ViajeForm(usuario=request.user)
    
    return render(request,'crear_viaje.html',{'form':form})

@login_required
def solicitar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)

    if request.user == viaje.auto.duenio:
        messages.error(request, "No puedes unirte a tu propio viaje.")
        return redirect('home')

    if viaje.asientos_disponibles <= 0:
        messages.error(request, "Lo sentimos, este viaje ya está lleno.")
        return redirect('home')

    solicitud_existente = Solicitud.objects.filter(viaje=viaje, pasajero=request.user).first()
    
    if solicitud_existente:
        if solicitud_existente.estado_solicitud == 'EN_ESPERA':
            messages.warning(request, "Ya enviaste una solicitud para este viaje. Espera a que el conductor responda.")
        elif solicitud_existente.estado_solicitud == 'APROBADA':
            messages.info(request, "¡Ya tienes un asiento asegurado en este viaje!")
        else:
            messages.error(request, "No puedes volver a solicitar unirte a este viaje.")
        return redirect('home')

    nueva_solicitud = Solicitud.objects.create(
        viaje=viaje,
        pasajero=request.user,
        estado_solicitud=Solicitud.EstadoSolicitud.EN_ESPERA
    )

    # RNF4: Registro de nueva solicitud
    logger.info(f"[SOLICITUD] El pasajero {request.user.email} solicitó unirse al Viaje #{viaje.id} (Solicitud #{nueva_solicitud.id}).")

    messages.success(request, f"Solicitud enviada al conductor. Te notificaremos cuando te acepte.")
    return redirect('home')

@login_required
def mis_viajes(request):
    if not request.user.es_conductor:
        messages.warning(request, "Debes registrar un vehículo para acceder al panel de conductor.")
        return redirect('home')

    solicitudes_en_espera = Solicitud.objects.filter(estado_solicitud=Solicitud.EstadoSolicitud.EN_ESPERA)
    solicitudes_aprobadas = Solicitud.objects.filter(estado_solicitud=Solicitud.EstadoSolicitud.APROBADA)

    viajes_del_conductor = Viaje.objects.filter(
        auto__duenio=request.user
    ).prefetch_related(
        Prefetch('solicitudes', queryset=solicitudes_en_espera, to_attr='solicitudes_pendientes'),
        Prefetch('solicitudes', queryset=solicitudes_aprobadas, to_attr='pasajeros_confirmados') 
    ).order_by('-fecha_hora_salida')

    return render(request, 'mis_viajes.html', {'viajes': viajes_del_conductor})

@login_required
def responder_solicitud(request, solicitud_id, accion):
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        viaje = solicitud.viaje

        if request.user != viaje.auto.duenio:
            messages.error(request, "No tienes permiso para moderar este viaje.")
            return redirect('mis_viajes')

        if viaje.esta_expirado:
            messages.error(request, "Este viaje ha expirado. Ya no puedes aceptar ni rechazar pasajeros.")
            return redirect('mis_viajes')

        if solicitud.estado_solicitud != Solicitud.EstadoSolicitud.EN_ESPERA:
            messages.warning(request, "Esta solicitud ya fue procesada anteriormente.")
            return redirect('mis_viajes')

        # LÓGICA DE ACEPTAR
        if accion == 'aceptar':
            if viaje.asientos_disponibles > 0:
                solicitud.estado_solicitud = Solicitud.EstadoSolicitud.APROBADA
                viaje.asientos_disponibles -= 1  
                solicitud.save()
                viaje.save()
                
                # RNF4: Registro de solicitud aceptada
                logger.info(f"[PASAJERO ACEPTADO] El conductor {request.user.email} ACEPTÓ la Solicitud #{solicitud.id} del pasajero {solicitud.pasajero.email} para el Viaje #{viaje.id}.")

                messages.success(request, f"¡Has aceptado a {solicitud.pasajero.email} en tu viaje!")
            else:
                messages.error(request, "Ya no tienes asientos disponibles para este viaje.")

        # LÓGICA DE RECHAZAR
        elif accion == 'rechazar':
            solicitud.estado_solicitud = Solicitud.EstadoSolicitud.RECHAZADA
            solicitud.save() 
            
            # RNF4: Registro de solicitud rechazada
            logger.info(f"[PASAJERO RECHAZADO] El conductor {request.user.email} RECHAZÓ la Solicitud #{solicitud.id} del pasajero {solicitud.pasajero.email} para el Viaje #{viaje.id}.")
            
            messages.info(request, "Solicitud rechazada correctamente.")

    return redirect('mis_viajes')

@login_required
def cambiar_estado_viaje(request, viaje_id, nuevo_estado):
    if request.method == 'POST':
        viaje = get_object_or_404(Viaje, id=viaje_id)
        estado_anterior = viaje.get_estado_viaje_display() # Guardamos el estado anterior para el log
        
        if request.user != viaje.auto.duenio:
            messages.error(request, "No tienes permiso para alterar este viaje.")
            return redirect('mis_viajes')
            
        if nuevo_estado == 'EN_CURSO' and not viaje.puede_iniciarse:
            messages.error(request, "Solo puedes iniciar el viaje 15 minutos antes de la hora programada.")
            return redirect('mis_viajes')

        estados_validos = [est[0] for est in Viaje.EstadoViaje.choices]
        if nuevo_estado in estados_validos:
            viaje.estado_viaje = nuevo_estado
            viaje.save()
            
            # RNF4: Registro de cambio de estado del viaje
            logger.info(f"[ESTADO VIAJE] El Viaje #{viaje.id} cambió de {estado_anterior} a {viaje.get_estado_viaje_display()} por el conductor {request.user.email}.")
            
            messages.success(request, f"Estado del viaje actualizado a: {viaje.get_estado_viaje_display()}")
            
    return redirect('mis_viajes')

@login_required
def mis_reservas(request):
    solicitudes = Solicitud.objects.filter(
        pasajero=request.user
    ).select_related(
        'viaje', 'viaje__auto', 'viaje__auto__duenio'
    ).order_by('-viaje__fecha_hora_salida')

    return render(request, 'mis_reservas.html', {'solicitudes': solicitudes})

@login_required
def cancelar_solicitud(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        viaje = solicitud.viaje

        if request.user != solicitud.pasajero:
            messages.error(request, "No tienes permiso para alterar esta reserva.")
            return redirect('mis_reservas')

        if viaje.estado_viaje != Viaje.EstadoViaje.NO_INICIADO or viaje.esta_expirado:
            messages.error(request, "No puedes cancelar la reserva de un viaje que ya pasó o está en curso.")
            return redirect('mis_reservas')

        if solicitud.estado_solicitud == Solicitud.EstadoSolicitud.CANCELADA:
            messages.warning(request, "Esta solicitud ya fue cancelada anteriormente.")
            return redirect('mis_reservas')

        if solicitud.estado_solicitud == Solicitud.EstadoSolicitud.APROBADA:
            viaje.asientos_disponibles += 1  
            viaje.save()

        solicitud.estado_solicitud = Solicitud.EstadoSolicitud.CANCELADA
        solicitud.save()

        # RNF4: Registro de reserva cancelada
        logger.info(f"[RESERVA CANCELADA] El pasajero {request.user.email} CANCELÓ su reserva (Solicitud #{solicitud.id}) para el Viaje #{viaje.id}.")

        messages.success(request, "Has cancelado tu reserva con éxito. El asiento ha sido liberado.")
        
    return redirect('mis_reservas')

@login_required
def detalle_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje.objects.select_related('auto', 'auto__duenio'), id=viaje_id)
    solicitud_previa = Solicitud.objects.filter(viaje=viaje, pasajero=request.user).first()
    
    contexto = {
        'viaje': viaje,
        'solicitud_previa': solicitud_previa
    }
    
    return render(request, 'detalle_viaje.html', contexto)