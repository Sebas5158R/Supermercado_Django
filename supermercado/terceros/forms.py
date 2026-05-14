from django import forms

class FormularioCliente(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    telefono = forms.IntegerField(label="Telefono", widget=forms.TextInput(attrs={'class': 'form-input'}))
    activo = forms.BooleanField(label="Activo", widget=forms.TextInput(attrs={'class': 'form-input'}))

class FormularioProveedor(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    telefono = forms.IntegerField(label="Telefono", widget=forms.TextInput(attrs={'class': 'form-input'}))
    direccion = forms.CharField(label="Direccion", max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    ciudad = forms.CharField(label="Ciudad", max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    estado = forms.CharField(label="Estado", max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    activo = forms.BooleanField(label="Activo", widget=forms.TextInput(attrs={'class': 'form-input'}))