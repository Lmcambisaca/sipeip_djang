from django.shortcuts import redirect
from django.contrib import messages


def permiso_requerido(nombre_permiso):

    def decorador(view_func):

        def wrapper(request, *args, **kwargs):

            usuario = request.user

            if not usuario.is_authenticated:
                return redirect("login")


            permisos = usuario.rol.permisos.filter(
                nombre=nombre_permiso,
                estado=True
            ).exists()


            if not permisos:

                messages.error(
                    request,
                    "No tiene permisos para realizar esta acción."
                )

                return redirect("inicio")


            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorador