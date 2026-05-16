from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from . import models
from . import forms
from notificaciones.email import enviar_confirmacion_venta, enviar_notificacion_anulacion_venta


def lista_ventas(request):
    buscar = request.GET.get('buscar', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    ventas = models.Venta.objects.select_related('cliente').order_by('-fecha_venta', '-id')

    if buscar:
        ventas = ventas.filter(
            Q(cliente__nombre__icontains=buscar) | Q(cliente__email__icontains=buscar)
        )
    if estado_filtro:
        ventas = ventas.filter(estado=estado_filtro)
    if fecha_desde:
        ventas = ventas.filter(fecha_venta__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha_venta__lte=fecha_hasta)

    total_periodo = ventas.aggregate(t=Sum('total_venta'))['t'] or 0

    datos = {
        'ventas': ventas,
        'buscar': buscar,
        'estado_filtro': estado_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estados': models.ESTADOS_VENTA,
        'total_periodo': total_periodo,
    }
    return render(request, 'lista_ventas.html', datos)


def crear_venta(request):
    detalles_pendientes = models.DetalleVenta.objects.filter(venta_id=None).select_related('producto')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'agregar_producto_venta':
            producto_id = request.POST.get('producto')
            cantidad_raw = request.POST.get('cantidad', '0')
            cantidad = int(cantidad_raw) if cantidad_raw.isdigit() else 0
            if cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a cero.')
                return redirect('ventas:crear_venta')
            producto = get_object_or_404(models.Producto, uuid_public=producto_id)
            if producto.stock < cantidad:
                messages.error(request, f'Stock insuficiente. Disponible: {producto.stock}.')
                return redirect('ventas:crear_venta')
            subtotal = cantidad * producto.precio
            models.DetalleVenta.objects.create(
                producto_id=producto.uuid_public,
                cantidad=cantidad,
                subtotal=subtotal,
            )

        elif accion == 'finalizar_venta':
            cliente_id = request.POST.get('cliente')
            nota = request.POST.get('nota', '').strip()
            if not detalles_pendientes.exists():
                messages.error(request, 'Agrega al menos un producto antes de finalizar.')
                return redirect('ventas:crear_venta')
            total = sum(d.subtotal for d in detalles_pendientes)
            venta = models.Venta.objects.create(
                total_venta=total,
                cliente_id=cliente_id,
                nota=nota or None,
                estado='completada',
            )
            for detalle in detalles_pendientes:
                detalle.venta_id = venta.id
                detalle.save()
                detalle.producto.stock -= detalle.cantidad
                detalle.producto.save()

            detalles_finalizados = models.DetalleVenta.objects.filter(venta=venta).select_related('producto')
            enviado = enviar_confirmacion_venta(venta, detalles_finalizados)
            if enviado:
                messages.success(request, f'Venta #{venta.id} registrada. Confirmación enviada al cliente.')
            else:
                messages.success(request, f'Venta #{venta.id} registrada.')
            return redirect('ventas:lista_ventas')

    return render(request, 'formulario_venta.html', {
        'form': forms.FormularioVenta,
        'detalles_venta': detalles_pendientes,
    })


def detalle_venta(request, venta_id):
    venta = get_object_or_404(models.Venta, id=venta_id)
    detalles = models.DetalleVenta.objects.filter(venta_id=venta_id).select_related('producto')
    datos = {
        'venta': venta,
        'detalles_venta': detalles,
        'estados': models.ESTADOS_VENTA,
    }
    return render(request, 'detalle_venta.html', datos)


def anular_venta(request, venta_id):
    venta = get_object_or_404(models.Venta, id=venta_id)
    if request.method == 'POST':
        if venta.estado == 'anulada':
            messages.error(request, 'Esta venta ya estaba anulada.')
            return redirect('ventas:detalle_venta', venta_id=venta_id)
        for detalle in venta.detalles_venta.select_related('producto').all():
            detalle.producto.stock += detalle.cantidad
            detalle.producto.save()
        venta.estado = 'anulada'
        venta.save()
        enviar_notificacion_anulacion_venta(venta)
        messages.success(request, f'Venta #{venta.id} anulada. Stock restaurado.')
        return redirect('ventas:lista_ventas')
    return render(request, 'confirmar_anular_venta.html', {'venta': venta})


def eliminar_producto_venta(request, producto_venta_id):
    detalle = get_object_or_404(models.DetalleVenta, id=producto_venta_id)
    detalle.delete()
    return redirect('ventas:crear_venta')


def historial_cliente(request, cliente_id):
    from terceros.models import Cliente
    cliente = get_object_or_404(Cliente, id=cliente_id)
    ventas = models.Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')
    total_comprado = ventas.aggregate(t=Sum('total_venta'))['t'] or 0
    datos = {
        'cliente': cliente,
        'ventas': ventas,
        'total_comprado': total_comprado,
    }
    return render(request, 'historial_cliente.html', datos)
