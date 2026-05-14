from django.db import models
from productos.models import Producto

class Compra(models.Model):
    fecha_compra = models.DateField(auto_now_add=True)
    total_compra = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"Compra: {self.fecha_compra}, {self.total_compra}"
    
class DetalleCompra(models.Model):
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_compra_producto',
        related_query_name='detalle_compra_producto'
    )
    
    compra = models.ForeignKey(
        Compra,
        on_delete=models.PROTECT,
        related_name='detalles_compra',
        null=True,
        blank=True,
        related_query_name='detalle_compra'
    )
    
    def __str__(self):
        return f"DetalleCompra: {self.cantidad}, {self.subtotal}, Producto: {self.producto.nombre_producto}"
