from django.db import models
import uuid

TIPOS_REPORTE = [
    ('ventas', 'Ventas'),
    ('compras', 'Compras'),
    ('productos', 'Productos'),
    ('clientes', 'Clientes'),
    ('proveedores', 'Proveedores'),
    ('stock_critico', 'Stock crítico'),
    ('rentabilidad', 'Rentabilidad por producto'),
]

COLUMNAS_POR_TIPO = {
    'ventas': [
        ('id', 'ID Venta'),
        ('fecha_venta', 'Fecha'),
        ('cliente__nombre', 'Cliente'),
        ('total_venta', 'Total'),
    ],
    'compras': [
        ('id', 'ID Compra'),
        ('fecha_compra', 'Fecha'),
        ('total_compra', 'Total'),
    ],
    'productos': [
        ('nombre_producto', 'Nombre'),
        ('precio', 'Precio'),
        ('stock', 'Stock'),
        ('proveedor__nombre', 'Proveedor'),
        ('fecha_vencimiento', 'Vencimiento'),
        ('codigo_barras', 'Código de barras'),
    ],
    'clientes': [
        ('nombre', 'Nombre'),
        ('email', 'Email'),
        ('telefono', 'Teléfono'),
        ('activo', 'Activo'),
        ('fecha_registro', 'Fecha de registro'),
    ],
    'proveedores': [
        ('nombre', 'Nombre'),
        ('email', 'Email'),
        ('ciudad', 'Ciudad'),
        ('telefono', 'Teléfono'),
        ('activo', 'Activo'),
    ],
    'stock_critico': [
        ('nombre_producto', 'Nombre'),
        ('stock', 'Stock actual'),
        ('precio', 'Precio'),
        ('proveedor__nombre', 'Proveedor'),
        ('fecha_vencimiento', 'Vencimiento'),
    ],
    'rentabilidad': [
        ('nombre_producto', 'Producto'),
        ('precio', 'Precio venta'),
        ('unidades_vendidas', 'Unidades vendidas'),
        ('ingreso_total', 'Ingreso total'),
        ('stock', 'Stock restante'),
    ],
}

AGRUPACIONES_POR_TIPO = {
    'ventas': [
        ('', 'Sin agrupar'),
        ('fecha_venta', 'Por fecha'),
        ('cliente__nombre', 'Por cliente'),
    ],
    'compras': [
        ('', 'Sin agrupar'),
        ('fecha_compra', 'Por fecha'),
    ],
    'productos': [
        ('', 'Sin agrupar'),
        ('proveedor__nombre', 'Por proveedor'),
    ],
    'clientes': [
        ('', 'Sin agrupar'),
    ],
    'proveedores': [
        ('', 'Sin agrupar'),
        ('ciudad', 'Por ciudad'),
    ],
    'stock_critico': [
        ('', 'Sin agrupar'),
        ('proveedor__nombre', 'Por proveedor'),
    ],
    'rentabilidad': [
        ('', 'Sin agrupar'),
    ],
}


class Reporte(models.Model):
    id_reporte = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, db_index=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_REPORTE, default='ventas', db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=60, default='admin')
    activo_tf = models.BooleanField(default=True)
    columnas_seleccionadas = models.JSONField(default=list)
    filtros = models.JSONField(default=dict)
    agrupacion = models.CharField(max_length=60, blank=True, null=True)
    orden = models.CharField(max_length=60, blank=True, null=True)
    limite = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    def columnas_disponibles(self):
        return COLUMNAS_POR_TIPO.get(self.tipo, [])

    def agrupaciones_disponibles(self):
        return AGRUPACIONES_POR_TIPO.get(self.tipo, [('', 'Sin agrupar')])

    def etiquetas_columnas(self):
        mapa = dict(COLUMNAS_POR_TIPO.get(self.tipo, []))
        return {col: mapa.get(col, col) for col in self.columnas_seleccionadas}


class CategoriaReporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    reportes = models.ManyToManyField(Reporte, related_name='categorias', blank=True)

    def __str__(self):
        return self.nombre
