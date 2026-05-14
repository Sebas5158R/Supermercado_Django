from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('lista_compras/', views.getCompras, name='lista_compras'),
    path('crear_compra/', views.template_formulario, name='crear_compra'),
    path('detalle_compra/<int:compra_id>/', views.getDetalle, name='detalle_compra'),
    path('eliminar_producto_compra/<int:producto_compra_id>/', views.deleteProductoCompra, name='eliminar_producto_compra'),
]