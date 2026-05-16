from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from . import models
from . import forms
from notificaciones.email import enviar_confirmacion_compra, enviar_alerta_stock_critico
from django.conf import settings


def lista_compras(request):
    buscar = request.GET.get('buscar', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    compras = models.Compra.objects.select_related('proveedor').order_by('-fecha_compra', '-id')

    if buscar:
        compras = compras.filter(
            Q(proveedor__nombre__icontains=buscar)
        )
    if estado_filtro:
        compras = compras.filter(estado=estado_filtro)
    if fecha_desde:
        compras = compras.filter(fecha_compra__gte=fecha_desde)
    if fecha_hasta:
        compras = compras.filter(fecha_compra__lte=fecha_hasta)

    total_periodo = compras.aggregate(t=Sum('total_compra'))['t'] or 0

    datos = {
        'compras': compras,
        'buscar': buscar,
        'estado_filtro': estado_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estados': models.ESTADOS_COMPRA,
        'total_periodo': total_periodo,
    }
    return render(request, 'lista_compras.html', datos)


def crear_compra(request):
    detalles_pendientes = models.DetalleCompra.objects.filter(compra_id=None).select_related('producto')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'agregar_producto_compra':
            producto_id = request.POST.get('producto')
            cantidad_raw = request.POST.get('cantidad', '0')
            cantidad = int(cantidad_raw) if cantidad_raw.isdigit() else 0
            if cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a cero.')
                return redirect('compras:crear_compra')
            producto = get_object_or_404(models.Producto, uuid_public=producto_id)
            subtotal = cantidad * producto.precio
            models.DetalleCompra.objects.create(
                producto_id=producto.uuid_public,
                cantidad=cantidad,
                subtotal=subtotal,
            )

        elif accion == 'finalizar_compra':
            if not detalles_pendientes.exists():
                messages.error(request, 'Agrega al menos un producto antes de finalizar.')
                return redirect('compras:crear_compra')

            proveedor_id = request.POST.get('proveedor')
            nota = request.POST.get('nota', '').strip()
            total = sum(d.subtotal for d in detalles_pendientes)

            compra = models.Compra.objects.create(
                total_compra=total,
                proveedor_id=proveedor_id if proveedor_id else None,
                nota=nota or None,
                estado='recibida',
            )
            for detalle in detalles_pendientes:
                detalle.compra_id = compra.id
                detalle.save()
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()

            detalles_finalizados = models.DetalleCompra.objects.filter(compra=compra).select_related('producto')
            enviado = enviar_confirmacion_compra(compra, detalles_finalizados)

            umbral = getattr(settings, 'UMBRAL_STOCK_CRITICO', 10)
            from productos.models import Producto
            criticos = list(Producto.objects.filter(stock__lte=umbral))
            if criticos and compra.proveedor:
                enviar_alerta_stock_critico(criticos, [compra.proveedor.email])

            if enviado:
                messages.success(request, f'Compra #{compra.id} registrada. Confirmación enviada al proveedor.')
            else:
                messages.success(request, f'Compra #{compra.id} registrada.')
            return redirect('compras:lista_compras')

    return render(request, 'formulario_compra.html', {
        'form': forms.FormularioCompra,
        'detalles_compra': detalles_pendientes,
    })


def detalle_compra(request, compra_id):
    compra = get_object_or_404(models.Compra, id=compra_id)
    detalles = models.DetalleCompra.objects.filter(compra_id=compra_id).select_related('producto')
    datos = {
        'compra': compra,
        'detalles_compra': detalles,
        'estados': models.ESTADOS_COMPRA,
    }
    return render(request, 'detalles_compra.html', datos)


def anular_compra(request, compra_id):
    compra = get_object_or_404(models.Compra, id=compra_id)
    if request.method == 'POST':
        if compra.estado == 'anulada':
            messages.error(request, 'Esta compra ya estaba anulada.')
            return redirect('compras:detalle_compra', compra_id=compra_id)
        for detalle in compra.detalles_compra.select_related('producto').all():
            detalle.producto.stock -= detalle.cantidad
            if detalle.producto.stock < 0:
                detalle.producto.stock = 0
            detalle.producto.save()
        compra.estado = 'anulada'
        compra.save()
        messages.success(request, f'Compra #{compra.id} anulada. Stock revertido.')
        return redirect('compras:lista_compras')
    return render(request, 'confirmar_anular_compra.html', {'compra': compra})


def eliminar_producto_compra(request, producto_compra_id):
    detalle = get_object_or_404(models.DetalleCompra, id=producto_compra_id)
    detalle.delete()
    return redirect('compras:crear_compra')


def historial_proveedor(request, proveedor_id):
    from terceros.models import Proveedor
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    compras = models.Compra.objects.filter(proveedor=proveedor).order_by('-fecha_compra')
    total_comprado = compras.aggregate(t=Sum('total_compra'))['t'] or 0
    datos = {
        'proveedor': proveedor,
        'compras': compras,
        'total_comprado': total_comprado,
    }
    return render(request, 'historial_proveedor.html', datos)
