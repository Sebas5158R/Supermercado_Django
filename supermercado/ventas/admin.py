from django.contrib import admin
from .models import Venta, DetalleVenta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'cliente', 'total_venta', 'estado')
    list_filter = ('estado', 'fecha_venta')
    search_fields = ('cliente__nombre', 'cliente__email')
    readonly_fields = ('fecha_venta',)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'subtotal')
    search_fields = ('producto__nombre_producto',)
