from django.test import TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Vehiculo, Viaje, Solicitud

Usuario = get_user_model()

class CancelacionSolicitudTest(TestCase):
    def setUp(self):
        # 1. Creamos los actores
        self.conductor = Usuario.objects.create_user(email='conductor@uta.edu.ec', password='123', es_conductor=True)
        self.pasajero = Usuario.objects.create_user(email='pasajero@uta.edu.ec', password='123', es_conductor=False)
        
        # 2. Creamos el auto y el viaje
        self.auto = Vehiculo.objects.create(duenio=self.conductor, placa='ABC-1234', marca='Kia', modelo='Picanto', asientos_totales=4)
        
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