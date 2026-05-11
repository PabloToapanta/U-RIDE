Me olvide de aumentar el campo de numero de contacto en los modelos
Lo aniadimos 
``` python
# Añadimos el campo que faltaba para el RF2
    numero_contacto = models.CharField(max_length=10, null=True, blank=True)
```

Realizamos la migraciones y migramos a la base de datos

Luego creamos un formulario para actualizar datos llamada PerfilEstudiante
``` python 
class PerfilEstudianteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'carrera', 'zona_referencial', 'numero_contacto', 'foto')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
```

Despues de esto vamos a views y creamos la logica 
``` python
@login_required 
def perfil(request):
    if request.method == 'POST':
        # instance=request.user es la clave para EDITAR y no crear uno nuevo
        form = PerfilEstudianteForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡tu perfil ha sido actualizado con exito')
            return redirect('perfil')
    else:
        # Si es GET, cargamos el formulario con los datos actuales del estudiante
        form = PerfilEstudianteForm(instance=request.user)
    
    return render(request, 'perfil.html', {'form': form})
```
### Get
Get es un metodo para ver u obtener informacion

### Post
Post es un metodo para enviar o modificar algo, en el codigo, el primer if representa cuando el usuario esta enviando informacion

### Flujo
Cuando se carga la pagina se hace uso de GET y cuando se presiona Guardar es Post

### Request

Es conocida como una peticion, es lo que el cliente le pide al servidor, request es un objeto que django contiene toda la informacion que el navegador envia

Ejemplo
``` python
def mi_vista(request):
    # ¿Qué método usó? (GET, POST, etc.)
    metodo = request.method  # "GET" o "POST"
    
    # Datos de formulario POST
    nombre = request.POST.get('nombre')  # Lo que escribió el usuario
    
    # Datos de la URL (GET)
    busqueda = request.GET.get('q')  # ?q=python
    
    # Archivos subidos
    foto = request.FILES.get('avatar')  # Foto que subió el usuario
    
    # El usuario autenticado
    usuario = request.user  # Quién está visitando
    
    # La URL actual
    path = request.path  # "/perfil/"
    
    # Headers del navegador
    user_agent = request.META.get('HTTP_USER_AGENT')  # Chrome, Firefox, etc.
```

### Response

Es lo que el servidor responde al navegador, es lo que TU SERVIDOR le devuelve al navegador. Puede ser HTML, JSON, un archivo, etc.

Usos mas comunes
``` python
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

def ejemplos_response(request):
    # 1. Texto plano
    return HttpResponse("Hola mundo")
    
    # 2. HTML (más común)
    return render(request, 'mi_template.html', {'datos': [1, 2, 3]})
    
    # 3. JSON (para APIs)
    return JsonResponse({'mensaje': 'éxito', 'id': 123})
    
    # 4. Redirigir a otra URL
    return redirect('perfil')
    
    # 5. Archivo PDF
    with open('documento.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="documento.pdf"'
        return response
```