from django.urls import path
from . import views

app_name = "ayuda"

urlpatterns = [
    path('', views.vista_principal, name='ayuda_inicio'),
    path('acerca/', views.acerca, name='acerca'),
    path('informacion/', views.informacion, name='informacion'),
    path('manual/', views.manual, name='manual'),
    path('manual/descargar/', views.descargar_manual_usuario, name='descargar_manual_usuario'),
]
