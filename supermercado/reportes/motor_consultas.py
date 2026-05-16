from django.db.models import Sum, Count, Avg, F, Max, Min
from ventas.models import Venta, DetalleVenta
from productos.models import Producto
from compras.models import Compra, DetalleCompra
from terceros.models import Cliente, Proveedor
from decimal import Decimal

CAMPOS_ORDEN_VALIDOS = {
    'ventas': {'id', 'fecha_venta', 'total_venta', '-id', '-fecha_venta', '-total_venta'},
    'compras': {'id', 'fecha_compra', 'total_compra', '-id', '-fecha_compra', '-total_compra'},
    'productos': {'nombre_producto', 'precio', 'stock', 'fecha_vencimiento', '-nombre_producto', '-precio', '-stock', '-fecha_vencimiento'},
    'clientes': {'nombre', 'email', 'fecha_registro', '-nombre', '-fecha_registro'},
    'proveedores': {'nombre', 'ciudad', 'fecha_registro', '-nombre', '-ciudad', '-fecha_registro'},
    'stock_critico': {'stock', 'nombre_producto', 'precio', '-stock', '-nombre_producto', '-precio'},
    'rentabilidad': {'ingreso_total', 'unidades_vendidas', 'precio', '-ingreso_total', '-unidades_vendidas', '-precio'},
}

ORDEN_DEFAULT = {
    'ventas': '-fecha_venta',
    'compras': '-fecha_compra',
    'productos': 'nombre_producto',
    'clientes': 'nombre',
    'proveedores': 'nombre',
    'stock_critico': 'stock',
    'rentabilidad': '-ingreso_total',
}


def _limpiar_orden(orden_raw, tipo):
    if not orden_raw:
        return ORDEN_DEFAULT.get(tipo, '')
    valor = str(orden_raw).strip()
    if valor.lower() in ('none', ''):
        return ORDEN_DEFAULT.get(tipo, '')
    if valor in CAMPOS_ORDEN_VALIDOS.get(tipo, set()):
        return valor
    return ORDEN_DEFAULT.get(tipo, '')


def ejecutar(reporte):
    tipo = reporte.tipo
    filtros = reporte.filtros or {}
    columnas = reporte.columnas_seleccionadas or []
    _agrup_raw = reporte.agrupacion
    agrupacion = '' if not _agrup_raw or str(_agrup_raw).strip().lower() in ('none', '') else str(_agrup_raw).strip()
    orden = _limpiar_orden(reporte.orden, tipo)
    limite = reporte.limite or 100

    despachador = {
        'ventas': _ventas,
        'compras': _compras,
        'productos': _productos,
        'clientes': _clientes,
        'proveedores': _proveedores,
        'stock_critico': _stock_critico,
        'rentabilidad': _rentabilidad,
    }
    funcion = despachador.get(tipo)
    if funcion:
        return funcion(filtros, columnas, agrupacion, orden, limite)
    return {'filas': [], 'etiquetas': {}, 'totales': {}, 'cantidad': 0, 'graficas': {}}


def _aplicar_rango_fecha(qs, filtros, campo):
    desde = filtros.get('fecha_desde', '')
    hasta = filtros.get('fecha_hasta', '')
    if desde:
        qs = qs.filter(**{f'{campo}__gte': desde})
    if hasta:
        qs = qs.filter(**{f'{campo}__lte': hasta})
    return qs


