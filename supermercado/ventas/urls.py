from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('lista_ventas/', views.getAllVentas, name='lista_ventas'),
    path('crear_venta/', views.template_formulario, name='crear_venta')
]