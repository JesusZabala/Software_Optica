from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from principal.models import Empleados
from django.urls import reverse

# REGISTRAR EMPLEADO
def registrar_empleado(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        rol = request.POST.get('rol', '').strip()

        # Validaciones
        if not all([usuario, contrasena, nombre, rol]):
            messages.error(request, 'Debe completar todos los campos.')
        elif len(usuario) < 4 or len(usuario) > 20 or ' ' in usuario:
            messages.error(request, 'El usuario debe tener entre 4 y 20 caracteres y no debe contener espacios.')
        elif not usuario.isalnum():
            messages.error(request, 'El usuario solo debe contener letras y números.')
        elif len(contrasena) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
        elif len(nombre) < 2 or len(nombre) > 50:
            messages.error(request, 'El nombre debe tener entre 2 y 50 caracteres.')
        elif not all(x.isalpha() or x.isspace() for x in nombre):
            messages.error(request, 'El nombre solo debe contener letras y espacios.')
        elif rol not in ['optometrista', 'recepcionista', 'tecnico', 'supervisor']:
            messages.error(request, 'Seleccione un rol válido.')
        elif Empleados.objects.filter(usuario=usuario).exists():
            messages.error(request, 'Ya existe un empleado con ese usuario.')
        else:
            Empleados.objects.create(usuario=usuario, contraseña=contrasena, nombre=nombre, rol=rol)
            messages.success(request, 'Empleado registrado correctamente.')
            return redirect('empleados:registrar_empleado')

    return render(request, 'empleado/registrar_empleado.html')

def consultar_empleado(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        try:
            empleado = Empleados.objects.get(usuario=usuario)
            
            request.session['empleado_consultado'] = usuario
            return redirect(reverse('empleados:consultar_empleado'))
        except Empleados.DoesNotExist:
            messages.error(request, 'Empleado no encontrado.')
            return redirect(reverse('empleados:consultar_empleado'))

    
    empleado = None
    usuario_guardado = request.session.pop('empleado_consultado', None)
    if usuario_guardado:
        try:
            empleado = Empleados.objects.get(usuario=usuario_guardado)
        except Empleados.DoesNotExist:
            pass

    return render(request, 'empleado/consultar_empleado.html', {'empleado': empleado})

# MODIFICAR EMPLEADO


def modificar_empleado(request):
    empleado = None
    datos_mostrados = False
    if request.method == 'POST':
        if 'usuario_busqueda' in request.POST and 'actualizar' not in request.POST:
            usuario_busqueda = request.POST['usuario_busqueda'].strip()
            if not usuario_busqueda or len(usuario_busqueda) < 4 or len(usuario_busqueda) > 20 or ' ' in usuario_busqueda:
                messages.error(request, 'Ingrese un usuario válido para buscar (4-20 caracteres, sin espacios).')
            else:
                try:
                    empleado = Empleados.objects.get(usuario=usuario_busqueda)
                    datos_mostrados = True
                except Empleados.DoesNotExist:
                    messages.error(request, 'Empleado no encontrado.')
        elif 'actualizar' in request.POST:
            usuario_original = request.POST['usuario_original']
            try:
                empleado = Empleados.objects.get(usuario=usuario_original)
                nuevo_usuario = request.POST['usuario'].strip()
                nueva_contrasena = request.POST['contrasena'].strip()
                nuevo_nombre = request.POST['nombre'].strip()
                nuevo_rol = request.POST['rol'].strip()
                # Validaciones
                if not all([nuevo_usuario, nuevo_nombre, nuevo_rol]):
                    messages.error(request, 'Debe completar todos los campos.')
                    datos_mostrados = True
                elif len(nuevo_usuario) < 4 or len(nuevo_usuario) > 20 or ' ' in nuevo_usuario:
                    messages.error(request, 'El usuario debe tener entre 4 y 20 caracteres y no debe contener espacios.')
                    datos_mostrados = True
                elif not nuevo_usuario.isalnum():
                    messages.error(request, 'El usuario solo debe contener letras y números.')
                    datos_mostrados = True
                elif len(nuevo_nombre) < 2 or len(nuevo_nombre) > 50:
                    messages.error(request, 'El nombre debe tener entre 2 y 50 caracteres.')
                    datos_mostrados = True
                elif not all(x.isalpha() or x.isspace() for x in nuevo_nombre):
                    messages.error(request, 'El nombre solo debe contener letras y espacios.')
                    datos_mostrados = True
                elif nuevo_rol not in ['optometrista', 'recepcionista', 'tecnico', 'supervisor']:
                    messages.error(request, 'Seleccione un rol válido.')
                    datos_mostrados = True
                elif nuevo_usuario != empleado.usuario and Empleados.objects.filter(usuario=nuevo_usuario).exists():
                    messages.error(request, 'Ese usuario ya está en uso.')
                    datos_mostrados = True
                else:
                    empleado.usuario = nuevo_usuario
                    if nueva_contrasena:
                        if len(nueva_contrasena) < 6:
                            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                            datos_mostrados = True
                        else:
                            empleado.contraseña = nueva_contrasena
                    empleado.nombre = nuevo_nombre
                    empleado.rol = nuevo_rol
                    empleado.save()
                    messages.success(request, 'Empleado actualizado correctamente.')
                    empleado = None
                    datos_mostrados = False
            except Empleados.DoesNotExist:
                messages.error(request, 'Empleado no encontrado.')
    return render(request, 'empleado/modificar_empleado.html', {
        'empleado': empleado,
        'datos_mostrados': datos_mostrados
    })

# Mostrar lista de empleados para eliminar
def lista_empleados_para_eliminar(request):
    empleados = Empleados.objects.filter(rol__in=['optometrista', 'recepcionista', 'tecnico'])

    return render(request, 'empleado/eliminar_empleado.html', {'empleados': empleados})

# Eliminar empleado por ID
def borrar_empleado(request, id_empleado):
    empleado = get_object_or_404(Empleados, id_empleado=id_empleado)
    empleado.delete()
    messages.success(request, 'Empleado eliminado correctamente.')
    return redirect('empleados:eliminar_empleado')