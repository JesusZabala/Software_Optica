from django.contrib import admin
from .models import Empleados

class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ('id_empleado', 'usuario', 'nombre', 'rol')  # columnas visibles
    list_filter = ('rol',)  
    search_fields = ('usuario', 'nombre')  
    
admin.site.register(Empleados, EmpleadosAdmin)
