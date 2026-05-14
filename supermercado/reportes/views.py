from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Avg, Q
from django.contrib import messages
from . import models
from .forms import ReporteForm
from ventas.models import Venta, DetalleVenta
from productos.models import Producto
from terceros.models import Proveedor, Cliente
from decimal import Decimal


TIPOS_REPORTE = {
    'ventas': 'Reporte de Ventas',
    'productos': 'Reporte de Productos',
    'proveedores': 'Reporte de Proveedores',
}

def listar(request):
    buscar = request.GET.get('buscar', '')
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')

    reportes = models.Reporte.objects.all().order_by('-fecha_creacion')

    if buscar:
        reportes = reportes.filter(
            Q(nombre__icontains=buscar) | Q(descripcion__icontains=buscar)
        )
    if tipo_filtro:
        reportes = reportes.filter(tipo=tipo_filtro)
    if estado_filtro == 'activo':
        reportes = reportes.filter(activo_tf=True)
    elif estado_filtro == 'inactivo':
        reportes = reportes.filter(activo_tf=False)

    data = {
        'reportes': reportes,
        'existe': reportes.exists(),
        'tipos': TIPOS_REPORTE,
        'buscar': buscar,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'total_reportes': reportes.count(),
    }
    return render(request, 'list.html', data)


def crear(request):
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            tipo = reporte.tipo
            fecha_desde = request.POST.get('fecha_desde')
            fecha_hasta = request.POST.get('fecha_hasta')
            parametros = {'fecha_desde': fecha_desde, 'fecha_hasta': fecha_hasta}
            reporte.parametros = parametros

            total = Decimal('0')
            if tipo == 'ventas':
                qs = Venta.objects.all()
                if fecha_desde:
                    qs = qs.filter(fecha_venta__gte=fecha_desde)
                if fecha_hasta:
                    qs = qs.filter(fecha_venta__lte=fecha_hasta)
                total = qs.aggregate(t=Sum('total_venta'))['t'] or Decimal('0')

            elif tipo == 'productos':
                total = Producto.objects.aggregate(
                    t=Sum('precio')
                )['t'] or Decimal('0')

            elif tipo == 'proveedores':
                total = Decimal(Proveedor.objects.filter(activo=True).count())

            reporte.total_monto = total
            reporte.save()
            messages.success(request, f'Reporte "{reporte.nombre}" creado exitosamente.')
            return redirect('reportes:listar')
    else:
        form = ReporteForm()

    data = {
        'form': form,
        'tipos': TIPOS_REPORTE,
        'accion': 'Crear',
    }
    return render(request, 'crear_reporte.html', data)


def editar(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)
    if request.method == 'POST':
        form = ReporteForm(request.POST, instance=reporte)
        if form.is_valid():
            form.save()
            messages.success(request, f'Reporte "{reporte.nombre}" actualizado.')
            return redirect('reportes:listar')
    else:
        form = ReporteForm(instance=reporte)

    data = {
        'form': form,
        'reporte': reporte,
        'tipos': TIPOS_REPORTE,
        'accion': 'Editar',
    }
    return render(request, 'crear_reporte.html', data)


def eliminar(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)
    if request.method == 'POST':
        nombre = reporte.nombre
        reporte.delete()
        messages.success(request, f'Reporte "{nombre}" eliminado.')
        return redirect('reportes:listar')
    return render(request, 'confirmar_eliminar.html', {'reporte': reporte})


def config(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)

    if request.method == 'POST':
        ids_seleccionados = request.POST.getlist('categorias')
        reporte.categorias.set(
            models.CategoriaReporte.objects.filter(id__in=ids_seleccionados)
        )
        messages.success(request, 'Categorías actualizadas correctamente.')
        return redirect('reportes:config', id_reporte=id_reporte)

    todas_categorias = models.CategoriaReporte.objects.all().order_by('nombre')
    ids_asignados = reporte.categorias.values_list('id', flat=True)

    data = {
        'reporte': reporte,
        'todas_categorias': todas_categorias,
        'ids_asignados': ids_asignados,
        'tipos': TIPOS_REPORTE,
    }
    return render(request, 'config.html', data)


def categorias(request):
    todas = models.CategoriaReporte.objects.all().order_by('nombre')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if nombre:
            if models.CategoriaReporte.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'Ya existe una categoría con el nombre "{nombre}".')
            else:
                models.CategoriaReporte.objects.create(nombre=nombre, descripcion=descripcion or None)
                messages.success(request, f'Categoría "{nombre}" creada exitosamente.')
                return redirect('reportes:categorias')
        else:
            messages.error(request, 'El nombre de la categoría es obligatorio.')

    data = {
        'todas': todas,
        'tipos': TIPOS_REPORTE,
    }
    return render(request, 'categorias.html', data)


def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(models.CategoriaReporte, id=categoria_id)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada.')
        return redirect('reportes:categorias')
    data = {
        'categoria': categoria,
        'tipos': TIPOS_REPORTE,
    }
    return render(request, 'confirmar_eliminar_categoria.html', data)


def reportes(request, tipo):
    if tipo not in TIPOS_REPORTE:
        messages.error(request, 'Tipo de reporte no válido.')
        return redirect('reportes:listar')

    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    contexto = {
        'tipo': tipo,
        'titulo': TIPOS_REPORTE[tipo],
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tipos': TIPOS_REPORTE,
    }

    if tipo == 'ventas':
        qs = Venta.objects.all().order_by('-fecha_venta')
        if fecha_desde:
            qs = qs.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_venta__lte=fecha_hasta)

        total_ventas = qs.aggregate(t=Sum('total_venta'))['t'] or 0
        promedio = qs.aggregate(a=Avg('total_venta'))['a'] or 0
        por_fecha = (
            qs.values('fecha_venta')
            .annotate(total=Sum('total_venta'), cantidad=Count('id'))
            .order_by('-fecha_venta')[:10]
        )
        contexto.update({
            'ventas': qs[:50],
            'total_ventas': total_ventas,
            'promedio_venta': promedio,
            'total_registros': qs.count(),
            'ventas_por_fecha': por_fecha,
        })

    elif tipo == 'productos':
        qs = Producto.objects.all().order_by('nombre_producto')
        sin_stock = qs.filter(stock=0).count()
        stock_bajo = qs.filter(stock__gt=0, stock__lt=10).count()
        valor_total = qs.aggregate(
            t=Sum('precio')
        )['t'] or 0
        contexto.update({
            'productos': qs[:50],
            'total_productos': qs.count(),
            'sin_stock': sin_stock,
            'stock_bajo': stock_bajo,
            'valor_inventario': valor_total,
        })

    elif tipo == 'proveedores':
        qs = Proveedor.objects.all().order_by('nombre')
        activos = qs.filter(activo=True).count()
        inactivos = qs.filter(activo=False).count()
        por_ciudad = (
            qs.values('ciudad')
            .annotate(cantidad=Count('id'))
            .order_by('-cantidad')[:5]
        )
        contexto.update({
            'proveedores': qs[:50],
            'activos': activos,
            'inactivos': inactivos,
            'total_proveedores': qs.count(),
            'por_ciudad': por_ciudad,
        })

    return render(request, 'reportes.html', contexto)