def _ventas(filtros, columnas, agrupacion, orden, limite):
    from reportes.models import COLUMNAS_POR_TIPO
    mapa = dict(COLUMNAS_POR_TIPO['ventas'])
    cols = columnas or ['id', 'fecha_venta', 'cliente__nombre', 'total_venta']
    etiquetas = {c: mapa.get(c, c) for c in cols}

    qs = Venta.objects.select_related('cliente').all()
    qs = _aplicar_rango_fecha(qs, filtros, 'fecha_venta')
    if filtros.get('cliente_id'):
        qs = qs.filter(cliente_id=filtros['cliente_id'])

    total = qs.aggregate(t=Sum('total_venta'))['t'] or Decimal('0')
    promedio = qs.aggregate(p=Avg('total_venta'))['p'] or Decimal('0')
    maximo = qs.aggregate(m=Max('total_venta'))['m'] or Decimal('0')

    por_fecha = list(qs.values('fecha_venta')
                     .annotate(total=Sum('total_venta'), cantidad=Count('id'))
                     .order_by('fecha_venta')[:30])

    por_cliente = list(qs.values('cliente__nombre')
                       .annotate(total=Sum('total_venta'), cantidad=Count('id'))
                       .order_by('-total')[:10])

    por_estado = list(qs.values('estado')
                      .annotate(cantidad=Count('id'), total=Sum('total_venta'))
                      .order_by('-cantidad'))

    graficas = {
        'evolucion': {
            'etiquetas': [str(r['fecha_venta']) for r in por_fecha],
            'valores': [float(r['total']) for r in por_fecha],
            'tipo': 'line',
            'titulo': 'Evolución de ventas por fecha',
        },
        'top_clientes': {
            'etiquetas': [r['cliente__nombre'] for r in por_cliente],
            'valores': [float(r['total']) for r in por_cliente],
            'tipo': 'bar',
            'titulo': 'Top clientes por monto',
        },
        'por_estado': {
            'etiquetas': [r['estado'].capitalize() for r in por_estado],
            'valores': [r['cantidad'] for r in por_estado],
            'tipo': 'doughnut',
            'titulo': 'Ventas por estado',
        },
    }

    if agrupacion == 'fecha_venta':
        filas = [{'Fecha': str(r['fecha_venta']), 'Total acumulado': r['total'], 'Cantidad de ventas': r['cantidad']} for r in por_fecha]
        etiquetas = {'Fecha': 'Fecha', 'Total acumulado': 'Total acumulado', 'Cantidad de ventas': 'Cantidad de ventas'}
    elif agrupacion == 'cliente__nombre':
        filas = [{'Cliente': r['cliente__nombre'], 'Total comprado': r['total'], 'Número de ventas': r['cantidad']} for r in por_cliente]
        etiquetas = {'Cliente': 'Cliente', 'Total comprado': 'Total comprado', 'Número de ventas': 'Número de ventas'}
    else:
        filas = []
        for v in qs.order_by(orden)[:limite]:
            fila = {}
            for col in cols:
                if col == 'id':
                    fila[col] = v.id
                elif col == 'fecha_venta':
                    fila[col] = str(v.fecha_venta)
                elif col == 'cliente__nombre':
                    fila[col] = v.cliente.nombre
                elif col == 'total_venta':
                    fila[col] = float(v.total_venta)
            filas.append(fila)

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Total de ventas': f'${float(total):,.2f}',
            'Promedio por venta': f'${float(promedio):,.2f}',
            'Venta máxima': f'${float(maximo):,.2f}',
            'Número de ventas': qs.count(),
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }


def _compras(filtros, columnas, agrupacion, orden, limite):
    from reportes.models import COLUMNAS_POR_TIPO
    mapa = dict(COLUMNAS_POR_TIPO['compras'])
    cols = columnas or ['id', 'fecha_compra', 'total_compra']
    etiquetas = {c: mapa.get(c, c) for c in cols}

    qs = Compra.objects.select_related('proveedor').all()
    qs = _aplicar_rango_fecha(qs, filtros, 'fecha_compra')

    total = qs.aggregate(t=Sum('total_compra'))['t'] or Decimal('0')
    promedio = qs.aggregate(p=Avg('total_compra'))['p'] or Decimal('0')

    por_fecha = list(qs.values('fecha_compra')
                     .annotate(total=Sum('total_compra'), cantidad=Count('id'))
                     .order_by('fecha_compra')[:30])

    por_proveedor = list(qs.filter(proveedor__isnull=False)
                         .values('proveedor__nombre')
                         .annotate(total=Sum('total_compra'), cantidad=Count('id'))
                         .order_by('-total')[:10])

    por_estado = list(qs.values('estado')
                      .annotate(cantidad=Count('id'))
                      .order_by('-cantidad'))

    graficas = {
        'evolucion': {
            'etiquetas': [str(r['fecha_compra']) for r in por_fecha],
            'valores': [float(r['total']) for r in por_fecha],
            'tipo': 'line',
            'titulo': 'Evolución de compras por fecha',
        },
        'top_proveedores': {
            'etiquetas': [r['proveedor__nombre'] for r in por_proveedor],
            'valores': [float(r['total']) for r in por_proveedor],
            'tipo': 'bar',
            'titulo': 'Top proveedores por monto',
        },
        'por_estado': {
            'etiquetas': [r['estado'].capitalize() for r in por_estado],
            'valores': [r['cantidad'] for r in por_estado],
            'tipo': 'doughnut',
            'titulo': 'Compras por estado',
        },
    }

    if agrupacion == 'fecha_compra':
        filas = [{'Fecha': str(r['fecha_compra']), 'Total acumulado': r['total'], 'Cantidad de compras': r['cantidad']} for r in por_fecha]
        etiquetas = {'Fecha': 'Fecha', 'Total acumulado': 'Total acumulado', 'Cantidad de compras': 'Cantidad de compras'}
    else:
        filas = []
        for c in qs.order_by(orden)[:limite]:
            fila = {}
            for col in cols:
                if col == 'id':
                    fila[col] = c.id
                elif col == 'fecha_compra':
                    fila[col] = str(c.fecha_compra)
                elif col == 'total_compra':
                    fila[col] = float(c.total_compra)
            filas.append(fila)

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Total invertido': f'${float(total):,.2f}',
            'Promedio por compra': f'${float(promedio):,.2f}',
            'Número de compras': qs.count(),
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }


