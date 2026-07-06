from django.urls import path
from . import views

urlpatterns = [

    path(
        "registrar/",
        views.registrar_rol,
        name="registrar_rol"
    ),

    path(
        "consultar/",
        views.consultar_roles,
        name="consultar_roles"
    ),

    path(
        "editar/<int:id>/",
        views.editar_rol,
        name="editar_rol"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_rol,
        name="eliminar_rol"
    ),

    path(
        "permisos/<int:id>/",
        views.asignar_permiso,
        name="asignar_permiso"
    ),
]