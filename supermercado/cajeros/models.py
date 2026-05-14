from django.db import models

class Cajero(models.Model):
    identificacion = models.CharField(max_length=15)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    correo = models.EmailField(max_length=90)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=150)
    salario = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField()
