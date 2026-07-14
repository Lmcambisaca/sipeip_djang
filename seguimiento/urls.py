from django.urls import path
from . import views

urlpatterns=[

    path("registrar/", views.registrar_meta, name="registrar_meta"),

    path("consultar/", views.consultar_metas, name="consultar_metas"),
    
    path("editar/<int:id>/", views.editar_meta, name="editar_meta"),
    
    path("indicadores/registrar/", views.registrar_indicador, name="registrar_indicador"),

    path("indicadores/consultar/", views.consultar_indicadores, name="consultar_indicadores"),
    
    path("indicadores/editar/<int:id>/", views.editar_indicador, name="editar_indicador"),
    
    path("avances/registrar/", views.registrar_avance, name="registrar_avance"),

    path("avances/consultar/", views.consultar_avances, name="consultar_avances"),
    
    path("avances/editar/<int:id>/", views.editar_avance, name="editar_avance"),
    
    path("indicadores/grafico/<int:id>/", views.grafico_indicador, name="grafico_indicador"),
]