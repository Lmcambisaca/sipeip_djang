from django.urls import path

from . import views


urlpatterns = [
    path("registrar/", views.registrar_inversion, name="registrar_inversion"),
    path("consultar/", views.consultar_inversiones, name="consultar_inversiones"),
    path("editar/<int:id>/", views.editar_inversion, name="editar_inversion"),
    path("seguimiento/", views.seguimiento_inversiones, name="seguimiento_inversiones"),
    path("reporte/", views.reporte_inversiones, name="reporte_inversiones"),
]