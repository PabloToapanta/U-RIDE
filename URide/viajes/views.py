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

from .forms import VehiculoForm,ViajeForm
from .models import Vehiculo,Viaje,Solicitud


@login_required
def registrar_vehiculo(request):
    # Verificar si el usuario ya tiene un vehículo registrado
    if hasattr(request.user, "vehiculo"):
        messages.warning(
            request, "Ya tienes un vehículo registrado. Solo puedes tener uno."
        )
        return redirect("home")  # VIsta home aun por implementa

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
    asientos_buscados = request.GET.get('asientos') # <--- CAPTURAMOS EL NUEVO CAMPO
    
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
            # Si alguien escribe ?asientos=hola en la URL, simplemente lo ignoramos para evitar que la página se rompa
            pass
    
    # 5. Empacamos los viajes y los filtros usados
    contexto = {
        'viajes': viajes_disponibles,
        'filtros': {
            'origen': origen_buscado,
            'destino': destino_buscado,
            'fecha': fecha_buscada,
            'asientos': asientos_buscados, # <--- LO ENVIAMOS AL HTML
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
            #Aqui no puse el estado viaje porque en el modelo esta como default NO_INICIADO

            nuevo_viaje.save()

            messages.success(request,'Viaje creado con exito')
            return redirect('home')
    else:
        form = ViajeForm(usuario=request.user)
    
    return render(request,'crear_viaje.html',{'form':form})

@login_required
def solicitar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)

    # REGLA 1: El conductor no puede solicitar un asiento en su propio auto
    if request.user == viaje.auto.duenio:
        messages.error(request, "No puedes unirte a tu propio viaje.")
        return redirect('home')

    # REGLA 2: No permitir sobrecupo (aunque el asiento no se reste aún, 
    # no tiene sentido dejar que soliciten si ya no hay espacio físico)
    if viaje.asientos_disponibles <= 0:
        messages.error(request, "Lo sentimos, este viaje ya está lleno.")
        return redirect('home')

    # REGLA 3: Evitar solicitudes duplicadas
    # Buscamos si ya existe una solicitud de este usuario para este viaje
    solicitud_existente = Solicitud.objects.filter(viaje=viaje, pasajero=request.user).first()
    
    if solicitud_existente:
        # Si ya existe, le avisamos en qué estado está
        if solicitud_existente.estado_solicitud == 'EN_ESPERA':
            messages.warning(request, "Ya enviaste una solicitud para este viaje. Espera a que el conductor responda.")
        elif solicitud_existente.estado_solicitud == 'APROBADA':
            messages.info(request, "¡Ya tienes un asiento asegurado en este viaje!")
        else:
            messages.error(request, "No puedes volver a solicitar unirte a este viaje.")
        return redirect('home')

    # LA ACCIÓN PRINCIPAL: Si pasa todas las reglas, creamos la solicitud en estado 'EN_ESPERA'
    # Fíjate que NO restamos viaje.asientos_disponibles aquí.
    Solicitud.objects.create(
        viaje=viaje,
        pasajero=request.user,
        estado_solicitud=Solicitud.EstadoSolicitud.EN_ESPERA
    )

    messages.success(request, f"Solicitud enviada al conductor. Te notificaremos cuando te acepte.")
    return redirect('home')

@login_required
def mis_viajes(request):
    if not request.user.es_conductor:
        messages.warning(request, "Debes registrar un vehículo para acceder al panel de conductor.")
        return redirect('home')

    # 1. Filtramos las solicitudes en sus dos estados importantes
    solicitudes_en_espera = Solicitud.objects.filter(estado_solicitud=Solicitud.EstadoSolicitud.EN_ESPERA)
    solicitudes_aprobadas = Solicitud.objects.filter(estado_solicitud=Solicitud.EstadoSolicitud.APROBADA)

    # 2. Inyectamos AMBAS listas dentro de cada viaje usando Prefetch
    viajes_del_conductor = Viaje.objects.filter(
        auto__duenio=request.user
    ).prefetch_related(
        Prefetch('solicitudes', queryset=solicitudes_en_espera, to_attr='solicitudes_pendientes'),
        Prefetch('solicitudes', queryset=solicitudes_aprobadas, to_attr='pasajeros_confirmados') # <-- NUEVO
    ).order_by('-fecha_hora_salida')

    return render(request, 'mis_viajes.html', {'viajes': viajes_del_conductor})

@login_required
def responder_solicitud(request, solicitud_id, accion):
    # Obligamos a que sea un método POST por seguridad
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        viaje = solicitud.viaje

        # 1. Regla: Solo el dueño puede moderar
        if request.user != viaje.auto.duenio:
            messages.error(request, "No tienes permiso para moderar este viaje.")
            return redirect('mis_viajes')

        # 2. NUEVA REGLA TEMPORAL: Bloquear acciones en viajes expirados
        if viaje.esta_expirado:
            messages.error(request, "Este viaje ha expirado. Ya no puedes aceptar ni rechazar pasajeros.")
            return redirect('mis_viajes')

        # 3. Regla: La solicitud debe estar en espera
        if solicitud.estado_solicitud != Solicitud.EstadoSolicitud.EN_ESPERA:
            messages.warning(request, "Esta solicitud ya fue procesada anteriormente.")
            return redirect('mis_viajes')

        # REGLA DE NEGOCIO: Solo el dueño del vehículo puede aceptar/rechazar
        if request.user != viaje.auto.duenio:
            messages.error(request, "No tienes permiso para moderar este viaje.")
            return redirect('mis_viajes')

        # Verificamos que la solicitud aún esté pendiente
        if solicitud.estado_solicitud != Solicitud.EstadoSolicitud.EN_ESPERA:
            messages.warning(request, "Esta solicitud ya fue procesada anteriormente.")
            return redirect('mis_viajes')

        # LÓGICA DE ACEPTAR
        if accion == 'aceptar':
            if viaje.asientos_disponibles > 0:
                solicitud.estado_solicitud = Solicitud.EstadoSolicitud.APROBADA
                viaje.asientos_disponibles -= 1  # Restamos 1 asiento físico
                
                # Guardamos los cambios en ambas tablas
                solicitud.save()
                viaje.save()
                
                messages.success(request, f"¡Has aceptado a {solicitud.pasajero.email} en tu viaje!")
            else:
                messages.error(request, "Ya no tienes asientos disponibles para este viaje.")

        # LÓGICA DE RECHAZAR
        elif accion == 'rechazar':
            solicitud.estado_solicitud = Solicitud.EstadoSolicitud.RECHAZADA
            solicitud.save() # Aquí no modificamos los asientos
            messages.info(request, "Solicitud rechazada correctamente.")

    # Finalmente, redirigimos al conductor de vuelta a su panel
    return redirect('mis_viajes')

@login_required
def cambiar_estado_viaje(request, viaje_id, nuevo_estado):
    if request.method == 'POST':
        viaje = get_object_or_404(Viaje, id=viaje_id)
        
        if request.user != viaje.auto.duenio:
            messages.error(request, "No tienes permiso para alterar este viaje.")
            return redirect('mis_viajes')
            
        # NUEVA REGLA: Si quiere iniciar el viaje, debe estar en la ventana de tiempo
        if nuevo_estado == 'EN_CURSO' and not viaje.puede_iniciarse:
            messages.error(request, "Solo puedes iniciar el viaje 15 minutos antes de la hora programada.")
            return redirect('mis_viajes')

        estados_validos = [est[0] for est in Viaje.EstadoViaje.choices]
        if nuevo_estado in estados_validos:
            viaje.estado_viaje = nuevo_estado
            viaje.save()
            messages.success(request, f"Estado del viaje actualizado a: {viaje.get_estado_viaje_display()}")
            
    return redirect('mis_viajes')

@login_required
def mis_reservas(request):
    # Buscamos todas las solicitudes donde el pasajero es el usuario actual.
    # select_related optimiza la consulta trayendo el viaje, el auto y al dueño de una vez.
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

        # 1. SEGURIDAD: Solo el pasajero dueño de la solicitud puede cancelarla
        if request.user != solicitud.pasajero:
            messages.error(request, "No tienes permiso para alterar esta reserva.")
            return redirect('mis_reservas')

        # 2. REGLA: No se puede cancelar si el viaje ya inició, terminó o expiró
        if viaje.estado_viaje != Viaje.EstadoViaje.NO_INICIADO or viaje.esta_expirado:
            messages.error(request, "No puedes cancelar la reserva de un viaje que ya pasó o está en curso.")
            return redirect('mis_reservas')

        # 3. REGLA: Evitar procesar solicitudes que ya están canceladas o rechazadas
        if solicitud.estado_solicitud == Solicitud.EstadoSolicitud.CANCELADA:
            messages.warning(request, "Esta solicitud ya fue cancelada anteriormente.")
            return redirect('mis_reservas')

        # 4. REGLA CRÍTICA DE INVENTARIO: Si ya estaba APROBADA, devolvemos el asiento físico
        if solicitud.estado_solicitud == Solicitud.EstadoSolicitud.APROBADA:
            viaje.asientos_disponibles += 1  # Devolvemos el asiento libre
            viaje.save()

        # 5. Cambiamos el estado a CANCELADA
        solicitud.estado_solicitud = Solicitud.EstadoSolicitud.CANCELADA
        solicitud.save()

        messages.success(request, "Has cancelado tu reserva con éxito. El asiento ha sido liberado.")
        
    return redirect('mis_reservas')

@login_required
def detalle_viaje(request, viaje_id):
    # Traemos el viaje con toda la información de su auto y dueño
    viaje = get_object_or_404(Viaje.objects.select_related('auto', 'auto__duenio'), id=viaje_id)
    
    # Verificamos si el usuario actual ya solicitó unirse a este viaje
    solicitud_previa = Solicitud.objects.filter(viaje=viaje, pasajero=request.user).first()
    
    contexto = {
        'viaje': viaje,
        'solicitud_previa': solicitud_previa
    }
    
    return render(request, 'detalle_viaje.html', contexto)