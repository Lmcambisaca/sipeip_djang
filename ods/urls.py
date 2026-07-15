from django.urls import path

from . import views

urlpatterns = [

    path("registrar/", views.registrar_objetivo, name="registrar_objetivo"),
    
    path("consultar/", views.consultar_objetivos, name="consultar_objetivos"),
    
    path("editar/<int:id>/", views.editar_objetivo, name="editar_objetivo"),

    path("seguimiento/<int:id>/", views.seguimiento_objetivo, name="seguimiento_objetivo"),
    
    path("dashboard/", views.dashboard_ods, name="dashboard_ods"),
]