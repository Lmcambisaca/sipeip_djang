from django.urls import path

from . import views

urlpatterns = [

    path("registrar/", views.registrar_proyecto, name="registrar_proyecto"),

    path("consultar/", views.consultar_proyectos, name="consultar_proyectos"),
    
    path("editar/<int:id>/", views.editar_proyecto, name="editar_proyecto"),

    path("eliminar/<int:id>/", views.eliminar_proyecto, name="eliminar_proyecto"),
    
    path("cronograma/registrar/", views.registrar_cronograma, name="registrar_cronograma"),

    path("cronograma/consultar/", views.consultar_cronogramas, name="consultar_cronogramas"),
    
    path("documentos/registrar/", views.registrar_documento, name="registrar_documento"),

    path("documentos/consultar/", views.consultar_documentos, name="consultar_documentos"),

]