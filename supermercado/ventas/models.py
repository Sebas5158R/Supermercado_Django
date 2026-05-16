from django.db import models
from productos.models import Producto
from terceros.models import Cliente

ESTADOS_VENTA = [
    ('pendiente', 'Pendiente'),
    ('completada', 'Completada'),
    ('anulada', 'Anulada'),
]


class Venta(models.Model):
    fecha_venta = models.DateField(auto_now_add=True)
    total_venta = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_VENTA, default='completada')
    nota = models.TextField(blank=True, null=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ventas_cliente',
        related_query_name='venta_cliente',
    )

    def __str__(self):
        return f"Venta #{self.id} — {self.fecha_venta} — ${self.total_venta}"


class DetalleVenta(models.Model):
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_venta_producto',
        related_query_name='detalle_venta_producto',
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        null=True,
        blank=True,
        related_query_name='detalle_venta',
    )

    def __str__(self):
        return f"Detalle venta: {self.cantidad} × {self.producto.nombre_producto}"
