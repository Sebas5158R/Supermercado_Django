from django.shortcuts import render
from . import models
from . import forms

def template_formulario(request):
    
    return render(request, 'formulario_venta.html', {'form': forms.FormularioVenta})

def getDetalle(request, venta_id):

    detalles_venta = models.DetalleVenta.objects.filter(venta_id=venta_id)
    venta = models.Venta.objects.get(id=venta_id)

    data = {
        'venta': venta,
        'detalles_venta': detalles_venta
    }

    return render(request, 'detalle_venta.html', data)

def getVentas(request):

    ventas = models.Venta.objects.all()

    data = {
        'ventas': ventas
    }

    return render(request, 'lista_ventas.html', data)
