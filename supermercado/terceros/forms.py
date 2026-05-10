from django import forms

class FormularioTercero(forms.Form):
    identificador = forms.IntegerField(label="Id")
    nombre = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)
    telefono = forms.IntegerField(label="Telefono")
    activo = forms.BooleanField(label="Activo")
    # fecha_nacimiento = forms.DateField(label="Fecha de nacimiento", widget=forms.DateInput(attrs={"type":"date"}))