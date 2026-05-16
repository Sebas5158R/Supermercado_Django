from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('lista/', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('anular/<int:venta_id>/', views.anular_venta, name='anular_venta'),
    path('eliminar_producto/<int:producto_venta_id>/', views.eliminar_producto_venta, name='eliminar_producto_venta'),
    path('historial_cliente/<int:cliente_id>/', views.historial_cliente, name='historial_cliente'),
]
