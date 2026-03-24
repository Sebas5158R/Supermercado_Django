from django.shortcuts import render
from django.http import HttpResponse
from . import models

def inicio(request, venta_id):
    
    data_id = models.Venta.objects.get(id=venta_id)
    data = models.Venta.objects.all()
    data_detalle = models.DetalleVenta.objects.all()
    
    dataEnvio = {
        'venta': data_id,
        'ventas': data,
        'detalle_venta': data_detalle,
        'existe': True
    }
    
    return render(request, 'index.html', dataEnvio)

def home(request):
    return render(request, 'home.html')
