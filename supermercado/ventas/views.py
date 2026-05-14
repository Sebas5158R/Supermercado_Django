from django.shortcuts import redirect, render
from . import models
from . import forms

def template_formulario(request):
    
    detalles_venta = models.DetalleVenta.objects.filter(venta_id=None)
    
    if request.method == 'POST':
        accion = request.POST.get("accion")
        
        if accion == "agregar_producto_venta":
            producto_id = request.POST["producto"]
            cantidad = int(request.POST["cantidad"])
            
            producto = models.Producto.objects.get(uuid_public=producto_id)
            
            subtotal = cantidad * producto.precio
            
            detalle_venta = models.DetalleVenta(producto_id = producto.uuid_public, cantidad = cantidad, subtotal = subtotal)
            detalle_venta.save()
            
        if accion == "finalizar_venta":
            total = 0
            cliente_id = request.POST["cliente"]
            
            for detalle in detalles_venta:
                total += detalle.subtotal
            
            venta = models.Venta(total_venta = total, cliente_id = cliente_id)
            venta.save()
            
            for detalle in detalles_venta:
                detalle.venta_id = venta.id
                detalle.save()
                
                detalle.producto.stock -= detalle.cantidad
                detalle.producto.save()
                
            return  redirect('ventas:lista_ventas')
            
    return render(request, 'formulario_venta.html', {'form': forms.FormularioVenta, 'detalles_venta': detalles_venta})

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

def deleteProductoVenta(request, producto_venta_id):

    detalle_venta = models.DetalleVenta.objects.get(id=producto_venta_id)

    detalle_venta.delete()

    return redirect('ventas:crear_venta')
