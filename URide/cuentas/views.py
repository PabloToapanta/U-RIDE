# cuentas/views.py
from django.contrib import messages

# Importacion para la actualizacion de perfil de un login requerido
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .forms import PerfilEstudianteForm, RegistroEstudianteForm
from .models import Usuario


def registro(request):
    # Cuando el usuario envie los datos del formulario
    if request.method == "POST":
        form = RegistroEstudianteForm(
            request.POST, request.FILES
        )  # Post para datos y Files para informacion
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # El usuario nace desactivado
            user.save()

            # 1. Encriptamos el ID del usuario para que sea seguro mandarlo por URL
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # 2. Generamos un Token criptográfico de un solo uso
            token = default_token_generator.make_token(user)
            # 3. Construimos la URL completa
            enlace = request.build_absolute_uri(
                reverse("activar", kwargs={"uidb64": uid, "token": token})
            )

            # 4. Redactamos el correo
            mensaje = f"Hola {user.first_name},\n\nGracias por unirte a U-Ride. Para activar tu cuenta y poder iniciar sesión, por favor haz clic en el siguiente enlace:\n\n{enlace}\n\nSi no solicitaste este registro, ignora este correo."

            # 5. Enviamos el correo (Como configuramos la consola, saldrá en tu terminal)
            send_mail(
                "Activa tu cuenta de U-Ride",
                mensaje,
                "admin@uride.uta.edu.ec",
                [user.email],
                fail_silently=False,
            )

            messages.success(
                request,
                "¡Registro exitoso! Por favor revisa la bandeja de entrada (y el Spam) de tu correo institucional para activar tu cuenta.",
            )
            return redirect("login")
    else:
        form = RegistroEstudianteForm()

    return render(request, "registro.html", {"form": form})


def activar_cuenta(request, uidb64, token):
    try:
        # Desencriptamos el ID para saber qué usuario es
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    # Si el usuario existe y el token es matemáticamente válido
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activamos la cuenta
        user.save()
        messages.success(
            request,
            "¡Tu cuenta ha sido activada exitosamente! Ya puedes iniciar sesión.",
        )
        return redirect("login")
    else:
        messages.error(request, "El enlace de activación es inválido o ya ha expirado.")
        return redirect("registro")


@login_required
def perfil(request):
    if request.method == "POST":
        # instance=request.user es la clave para EDITAR y no crear uno nuevo
        form = PerfilEstudianteForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "¡tu perfil ha sido actualizado con exito")
            return redirect("perfil")
    else:
        # Si es GET, cargamos el formulario con los datos actuales del estudiante
        form = PerfilEstudianteForm(instance=request.user)

    resenias = request.user.evaluaciones_recibidas.all().order_by('-fecha')
    
    contexto = {
        'form': form, # el form que ya tenías
        'resenias': resenias
    }
    return render(request, 'perfil.html', contexto)

Usuario = get_user_model()

def perfil_publico(request, usuario_id):
    # Buscamos al usuario por su ID
    perfil_usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Extraemos las reseñas donde él es el 'evaluado', ordenadas de la más reciente a la más antigua
    resenias = perfil_usuario.evaluaciones_recibidas.all().order_by('-fecha')
    
    contexto = {
        'perfil_usuario': perfil_usuario,
        'resenias': resenias
    }
    return render(request, 'perfil_publico.html', contexto)