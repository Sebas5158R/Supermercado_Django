from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
from . import forms


def lista_productos(request):
    buscar = request.GET.get('buscar', '')
    
    productos = models.Producto.objects.all()
    
    if buscar:
        productos = productos.filter(
            Q(nombre_producto__icontains=buscar) | Q(descripcion__icontains=buscar)
        )
    
    return render(request, 'gestion_productos.html', {'productos': productos})



def crear_producto(request):
    if request.method == 'POST':
        form = forms.FormularioProducto(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            models.Producto.objects.create(
                nombre_producto=data['nombre_producto'],
                fecha_vencimiento=data['fecha_vencimiento'],
                descripcion=data['descripcion'],
                precio=data['precio'],
                stock=data['stock'],
                codigo_barras=data['codigo_barras']
            )
            messages.success(request, "Producto creado exitosamente.")
            return redirect('productos:gestion_productos')
    else:
        form = forms.FormularioProducto()
    
    data = {
        'form': form,
        'accion': 'Crear'
    }
    return render(request, 'formulario_producto.html', data)



def editar_producto(request, id):
    producto = models.Producto.objects.get(uuid_public=id)
    Formulario = forms.FormularioProducto

    if request.method == 'POST':
        form = Formulario(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado exitosamente.")
            return redirect('productos:gestion_productos')
    else:
        form = Formulario(instance=producto)

    data = {
        'form': form,
        'id': id,
        'accion': 'Editar'
    }
    return render(request, 'formulario_producto.html', data)



def eliminar_producto(request, id):
    producto = models.Producto.objects.get(uuid_public=id)
    producto.delete()
    messages.success(request, "Producto eliminado exitosamente.")
    return redirect('productos:gestion_productos')

