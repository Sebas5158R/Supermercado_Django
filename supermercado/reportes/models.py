from django.db import models
import uuid

class Reporte(models.Model):
    id_reporte = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, db_index=True, help_text="Descripción del reporte...")
    tipo = models.CharField(max_length=20, default='models', db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True, null=True, blank=True)
    usuario_creacion = models.CharField(max_length=30, default='nombre_usuario')
    activo_tf = models.BooleanField(default=True) 
    total_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total monetario calculado (si aplica)")
    parametros = models.JSONField(blank=True, null=True, help_text="Filtros dinámicos usados para generar el reporte")

    def __str__(self):
        return f"Reporte con ID {self.id_reporte} -> {self.nombre} ({self.tipo})"

class CategoriaReporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    reportes = models.ManyToManyField(Reporte, related_name='categorias')

    def __str__(self):
        return f"Agrupación del reporte: {self.nombre}"
