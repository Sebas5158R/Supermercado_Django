from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'proveedor', 'precio', 'stock', 'fecha_vencimiento', 'codigo_barras')
    list_filter = ('proveedor',)
    search_fields = ('nombre_producto', 'descripcion', 'codigo_barras')
    readonly_fields = ('uuid_public',)
