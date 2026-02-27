from django.db import models

# Create your models here.
class Venta(models.Model):
    fecha_venta = models.DateField(auto_now_add=True)
    total_venta = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"Venta: {self.fecha_venta}, {self.total_venta}"
    
class DetalleVenta(models.Model):
    id_producto = models.IntegerField()
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    venta = models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        related_query_name='detalle_venta'
    )
    
    def __str__(self):
        return f"DetalleVenta: {self.id_producto}, {self.cantidad}"
