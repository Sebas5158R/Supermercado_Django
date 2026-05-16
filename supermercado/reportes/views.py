import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from . import models
from .models import TIPOS_REPORTE, COLUMNAS_POR_TIPO, AGRUPACIONES_POR_TIPO
from .motor_consultas import ejecutar
from .exportadores import exportar_pdf, exportar_excel
from terceros.models import Proveedor, Cliente


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

    datos = {
        'reportes': reportes,
        'existe': reportes.exists(),
        'tipos': TIPOS_REPORTE,
        'buscar': buscar,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'total_reportes': reportes.count(),
    }
    return render(request, 'list.html', datos)


def crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        tipo = request.POST.get('tipo', 'ventas')
        descripcion = request.POST.get('descripcion', '').strip()
        usuario = request.POST.get('usuario_creacion', 'admin').strip()

        if not nombre:
            messages.error(request, 'El nombre del reporte es obligatorio.')
            return redirect('reportes:crear')

        columnas = request.POST.getlist('columnas')
        if not columnas:
            columnas = [c[0] for c in COLUMNAS_POR_TIPO.get(tipo, [])[:4]]

        filtros = {}
        fecha_desde = request.POST.get('fecha_desde', '').strip()
        fecha_hasta = request.POST.get('fecha_hasta', '').strip()
        if fecha_desde:
            filtros['fecha_desde'] = fecha_desde
        if fecha_hasta:
            filtros['fecha_hasta'] = fecha_hasta

        if tipo == 'stock_critico':
            umbral = request.POST.get('umbral', '10').strip()
            filtros['umbral'] = int(umbral) if umbral.isdigit() else 10

        if tipo in ('productos', 'rentabilidad', 'stock_critico'):
            proveedor_id = request.POST.get('proveedor_id', '').strip()
            if proveedor_id:
                filtros['proveedor_id'] = proveedor_id

        if tipo == 'ventas':
            cliente_id = request.POST.get('cliente_id', '').strip()
            if cliente_id:
                filtros['cliente_id'] = cliente_id

        if tipo in ('clientes', 'proveedores'):
            if request.POST.get('solo_activos'):
                filtros['solo_activos'] = True

        reporte = models.Reporte.objects.create(
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion or None,
            usuario_creacion=usuario,
            columnas_seleccionadas=columnas,
            filtros=filtros,
            agrupacion=request.POST.get('agrupacion', '').strip() or None,
            orden=request.POST.get('orden', '').strip() or None,
            limite=int(request.POST.get('limite', 100)) if request.POST.get('limite', '').isdigit() else 100,
        )
        messages.success(request, f'Reporte "{reporte.nombre}" creado exitosamente.')
        return redirect('reportes:visualizar', id_reporte=reporte.id_reporte)

    tipo_inicial = request.GET.get('tipo', 'ventas')
    datos = {
        'tipos': TIPOS_REPORTE,
        'columnas_por_tipo_json': json.dumps({t: [list(par) for par in cols] for t, cols in COLUMNAS_POR_TIPO.items()}, ensure_ascii=False),
        'agrupaciones_por_tipo_json': json.dumps({t: [list(par) for par in ag] for t, ag in AGRUPACIONES_POR_TIPO.items()}, ensure_ascii=False),
        'tipo_inicial': tipo_inicial,
        'proveedores': Proveedor.objects.filter(activo=True).order_by('nombre'),
        'clientes': Cliente.objects.filter(activo=True).order_by('nombre'),
        'accion': 'Crear',
    }
    return render(request, 'crear_reporte.html', datos)


