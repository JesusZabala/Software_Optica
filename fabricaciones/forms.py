from django import forms
from principal.models import Fabricacion, Diagnostico
from django.forms.widgets import DateInput
from datetime import date

from django import forms
from principal.models import Fabricacion, Diagnostico
from django.forms.widgets import DateInput
from datetime import date

class FabricacionForm(forms.ModelForm):

    # tipo de producto
    PRODUCTO_OPCIONES = [
        ('Lente monofocal', 'Lente monofocal'),
        ('Lente bifocal', 'Lente bifocal'),
        ('Lente progresivo', 'Lente progresivo'),
    ]

    # materiales
    MATERIALES_OPCIONES = [
        ('Policarbonato', 'Policarbonato'),
        ('CR39', 'CR39'),
        ('Trivex', 'Trivex'),
        ('Vidrio', 'Vidrio'),
    ]

    # tratamientos
    TRATAMIENTOS_OPCIONES = [
        ('Fotocromático', 'Fotocromático'),
        ('Antirreflejo', 'Antirreflejo'),
        ('Anti blue', 'Anti blue'),
        ('Antirreflejo + Anti blue', 'Antirreflejo + Anti blue'),
        ('Fotocromático + Antirreflejo + Anti blue', 'Fotocromático + Antirreflejo + Anti blue'),
    ]

    # esfera de -10 a +10 en pasos de 0.25
    ESFERA_OPCIONES = [ (f"{x:+.2f}", f"{x:+.2f}") for x in [i * 0.25 for i in range(-40,41)] ]

    # cilindro de -6 a 0 en pasos de 0.25
    CILINDRO_OPCIONES = [ (f"{x:+.2f}", f"{x:+.2f}") for x in [i * 0.25 for i in range(-24,1)] ]

    # eje 0 a 180
    EJE_OPCIONES = [ (str(x), f"{x}°") for x in range(0,181,5) ]

    # adición +1 a +3 en pasos de 0.25
    ADICCION_OPCIONES = [ ("", "---------") ] + [ (f"{x:+.2f}", f"{x:+.2f}") for x in [1 + 0.25*i for i in range(0,9)] ]


    # campos ojo izquierdo
    esfera_oi = forms.ChoiceField(label="Esfera OI", choices=ESFERA_OPCIONES)
    cilindro_oi = forms.ChoiceField(label="Cilindro OI", choices=CILINDRO_OPCIONES, required=False)
    eje_oi = forms.ChoiceField(label="Eje OI", choices=EJE_OPCIONES, required=False)

    # campos ojo derecho
    esfera_od = forms.ChoiceField(label="Esfera OD", choices=ESFERA_OPCIONES)
    cilindro_od = forms.ChoiceField(label="Cilindro OD", choices=CILINDRO_OPCIONES, required=False)
    eje_od = forms.ChoiceField(label="Eje OD", choices=EJE_OPCIONES, required=False)

    # adición
    adicion = forms.ChoiceField(label="Adición", choices=ADICCION_OPCIONES, required=False)

    # tipo de producto
    tipo_producto = forms.ChoiceField(
        label="Tipo de Producto",
        choices=PRODUCTO_OPCIONES
    )

    # materiales
    materiales = forms.ChoiceField(
        label="Materiales",
        choices=MATERIALES_OPCIONES
    )

    # tratamientos
    tratamientos = forms.ChoiceField(
        label="Tratamientos",
        choices=TRATAMIENTOS_OPCIONES,
        required=False
    )

    class Meta:
        model = Fabricacion
        fields = ['diagnostico', 'tipo_producto', 'materiales', 'tratamientos', 'fecha_entrega_estimada']
        widgets = {
            'fecha_entrega_estimada': DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'diagnostico': {'required': 'El diagnóstico es obligatorio.'},
            'fecha_entrega_estimada': {'required': 'La fecha estimada de entrega es obligatoria.'},
        }

    def clean_fecha_entrega_estimada(self):
        fecha = self.cleaned_data.get('fecha_entrega_estimada')
        if not fecha:
            raise forms.ValidationError('Debe ingresar una fecha de entrega estimada.')
        if fecha < date.today():
            raise forms.ValidationError('La fecha de entrega no puede ser en el pasado.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()

        tipo_producto = cleaned_data.get('tipo_producto')
        adicion = cleaned_data.get('adicion')

        if tipo_producto in ['Lente bifocal', 'Lente progresivo']:
            if not adicion:
                raise forms.ValidationError("Debe indicar la adición para lentes bifocales o progresivos.")
        elif tipo_producto == 'Lente monofocal':
            if adicion:
                raise forms.ValidationError("No se permite adición en lentes monofocales.")
            cleaned_data['adicion'] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        esfera_oi = self.cleaned_data.get('esfera_oi')
        cilindro_oi = self.cleaned_data.get('cilindro_oi')
        eje_oi = self.cleaned_data.get('eje_oi')

        esfera_od = self.cleaned_data.get('esfera_od')
        cilindro_od = self.cleaned_data.get('cilindro_od')
        eje_od = self.cleaned_data.get('eje_od')

        adicion = self.cleaned_data.get('adicion')

        formula_oi = f"{esfera_oi}"
        if cilindro_oi and cilindro_oi != "0.00":
            formula_oi += f" {cilindro_oi} x{eje_oi}"
        if adicion:
            formula_oi += f" ADD {adicion}"

        formula_od = f"{esfera_od}"
        if cilindro_od and cilindro_od != "0.00":
            formula_od += f" {cilindro_od} x{eje_od}"
        if adicion:
            formula_od += f" ADD {adicion}"

        instance.formula = f"OI: {formula_oi} | OD: {formula_od}"
        instance.estado = 'en proceso'

        if commit:
            instance.save()
        return instance


class CambiarEstadoForm(forms.ModelForm):
    class Meta:
        model = Fabricacion
        fields = ['diagnostico', 'estado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['diagnostico'].label_from_instance = lambda obj: f"Diagnóstico #{obj.id_diagnostico}"

    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '').strip()
        if not estado:
            raise forms.ValidationError('Debe seleccionar un estado.')
        if estado not in ['en proceso', 'terminada', 'cancelada']:
            raise forms.ValidationError('Estado no válido.')
        return estado
