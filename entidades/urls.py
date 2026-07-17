from django.urls import path
from . import views

urlpatterns = [

    path(
        "registrar/", views.registrar_entidad, name="registrar_entidad"),

    path("consultar/", views.consultar_entidades, name="consultar_entidades"),

    path("editar/<int:id>/", views.editar_entidad, name="editar_entidad"),

    path("eliminar/<int:id>/", views.eliminar_entidad, name="eliminar_entidad"),
    
    path("cambiar_estado/<int:id>/", views.cambiar_estado_entidad, name="cambiar_estado_entidad"),
    
]