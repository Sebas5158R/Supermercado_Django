from django import forms
from terceros.models import Proveedor
from .models import Producto

class FormularioProducto(forms.ModelForm):  
        class Meta:
            model = Producto
            fields = ['nombre_producto', 'fecha_vencimiento', 'descripcion', 'precio', 'proveedor', 'stock', 'codigo_barras']
            widgets = {
                'nombre_producto': forms.TextInput(attrs={'class': 'form-input'}),
                'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
                'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
                'precio': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
                'stock': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
                'proveedor': forms.Select(attrs={'class': 'form-select'}),
                'codigo_barras': forms.NumberInput(attrs={'class': 'form-input'}),
            }  
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['proveedor'].queryset = Proveedor.objects.all()
