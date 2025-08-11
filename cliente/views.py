from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from principal.models import Clientes  
from django.db.models import Q
import re


def registrar_cliente(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validar que todos los campos estén completos
        if not all([cedula, nombre, telefono, direccion, correo]):
            messages.error(request, 'Debe completar todos los campos.')
            return render(request, 'cliente/registrar_cliente.html')

        # Validar formato de cédula (solo números, longitud razonable)
        if not cedula.isdigit() or not (6 <= len(cedula) <= 10):
            messages.error(request, 'La cédula debe ser numérica y tener entre 6 y 10 dígitos.')
            return render(request, 'cliente/registrar_cliente.html')

        # Validar formato de teléfono (solo números, longitud razonable)
        if not telefono.isdigit() or not (7 <= len(telefono) <= 15):
            messages.error(request, 'El teléfono debe ser numérico y tener entre 7 y 15 dígitos.')
            return render(request, 'cliente/registrar_cliente.html')

        # Validar formato de correo
        email_regex = r'^\S+@\S+\.\S+$'
        if not re.match(email_regex, correo):
            messages.error(request, 'Ingrese un correo electrónico válido.')
            return render(request, 'cliente/registrar_cliente.html')

        # Validar si ya existe cliente con esa cédula
        if Clientes.objects.filter(cedula=cedula).exists():
            messages.error(request, 'El cliente con esa cédula ya existe.')
            return render(request, 'cliente/registrar_cliente.html')

        # Guardar el cliente
        cliente = Clientes(
            cedula=cedula,
            nombre=nombre,
            telefono=telefono,
            direccion=direccion,
            correo=correo
        )
        cliente.save()
        messages.success(request, 'Cliente registrado exitosamente.')
        return redirect('cliente:registrar_cliente')

    return render(request, 'cliente/registrar_cliente.html')



def consultar_cliente(request):
    cliente = None
    mensaje = ''
    cedula = request.GET.get('cedula')

    if cedula:
        try:
            cliente = Clientes.objects.get(cedula=cedula)
        except Clientes.DoesNotExist:
            mensaje = "Cliente no encontrado."

    return render(request, 'cliente/consultar_cliente.html', {'cliente': cliente, 'mensaje': mensaje})

def modificar_cliente(request):
    cliente = None
    if request.method == 'GET':
        cedula_buscar = request.GET.get('cedula', '').strip()
        if cedula_buscar:
            if not cedula_buscar.isdigit() or not (6 <= len(cedula_buscar) <= 10):
                messages.error(request, "La cédula debe ser numérica y tener entre 6 y 10 dígitos.")
            else:
                try:
                    cliente = Clientes.objects.get(cedula=cedula_buscar)
                except Clientes.DoesNotExist:
                    messages.error(request, "Cliente no encontrado con esa cédula.")
    elif request.method == 'POST':
        cedula_original = request.POST.get('cedula_original', '').strip()
        cedula_nueva = request.POST.get('cedula', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        direccion = request.POST.get('direccion', '').strip()

        cliente = get_object_or_404(Clientes, cedula=cedula_original)

        # Validaciones
        if not all([cedula_nueva, nombre, telefono, correo, direccion]):
            messages.error(request, "Debe completar todos los campos.")
            return render(request, 'cliente/modificar_cliente.html', {'cliente': cliente})
        if not cedula_nueva.isdigit() or not (6 <= len(cedula_nueva) <= 10):
            messages.error(request, "La cédula debe ser numérica y tener entre 6 y 10 dígitos.")
            return render(request, 'cliente/modificar_cliente.html', {'cliente': cliente})
        if not telefono.isdigit() or not (7 <= len(telefono) <= 15):
            messages.error(request, "El teléfono debe ser numérico y tener entre 7 y 15 dígitos.")
            return render(request, 'cliente/modificar_cliente.html', {'cliente': cliente})
        email_regex = r'^\S+@\S+\.\S+$'
        if not re.match(email_regex, correo):
            messages.error(request, "Ingrese un correo electrónico válido.")
            return render(request, 'cliente/modificar_cliente.html', {'cliente': cliente})
        if cedula_original != cedula_nueva:
            if Clientes.objects.filter(cedula=cedula_nueva).exists():
                messages.error(request, "La cédula nueva ya está registrada para otro cliente.")
                return render(request, 'cliente/modificar_cliente.html', {'cliente': cliente})
        cliente.cedula = cedula_nueva
        cliente.nombre = nombre
        cliente.telefono = telefono
        cliente.correo = correo
        cliente.direccion = direccion
        cliente.save()
        messages.success(request, "Cliente actualizado correctamente.")
        cliente = None
    return render(request, 'cliente/modificar_cliente.html', {'cliente': cliente})
