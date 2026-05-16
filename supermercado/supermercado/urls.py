from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('productos/', include('productos.urls', namespace='productos')),
    path('reportes/', include('reportes.urls', namespace='reportes')),
    path('terceros/', include('terceros.urls', namespace='terceros')),
    path('ventas/', include('ventas.urls', namespace='ventas')),
    path('compras/', include('compras.urls', namespace='compras')),
]
