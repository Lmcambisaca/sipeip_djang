from django.urls import path

from . import views

urlpatterns = [

    path("registrar/", views.registrar_objetivo_institucional, name="registrar_objetivo_institucional"),

    path("consultar/", views.consultar_objetivos_institucionales, name="consultar_objetivos_institucionales"),

    path("editar/<int:id>/", views.editar_objetivo_institucional, name="editar_objetivo_institucional"),
    
    path("seguimiento/<int:id>/", views.seguimiento_objetivo_institucional, name="seguimiento_objetivo_institucional"),
    
    path("dashboard/", views.dashboard_objetivos_institucionales, name="dashboard_objetivos_institucionales"),
]