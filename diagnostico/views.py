from django.shortcuts import render
from .forms import DiagnosticoForm
from principal.models import Diagnostico, Empleados
from django.contrib import messages
from django.utils import timezone


def registrar_diagnostico(request):
    empleado_id = request.session.get('empleado_id')
    empleado = None
    if empleado_id:
        try:
            empleado = Empleados.objects.get(id_empleado=empleado_id)
        except Empleados.DoesNotExist:
            empleado = None
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST, empleado=empleado)
        if form.is_valid():
            diagnostico = form.save(commit=False)
            diagnostico.fecha = timezone.now().date()
            diagnostico.save()
            messages.success(request, 'Diagnóstico registrado correctamente.')
            form = DiagnosticoForm(empleado=empleado)  # Refrescar formulario con nuevas citas disponibles
    else:
        form = DiagnosticoForm(empleado=empleado)

    return render(request, 'diagnostico/registrar.html', {'form': form})

def consultar_diagnosticos(request):
    cedula = request.GET.get('cedula', '').strip()
    diagnosticos = []

    if cedula:
        diagnosticos = Diagnostico.objects.filter(id_cita__id_cliente__cedula=cedula)

    return render(request, 'diagnostico/consultar.html', {
        'diagnosticos': diagnosticos,
        'cedula': cedula
    })