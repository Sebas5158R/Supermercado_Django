from django.urls import path
from . import views

app_name = 'terceros'

urlpatterns = [
    path('lista/', views.lista_terceros, name='lista_terceros'),
    path('crear/<str:tipo>/', views.crear_tercero, name='crear_tercero'),
    path('editar/<str:tipo>/<int:id>/', views.editar_tercero, name='editar_tercero'),
    path('eliminar/<str:tipo>/<int:id>/', views.eliminar_tercero, name='eliminar_tercero'),
    path('estado/<str:tipo>/<int:id>/', views.cambiar_estado_tercero, name='cambiar_estado'),
    path('cliente/<int:id>/', views.perfil_cliente, name='perfil_cliente'),
    path('proveedor/<int:id>/', views.perfil_proveedor, name='perfil_proveedor'),
]
