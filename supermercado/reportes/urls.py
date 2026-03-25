from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list),
    path('reportes/<str:tipo>', views.reportes),
    path('config/<uuid:id_reporte>/', views.config)
]