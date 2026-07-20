from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from usuarios.models import AuditoriaSesion


from .forms import (
    LoginForm,
    UsuarioForm,
    UsuarioEditarForm,
    RecuperarPasswordForm,
)

from .models import (
    Usuario,
    RecuperacionPassword,
    AuditoriaSesion,
)

from roles.models import Rol

from .permisos import validar_permiso
@login_required
def registrar_usuario(request):

    permiso = validar_permiso(
        request,
        "Administrar usuarios"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = UsuarioForm(request.POST)

        if form.is_valid():
            
            registrar_auditoria(

                request.user,

                "Registró un usuario"

            )

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


@login_required
def consultar_usuarios(request):
    
    permiso = validar_permiso(
    request,
    "Administrar usuarios"
    )

    if permiso:
        return permiso

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


@login_required
def editar_usuario(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar usuarios"
    )

    if permiso:
        return permiso

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
    
@login_required
def cambiar_estado_usuario(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar usuarios"
)

    if permiso:
        return permiso

    usuario = get_object_or_404(
        Usuario,
        pk=id
    )

    if request.user.id == usuario.id:

        messages.error(
            request,
            "No puede desactivar su propia cuenta mientras tiene la sesión iniciada."
        )

        return redirect("consultar_usuarios")

    usuario.estado = not usuario.estado

    if usuario.estado:

        usuario.intentos_fallidos = 0
        usuario.bloqueado = False

        messages.success(
            request,
            "Usuario activado correctamente."
        )

    else:

        messages.success(
            request,
            "Usuario desactivado correctamente."
        )

    usuario.save()

    return redirect("consultar_usuarios")

@login_required
def eliminar_usuario(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar usuarios"
    )

    if permiso:
        return permiso

    usuario = get_object_or_404(
        Usuario,
        pk=id
    )

    # TAR-15 y TAR-16

    if usuario.cronograma_set.exists():

        messages.error(
            request,
            "No se puede eliminar el usuario porque está asignado como responsable de uno o más cronogramas."
        )

        return redirect("consultar_usuarios")

    if usuario.auditoriaproyecto_set.exists():

        messages.error(
            request,
            "No se puede eliminar el usuario porque posee registros de auditoría."
        )

        return redirect("consultar_usuarios")

    usuario.delete()

    messages.success(
        request,
        "Usuario eliminado correctamente."
    )

    return redirect("consultar_usuarios")



def login_usuario(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        username = request.POST.get("username")

        usuario_bd = Usuario.objects.filter(
            username=username
        ).first()

        if usuario_bd and usuario_bd.bloqueado:

            messages.error(
                request,
                "Su cuenta ha sido bloqueada por exceder los 3 intentos permitidos."
            )

            return render(
                request,
                "usuarios/login.html",
                {
                    "form": form
                }
            )

        if form.is_valid():

            usuario = form.get_user()

            if not usuario.estado:

                messages.error(
                    request,
                    "Este usuario se encuentra inactivo."
                )

            else:

                usuario.intentos_fallidos = 0
                usuario.save()

                login(request, usuario)
                
                registrar_auditoria(

                    usuario,

                    "Inicio de sesión"

                )
                
                AuditoriaSesion.objects.create(
                    usuario=usuario,
                    accion="Inicio de sesión"
                )

                messages.success(
                    request,
                    "Bienvenido al sistema."
                )

                return redirect("dashboard")

        else:

            if usuario_bd:

                usuario_bd.intentos_fallidos += 1

                if usuario_bd.intentos_fallidos >= 3:

                    usuario_bd.bloqueado = True

                    messages.error(
                        request,
                        "Su cuenta ha sido bloqueada por exceder los intentos permitidos."
                    )

                else:

                    messages.error(
                        request,
                        f"Usuario o contraseña incorrectos. Intento {usuario_bd.intentos_fallidos} de 3."
                    )

                usuario_bd.save()

            else:

                messages.error(
                    request,
                    "Usuario o contraseña incorrectos."
                )

    return render(
        request,
        "usuarios/login.html",
        {
            "form": form
        }
    )
    
def recuperar_password(request):

    if request.method == "POST":

        form = RecuperarPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            actual = form.cleaned_data["password_actual"]

            nueva = form.cleaned_data["nueva_password"]

            confirmar = form.cleaned_data["confirmar_password"]

            if nueva != confirmar:

                messages.error(
                    request,
                    "Las contraseñas no coinciden."
                )

            else:

                try:

                    usuario = Usuario.objects.get(email=email)
                    
                    if not check_password(
                        actual,
                        usuario.password
                    ):

                        messages.error(
                            request,
                            "La contraseña actual es incorrecta."
                        )

                        return render(
                            request,
                            "usuarios/recuperar_password.html",
                            {
                                "form": form
                            }
                        )

                    usuario.password = make_password(nueva)

                    usuario.save()
                    
                    RecuperacionPassword.objects.create(
                        usuario=usuario
                    )
                    
                    

                    messages.success(
                        request,
                        "Contraseña actualizada correctamente."
                    )

                    return redirect("login")

                except Usuario.DoesNotExist:

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



def logout_usuario(request):

    if request.user.is_authenticated:

        AuditoriaSesion.objects.create(
            usuario=request.user,
            accion="Cierre de sesión"
        )
        
        registrar_auditoria(

        request.user,

        "Cierre de sesión"

        )

    logout(request)

    return redirect("login")


@login_required
def dashboard(request):

    rol = None

    if hasattr(request.user, "rol") and request.user.rol:
        rol = request.user.rol.nombre
        
    permisos = []

    if request.user.is_authenticated and request.user.rol:

        permisos = list(
            request.user.rol.permisos.filter(
                estado=True
            ).values_list(
                "nombre",
                flat=True
            )
        )

    return render(
        request,
        "usuarios/dashboard.html",
        {
            "permisos": permisos,
        }
    )
    
def registrar_auditoria(usuario, accion):

    AuditoriaSesion.objects.create(

        usuario=usuario,

        accion=accion

    )
    
@login_required
def consultar_auditoria(request):

    auditorias = AuditoriaSesion.objects.select_related(

        "usuario"

    ).order_by("-fecha")

    return render(

        request,

        "usuarios/consultar_auditoria.html",

        {

            "auditorias": auditorias

        }

    )