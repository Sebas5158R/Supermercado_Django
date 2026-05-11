from django import forms
from .models import Reporte

TIPO_CHOICES = [
    ('ventas', 'Reporte de Ventas'),
    ('inventario', 'Reporte de Inventario'),
    ('productos', 'Reporte de Productos'),
    ('proveedores', 'Reporte de Proveedores'),
]

class ReporteForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select',
    }))
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label='Fecha Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label='Fecha Hasta'
    )

    class Meta:
        model = Reporte
        fields = ['nombre', 'tipo', 'descripcion', 'usuario_creacion', 'activo_tf']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del reporte...',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Descripción opcional...',
            }),
            'usuario_creacion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Usuario que genera el reporte',
            }),
            'activo_tf': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
        labels = {
            'nombre': 'Nombre del Reporte',
            'tipo': 'Tipo de Reporte',
            'descripcion': 'Descripción',
            'usuario_creacion': 'Usuario',
            'activo_tf': 'Activo',
        }
