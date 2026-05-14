from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('lista_ventas/', views.getVentas, name='lista_ventas'),
    path('crear_venta/', views.template_formulario, name='crear_venta'),
    path('detalle_venta/<int:venta_id>/', views.getDetalle, name='detalle_venta'),
    path('eliminar_producto_venta/<int:producto_venta_id>/', views.deleteProductoVenta, name='eliminar_producto_venta'),
]