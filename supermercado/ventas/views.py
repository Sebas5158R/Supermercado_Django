from django.shortcuts import render

def template_formulario(request):
    return render(request, 'formulario_venta.html')

def getAllVentas(request):
    return render(request, 'lista_ventas.html')
