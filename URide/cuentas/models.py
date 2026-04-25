from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.exceptions import ValidationError
# Create your models here.

class GerenteUsuarioPersonalizado(BaseUserManager):
    """
    Gerente personalizado donde el email es el identificador único
    en lugar de los nombres de usuario.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # Esto cifra la contraseña (Tu RNF1)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
class Usuario(AbstractUser):

    #Funcion validador de correo
    def validate_email(correo:str):
        if not correo.endswith("@uta.edu.ec"):
            raise ValidationError(
                f"El correo {correo} no termina en @uta.edu.ec",
                params={"correo":correo}
            )
    #Sobreescribimos el atributo email
    email=models.EmailField(validators=[validate_email],unique=True) #Para que no se repitan
    # DEfinimos que el campo para registro sera el email del usuario
    USERNAME_FIELD='email' 
    #Definicion de campos carrera,foto,zona_referencial,es_conductor,fecha_fin_suspension
    carrera=models.CharField(max_length=50)
    foto=models.ImageField(upload_to='perfiles/',null=True,blank=True)
    zona_referencial=models.CharField(max_length=50)
    es_conductor=models.BooleanField(default=False)
    fecha_fin_suspension=models.DateField(null=True,blank=True) #SOLO FECHA, NO HORA

    objects=GerenteUsuarioPersonalizado()
    #QUITAMOS ATRIBUTO USERNAME
    username=None
    #Evitar error de sobreescritura
    REQUIRED_FIELDS = []
