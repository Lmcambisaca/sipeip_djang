from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from usuarios.models import AuditoriaSesion
from django.views.decorators.http import require_POST
from django.contrib.auth.views import PasswordResetConfirmView
from django.db.models.deletion import ProtectedError



from .forms import (LoginForm, UsuarioForm, UsuarioEditarForm, RecuperarPasswordForm,)

from .models import (Usuario, RecuperacionPassword, AuditoriaSesion,)

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
        "Administrar usuarios",
    )

    if permiso:
        return permiso

    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "")
    rol = request.GET.get("rol", "")

    usuarios = Usuario.objects.select_related(
        "rol",
        "entidad",
    ).all()

    if buscar:
    
        usuarios = usuarios.filter(
            Q(username__icontains=buscar)
            | Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(identificacion__icontains=buscar)
            | Q(cargo__icontains=buscar)
            | Q(email__icontains=buscar)
            | Q(entidad__nombre__icontains=buscar)
        )

    if estado in {"0", "1"}:
        usuarios = usuarios.filter(estado=(estado == "1"))
    else:
        estado = ""

    if rol.isdecimal():
        usuarios = usuarios.filter(rol_id=rol)
    else:
        rol = ""

    usuarios = usuarios.order_by(
        "last_name",
        "first_name",
        "username",
    )

    roles = Rol.objects.filter(estado=True).order_by("nombre")
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
        },
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
@require_POST
def cambiar_estado_usuario(request, id):
    permiso = validar_permiso(request, "Administrar usuarios")
    if permiso:
        return permiso

    usuario = get_object_or_404(Usuario, pk=id)
    accion = request.POST.get("accion")

    if accion not in {"activar", "desactivar"}:
        messages.error(request, "La acción solicitada no es válida.")
        return redirect("consultar_usuarios")

    if accion == "desactivar" and request.user.pk == usuario.pk:
        messages.error(
            request,
            "No puede desactivar su propia cuenta mientras tiene la sesión iniciada.",
        )
        return redirect("consultar_usuarios")

    nuevo_estado = accion == "activar"

    if usuario.estado == nuevo_estado:
        messages.info(
            request,
            "La cuenta ya se encuentra en ese estado.",
        )
        return redirect("consultar_usuarios")

    usuario.estado = nuevo_estado
    usuario.is_active = nuevo_estado

    if nuevo_estado:
        usuario.intentos_fallidos = 0
        usuario.bloqueado = False
        messages.success(request, "Usuario activado correctamente.")
    else:
        messages.success(request, "Usuario desactivado correctamente.")

    usuario.save(
        update_fields=[
            "estado",
            "is_active",
            "intentos_fallidos",
            "bloqueado",
        ]
    )
    return redirect("consultar_usuarios")


@login_required
@require_POST
def eliminar_usuario(request, id):
    permiso = validar_permiso(request, "Administrar usuarios")
    if permiso:
        return permiso

    usuario = get_object_or_404(Usuario, pk=id)

    if usuario.pk == request.user.pk:
        messages.error(request, "No puede eliminar su propia cuenta.")
        return redirect("consultar_usuarios")

    dependencias = (
        ("cronograma_set", "responsable de actividades de cronograma"),
        ("proyectos", "responsable de proyectos"),
        ("auditoriaproyecto_set", "registros de auditoría de proyectos"),
        ("auditorias", "registros de auditoría de sesiones"),
    )

    for relacion, descripcion in dependencias:
        if getattr(usuario, relacion).exists():
            messages.error(
                request,
                f"No se puede eliminar el usuario porque tiene {descripcion}.",
            )
            return redirect("consultar_usuarios")

    try:
        usuario.delete()
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar el usuario porque tiene información relacionada.",
        )
        return redirect("consultar_usuarios")

    messages.success(request, "Usuario eliminado correctamente.")
    return redirect("consultar_usuarios")



def login_usuario(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        email = request.POST.get("username", "").strip()

        usuario_bd = Usuario.objects.filter(
            email__iexact=email
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
                    
                    "Autenticación",
                    
                    "Inicio de sesión",
                    
                    "El usuario inició sesión correctamente."
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
    
@require_POST
def logout_usuario(request):

    if request.user.is_authenticated:

        AuditoriaSesion.objects.create(
            usuario=request.user,
            modulo="Autenticación",
            accion="Cierre de sesión",
            descripcion="El usuario cerró sesión."
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
    
def registrar_auditoria(usuario, modulo, accion=None, descripcion=""):
    # Compatibilidad con llamadas antiguas: registrar_auditoria(usuario, accion)
    if accion is None:
        accion = modulo
        modulo = "Usuarios"

    AuditoriaSesion.objects.create(
        usuario=usuario,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
    )
    
@login_required
def consultar_auditoria(request):
    permiso = validar_permiso(request, "Consultar auditoría")
    if permiso:
        return permiso

    auditorias = AuditoriaSesion.objects.select_related(
        "usuario"
    ).order_by("-fecha", "-pk")

    usuario_id = request.GET.get("usuario", "").strip()
    modulo = request.GET.get("modulo", "").strip()
    accion = request.GET.get("accion", "").strip()
    fecha = request.GET.get("fecha", "").strip()

    usuarios = Usuario.objects.order_by("username")
    modulos = list(
        AuditoriaSesion.objects.order_by("modulo")
        .values_list("modulo", flat=True)
        .distinct()
    )

    if usuario_id.isdecimal() and usuarios.filter(pk=usuario_id).exists():
        auditorias = auditorias.filter(usuario_id=usuario_id)
    else:
        usuario_id = ""

    if modulo in modulos:
        auditorias = auditorias.filter(modulo=modulo)
    else:
        modulo = ""

    if accion:
        auditorias = auditorias.filter(accion__icontains=accion)

    from django.utils.dateparse import parse_date

    fecha_valida = parse_date(fecha) if fecha else None
    if fecha_valida:
        auditorias = auditorias.filter(fecha__date=fecha_valida)
    else:
        fecha = ""

        return render(
        request,
        "usuarios/consultar_auditoria.html",
        {
            "auditorias": auditorias,
            "usuarios": usuarios,
            "modulos": modulos,
            "usuario_id": usuario_id,
            "modulo_seleccionado": modulo,
            "accion": accion,
            "fecha": fecha,
        }
    )


class ConfirmarRecuperacionPasswordView(PasswordResetConfirmView):
    pass