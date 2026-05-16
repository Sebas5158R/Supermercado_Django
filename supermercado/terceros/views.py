from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from . import models
from . import forms


def lista_terceros(request):
    buscar = request.GET.get('buscar', '')
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')

    clientes = models.Cliente.objects.all()
    proveedores = models.Proveedor.objects.all()

    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar) | Q(email__icontains=buscar) | Q(telefono__icontains=buscar)
        )
        proveedores = proveedores.filter(
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

    for cliente in clientes:
        cliente.rol = 'Cliente'
    for proveedor in proveedores:
        proveedor.rol = 'Proveedor'

    terceros = list(clientes) + list(proveedores)
    datos = {
        'terceros': terceros,
        'buscar': buscar,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'lista_terceros.html', datos)


def crear_tercero(request, tipo):
    if tipo not in ('cliente', 'proveedor'):
        return HttpResponse('Tipo de tercero no válido.', status=400)

    if request.method == 'POST':
        form = forms.FormularioCliente(request.POST) if tipo == 'cliente' else forms.FormularioProveedor(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            if tipo == 'cliente':
                models.Cliente.objects.create(
                    nombre=datos['nombre'],
                    email=datos['email'],
                    telefono=datos['telefono'],
                    activo=True,
                )
            else:
                models.Proveedor.objects.create(
                    nombre=datos['nombre'],
                    email=datos['email'],
                    telefono=datos['telefono'],
                    direccion=datos['direccion'],
                    ciudad=datos['ciudad'],
                    estado='activo',
                    activo=True,
                )
            messages.success(request, f'{tipo.capitalize()} creado exitosamente.')
            return redirect('terceros:lista_terceros')
    else:
        form = forms.FormularioCliente() if tipo == 'cliente' else forms.FormularioProveedor()

    datos = {'form': form, 'tipo': tipo, 'accion': 'Crear'}
    return render(request, 'formulario_tercero.html', datos)


def editar_tercero(request, tipo, id):
    if tipo not in ('cliente', 'proveedor'):
        return HttpResponse('Tipo de tercero no válido.', status=400)

    if tipo == 'cliente':
        tercero = get_object_or_404(models.Cliente, id=id)
        Formulario = forms.FormularioCliente
    else:
        tercero = get_object_or_404(models.Proveedor, id=id)
        Formulario = forms.FormularioProveedor

    if request.method == 'POST':
        form = Formulario(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            tercero.nombre = datos['nombre']
            tercero.email = datos['email']
            tercero.telefono = datos['telefono']
            tercero.activo = True
            if tipo == 'proveedor':
                tercero.direccion = datos['direccion']
                tercero.ciudad = datos['ciudad']
            tercero.save()
            messages.success(request, f'{tipo.capitalize()} actualizado exitosamente.')
            return redirect('terceros:lista_terceros')
    else:
        inicial = {
            'nombre': tercero.nombre,
            'email': tercero.email,
            'telefono': tercero.telefono,
        }
        if tipo == 'proveedor':
            inicial.update({'direccion': tercero.direccion, 'ciudad': tercero.ciudad})
        form = Formulario(initial=inicial)

    datos = {'form': form, 'tipo': tipo, 'id': id, 'accion': 'Editar'}
    return render(request, 'formulario_tercero.html', datos)


def eliminar_tercero(request, tipo, id):
    if tipo not in ('cliente', 'proveedor'):
        return HttpResponse('Tipo de tercero no válido.', status=400)
    if tipo == 'cliente':
        tercero = get_object_or_404(models.Cliente, id=id)
    else:
        tercero = get_object_or_404(models.Proveedor, id=id)
    messages.success(request, f'{tipo.capitalize()} eliminado exitosamente.')
    tercero.delete()
    return redirect('terceros:lista_terceros')


def perfil_cliente(request, id):
    cliente = get_object_or_404(models.Cliente, id=id)
    from ventas.models import Venta, DetalleVenta
    ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')
    total_comprado = ventas.aggregate(t=Sum('total_venta'))['t'] or 0
    productos_comprados = (
        DetalleVenta.objects
        .filter(venta__cliente=cliente)
        .values('producto__nombre_producto')
        .annotate(total_unidades=Sum('cantidad'), total_gastado=Sum('subtotal'))
        .order_by('-total_gastado')[:10]
    )
    datos = {
        'cliente': cliente,
        'ventas': ventas,
        'total_comprado': total_comprado,
        'productos_comprados': productos_comprados,
    }
    return render(request, 'perfil_cliente.html', datos)


def perfil_proveedor(request, id):
    proveedor = get_object_or_404(models.Proveedor, id=id)
    from compras.models import Compra
    compras = Compra.objects.filter(proveedor=proveedor).order_by('-fecha_compra')
    total_comprado = compras.aggregate(t=Sum('total_compra'))['t'] or 0
    productos = models.Proveedor.objects.get(id=id).productos_proveedor.all()
    datos = {
        'proveedor': proveedor,
        'compras': compras,
        'total_comprado': total_comprado,
        'productos': productos,
    }
    return render(request, 'perfil_proveedor.html', datos)


def cambiar_estado_tercero(request, tipo, id):
    if tipo not in ('cliente', 'proveedor'):
        return HttpResponse('Tipo no válido.', status=400)
    if tipo == 'cliente':
        tercero = get_object_or_404(models.Cliente, id=id)
    else:
        tercero = get_object_or_404(models.Proveedor, id=id)
    if request.method == 'POST':
        tercero.activo = not tercero.activo
        tercero.save()
        estado_texto = 'activado' if tercero.activo else 'desactivado'
        messages.success(request, f'{tipo.capitalize()} {estado_texto} exitosamente.')
    return redirect('terceros:lista_terceros')
