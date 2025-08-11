from django.urls import path
from fabricaciones import views

app_name = 'fabricaciones'

urlpatterns = [
    path('registrar/', views.registrar_fabricacion, name='registrar_fabricacion'),
    path('consultar/', views.consultar_fabricaciones, name='consultar_fabricaciones'),
    path('estado/', views.cambiar_estado_fabricacion, name='cambiar_estado_fabricacion'),
]