def editar(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)

    if request.method == 'POST':
        reporte.nombre = request.POST.get('nombre', reporte.nombre).strip()
        reporte.descripcion = request.POST.get('descripcion', '').strip() or None
        reporte.usuario_creacion = request.POST.get('usuario_creacion', reporte.usuario_creacion).strip()
        reporte.activo_tf = 'activo_tf' in request.POST

        columnas = request.POST.getlist('columnas')
        if columnas:
            reporte.columnas_seleccionadas = columnas

        filtros = {}
        fecha_desde = request.POST.get('fecha_desde', '').strip()
        fecha_hasta = request.POST.get('fecha_hasta', '').strip()
        if fecha_desde:
            filtros['fecha_desde'] = fecha_desde
        if fecha_hasta:
            filtros['fecha_hasta'] = fecha_hasta

        if reporte.tipo == 'stock_critico':
            umbral = request.POST.get('umbral', '10').strip()
            filtros['umbral'] = int(umbral) if umbral.isdigit() else 10

        if reporte.tipo in ('productos', 'rentabilidad', 'stock_critico'):
            proveedor_id = request.POST.get('proveedor_id', '').strip()
            if proveedor_id:
                filtros['proveedor_id'] = proveedor_id

        if reporte.tipo == 'ventas':
            cliente_id = request.POST.get('cliente_id', '').strip()
            if cliente_id:
                filtros['cliente_id'] = cliente_id

        if reporte.tipo in ('clientes', 'proveedores'):
            if request.POST.get('solo_activos'):
                filtros['solo_activos'] = True

        reporte.filtros = filtros
        reporte.agrupacion = request.POST.get('agrupacion', '').strip() or None
        reporte.orden = request.POST.get('orden', '').strip() or None
        limite_raw = request.POST.get('limite', '100').strip()
        reporte.limite = int(limite_raw) if limite_raw.isdigit() else 100
        reporte.save()

        messages.success(request, f'Reporte "{reporte.nombre}" actualizado.')
        return redirect('reportes:visualizar', id_reporte=reporte.id_reporte)

    datos = {
        'reporte': reporte,
        'tipos': TIPOS_REPORTE,
        'columnas_por_tipo_json': json.dumps({t: [list(par) for par in cols] for t, cols in COLUMNAS_POR_TIPO.items()}, ensure_ascii=False),
        'agrupaciones_por_tipo_json': json.dumps({t: [list(par) for par in ag] for t, ag in AGRUPACIONES_POR_TIPO.items()}, ensure_ascii=False),
        'proveedores': Proveedor.objects.filter(activo=True).order_by('nombre'),
        'clientes': Cliente.objects.filter(activo=True).order_by('nombre'),
        'accion': 'Editar',
    }
    return render(request, 'crear_reporte.html', datos)


def eliminar(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)
    if request.method == 'POST':
        nombre = reporte.nombre
        reporte.delete()
        messages.success(request, f'Reporte "{nombre}" eliminado.')
        return redirect('reportes:listar')
    return render(request, 'confirmar_eliminar.html', {'reporte': reporte})


def visualizar(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)
    resultado = ejecutar(reporte)
    datos = {
        'reporte': reporte,
        'resultado': resultado,
        'filas': resultado['filas'],
        'etiquetas': resultado['etiquetas'],
        'totales': resultado['totales'],
        'graficas': resultado.get('graficas', {}),
        'graficas_json': json.dumps(resultado.get('graficas', {}), ensure_ascii=False),
        'tipos': dict(TIPOS_REPORTE),
    }
    return render(request, 'visualizar_reporte.html', datos)


def exportar(request, id_reporte, formato):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)
    resultado = ejecutar(reporte)
    if formato == 'pdf':
        return exportar_pdf(reporte, resultado)
    if formato == 'excel':
        return exportar_excel(reporte, resultado)
    messages.error(request, 'Formato de exportación no válido.')
    return redirect('reportes:visualizar', id_reporte=id_reporte)


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
                messages.success(request, f'Categoría "{nombre}" creada.')
                return redirect('reportes:categorias')
        else:
            messages.error(request, 'El nombre es obligatorio.')

    datos = {
        'todas': todas,
        'tipos': dict(TIPOS_REPORTE),
    }
    return render(request, 'categorias.html', datos)


def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(models.CategoriaReporte, id=categoria_id)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada.')
        return redirect('reportes:categorias')
    datos = {
        'categoria': categoria,
        'tipos': dict(TIPOS_REPORTE),
    }
    return render(request, 'confirmar_eliminar_categoria.html', datos)


def asignar_categorias(request, id_reporte):
    reporte = get_object_or_404(models.Reporte, id_reporte=id_reporte)
    if request.method == 'POST':
        ids_seleccionados = request.POST.getlist('categorias')
        reporte.categorias.set(
            models.CategoriaReporte.objects.filter(id__in=ids_seleccionados)
        )
        messages.success(request, 'Categorías actualizadas.')
        return redirect('reportes:visualizar', id_reporte=id_reporte)

    todas_categorias = models.CategoriaReporte.objects.all().order_by('nombre')
    ids_asignados = list(reporte.categorias.values_list('id', flat=True))
    datos = {
        'reporte': reporte,
        'todas_categorias': todas_categorias,
        'ids_asignados': ids_asignados,
    }
    return render(request, 'asignar_categorias.html', datos)
