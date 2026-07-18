from django.contrib import messages
from django.shortcuts import redirect


def validar_permiso(request, nombre_permiso):

    if not request.user.is_authenticated:
        return redirect("login")


    if (
        request.user.rol
        and request.user.rol.nombre == "Administrador del Sistema"
    ):
        return None


    if not request.user.rol:

        messages.error(
            request,
            "No tiene un rol asignado."
        )

        return redirect("dashboard")


    permiso = request.user.rol.permisos.filter(
    nombre__iexact=nombre_permiso.strip(),
    estado=True
    ).exists()


    if not permiso:

        messages.error(
            request,
            f"No tiene permisos para: {nombre_permiso}"
        )

        return redirect("dashboard")


    return None