from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('gestion/', views.lista_productos, name='gestion_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<uuid:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<uuid:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('top/', views.top_productos, name='top_productos'),
    path('alertas_stock/', views.alertas_stock, name='alertas_stock'),
    path('alertas_vencimiento/', views.alertas_vencimiento, name='alertas_vencimiento'),
    path('resumen_diario/', views.resumen_diario, name='resumen_diario'),
]
