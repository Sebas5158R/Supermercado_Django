from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reportes/', include('reportes.urls', namespace='reportes')),
    path('terceros/', include('terceros.urls', namespace='terceros')),
    path('ventas/', include('ventas.urls', namespace='ventas')),
]
