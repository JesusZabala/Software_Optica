from django import forms
from django.core.exceptions import ValidationError
from principal.models import Cita, Empleados, Clientes
from django.utils import timezone

class AgendarCitaForm(forms.ModelForm):
    cedula = forms.CharField(max_length=10, label="Cédula del cliente")

    class Meta:
        model = Cita
        fields = ['cedula', 'id_empleado', 'fecha_hora']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'step': 3600}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_empleado'].queryset = Empleados.objects.filter(rol='optometrista')
        self.fields['id_empleado'].label = "Optometrista"

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula', '').strip()
        if not cedula.isdigit() or not (6 <= len(cedula) <= 10):
            raise forms.ValidationError('La cédula debe ser numérica y tener entre 6 y 10 dígitos.')
        return cedula

    def clean(self):
        cleaned_data = super().clean()
        cedula = cleaned_data.get('cedula')
        optometrista = cleaned_data.get('id_empleado')
        fecha_hora = cleaned_data.get('fecha_hora')

        # Validar cliente
        try:
            cliente = Clientes.objects.get(cedula=cedula)
            cleaned_data['id_cliente'] = cliente
        except Clientes.DoesNotExist:
            raise forms.ValidationError("El cliente con esa cédula no existe.")

        if fecha_hora and optometrista:
            fecha_hora_redondeada = fecha_hora.replace(minute=0, second=0, microsecond=0)
            cleaned_data['fecha_hora'] = fecha_hora_redondeada

            ahora = timezone.localtime(timezone.now())
            fecha_actual = ahora.date()
            fecha_cita = fecha_hora_redondeada.date()

            if fecha_cita < fecha_actual:
                raise forms.ValidationError("No puedes agendar citas en fechas pasadas.")

            # Validar rango horario
            if not (9 <= fecha_hora_redondeada.hour < 18):
                raise forms.ValidationError("Solo puedes agendar citas entre las 9:00 y las 18:00.")

            # Validar colisión en la misma hora
            existe = Cita.objects.filter(
                id_empleado=optometrista,
                fecha_hora__year=fecha_hora_redondeada.year,
                fecha_hora__month=fecha_hora_redondeada.month,
                fecha_hora__day=fecha_hora_redondeada.day,
                fecha_hora__hour=fecha_hora_redondeada.hour,
                estado='agendada'
            ).exists()
            if existe:
                citas_dia = Cita.objects.filter(
                    id_empleado=optometrista,
                    fecha_hora__date=fecha_hora_redondeada.date(),
                    estado='agendada'
                ).values_list('fecha_hora', flat=True)
                horas_ocupadas = set(dt.hour for dt in citas_dia)
                horas_disponibles = [h for h in range(9, 18) if h not in horas_ocupadas]
                if not horas_disponibles:
                    raise forms.ValidationError("Todas las horas de este día ya están ocupadas para este optometrista.")
                sugerencias = ', '.join(f"{h}:00" for h in horas_disponibles)
                raise forms.ValidationError(
                    f"Ya existe una cita a las {fecha_hora_redondeada.hour}:00. Horas disponibles: {sugerencias}."
                )

        return cleaned_data


class ModificarCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['id_empleado', 'fecha_hora']

    def __init__(self, *args, **kwargs):
        super(ModificarCitaForm, self).__init__(*args, **kwargs)
        self.fields['id_empleado'].queryset = Empleados.objects.filter(rol='optometrista')
        self.fields['fecha_hora'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'step': 3600}  # paso de 1 hora
        )

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get('fecha_hora')
        id_empleado = cleaned_data.get('id_empleado')

        if fecha_hora and id_empleado:
            fecha_hora_redondeada = fecha_hora.replace(minute=0, second=0, microsecond=0)
            cleaned_data['fecha_hora'] = fecha_hora_redondeada

            ahora = timezone.localtime(timezone.now())
            fecha_actual = ahora.date()
            fecha_cita = fecha_hora_redondeada.date()

            if fecha_cita < fecha_actual:
                raise forms.ValidationError("No puedes modificar la cita a una fecha pasada.")

            # Validar rango horario
            if not (9 <= fecha_hora_redondeada.hour < 18):
                raise forms.ValidationError("Solo puedes modificar citas entre las 9:00 y las 18:00.")

            # Validar colisiones, excluyendo la cita actual
            existe = Cita.objects.filter(
                id_empleado=id_empleado,
                fecha_hora__year=fecha_hora_redondeada.year,
                fecha_hora__month=fecha_hora_redondeada.month,
                fecha_hora__day=fecha_hora_redondeada.day,
                fecha_hora__hour=fecha_hora_redondeada.hour,
                estado='agendada'
            ).exclude(id_cita=self.instance.id_cita).exists()

            if existe:
                raise forms.ValidationError(
                    f"Ya existe una cita agendada para este optometrista a las {fecha_hora_redondeada.hour}:00 en ese día."
                )

        return cleaned_data

