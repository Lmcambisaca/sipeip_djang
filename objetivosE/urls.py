from django.urls import path

from . import views

urlpatterns = [

    path(

        "registrar/",

        views.registrar_objetivo_estrategico,

        name="registrar_objetivo_estrategico"

    ),

    path(

        "consultar/",

        views.consultar_objetivos_estrategicos,

        name="consultar_objetivos_estrategicos"

    ),

    path(

        "editar/<int:id>/",

        views.editar_objetivo_estrategico,

        name="editar_objetivo_estrategico"

    ),
    
    path(
    "seguimiento/<int:id>/",
    views.seguimiento_objetivo_estrategico,
    name="seguimiento_objetivo_estrategico"
    ),

    path(
        "dashboard/",
        views.dashboard_objetivos_estrategicos,
        name="dashboard_objetivos_estrategicos"
    ),

]