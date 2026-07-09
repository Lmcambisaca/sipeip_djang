from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from .models import Usuario
from roles.models import Rol

from .forms import (
    UsuarioForm,
    UsuarioEditarForm,
    RecuperarPasswordForm,
)


def registrar_usuario(request):

    if request.method == "POST":

        form = UsuarioForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Usuario registrado correctamente."
            )

            return redirect("consultar_usuarios")

        else:

            messages.error(
                request,
                "Revise la información ingresada."
            )

    else:

        form = UsuarioForm()

    return render(
        request,
        "usuarios/registrar_usuario.html",
        {
            "form": form
        }
    )


def consultar_usuarios(request):

    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "")
    rol = request.GET.get("rol", "")

    usuarios = Usuario.objects.select_related("rol").all()

    if buscar:

        usuarios = usuarios.filter(
            Q(username__icontains=buscar)
            | Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(email__icontains=buscar)
        )

    if estado != "":

        usuarios = usuarios.filter(
            estado=(estado == "1")
        )

    if rol:

        usuarios = usuarios.filter(
            rol_id=rol
        )

    roles = Rol.objects.filter(
        estado=True
    ).order_by("nombre")

    mensaje = ""

    if not usuarios.exists():

        mensaje = "No existen usuarios que coincidan con la búsqueda."

    return render(
        request,
        "usuarios/consultar_usuario.html",
        {
            "usuarios": usuarios,
            "roles": roles,
            "mensaje": mensaje,
            "buscar": buscar,
            "estado": estado,
            "rol": rol,
        }
    )


def editar_usuario(request, id):

    usuario = get_object_or_404(
        Usuario,
        pk=id
    )

    if request.method == "POST":

        formulario = UsuarioEditarForm(
            request.POST,
            instance=usuario
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Usuario actualizado correctamente."
            )

            return redirect(
                "consultar_usuarios"
            )

    else:

        formulario = UsuarioEditarForm(
            instance=usuario
        )

    return render(
        request,
        "usuarios/editar_usuario.html",
        {
            "form": formulario,
            "usuario": usuario
        }
    )

def cambiar_estado_usuario(request, id):

    usuario = get_object_or_404(
        Usuario,
        pk=id
    )
    
    print("Usuario autenticado:", request.user)
    print("ID autenticado:", request.user.id)
    print("ID a desactivar:", usuario.id)

    usuario.estado = not usuario.estado
    usuario.save()

    if usuario.estado:
        messages.success(
            request,
            "Usuario activado correctamente."
        )
    else:
        messages.success(
            request,
            "Usuario desactivado correctamente."
        )

    return redirect("consultar_usuarios")

User = get_user_model()


def recuperar_password(request):

    if request.method == "POST":

        form = RecuperarPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]
            nueva = form.cleaned_data["nueva_password"]
            confirmar = form.cleaned_data["confirmar_password"]

            if nueva != confirmar:

                messages.error(
                    request,
                    "Las contraseñas no coinciden."
                )

            else:

                try:

                    usuario = User.objects.get(email=email)

                    usuario.password = make_password(nueva)

                    usuario.save()

                    messages.success(
                        request,
                        "Contraseña actualizada correctamente."
                    )

                    return redirect("login")

                except User.DoesNotExist:

                    messages.error(
                        request,
                        "No existe un usuario con ese correo."
                    )

    else:

        form = RecuperarPasswordForm()

    return render(
        request,
        "usuarios/recuperar_password.html",
        {
            "form": form
        }
    )

def eliminar_usuario(request, id):

    usuario = get_object_or_404(
        Usuario,
        pk=id
    )

    # No permitir eliminar al propio usuario
    if request.user.id == usuario.id:

        messages.error(
            request,
            "No puede eliminar su propio usuario."
        )

        return redirect("consultar_usuarios")

    # Si ya está inactivo
    if not usuario.estado:

        messages.warning(
            request,
            "El usuario ya se encuentra inactivo."
        )

        return redirect("consultar_usuarios")

    # Eliminación lógica
    usuario.estado = False
    usuario.save()

    messages.success(
        request,
        "Usuario eliminado correctamente."
    )

    return redirect("consultar_usuarios")