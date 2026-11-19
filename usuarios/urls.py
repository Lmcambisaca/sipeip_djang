from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path("login/", views.login_usuario, name="login_usuario"),
    path("logout/", views.logout_usuario, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("registrar/", views.registrar_usuario, name="registrar_usuario"),
    path("consultar/", views.consultar_usuarios, name="consultar_usuarios"),
    path("editar/<int:id>/", views.editar_usuario, name="editar_usuario"),
    path("estado/<int:id>/", views.cambiar_estado_usuario, name="cambiar_estado_usuario"),
    path("eliminar/<int:id>/", views.eliminar_usuario, name="eliminar_usuario"),
    path(
        "recuperar-password/",
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/recuperar_password.html",
            email_template_name="usuarios/recuperar_password_email.txt",
            subject_template_name="usuarios/recuperar_password_asunto.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="recuperar_password",
    ),
    path(
        "recuperar-password/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/recuperar_password_enviado.html",
        ),
        name="password_reset_done",
    ),
    path(
        "restablecer-password/<uidb64>/<token>/",
        views.ConfirmarRecuperacionPasswordView.as_view(
            template_name="usuarios/restablecer_password.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "restablecer-password/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/recuperar_password_completo.html",
        ),
        name="password_reset_complete",
    ),
    path("auditoria/", views.consultar_auditoria, name="consultar_auditoria"),
    path("historial-cambios/", views.consultar_historial_cambios, name="consultar_historial_cambios",),
    path("auditoria/exportar/pdf/", views.exportar_auditoria_pdf, name="exportar_auditoria_pdf",),
    path("auditoria/exportar/excel/", views.exportar_auditoria_excel, name="exportar_auditoria_excel",),
]