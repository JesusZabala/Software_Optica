from django import forms
from principal.models import Diagnostico, Cita
from django.core.exceptions import ValidationError

from datetime import date

from datetime import datetime
from django.utils.timezone import make_aware
from django import forms
from principal.models import Diagnostico, Cita

from datetime import datetime
from django.utils.timezone import make_aware
from django import forms
from principal.models import Diagnostico, Cita

class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnostico
        fields = ['id_cita', 'descripcion']

    def __init__(self, *args, **kwargs):
        empleado = kwargs.pop('empleado', None)
        super(DiagnosticoForm, self).__init__(*args, **kwargs)

        citas_diagnosticadas = Diagnostico.objects.values_list('id_cita', flat=True)
        ahora = make_aware(datetime.now())

        if empleado is not None:
            self.fields['id_cita'].queryset = (
                Cita.objects
                .filter(estado='agendada', id_empleado=empleado, fecha_hora__lte=ahora)
                .exclude(id_cita__in=citas_diagnosticadas)
            )
        else:
            self.fields['id_cita'].queryset = (
                Cita.objects
                .filter(estado='agendada', fecha_hora__lte=ahora)
                .exclude(id_cita__in=citas_diagnosticadas)
            )

        self.fields['id_cita'].label_from_instance = lambda obj: (
            f"Cita #{obj.id_cita} - "
            f"Cliente: {obj.id_cliente.nombre if obj.id_cliente else 'N/A'} - "
            f"Optometrista: {obj.id_empleado.nombre if obj.id_empleado else 'N/A'} - "
            f"Fecha: {obj.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
        )

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        if not descripcion:
            raise forms.ValidationError('La descripción es obligatoria.')
        if len(descripcion) < 5:
            raise forms.ValidationError('La descripción debe tener al menos 5 caracteres.')
        return descripcion


