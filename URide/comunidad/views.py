from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import EvaluacionViaje
from .forms import EvaluacionForm
from viajes.models import Viaje
from .models import Reporte
from .forms import ReporteForm

Usuario = get_user_model()

@login_required
def calificar_usuario(request, viaje_id, evaluado_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)
    evaluado = get_object_or_404(Usuario, id=evaluado_id)
    evaluador = request.user

    # 1. Seguridad: Solo viajes finalizados
    if viaje.estado_viaje != 'FINALIZADO':
        messages.error(request, "Solo puedes calificar en viajes que ya terminaron.")
        return redirect('home')

    # 2. Seguridad: No autocalificarse
    if evaluador == evaluado:
        messages.error(request, "No puedes calificarte a ti mismo.")
        return redirect('home')

    # 3. Seguridad: Verificar si ya lo calificó antes
    ya_califico = EvaluacionViaje.objects.filter(viaje=viaje, evaluador=evaluador, evaluado=evaluado).exists()
    if ya_califico:
        messages.warning(request, f"Ya evaluaste a este usuario en este viaje.")
        return redirect('mis_viajes' if evaluador == viaje.auto.duenio else 'mis_reservas')

    # PROCESAR EL FORMULARIO
    if request.method == 'POST':
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            evaluacion = form.save(commit=False)
            evaluacion.viaje = viaje
            evaluacion.evaluador = evaluador
            evaluacion.evaluado = evaluado
            evaluacion.save()
            
            messages.success(request, f"¡Tu calificación para {evaluado.get_full_name() or evaluado.email} ha sido guardada!")
            
            # Redirigir dependiendo de si soy conductor o pasajero
            if evaluador == viaje.auto.duenio:
                return redirect('mis_viajes')
            else:
                return redirect('mis_reservas')
    else:
        form = EvaluacionForm()

    return render(request, 'calificar_usuario.html', {
        'form': form,
        'viaje': viaje,
        'evaluado': evaluado
    })



@login_required
def crear_reporte(request, viaje_id, reportado_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)
    reportado = get_object_or_404(Usuario, id=reportado_id)
    reportador = request.user

    # Regla de negocio 1: No se puede reportar a sí mismo
    if reportador == reportado:
        messages.error(request, "No puedes reportarte a ti mismo.")
        return redirect('home')

    # NUEVA REGLA DE NEGOCIO: Evitar spam de reportes
    ya_reporto = Reporte.objects.filter(viaje=viaje, reportador=reportador, reportado=reportado).exists()
    if ya_reporto:
        messages.warning(request, "Ya has enviado un reporte contra este usuario por este viaje. La administración lo está revisando.")
        return redirect('home')

    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.viaje = viaje
            reporte.reportador = reportador
            reporte.reportado = reportado
            reporte.save()
            
            messages.success(request, f"Tu reporte contra {reportado.get_full_name() or reportado.email} ha sido enviado al administrador.")
            return redirect('home')
    else:
        form = ReporteForm()

    return render(request, 'crear_reporte.html', {
        'form': form,
        'viaje': viaje,
        'reportado': reportado
    })