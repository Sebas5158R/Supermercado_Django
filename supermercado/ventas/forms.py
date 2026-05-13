from django import forms

class FormularioVenta(forms.Form):
    total_venta = forms.DecimalField(label="Total de la venta", max_digits=12, decimal_places=2)