from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('consultar/', views.consultar_usuarios, name='consultar_usuarios'),
    path(
    'editar/<int:id>/',
    views.editar_usuario,
    name='editar_usuario'
),
    path(
    'estado/<int:id>/',
    views.cambiar_estado_usuario,
    name='cambiar_estado_usuario'
),
    path(
    'recuperar-password/',
    views.recuperar_password,
    name='recuperar_password'
),
]