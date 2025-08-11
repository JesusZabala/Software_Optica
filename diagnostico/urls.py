from django.urls import path
from diagnostico import views

app_name = 'diagnostico'

urlpatterns = [
    path('registrar/', views.registrar_diagnostico, name='registrar_diagnostico'),
    path('consultar/', views.consultar_diagnosticos, name='consultar'),
]
