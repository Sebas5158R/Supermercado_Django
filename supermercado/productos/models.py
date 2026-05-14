from django.db import models
from terceros.models import Proveedor
import uuid

# Create your models here.
class Producto(models.Model):
    nombre_producto = models.CharField(max_length=80) 
    fecha_vencimiento = models.DateField()
    codigo_barras = models.BigIntegerField(unique=True, db_index=True)
    uuid_public = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='productos_proveedor',
        related_query_name='producto_proveedor'
    )
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"Producto: {self.nombre_producto} - {self.precio}"
    
