from django import forms
from productos.models import Producto
from terceros.models import Proveedor


class FormularioCompra(forms.Form):
    cantidad = forms.IntegerField(
        label='Cantidad',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-input'}),
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label='Producto',
        empty_label='-- Elige un producto --',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True),
        label='Proveedor',
        empty_label='-- Elige un proveedor --',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    nota = forms.CharField(
        label='Nota',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
    )
