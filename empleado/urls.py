# URLS (en urls.py de la app empleado)
from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    path('registrar/', views.registrar_empleado, name='registrar_empleado'),
    path('modificar/', views.modificar_empleado, name='modificar_empleado'),
    path('eliminar/', views.lista_empleados_para_eliminar, name='eliminar_empleado'),
    path('eliminar/<int:id_empleado>/', views.borrar_empleado, name='borrar_empleado'),
    path('consultar/', views.consultar_empleado, name='consultar_empleado'),
]