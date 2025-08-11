from django.shortcuts import render, redirect, get_object_or_404
from .forms import FabricacionForm, CambiarEstadoForm
from principal.models import Fabricacion
from django.contrib import messages

def registrar_fabricacion(request):
    if request.method == 'POST':
        form = FabricacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fabricación registrada correctamente.')
            return redirect('fabricaciones:registrar_fabricacion')
    else:
        form = FabricacionForm()
    return render(request, 'fabricaciones/registrar.html', {'form': form})

def consultar_fabricaciones(request):
    fabricaciones = Fabricacion.objects.select_related('diagnostico').all()
    return render(request, 'fabricaciones/consultar.html', {'fabricaciones': fabricaciones})

def cambiar_estado_fabricacion(request):
    
    fabricaciones = Fabricacion.objects.filter(estado='en proceso')

    if request.method == 'POST':
        id_fabricacion = request.POST.get('fabricacion')
        nuevo_estado = request.POST.get('estado')
        
        fabricacion = get_object_or_404(Fabricacion, id_fabricacion=id_fabricacion)
        fabricacion.estado = nuevo_estado
        fabricacion.save()
        
        messages.success(request, 'Estado de fabricación actualizado correctamente.')
        return redirect('fabricaciones:cambiar_estado_fabricacion')
    
    return render(request, 'fabricaciones/estado.html', {
        'fabricaciones': fabricaciones
    })