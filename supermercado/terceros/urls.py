from django.urls import path
from . import views

app_name = 'terceros'

urlpatterns = [
    path('lista_terceros/', views.lista_terceros, name='lista_terceros'),
    path('crear_tercero/<str:tipo>/', views.crear_tercero, name='crear_tercero'),
    path('editar_tercero/<str:tipo>/<int:id>/', views.editar_tercero, name='editar_tercero'),
    path('eliminar_tercero/<str:tipo>/<int:id>/', views.eliminar_tercero, name='eliminar_tercero'),
]
