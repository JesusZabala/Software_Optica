from django.urls import path
from . import views

app_name = 'cliente'

urlpatterns = [
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('modificar/', views.modificar_cliente, name='modificar_cliente'),
    path('consultar/', views.consultar_cliente, name='consultar_cliente'),
]
