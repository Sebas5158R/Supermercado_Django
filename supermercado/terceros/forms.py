from django import forms

class FormularioCliente(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)
    telefono = forms.IntegerField(label="Telefono")
    activo = forms.BooleanField(label="Activo")

class FormularioProveedor(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)
    telefono = forms.IntegerField(label="Telefono")
    direccion = forms.CharField(label="Direccion", max_length=200)
    ciudad = forms.CharField(label="Ciudad", max_length=50)
    estado = forms.CharField(label="Estado", max_length=50)
    activo = forms.BooleanField(label="Activo")