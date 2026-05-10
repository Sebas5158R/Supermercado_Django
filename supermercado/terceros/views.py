from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
from . import forms

# Create your views here.
def clientes(request, nombre, activo, fecha_registro):
    return HttpResponse(f"<h1 style='color: red; display: flex; justify-content: center; text-align: center;'>Bienvenido a nuestro supermercado:<span style='color: black;'>{nombre}</span></h1> <h1 style='display: flex; justify-content: center; text-align: center;'>Estado actual: <span style='color: green;'>{activo}</span></h1> <p style='color: black; display: flex; justify-content: center; text-align: center;'>Fecha de Registro: {fecha_registro}</p> <label style='color: black; display: flex; justify-content: center; text-align: center;'>Buscar producto</label> <input type='search' style='display: flex; justify-content: center; text-align: center; margin: 0 auto; padding: 10px; border-radius: 5px; border: 1px solid #ccc;'> <br/> <button style='display: flex; justify-content: center; text-align: center; margin: 0 auto; padding: 10px 20px; background-color: green; color: white; border: none; border-radius: 5px; cursor: pointer;'>Buscar</button> <h1 style='color: black; display: flex; justify-content: center; text-align: center;'>Productos disponibles</h1> <div style='display: flex; justify-content: center; text-align: center;'> <img style='width: 300px; height: 300px;' src='https://imgs.search.brave.com/qE6SHraEVE8BA6TOYPjpBwluas_ZgNwBYDS1b_VjSkU/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9zdGF0/aWMudmVjdGVlenku/Y29tL3N5c3RlbS9y/ZXNvdXJjZXMvdGh1/bWJuYWlscy8wNzIv/MTE4Lzg2OC9zbWFs/bC9yZWQtYW5kLWdy/ZWVuLWFwcGxlcy13/aXRoLWZyZXNoLXdh/dGVyLWRyb3BzLXBo/b3RvLmpwZw' alt='Manzanas'/> <img style='width: 300px; height: 300px;' src='https://imgs.search.brave.com/vnDGMF-OkJFoDX0kLVQuAqwPupjuy2eSjETLhk6xeAs/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdGF0/aWMudmVjdGVlenku/Y29tL3N5c3RlbS9y/ZXNvdXJjZXMvdGh1/bWJuYWlscy8wMzkv/NzYzLzg2MS9zbWFs/bC9haS1nZW5lcmF0/ZWQtcmlwZS1tYW5n/by1mcnVpdC1iYWNr/Z3JvdW5kLXBob3Rv/LmpwZw' alt='Mangos'/> <img style='width: 300px; height: 300px;' src='https://imgs.search.brave.com/rEEuYpOxJ7LggwHEOwiL0ApjT3FfmYoa2NfjwENKOpM/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly91cGxv/YWQud2lraW1lZGlh/Lm9yZy93aWtpcGVk/aWEvY29tbW9ucy82/LzYwL0NvcnRlX3Ry/YW5zdmVyc2FsX2Zy/ZXNhLmpwZw' alt='Fresas'/></div> <br/><br/> <h1 style='color: black; display: flex; justify-content: center; text-align: center;'>Gracias por visitarnos</h1>")

def inicio(request):
    data = {
        "usuario": "Juan Perez",
        "email": "juan@gmail.com"
    }
    return render(request, "index.html", data)

def saludo_cliente(request, cliente_id):
    data = models.Cliente.objects.get(id=cliente_id)
    # Se puede usar Try Catch para manejar el error en caso de que no exista el cliente
    return render(request, "saludo_cliente.html", {"cliente": data})

def lista_clientes(request, cliente_id):
    cliente_actual = models.Cliente.objects.get(id=cliente_id)
    clientes = models.Cliente.objects.all()
    return render(request, "lista_clientes.html", {"clientes": clientes, "cliente_actual": cliente_actual})

def template_formulario(request):
    if request.method == "GET":
        return render(request, "formulario.html", { "formulario": forms.FormularioTercero })
    
def guardar_cliente(request):
    # if request.method == "POST":
    #     id = request.POST["identificador"]
    #     nombre = request.POST["nombre"]
    #     email = request.POST["email"]
    #     telefono = request.POST["telefono"]
    #     activo = request.POST["activo"]
        
    #     nuevo_cliente = models.Cliente.objects.create(
    #         id = id,
    #         nombre = nombre,
    #         email = email,
    #         telefono = telefono,
    #         activo = True
    #     )
        
    #     return redirect("terceros:lista_clientes/1")
    
    id = request.POST["identificador"]
    nombre = request.POST["nombre"]
    email = request.POST["email"]
    telefono = request.POST["telefono"]
    
    try:
        nuevo_cliente = models.Cliente.objects.create(
            id = id,
            nombre = nombre,
            email = email,
            telefono = telefono,
            activo = True
            )
    except:
        print("Error")
        
        
    return redirect("terceros:lista_clientes/1")
        