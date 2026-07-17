from django.urls import path
from . import views

urlpatterns = [

    path("registrar/", views.registrar_configuracion, name="registrar_configuracion"),

    path("consultar/", views.consultar_configuracion, name="consultar_configuracion"),

    path("editar/<int:id>/", views.editar_configuracion, name="editar_configuracion"),
]