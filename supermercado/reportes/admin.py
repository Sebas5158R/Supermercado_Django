from django.contrib import admin
from .models import Reporte, CategoriaReporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'total_monto', 'fecha_creacion', 'usuario_creacion', 'activo_tf')
    list_filter = ('tipo', 'activo_tf', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'usuario_creacion')
    readonly_fields = ('id_reporte', 'fecha_creacion')
    list_editable = ('activo_tf',)


@admin.register(CategoriaReporte)
class CategoriaReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    filter_horizontal = ('reportes',)
