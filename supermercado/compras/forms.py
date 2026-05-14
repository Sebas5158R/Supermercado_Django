from django import forms
from productos.models import Producto
from terceros.models import Cliente

class FormularioCompra(forms.Form):
    cantidad = forms.IntegerField(label="Cantidad productos", widget=forms.NumberInput(attrs={'class': 'form-input'}))
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Selecciona el producto",
        empty_label="--Elige un producto--",
        widget=forms.Select(attrs={'class': 'form-select'})
    )