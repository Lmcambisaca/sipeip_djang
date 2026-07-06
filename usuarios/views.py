from django.shortcuts import render, redirect
from .forms import UsuarioForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(usuario.password)
            usuario.save()
            return redirect('/admin')
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/registrar_usuario.html', {
        'form': form
    })
    
    
from .models import Usuario


def consultar_usuarios(request):
    usuarios = Usuario.objects.all()

    return render(request, 'usuarios/consultar_usuario.html', {
        'usuarios': usuarios
    })
    
from django.shortcuts import get_object_or_404

from .forms import UsuarioEditarForm


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
            return redirect('consultar_usuarios')

    else:

        formulario = UsuarioEditarForm(
            instance=usuario
        )

    return render(
        request,
        "usuarios/editar_usuario.html",
        {
            "form": formulario
        }
    )
    
from django.contrib import messages


def cambiar_estado_usuario(request, id):

    usuario = get_object_or_404(
        Usuario,
        pk=id
    )

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

from .forms import RecuperarPasswordForm

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