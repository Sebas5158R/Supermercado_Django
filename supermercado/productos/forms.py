from django import forms
from .models import Producto

class FormularioProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'fecha_vencimiento', 'descripcion', 'precio', 'stock', 'codigo_barras']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-input'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'codigo_barras': forms.NumberInput(attrs={'class': 'form-input'}),
        }
