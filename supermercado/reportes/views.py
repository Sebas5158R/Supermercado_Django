from django.shortcuts import render
from django.http import HttpResponse
from . import models

def list(request):
    
    reportes = models.Reporte.objects.all()
    data = {
        'reportes': reportes,
        'existe': reportes.exists()
    }
    return render(request, 'list.html', data)

def reportes(request, tipo):
    return render(request, 'reportes.html')

def config(request, id_reporte):

    data = models.Reporte.objects.all()
    datos = {
        'reportes': data,
        'id_actual': str(id_reporte)
    }
    return render(request, 'config.html', datos)