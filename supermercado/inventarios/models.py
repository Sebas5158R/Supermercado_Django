import uuid
from django.db import models

class Inventario(models.Model):
    uuid_public = models.UUIDField(default=uuid.uuid4,editable=False,unique=True,primary_key=True)
    id_producto = models.IntegerField()
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    stock_maximo = models.IntegerField(default=100)
    ubicacion = models.CharField(max_length=100)
    id_proveedor = models.IntegerField()
    cantidad_entradas = models.IntegerField(default=0)
    cantidad_salidas = models.IntegerField(default=0)
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Inventario: {self.ubicacion}, Stock: {self.stock_actual}"