def _productos(filtros, columnas, agrupacion, orden, limite):
    from reportes.models import COLUMNAS_POR_TIPO
    mapa = dict(COLUMNAS_POR_TIPO['productos'])
    cols = columnas or ['nombre_producto', 'precio', 'stock', 'proveedor__nombre']
    etiquetas = {c: mapa.get(c, c) for c in cols}

    qs = Producto.objects.select_related('proveedor').all()
    if filtros.get('proveedor_id'):
        qs = qs.filter(proveedor_id=filtros['proveedor_id'])

    valor_inventario = qs.aggregate(v=Sum(F('precio') * F('stock')))['v'] or Decimal('0')
    sin_stock = qs.filter(stock=0).count()
    stock_bajo = qs.filter(stock__gt=0, stock__lte=10).count()
    stock_ok = qs.filter(stock__gt=10).count()

    por_proveedor = list(qs.values('proveedor__nombre')
                         .annotate(cantidad=Count('uuid_public'), stock_total=Sum('stock'))
                         .order_by('-cantidad')[:10])

    graficas = {
        'por_proveedor': {
            'etiquetas': [r['proveedor__nombre'] for r in por_proveedor],
            'valores': [r['cantidad'] for r in por_proveedor],
            'tipo': 'bar',
            'titulo': 'Productos por proveedor',
        },
        'distribucion_stock': {
            'etiquetas': ['Sin stock', 'Stock bajo (1-10)', 'Stock normal (>10)'],
            'valores': [sin_stock, stock_bajo, stock_ok],
            'tipo': 'doughnut',
            'titulo': 'Distribución de stock',
        },
    }

    if agrupacion == 'proveedor__nombre':
        filas = [{'Proveedor': r['proveedor__nombre'], 'Número de productos': r['cantidad'], 'Stock total': r['stock_total']} for r in por_proveedor]
        etiquetas = {'Proveedor': 'Proveedor', 'Número de productos': 'Número de productos', 'Stock total': 'Stock total'}
    else:
        filas = []
        for p in qs.order_by(orden)[:limite]:
            fila = {}
            for col in cols:
                if col == 'nombre_producto':
                    fila[col] = p.nombre_producto
                elif col == 'precio':
                    fila[col] = float(p.precio)
                elif col == 'stock':
                    fila[col] = p.stock
                elif col == 'proveedor__nombre':
                    fila[col] = p.proveedor.nombre
                elif col == 'fecha_vencimiento':
                    fila[col] = str(p.fecha_vencimiento)
                elif col == 'codigo_barras':
                    fila[col] = p.codigo_barras
            filas.append(fila)

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Valor del inventario': f'${float(valor_inventario):,.2f}',
            'Total de productos': qs.count(),
            'Sin stock': sin_stock,
            'Stock bajo': stock_bajo,
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }


