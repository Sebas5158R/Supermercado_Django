from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('lista/', views.lista_compras, name='lista_compras'),
    path('crear/', views.crear_compra, name='crear_compra'),
    path('detalle/<int:compra_id>/', views.detalle_compra, name='detalle_compra'),
    path('anular/<int:compra_id>/', views.anular_compra, name='anular_compra'),
    path('eliminar_producto/<int:producto_compra_id>/', views.eliminar_producto_compra, name='eliminar_producto_compra'),
    path('historial_proveedor/<int:proveedor_id>/', views.historial_proveedor, name='historial_proveedor'),
]
