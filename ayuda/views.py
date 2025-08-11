from django.shortcuts import render

def vista_principal(request):
    return render(request, 'ayuda/inicio.html')  
    
def acerca(request):
    return render(request, 'ayuda/acerca.html')

def informacion(request): 
    return render(request, 'ayuda/informacion.html')

def manual(request):
    return render(request, 'ayuda/manual.html')

# Vista para descargar el manual de usuario (placeholder)
from django.http import FileResponse, Http404
import os
from django.conf import settings

def descargar_manual_usuario(request):
    manual_path = os.path.join(settings.BASE_DIR, 'ayuda', 'static', 'ayuda', 'manual', 'manual_usuario.pdf')
    if os.path.exists(manual_path):
        return FileResponse(open(manual_path, 'rb'), as_attachment=True, filename='manual_usuario.pdf')
    else:
        raise Http404("El manual de usuario no se encuentra disponible.")