def _clientes(filtros, columnas, agrupacion, orden, limite):
    from reportes.models import COLUMNAS_POR_TIPO
    mapa = dict(COLUMNAS_POR_TIPO['clientes'])
    cols = columnas or ['nombre', 'email', 'telefono', 'activo']
    etiquetas = {c: mapa.get(c, c) for c in cols}

    qs = Cliente.objects.all()
    if filtros.get('solo_activos'):
        qs = qs.filter(activo=True)

    activos = qs.filter(activo=True).count()
    inactivos = qs.filter(activo=False).count()

    top_compradores = list(Venta.objects
                           .filter(cliente__in=qs)
                           .values('cliente__nombre')
                           .annotate(total=Sum('total_venta'), cantidad=Count('id'))
                           .order_by('-total')[:10])

    graficas = {
        'estado': {
            'etiquetas': ['Activos', 'Inactivos'],
            'valores': [activos, inactivos],
            'tipo': 'doughnut',
            'titulo': 'Clientes por estado',
        },
        'top_compradores': {
            'etiquetas': [r['cliente__nombre'] for r in top_compradores],
            'valores': [float(r['total']) for r in top_compradores],
            'tipo': 'bar',
            'titulo': 'Top clientes por monto comprado',
        },
    }

    filas = []
    for cli in qs.order_by(orden)[:limite]:
        fila = {}
        for col in cols:
            valor_campo = getattr(cli, col, '')
            if col == 'activo':
                valor_campo = 'Sí' if valor_campo else 'No'
            elif col == 'fecha_registro' and valor_campo:
                valor_campo = valor_campo.strftime('%d/%m/%Y')
            fila[col] = valor_campo
        filas.append(fila)

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Total clientes': qs.count(),
            'Clientes activos': activos,
            'Clientes inactivos': inactivos,
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }


def _proveedores(filtros, columnas, agrupacion, orden, limite):
    from reportes.models import COLUMNAS_POR_TIPO
    mapa = dict(COLUMNAS_POR_TIPO['proveedores'])
    cols = columnas or ['nombre', 'email', 'ciudad', 'activo']
    etiquetas = {c: mapa.get(c, c) for c in cols}

    qs = Proveedor.objects.all()
    if filtros.get('solo_activos'):
        qs = qs.filter(activo=True)
    if filtros.get('ciudad'):
        qs = qs.filter(ciudad__icontains=filtros['ciudad'])

    activos = qs.filter(activo=True).count()

    por_ciudad = list(qs.values('ciudad')
                      .annotate(cantidad=Count('id'))
                      .order_by('-cantidad')[:10])

    graficas = {
        'por_ciudad': {
            'etiquetas': [r['ciudad'] for r in por_ciudad],
            'valores': [r['cantidad'] for r in por_ciudad],
            'tipo': 'bar',
            'titulo': 'Proveedores por ciudad',
        },
        'estado': {
            'etiquetas': ['Activos', 'Inactivos'],
            'valores': [activos, qs.filter(activo=False).count()],
            'tipo': 'doughnut',
            'titulo': 'Proveedores por estado',
        },
    }

    if agrupacion == 'ciudad':
        filas = [{'Ciudad': r['ciudad'], 'Número de proveedores': r['cantidad']} for r in por_ciudad]
        etiquetas = {'Ciudad': 'Ciudad', 'Número de proveedores': 'Número de proveedores'}
    else:
        filas = []
        for p in qs.order_by(orden)[:limite]:
            fila = {}
            for col in cols:
                valor_campo = getattr(p, col, '')
                if col == 'activo':
                    valor_campo = 'Sí' if valor_campo else 'No'
                fila[col] = valor_campo
            filas.append(fila)

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Total proveedores': qs.count(),
            'Proveedores activos': activos,
            'Proveedores inactivos': qs.filter(activo=False).count(),
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }


