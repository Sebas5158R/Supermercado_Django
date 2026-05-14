from django import forms
from productos.models import Producto

class FormularioVenta(forms.Form):
    total_venta = forms.DecimalField(label="Total de la venta", widget=forms.NumberInput(attrs={'class': 'form-input', 'readonly': 'true'}), max_digits=12, decimal_places=2)
    cantidad = forms.IntegerField(label="Cantidad productos", widget=forms.NumberInput(attrs={'class': 'form-input'}))
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Selecciona el producto",
        empty_label="--Elige un producto--",
        widget=forms.Select(attrs={'class': 'form-select'})
    )