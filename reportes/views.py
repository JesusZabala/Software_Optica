import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime, time
from django.contrib import messages
from django.shortcuts import render
from principal.models import Clientes, Empleados, Cita, Diagnostico, Fabricacion

def generar_reporte(request):
    if request.method == 'POST':
        modulo = request.POST.get('modulo')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        except Exception:
            messages.error(request, 'Fechas inválidas.')
            return render(request, 'reportes/generar.html')
        if fecha_inicio_dt > fecha_fin_dt:
            messages.error(request, 'La fecha de inicio no puede ser mayor que la fecha de fin.')
            return render(request, 'reportes/generar.html')
        fecha_fin_dt = datetime.combine(fecha_fin_dt.date(), time.max)

        headers = []
        resultados = []

        if modulo == 'clientes':
            qs = Clientes.objects.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))
            headers = ['ID', 'Nombre', 'Cédula', 'Teléfono', 'Correo', 'Dirección']
            resultados = [ [c.id_cliente, c.nombre, c.cedula, c.telefono, c.correo, c.direccion] for c in qs ]
        elif modulo == 'empleados':
            qs = Empleados.objects.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))
            headers = ['ID', 'Nombre', 'Usuario', 'Rol']
            resultados = [ [e.id_empleado, e.nombre, e.usuario, e.rol] for e in qs ]
        elif modulo == 'citas':
            qs = Cita.objects.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))
            headers = ['ID', 'Cliente', 'Optometrista', 'Fecha/Hora', 'Estado']
            resultados = [ 
                [c.id_cita, c.id_cliente.nombre if c.id_cliente else '',
                 c.id_empleado.nombre if c.id_empleado else '',
                 c.fecha_hora.strftime('%Y-%m-%d %H:%M'), c.estado] for c in qs
            ]
        elif modulo == 'diagnosticos':
            qs = Diagnostico.objects.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))
            headers = ['ID', 'Cliente', 'Descripción', 'Fecha']
            resultados = [
                [d.id_diagnostico, d.id_cita.id_cliente.nombre if d.id_cita and d.id_cita.id_cliente else '',
                 d.descripcion, d.fecha.strftime('%Y-%m-%d')] for d in qs
            ]
        elif modulo == 'fabricaciones':
            qs = Fabricacion.objects.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))
            headers = ['ID', 'Cliente', 'Producto', 'Estado', 'Fecha registro']
            resultados = [
                [f.id_fabricacion, f.diagnostico.id_cita.id_cliente.nombre if f.diagnostico and f.diagnostico.id_cita else '',
                 f.tipo_producto, f.estado, f.fecha_registro.strftime('%Y-%m-%d')] for f in qs
            ]

        html_string = render_to_string('reportes/pdf_template.html', {
            'modulo': modulo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'headers': headers,
            'resultados': resultados
        })

        # Si wkhtmltopdf no está en el PATH, indica su ruta aquí:
        config = pdfkit.configuration(
            wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        )

        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
        }

        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_{modulo}.pdf"'
        return response

    return render(request, 'reportes/generar.html')
