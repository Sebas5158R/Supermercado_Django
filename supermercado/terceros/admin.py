from django.contrib import admin
from .models import Cliente, Proveedor


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'activo', 'fecha_registro')
    list_filter = ('activo',)
    search_fields = ('nombre', 'email', 'telefono')
    list_editable = ('activo',)
    readonly_fields = ('fecha_registro',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'ciudad', 'telefono', 'activo', 'fecha_registro')
    list_filter = ('activo', 'ciudad')
    search_fields = ('nombre', 'email', 'ciudad')
    list_editable = ('activo',)
    readonly_fields = ('fecha_registro',)
