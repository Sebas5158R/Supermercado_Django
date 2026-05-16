from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from . import models
from . import forms


def lista_productos(request):
    buscar = request.GET.get('buscar', '')
    proveedor_id = request.GET.get('proveedor', '')
    alerta = request.GET.get('alerta', '')

    productos = models.Producto.objects.select_related('proveedor').all()

    if buscar:
        productos = productos.filter(
            Q(nombre_producto__icontains=buscar)
            | Q(descripcion__icontains=buscar)
            | Q(proveedor__nombre__icontains=buscar)
        )
    if proveedor_id:
        productos = productos.filter(proveedor_id=proveedor_id)
    if alerta == 'stock':
        umbral = getattr(settings, 'UMBRAL_STOCK_CRITICO', 10)
        productos = productos.filter(stock__lte=umbral)
    elif alerta == 'vencimiento':
        limite = timezone.now().date() + timedelta(days=30)
        productos = productos.filter(fecha_vencimiento__lte=limite)

    umbral = getattr(settings, 'UMBRAL_STOCK_CRITICO', 10)
    total_criticos = models.Producto.objects.filter(stock__lte=umbral).count()
    limite_venc = timezone.now().date() + timedelta(days=30)
    total_por_vencer = models.Producto.objects.filter(fecha_vencimiento__lte=limite_venc).count()

    from terceros.models import Proveedor
    datos = {
        'productos': productos,
        'buscar': buscar,
        'proveedor_id': proveedor_id,
        'alerta': alerta,
        'proveedores': Proveedor.objects.filter(activo=True).order_by('nombre'),
        'total_criticos': total_criticos,
        'total_por_vencer': total_por_vencer,
    }
    return render(request, 'gestion_productos.html', datos)


def crear_producto(request):
    if request.method == 'POST':
        form = forms.FormularioProducto(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            models.Producto.objects.create(
                nombre_producto=datos['nombre_producto'],
                fecha_vencimiento=datos['fecha_vencimiento'],
                descripcion=datos['descripcion'],
                precio=datos['precio'],
                proveedor=datos['proveedor'],
                stock=datos['stock'],
                codigo_barras=datos['codigo_barras'],
            )
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('productos:gestion_productos')
    else:
        form = forms.FormularioProducto()
    datos = {'form': form, 'accion': 'Crear'}
    return render(request, 'formulario_producto.html', datos)


def editar_producto(request, id):
    producto = get_object_or_404(models.Producto, uuid_public=id)
    if request.method == 'POST':
        form = forms.FormularioProducto(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('productos:gestion_productos')
    else:
        form = forms.FormularioProducto(instance=producto)
    datos = {'form': form, 'id': id, 'accion': 'Editar'}
    return render(request, 'formulario_producto.html', datos)


def eliminar_producto(request, id):
    producto = get_object_or_404(models.Producto, uuid_public=id)
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente.')
    return redirect('productos:gestion_productos')


def top_productos(request):
    desde = request.GET.get('fecha_desde', '')
    hasta = request.GET.get('fecha_hasta', '')

    from ventas.models import DetalleVenta
    qs = DetalleVenta.objects.select_related('producto')
    if desde:
        qs = qs.filter(venta__fecha_venta__gte=desde)
    if hasta:
        qs = qs.filter(venta__fecha_venta__lte=hasta)

    ranking = (
        qs.values('producto__uuid_public', 'producto__nombre_producto', 'producto__precio')
        .annotate(unidades=Sum('cantidad'), ingreso=Sum('subtotal'))
        .order_by('-ingreso')[:20]
    )

    datos = {
        'ranking': ranking,
        'fecha_desde': desde,
        'fecha_hasta': hasta,
    }
    return render(request, 'top_productos.html', datos)


def resumen_diario(request):
    from notificaciones.email import enviar_resumen_diario
    from ventas.models import Venta
    from compras.models import Compra
    from django.utils import timezone
    from decimal import Decimal

    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(fecha_venta=hoy)
    compras_hoy = Compra.objects.filter(fecha_compra=hoy)
    umbral = getattr(settings, 'UMBRAL_STOCK_CRITICO', 10)
    stock_critico = models.Producto.objects.filter(stock__lte=umbral).count()

    resumen = {
        'ventas_hoy': ventas_hoy.aggregate(t=Sum('total_venta'))['t'] or Decimal('0'),
        'num_ventas': ventas_hoy.count(),
        'compras_hoy': compras_hoy.aggregate(t=Sum('total_compra'))['t'] or Decimal('0'),
        'num_compras': compras_hoy.count(),
        'stock_critico': stock_critico,
    }

    if request.method == 'POST':
        email_destino = request.POST.get('email_destino', '').strip()
        if email_destino:
            enviado = enviar_resumen_diario(resumen, [email_destino])
            if enviado:
                messages.success(request, f'Resumen diario enviado a {email_destino}.')
            else:
                messages.error(request, 'No se pudo enviar el correo.')
        else:
            messages.error(request, 'Ingresa un correo destinatario.')

    datos = {'resumen': resumen, 'hoy': hoy}
    return render(request, 'resumen_diario.html', datos)


def alertas_vencimiento(request):
    from notificaciones.email import enviar_alerta_vencimiento
    from django.utils import timezone
    from datetime import timedelta

    limite = timezone.now().date() + timedelta(days=30)
    proximos = list(models.Producto.objects.select_related('proveedor')
                    .filter(fecha_vencimiento__lte=limite)
                    .order_by('fecha_vencimiento'))

    if request.method == 'POST':
        email_destino = request.POST.get('email_destino', '').strip()
        if email_destino and proximos:
            enviado = enviar_alerta_vencimiento(proximos, [email_destino])
            if enviado:
                messages.success(request, f'Alerta de vencimiento enviada a {email_destino}.')
            else:
                messages.error(request, 'No se pudo enviar el correo.')
        elif not proximos:
            messages.info(request, 'No hay productos próximos a vencer.')
        else:
            messages.error(request, 'Ingresa un correo destinatario.')

    datos = {'proximos': proximos, 'limite': limite}
    return render(request, 'alertas_vencimiento.html', datos)


def alertas_stock(request):
    from notificaciones.email import enviar_alerta_stock_critico
    umbral = getattr(settings, 'UMBRAL_STOCK_CRITICO', 10)
    criticos = list(models.Producto.objects.select_related('proveedor').filter(stock__lte=umbral).order_by('stock'))

    if request.method == 'POST':
        email_destino = request.POST.get('email_destino', '').strip()
        if email_destino and criticos:
            enviado = enviar_alerta_stock_critico(criticos, [email_destino])
            if enviado:
                messages.success(request, f'Alerta enviada a {email_destino}.')
            else:
                messages.error(request, 'No se pudo enviar el correo. Verifica la configuración de email.')
        elif not criticos:
            messages.info(request, 'No hay productos con stock crítico.')
        else:
            messages.error(request, 'Ingresa un correo destinatario válido.')

    datos = {
        'criticos': criticos,
        'umbral': umbral,
    }
    return render(request, 'alertas_stock.html', datos)
