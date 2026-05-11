from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('list/', views.listar, name='listar'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_reporte>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_reporte>/', views.eliminar, name='eliminar'),
    path('config/<uuid:id_reporte>/', views.config, name='config'),
    path('ver/<str:tipo>/', views.reportes, name='ver'),
    path('categorias/', views.categorias, name='categorias'),
    path('categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
]
