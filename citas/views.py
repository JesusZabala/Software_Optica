from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import AgendarCitaForm, ModificarCitaForm
from principal.models import Cita, Empleados
from django.utils import timezone
from django.shortcuts import render
from .forms import AgendarCitaForm
from principal.models import Clientes, Cita
from django.contrib import messages

def agendar_cita(request):
    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            cliente = form.cleaned_data['id_cliente']
            cita = Cita(
                id_cliente=cliente,
                id_empleado=form.cleaned_data['id_empleado'],
                fecha_hora=form.cleaned_data['fecha_hora'],
                estado='agendada'
            )
            cita.save()
            messages.success(request, "Cita registrada correctamente.")
            form = AgendarCitaForm()  # limpiar formulario
    else:
        form = AgendarCitaForm()

    return render(request, 'citas/agendar_citas.html', {'form': form})

def modificar_cita(request):
    # Traer solo citas agendadas y con fecha mayor o igual a ahora
    citas = Cita.objects.filter(
        estado='agendada',
        fecha_hora__gte=timezone.now()
    ).order_by('fecha_hora')

    cita = None
    form = None

    if request.method == 'GET' and 'id_cita' in request.GET:
        id_cita = request.GET.get('id_cita')
        cita = get_object_or_404(Cita, id_cita=id_cita)
        form = ModificarCitaForm(instance=cita)

    elif request.method == 'POST':
        id_cita = request.GET.get('id_cita')
        cita = get_object_or_404(Cita, id_cita=id_cita)
        form = ModificarCitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita modificada exitosamente.")
            # Volver a selector sin formulario
            return render(request, 'citas/modificar_citas.html', {
                'citas': citas,
                'form': None,
                'cita': None
            })

    return render(request, 'citas/modificar_citas.html', {
        'citas': citas,
        'cita': cita,
        'form': form
    })

def cancelar_cita(request):
    if request.method == 'POST':
        id_cita = request.POST.get('id_cita')
        cita = get_object_or_404(Cita, id_cita=id_cita)
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, 'Cita cancelada exitosamente.')
        return redirect('cancelar_cita')
    else:
        citas = Cita.objects.filter(estado='agendada').order_by('fecha_hora')
        return render(request, 'citas/cancelar_citas.html', {'citas': citas})

def consultar_cita(request):
    citas = None  
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    cedula = request.GET.get('cedula')

    if fecha or estado or cedula:
        citas = Cita.objects.all()
        if fecha:
            citas = citas.filter(fecha_hora__date=fecha)
        if estado:
            citas = citas.filter(estado=estado)
        if cedula:
            citas = citas.filter(id_cliente__cedula=cedula)
    return render(request, 'citas/consultar_citas.html', {'citas': citas})