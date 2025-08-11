from django.shortcuts import render, redirect
from django.contrib import messages
from principal.models import Empleados, Cita, Clientes, Fabricacion, Diagnostico
from django.views.decorators.cache import never_cache
from functools import wraps
from django.db.models import Count


def login_required_custom(view_func):
    @wraps(view_func)
    @never_cache  
    def wrapper(request, *args, **kwargs):
        if not request.session.get('empleado_id'):
            return redirect('Login') 
        return view_func(request, *args, **kwargs)
    return wrapper

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            empleado = Empleados.objects.get(usuario=username)
        except Empleados.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos!!')
            return render(request, 'login/login.html')
        
        if empleado.contraseña == password:
            
            request.session['empleado_id'] = empleado.id_empleado
            request.session['rol'] = empleado.rol

            # Redirigir a la pantalla de carga para todos los roles válidos
            if empleado.rol in ['recepcionista', 'optometrista', 'tecnico', 'supervisor']:
                return redirect('loading_screen')
            else:
                messages.error(request, "Rol no reconocido")
                return render(request, 'login/login.html')

        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return render(request, 'login/login.html')


    return render(request, 'login/login.html')

@login_required_custom
def recepcionista_view(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleados.objects.get(id_empleado=empleado_id)

    # Estadísticas
    total_citas = Cita.objects.count()
    total_clientes = Clientes.objects.count()
    total_citas_confirmadas = Cita.objects.filter(estado='agendada').count()

    # Próximas citas (todas, ordenadas de la más próxima a la más lejana)
    proximas_citas = Cita.objects.select_related('id_cliente', 'id_empleado').order_by('fecha_hora')

    context = {
        'empleado': empleado,
        'total_citas': total_citas,
        'total_clientes': total_clientes,
        'total_citas_confirmadas': total_citas_confirmadas,
        'proximas_citas': proximas_citas,
    }
    return render(request, 'principal/recepcionista.html', context)

@login_required_custom
def optometrista_view(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleados.objects.get(id_empleado=empleado_id)

    # Citas relacionadas a este optometrista
    citas_optometrista = Cita.objects.filter(id_empleado=empleado)
    total_citas = citas_optometrista.count()
    total_diagnosticos = Diagnostico.objects.filter(id_cita__id_empleado=empleado).count()
    total_citas_confirmadas = citas_optometrista.filter(estado='agendada').count()

    context = {
        'empleado': empleado,
        'citas_optometrista': citas_optometrista.order_by('fecha_hora'),
        'total_citas': total_citas,
        'total_diagnosticos': total_diagnosticos,
        'total_citas_confirmadas': total_citas_confirmadas,
    }
    return render(request, 'principal/optometrista.html', context)

@login_required_custom
def tecnico_view(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        messages.error(request, "No hay sesión de empleado activa.")
        return redirect('login')  # Cambia 'login' por el nombre real de tu url de login

    try:
        empleado = Empleados.objects.get(id_empleado=empleado_id)
    except Empleados.DoesNotExist:
        messages.error(request, "Empleado no encontrado.")
        return redirect('login')

    total_fabricaciones = Fabricacion.objects.count()
    total_terminadas = Fabricacion.objects.filter(estado='terminada').count()
    total_enproceso_canceladas = Fabricacion.objects.filter(estado__in=['en proceso', 'cancelada']).count()

    fabricaciones = Fabricacion.objects.select_related('diagnostico__id_cita__id_cliente').all().order_by('-fecha_registro')

    context = {
        'empleado': empleado,
        'total_fabricaciones': total_fabricaciones,
        'total_terminadas': total_terminadas,
        'total_enproceso_canceladas': total_enproceso_canceladas,
        'fabricaciones': fabricaciones,
    }
    return render(request, 'principal/tecnico.html', context)

@login_required_custom
def supervisor_view(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleados.objects.get(id_empleado=empleado_id)

    # Estadísticas: contar TODO lo que hay en la BDD
    citas_total = Cita.objects.count()
    empleados_total = Empleados.objects.count()
    clientes_total = Clientes.objects.count()
    fabricaciones_total = Fabricacion.objects.count()

    # Alertas Recientes
    ultima_cita = Cita.objects.order_by('-fecha_hora').select_related('id_cliente').first()
    ultimo_empleado = Empleados.objects.order_by('-id_empleado').first()
    ultima_fabricacion = Fabricacion.objects.order_by('-id_fabricacion').select_related('diagnostico__id_cita__id_cliente').first()

    # Resumen de actividad: últimas 5 citas y fabricaciones (sin importar estado)
    ultimas_citas = list(Cita.objects.order_by('-fecha_hora').select_related('id_cliente')[:5]) if Cita.objects.exists() else []
    ultimas_fabricaciones = list(Fabricacion.objects.order_by('-id_fabricacion').select_related('diagnostico__id_cita__id_cliente')[:5]) if Fabricacion.objects.exists() else []

    context = {
        'empleado': empleado,
        'citas_total': citas_total,
        'empleados_total': empleados_total,
        'clientes_total': clientes_total,
        'fabricaciones_total': fabricaciones_total,
        'ultima_cita': ultima_cita,
        'ultimo_empleado': ultimo_empleado,
        'ultima_fabricacion': ultima_fabricacion,
        'ultimas_citas': ultimas_citas,
        'ultimas_fabricaciones': ultimas_fabricaciones,
    }
    return render(request, 'principal/supervisor.html', context)

@never_cache
def logout_view(request):
    
    request.session.flush()

    response = redirect('Login')

     
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

def loading_screen(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('Login')
    try:
        empleado = Empleados.objects.get(id_empleado=empleado_id)
    except Empleados.DoesNotExist:
        return redirect('Login')
    rol = empleado.rol.lower()
    # Mapeo de roles a URLs
    url_map = {
        'tecnico': 'tecnico',
        'optometrista': 'optometrista',
        'supervisor': 'supervisor',
        'recepcionista': 'recepcionista',
    }
    menu_url = None
    if rol in url_map:
        from django.urls import reverse
        menu_url = reverse(url_map[rol])
    else:
        menu_url = reverse('Login')
    return render(request, 'login/loading_screen.html', {'menu_url': menu_url})

def logout_loading_screen(request):
    from django.urls import reverse
    logout_url = reverse('Logout')
    return render(request, 'login/logout_loading_screen.html', {'logout_url': logout_url})
