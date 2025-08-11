from django.urls import path
from . import views

urlpatterns = [
    path('agendar/', views.agendar_cita, name='agendar_cita'),
    path('modificar/', views.modificar_cita, name='modificar_cita'),
    path('cancelar/', views.cancelar_cita, name='cancelar_cita'),
    path('consultar/', views.consultar_cita, name='consultar_cita'),
]
