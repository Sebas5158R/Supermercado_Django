from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('lista/', views.listar, name='listar'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_reporte>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_reporte>/', views.eliminar, name='eliminar'),
    path('visualizar/<uuid:id_reporte>/', views.visualizar, name='visualizar'),
    path('exportar/<uuid:id_reporte>/<str:formato>/', views.exportar, name='exportar'),
    path('categorias/', views.categorias, name='categorias'),
    path('categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('categorias/asignar/<uuid:id_reporte>/', views.asignar_categorias, name='asignar_categorias'),
]
