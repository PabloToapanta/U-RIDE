from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.apps import apps
# Create your models here.


class GerenteUsuarioPersonalizado(BaseUserManager):
    """
    Gerente personalizado donde el email es el identificador único
    en lugar de los nombres de usuario.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Esto cifra la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    # Funcion validador de correo
    def validate_email(correo: str):
        if not correo.endswith("@uta.edu.ec"):
            raise ValidationError(
                f"El correo {correo} no termina en @uta.edu.ec",
                params={"correo": correo},
            )

    # Sobreescribimos el atributo email
    email = models.EmailField(
        validators=[validate_email], unique=True
    )  # Para que no se repitan
    # DEfinimos que el campo para registro sera el email del usuario
    USERNAME_FIELD = "email"
    # Definicion de campos carrera,foto,zona_referencial,es_conductor,fecha_fin_suspension
    carrera = models.CharField(max_length=50)
    foto = models.ImageField(upload_to="perfiles/", null=True, blank=True)
    zona_referencial = models.CharField(max_length=50)
    es_conductor = models.BooleanField(default=False)
    fecha_fin_suspension = models.DateField(
        null=True, blank=True
    )  # SOLO FECHA, NO HORA
    # Añadimos el campo que faltaba para el RF2
    numero_contacto = models.CharField(max_length=10, null=True, blank=True)

    objects = GerenteUsuarioPersonalizado()
    # QUITAMOS ATRIBUTO USERNAME
    username = None
    # Evitar error de sobreescritura
    REQUIRED_FIELDS = []
    @property
    def total_viajes_conductor(self):
        Viaje = apps.get_model('viajes', 'Viaje')
        # Contamos solo los viajes de sus vehículos que ya hayan FINALIZADO
        return Viaje.objects.filter(auto__duenio=self, estado_viaje='FINALIZADO').count()

    # NUEVO: Contador dinámico de viajes como Pasajero
    @property
    def total_viajes_pasajero(self):
        Solicitud = apps.get_model('viajes', 'Solicitud')
        # Contamos las solicitudes APROBADAS en viajes que ya hayan FINALIZADO
        return Solicitud.objects.filter(
            pasajero=self, 
            estado_solicitud='APROBADA', 
            viaje__estado_viaje='FINALIZADO'
        ).count()
    @property
    def promedio_calificacion(self):
        """Calcula el promedio de todas las estrellas recibidas"""
        # 'evaluaciones_recibidas' es el related_name que pusimos en el modelo de Comunidad
        promedio = self.evaluaciones_recibidas.aggregate(Avg('calificacion'))['calificacion__avg']
        # Si tiene un promedio, lo redondea a 1 decimal (ej. 4.8). Si no tiene, devuelve 0.0
        return round(promedio, 1) if promedio else 0.0

    @property
    def total_evaluaciones(self):
        """Cuenta cuántas personas lo han calificado"""
        return self.evaluaciones_recibidas.count()