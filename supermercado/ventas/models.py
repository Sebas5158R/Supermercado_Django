from django.db import models
from productos.models import Producto

# Create your models here.
class Venta(models.Model):
    fecha_venta = models.DateField(auto_now_add=True)
    total_venta = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"Venta: {self.fecha_venta}, {self.total_venta}"
    
class DetalleVenta(models.Model):
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_producto',
        related_query_name='detalle_producto'
    )
    
    venta = models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        null=True,
        blank=True,
        related_query_name='detalle_venta'
    )
    
    def __str__(self):
        return f"DetalleVenta: {self.cantidad}, {self.subtotal}, Producto: {self.producto.nombre_producto}"
