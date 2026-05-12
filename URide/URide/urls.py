"""
URL configuration for URide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from cuentas import views as cuentas_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from viajes.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", cuentas_views.registro, name="registro"),
    path("activar/<uidb64>/<token>/", cuentas_views.activar_cuenta, name="activar"),
    path("perfil/", cuentas_views.perfil, name="perfil"),
    path("vehiculos/", include("viajes.urls")),  # Url de vehiculos
    path("", home, name="home"),
    # RECUPERACION DE CONTRASENIA
    # 1. Pantalla para ingresar el correo
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
        name="reset_password",
    ),
    # 2. Pantalla de "Correo enviado"
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_sent.html"
        ),
        name="password_reset_done",
    ),
    # 3. Pantalla para ingresar la nueva contraseña (el link del correo)
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    # 4. Pantalla de "Contraseña cambiada con éxito"
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_complete",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
