from django.urls import path
from . import views

app_name = 'terceros'

urlpatterns = [
    path('clientes/<str:nombre>/<str:activo>/<str:fecha_registro>/', views.clientes, name='clientes'),
    path('inicio/', views.inicio, name='inicio'),
    path('saludo_cliente/<int:cliente_id>/', views.saludo_cliente, name='saludo_cliente'),
    path('lista_clientes/<int:cliente_id>/', views.lista_clientes, name='lista_clientes'),
    path('registrar_cliente/', views.template_formulario, name="registrar_cliente"),
    path('guardar_cliente/', views.guardar_cliente, name="guardar_cliente")
]
