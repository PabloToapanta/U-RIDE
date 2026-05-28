from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class VerificarSuspensionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Verificamos si el usuario está logueado
        if request.user.is_authenticated:
            
            # 2. Revisamos si tiene un castigo activo (La fecha es HOY o en el FUTURO)
            if request.user.fecha_fin_suspension and request.user.fecha_fin_suspension >= timezone.localdate():
                
                # Formateamos la fecha para que se vea bonita en el mensaje
                fecha_str = request.user.fecha_fin_suspension.strftime("%d/%m/%Y")
                
                # 3. Lo expulsamos del sistema (cerramos sesión)
                logout(request)
                
                # 4. Le mandamos un mensaje rojo de alerta
                messages.error(request, f"🚫 Acceso denegado. Tu cuenta está suspendida por un administrador hasta el {fecha_str}.")
                
                # 5. Lo regresamos a la pantalla de login
                return redirect('login')
        
        # Si no está suspendido, la petición continúa normalmente
        response = self.get_response(request)
        return response