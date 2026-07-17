from django.urls import path
from . import views

urlpatterns = [

    path("registrar/", views.registrar_planificacion, name="registrar_planificacion"),
    
    path("consultar/", views.consultar_planificaciones, name="consultar_planificaciones"),
    
    path("editar/<int:id>/", views.editar_planificacion, name="editar_planificacion"),
    
    path("eliminar/<int:id>/", views.eliminar_planificacion, name="eliminar_planificacion"),
    
    path("validar/<int:id>/", views.validar_planificacion, name="validar_planificacion"),
    
    path("aprobar/<int:id>/", views.aprobar_planificacion, name="aprobar_planificacion"),

    path("rechazar/<int:id>/", views.rechazar_planificacion, name="rechazar_planificacion"),
]