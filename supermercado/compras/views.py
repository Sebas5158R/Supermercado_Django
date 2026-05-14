from django.shortcuts import redirect, render
from . import models
from . import forms

def template_formulario(request):
    
    detalles_compra = models.DetalleCompra.objects.filter(compra_id=None)
    
    if request.method == 'POST':
        accion = request.POST.get("accion")
        
        if accion == "agregar_producto_compra":
            producto_id = request.POST["producto"]
            cantidad = int(request.POST["cantidad"])
            
            producto = models.Producto.objects.get(uuid_public=producto_id)
            
            subtotal = cantidad * producto.precio
            
            detalle_compra = models.DetalleCompra(producto_id = producto.uuid_public, cantidad = cantidad, subtotal = subtotal)
            detalle_compra.save()
            
        if accion == "finalizar_compra":
            total = 0
            
            for detalle in detalles_compra:
                total += detalle.subtotal
            
            compra = models.Compra(total_compra = total)
            compra.save()

            for detalle in detalles_compra:
                detalle.compra_id = compra.id
                detalle.save()
                
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()
                
            return  redirect('compras:lista_compras')
            
    return render(request, 'formulario_compra.html', {'form': forms.FormularioCompra, 'detalles_compra': detalles_compra})

def getDetalle(request, compra_id):

    detalles_compra = models.DetalleCompra.objects.filter(compra_id=compra_id)
    compra = models.Compra.objects.get(id=compra_id)

    data = {
        'compra': compra,
        'detalles_compra': detalles_compra
    }

    return render(request, 'detalles_compra.html', data)

def getCompras(request):

    compras = models.Compra.objects.all()

    data = {
        'compras': compras
    }

    return render(request, 'lista_compras.html', data)

def deleteProductoCompra(request, producto_compra_id):

    detalle_compra = models.DetalleCompra.objects.get(id=producto_compra_id)

    detalle_compra.delete()

    return redirect('compras:crear_compra')
