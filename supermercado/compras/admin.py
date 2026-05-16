from django.contrib import admin
from .models import Compra, DetalleCompra


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_compra', 'proveedor', 'total_compra', 'estado')
    list_filter = ('estado', 'fecha_compra')
    search_fields = ('proveedor__nombre',)
    readonly_fields = ('fecha_compra',)


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'compra', 'producto', 'cantidad', 'subtotal')
    search_fields = ('producto__nombre_producto',)
