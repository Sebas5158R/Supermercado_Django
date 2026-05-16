from django.db import models
from productos.models import Producto
from terceros.models import Proveedor

ESTADOS_COMPRA = [
    ('pendiente', 'Pendiente'),
    ('recibida', 'Recibida'),
    ('anulada', 'Anulada'),
]


class Compra(models.Model):
    fecha_compra = models.DateField(auto_now_add=True)
    total_compra = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_COMPRA, default='recibida')
    nota = models.TextField(blank=True, null=True)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='compras_proveedor',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Compra #{self.id} — {self.fecha_compra} — ${self.total_compra}"


class DetalleCompra(models.Model):
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_compra_producto',
        related_query_name='detalle_compra_producto',
    )
    compra = models.ForeignKey(
        Compra,
        on_delete=models.PROTECT,
        related_name='detalles_compra',
        null=True,
        blank=True,
        related_query_name='detalle_compra',
    )

    def __str__(self):
        return f"Detalle compra: {self.cantidad} × {self.producto.nombre_producto}"
