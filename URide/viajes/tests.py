from django.test import TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Vehiculo, Viaje, Solicitud
from viajes.forms import ViajeForm
Usuario = get_user_model()

class CancelacionSolicitudTest(TestCase):
    def setUp(self):
        # 1. Creamos los actores
        self.conductor = Usuario.objects.create_user(email='conductor@uta.edu.ec', password='123', es_conductor=True)
        self.pasajero = Usuario.objects.create_user(email='pasajero@uta.edu.ec', password='123', es_conductor=False)
        
        # 2. Creamos el auto y el viaje
        self.auto = Vehiculo.objects.create(
    duenio=self.conductor, 
    placa='ABC-1234', 
    marca='Kia', 
    modelo='Picanto', 
    anio=2022, 
    color='Rojo', 
    max_capacidad=4
)
        
        # Viaje para mañana
        fecha_viaje = timezone.now() + timedelta(days=1)
        self.viaje = Viaje.objects.create(
            auto=self.auto, 
            zona_origen='Centro', 
            zona_destino='UTA', 
            fecha_hora_salida=fecha_viaje,
            asientos_disponibles=3,
            estado_viaje='NO_INICIADO'
        )
        
        # 3. Creamos una solicitud aprobada
        self.solicitud = Solicitud.objects.create(
            viaje=self.viaje,
            pasajero=self.pasajero,
            estado_solicitud='APROBADA'
        )

    def test_pasajero_puede_cancelar_solicitud(self):
        """Verifica si un pasajero real puede cancelar sin ser expulsado"""
        
        # Iniciamos sesión como el PASAJERO
        self.client.login(email='pasajero@uta.edu.ec', password='123')
        
        # Hacemos la petición POST para cancelar
        url = reverse('cancelar_solicitud', args=[self.solicitud.id])
        response = self.client.post(url)
        
        # Recargamos la solicitud desde la base de datos
        self.solicitud.refresh_from_db()
        self.viaje.refresh_from_db()
        
        # VERIFICACIONES CLAVE:
        # 1. ¿El estado cambió a cancelada?
        self.assertEqual(self.solicitud.estado_solicitud, 'CANCELADA')
        
        # 2. ¿Se devolvió el asiento? (Tenía 3, ahora debe tener 4)
        self.assertEqual(self.viaje.asientos_disponibles, 4)
        
        # 3. ¿A dónde nos redirigió? (Debería ser a mis_reservas, código HTTP 302)
        self.assertRedirects(response, reverse('mis_reservas'))



class ValidacionAsientosTest(TestCase):
    def setUp(self):
        # 1. Preparamos el entorno: Un conductor y un vehículo de 4 asientos (max_capacidad=4)
        self.conductor = Usuario.objects.create_user(email='profe@uta.edu.ec', password='123', es_conductor=True)
        self.auto = Vehiculo.objects.create(
            duenio=self.conductor, 
            marca='Toyota', 
            modelo='Corolla', 
            anio=2020, 
            color='Gris', 
            placa='XYZ-9876', 
            max_capacidad=4
        )

    def test_no_puede_ofrecer_mas_asientos_que_capacidad(self):
        """Verifica que el ViajeForm arroje error si los asientos superan la capacidad del auto"""
        
        # Simulamos los datos que enviaría el usuario por POST en el HTML
        datos_formulario = {
            'zona_origen': 'Centro',
            'zona_destino': 'Campus Huachi',
            'fecha_hora_salida': timezone.now() + timedelta(days=1),
            'asientos_disponibles': 5  # ¡Tratando de engañar al sistema!
        }
        
        # Inicializamos el formulario pasando el usuario (como lo tienes programado en views.py)
        form = ViajeForm(data=datos_formulario, usuario=self.conductor)
        
        # Ejecutamos la verificación
        es_valido = form.is_valid()
        
        # VERIFICACIONES:
        # 1. El formulario NO debe ser válido
        self.assertFalse(es_valido)
        # 2. Debe existir un error específico en el campo 'asientos_disponibles'
        self.assertIn('asientos_disponibles', form.errors)

class IntegracionSolicitudViajeTest(TestCase):
    def setUp(self):
        # 1. Creamos al Conductor y su Auto
        self.conductor = Usuario.objects.create_user(email='conductor@uta.edu.ec', password='123', es_conductor=True)
        self.auto = Vehiculo.objects.create(
            duenio=self.conductor, placa='XYZ-1234', marca='Chevrolet', modelo='Spark', 
            anio=2019, color='Azul', max_capacidad=4
        )
        
        # 2. Creamos el Viaje
        fecha_futura = timezone.now() + timedelta(days=2)
        self.viaje = Viaje.objects.create(
            auto=self.auto, zona_origen='Izamba', zona_destino='UTA', 
            fecha_hora_salida=fecha_futura, asientos_disponibles=3, estado_viaje='NO_INICIADO'
        )

        # 3. Creamos al Pasajero
        self.pasajero = Usuario.objects.create_user(email='pasajero@uta.edu.ec', password='123', es_conductor=False)

    def test_pasajero_puede_solicitar_unirse(self):
        """Verifica el flujo completo: el pasajero hace click en solicitar y se crea el registro en BD"""
        
        # 1. El pasajero inicia sesión en el navegador
        self.client.login(email='pasajero@uta.edu.ec', password='123')
        
        # 2. El pasajero hace POST a la URL de solicitar_viaje (como si diera click en el botón verde de Bootstrap)
        url = reverse('solicitar_viaje', args=[self.viaje.id])
        response = self.client.post(url)
        
        # 3. Verificamos que lo redirija al home (HTTP 302) con un mensaje de éxito
        self.assertRedirects(response, reverse('home'))
        
        # 4. LA PRUEBA DE FUEGO (PostgreSQL): Buscamos si la solicitud realmente se guardó en la base de datos
        solicitud_guardada = Solicitud.objects.filter(viaje=self.viaje, pasajero=self.pasajero).first()
        
        self.assertIsNotNone(solicitud_guardada, "La solicitud no se guardó en la base de datos.")
        self.assertEqual(solicitud_guardada.estado_solicitud, 'EN_ESPERA', "El estado inicial debe ser EN_ESPERA.")