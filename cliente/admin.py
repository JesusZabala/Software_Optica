from django.contrib import admin
from principal.models import Clientes

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'telefono', 'correo')
    search_fields = ('cedula', 'nombre')
    list_filter = ('nombre',) 