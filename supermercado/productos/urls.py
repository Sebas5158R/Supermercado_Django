from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('gestion_productos/', views.lista_productos, name='gestion_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<uuid:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<uuid:id>/', views.eliminar_producto, name='eliminar_producto'),
]

