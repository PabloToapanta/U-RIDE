from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class SuspensionMiddlewareTest(TestCase):
    def setUp(self):
        # 1. Creamos un usuario que se portó mal.
        # Le ponemos un castigo que expira MAÑANA
        maniana = timezone.localdate() + timedelta(days=1)
        
        self.usuario_castigado = Usuario.objects.create_user(
            email='mal_comportamiento@uta.edu.ec',
            password='123',
            fecha_fin_suspension=maniana
        )

    def test_usuario_suspendido_es_expulsado(self):
        """Verifica que el middleware intercepte y expulse a un usuario suspendido"""
        
        # 2. El usuario castigado intenta iniciar sesión
        self.client.login(email='mal_comportamiento@uta.edu.ec', password='123')

        # 3. Intenta navegar a la página principal ('home')
        response = self.client.get(reverse('home'))

        # VERIFICACIONES CLAVES:
        # 4. ¿El guardia (Middleware) lo interceptó y lo mandó a la página de login?
        self.assertRedirects(response, reverse('login'))
        
        # 5. Para ser doblemente seguros, revisamos que su sesión fue destruida
        # En Django, si la ID del usuario no está en la sesión, significa que fue deslogueado
        self.assertNotIn('_auth_user_id', self.client.session)

