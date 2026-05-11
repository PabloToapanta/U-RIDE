# Procesamiento de Imagenes
En nuestro proyecto se requiere que los usuarios tengan fotos de perfil, para ello utilizamos la libreria de python Pillow, esta biblioteca se encarga del procesamiento de imagenes, Pillow valida que el achivo subido realmente sea una imagen.

Para empezar definimos estas configuraciones en  nuestro archivo `settings.py`
``` python
# settings.py
import os

# BASE_DIR ya debería estar definido
MEDIA_URL = '/media/'  # URL para acceder a las imágenes
MEDIA_ROOT = BASE_DIR / 'media' # Carpeta donde se guardan físicamente
```

Despues nuestro modelo debe tener esto:

``` python
foto=models.ImageField(upload_to='perfiles/',null=True,blank=True)
```
`/perfiles` se refiere a nuestra subcarpeta dentro de la carpeta media

Para la visualizacion de imagenes utilizamos esta configuracion dentro de nuestro archivo `urls.py
`
``` python
f settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
Esto solo es para desarollo nunca para produccion