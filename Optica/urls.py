"""
URL configuration for Optica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('clientes/', include('cliente.urls', namespace='cliente')),
    path('empleados/', include('empleado.urls', namespace='empleados')),
    path('citas/', include('citas.urls')),
    path('diagnostico/', include('diagnostico.urls')),
    path('fabricaciones/', include('fabricaciones.urls')),
    path('reportes/', include('reportes.urls')),
    path('ayuda/', include('ayuda.urls')),
]
