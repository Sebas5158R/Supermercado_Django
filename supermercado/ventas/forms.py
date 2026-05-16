from django import forms
from productos.models import Producto
from terceros.models import Cliente


class FormularioVenta(forms.Form):
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-input"}),
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Producto",
        empty_label="-- Elige un producto --",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True),
        label="Cliente",
        empty_label="-- Elige un cliente --",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
