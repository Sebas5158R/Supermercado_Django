from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
from . import forms

# Create your views here.
def lista_terceros(request):
    buscar = request.GET.get('buscar', '')
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')
    
    clientes = models.Cliente.objects.all()
    proveedores = models.Proveedor.objects.all()
    
    if buscar:
        clientes = models.Cliente.objects.filter(
            Q(nombre__icontains=buscar) | Q(email__icontains=buscar) | Q(telefono__icontains=buscar)
            )
        proveedores = models.Proveedor.objects.filter(
            Q(nombre__icontains=buscar) | Q(email__icontains=buscar) | Q(telefono__icontains=buscar)
            )
        
    if tipo_filtro == 'cliente':
        proveedores = proveedores.none()
        
    elif tipo_filtro == 'proveedor':
        clientes = clientes.none()
        
    if estado_filtro == 'activo':
        clientes = clientes.filter(activo=True)
        proveedores = proveedores.filter(activo=True)
    elif estado_filtro == 'inactivo':
        clientes = clientes.filter(activo=False)
        proveedores = proveedores.filter(activo=False)
    
    
    # Agegar rol a cada tercero para diferenciarlos en la plantilla
    for cliente in clientes:
        cliente.rol = 'Cliente'
    for proveedor in proveedores:
        proveedor.rol = 'Proveedor'
        
    terceros = list(clientes) + list(proveedores)
    return render(request, 'lista_terceros.html', {'terceros': terceros})

def crear_tercero(request, tipo):
    if request.method == 'POST':
        if tipo == 'cliente':
            form = forms.FormularioCliente(request.POST)
        elif tipo == 'proveedor':
            form = forms.FormularioProveedor(request.POST)
        else:
            return HttpResponse("Tipo de tercero no válido", status=400)

        if form.is_valid():
            data = form.cleaned_data
            if tipo == 'cliente':
                models.Cliente.objects.create(
                    nombre=data['nombre'],
                    email=data['email'],
                    telefono=data['telefono'],
                    activo=data['activo']
                )
            elif tipo == 'proveedor':
                models.Proveedor.objects.create(
                    nombre=data['nombre'],
                    email=data['email'],
                    telefono=data['telefono'],
                    direccion=data['direccion'],
                    ciudad=data['ciudad'],
                    estado=data['estado'],
                    activo=data['activo']
                )
            messages.success(request, f"{tipo.capitalize()} creado exitosamente.")
            return redirect('terceros:lista_terceros')
    else:
        if tipo == 'cliente':
            form = forms.FormularioCliente()
        elif tipo == 'proveedor':
            form = forms.FormularioProveedor()
        else:
            return HttpResponse("Tipo de tercero no válido", status=400)
    
    data = {
        'form': form,
        'tipo': tipo,
        'accion': 'Crear'
    }

    return render(request, 'formulario_tercero.html', data)

def editar_tercero(request, tipo, id):
    if tipo == 'cliente':
        tercero = models.Cliente.objects.get(id=id)
        Formulario = forms.FormularioCliente
    elif tipo == 'proveedor':
        tercero = models.Proveedor.objects.get(id=id)
        Formulario = forms.FormularioProveedor
    else:
        return HttpResponse("Tipo de tercero no válido", status=400)

    if request.method == 'POST':
        form = Formulario(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            tercero.nombre = data['nombre']
            tercero.email = data['email']
            tercero.telefono = data['telefono']
            tercero.activo = data['activo']
            if tipo == 'proveedor':
                tercero.direccion = data['direccion']
                tercero.ciudad = data['ciudad']
                tercero.estado = data['estado']
            tercero.save()
            
            messages.success(request, f"{tipo.capitalize()} actualizado exitosamente.")
            return redirect('terceros:lista_terceros')
    else:
        initial_data = {
            'nombre': tercero.nombre,
            'email': tercero.email,
            'telefono': tercero.telefono,
            'activo': tercero.activo,
        }
        if tipo == 'proveedor':
            initial_data.update({
                'direccion': tercero.direccion,
                'ciudad': tercero.ciudad,
                'estado': tercero.estado,
            })
        form = Formulario(initial=initial_data)

    data = {
        'form': form,
        'tipo': tipo,
        'id': id,
        'accion': 'Editar'
    }
    return render(request, 'formulario_tercero.html', data)

def eliminar_tercero(request, tipo, id):
    if tipo == 'cliente':
        tercero = models.Cliente.objects.get(id=id)
    elif tipo == 'proveedor':
        tercero = models.Proveedor.objects.get(id=id)
    else:
        return HttpResponse("Tipo de tercero no válido", status=400)

    messages.success(request, f"{tipo.capitalize()} eliminado exitosamente.")
    tercero.delete()
    return redirect('terceros:lista_terceros')