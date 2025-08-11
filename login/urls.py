from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
    path('recepcionista/', views.recepcionista_view, name='recepcionista'),
    path('optometrista/', views.optometrista_view, name='optometrista'),
    path('tecnico/', views.tecnico_view, name='tecnico'),
    path('supervisor/', views.supervisor_view, name="supervisor"),
    path('loading/', views.loading_screen, name='loading_screen'),
    path('deslogueando/', views.logout_loading_screen, name='logout_loading_screen'),
]