def _stock_critico(filtros, columnas, agrupacion, orden, limite):
    from django.conf import settings
    from reportes.models import COLUMNAS_POR_TIPO
    mapa = dict(COLUMNAS_POR_TIPO['stock_critico'])
    cols = columnas or ['nombre_producto', 'stock', 'precio', 'proveedor__nombre']
    etiquetas = {c: mapa.get(c, c) for c in cols}

    umbral = int(filtros.get('umbral', getattr(settings, 'UMBRAL_STOCK_CRITICO', 10)))
    qs = Producto.objects.select_related('proveedor').filter(stock__lte=umbral)
    if filtros.get('proveedor_id'):
        qs = qs.filter(proveedor_id=filtros['proveedor_id'])

    sin_stock = qs.filter(stock=0).count()
    con_poco = qs.filter(stock__gt=0).count()

    por_proveedor = list(qs.values('proveedor__nombre')
                         .annotate(cantidad=Count('uuid_public'), stock_total=Sum('stock'))
                         .order_by('stock_total')[:10])

    graficas = {
        'por_proveedor': {
            'etiquetas': [r['proveedor__nombre'] for r in por_proveedor],
            'valores': [r['cantidad'] for r in por_proveedor],
            'tipo': 'bar',
            'titulo': 'Productos críticos por proveedor',
        },
        'nivel_stock': {
            'etiquetas': ['Sin stock (0)', f'Stock bajo (1-{umbral})'],
            'valores': [sin_stock, con_poco],
            'tipo': 'doughnut',
            'titulo': 'Nivel de criticidad',
        },
    }

    if agrupacion == 'proveedor__nombre':
        filas = [{'Proveedor': r['proveedor__nombre'], 'Productos críticos': r['cantidad'], 'Stock total': r['stock_total']} for r in por_proveedor]
        etiquetas = {'Proveedor': 'Proveedor', 'Productos críticos': 'Productos críticos', 'Stock total': 'Stock total'}
    else:
        filas = []
        for p in qs.order_by(orden)[:limite]:
            fila = {}
            for col in cols:
                if col == 'nombre_producto':
                    fila[col] = p.nombre_producto
                elif col == 'stock':
                    fila[col] = p.stock
                elif col == 'precio':
                    fila[col] = float(p.precio)
                elif col == 'proveedor__nombre':
                    fila[col] = p.proveedor.nombre
                elif col == 'fecha_vencimiento':
                    fila[col] = str(p.fecha_vencimiento)
            filas.append(fila)

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Productos en alerta': qs.count(),
            'Sin stock': sin_stock,
            'Stock bajo': con_poco,
            'Umbral configurado': umbral,
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }


def _rentabilidad(filtros, columnas, agrupacion, orden, limite):
    qs = (Producto.objects
          .select_related('proveedor')
          .annotate(
              unidades_vendidas=Sum('detalles_venta_producto__cantidad'),
              ingreso_total=Sum('detalles_venta_producto__subtotal'),
          ))
    if filtros.get('proveedor_id'):
        qs = qs.filter(proveedor_id=filtros['proveedor_id'])

    filas = []
    for p in qs.order_by(orden)[:limite]:
        filas.append({
            'nombre_producto': p.nombre_producto,
            'precio': float(p.precio),
            'unidades_vendidas': p.unidades_vendidas or 0,
            'ingreso_total': float(p.ingreso_total or 0),
            'stock': p.stock,
        })

    etiquetas = {
        'nombre_producto': 'Producto',
        'precio': 'Precio venta',
        'unidades_vendidas': 'Unidades vendidas',
        'ingreso_total': 'Ingreso total',
        'stock': 'Stock restante',
    }

    top_ingresos = sorted(filas, key=lambda x: x['ingreso_total'], reverse=True)[:10]
    top_unidades = sorted(filas, key=lambda x: x['unidades_vendidas'], reverse=True)[:10]
    ingreso_sum = sum(f['ingreso_total'] for f in filas)

    graficas = {
        'top_ingresos': {
            'etiquetas': [f['nombre_producto'] for f in top_ingresos],
            'valores': [f['ingreso_total'] for f in top_ingresos],
            'tipo': 'bar',
            'titulo': 'Top 10 productos por ingreso',
        },
        'top_unidades': {
            'etiquetas': [f['nombre_producto'] for f in top_unidades],
            'valores': [f['unidades_vendidas'] for f in top_unidades],
            'tipo': 'bar',
            'titulo': 'Top 10 productos por unidades vendidas',
        },
    }

    return {
        'filas': filas,
        'etiquetas': etiquetas,
        'totales': {
            'Ingreso total': f'${ingreso_sum:,.2f}',
            'Productos analizados': len(filas),
            'Promedio de ingreso': f'${(ingreso_sum / len(filas)) if filas else 0:,.2f}',
        },
        'cantidad': len(filas),
        'graficas': graficas,
    }
