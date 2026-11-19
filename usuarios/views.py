from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import PasswordResetConfirmView
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from roles.models import Rol
from .forms import LoginForm, UsuarioEditarForm, UsuarioForm
from .models import AuditoriaSesion, HistorialCambio, Usuario
from .permisos import validar_permiso

from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, legal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

@login_required
def registrar_usuario(request):
    permiso = validar_permiso(request, "Administrar usuarios")
    if permiso:
        return permiso

    if request.method == "POST":

        form = UsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            registrar_auditoria(

                request.user,
                "Usuarios",
                "Registro de usuario",
                "Se registró un usuario.",
            )
            messages.success(request, "Usuario registrado correctamente.")
            return redirect("consultar_usuarios")

        messages.error(request, "Revise la información ingresada.")
    else:

        form = UsuarioForm()

    return render(
        request,
        "usuarios/registrar_usuario.html",
        {"form": form},
    )


@login_required
def consultar_usuarios(request):
    permiso = validar_permiso(request, "Administrar usuarios")
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
    permiso = validar_permiso(request, "Administrar usuarios")
    if permiso:
        return permiso

    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == "POST":
        formulario = UsuarioEditarForm(request.POST, instance=usuario)

        if formulario.is_valid():

            formulario.save()
            registrar_auditoria(
                request.user,
                "Usuarios",
                "Actualización de usuario",
                f"Se actualizó el usuario {usuario.username}.",
            )
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("consultar_usuarios")
    else:
        formulario = UsuarioEditarForm(instance=usuario)

    return render(
        request,
        "usuarios/editar_usuario.html",
        {
            "form": formulario,
            "usuario": usuario,
        },
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
        messages.info(request, "La cuenta ya se encuentra en ese estado.")
        return redirect("consultar_usuarios")

    usuario.estado = nuevo_estado
    usuario.is_active = nuevo_estado

    if nuevo_estado:
        usuario.intentos_fallidos = 0
        usuario.bloqueado = False
        mensaje = "Usuario activado correctamente."
    else:
        mensaje = "Usuario desactivado correctamente."

    usuario.save(
        update_fields=[
            "estado",
            "is_active",
            "intentos_fallidos",
            "bloqueado",
        ]
    )

    registrar_auditoria(
        request.user,
        "Usuarios",
        "Cambio de estado",
        f"Se cambió el estado del usuario {usuario.username}.",
    )
    messages.success(request, mensaje)
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
        relacion_usuario = getattr(usuario, relacion, None)
        if relacion_usuario is not None and relacion_usuario.exists():
            messages.error(
                request,
                f"No se puede eliminar el usuario porque tiene {descripcion}.",
            )
            return redirect("consultar_usuarios")

    try:
        nombre_usuario = usuario.username
        usuario.delete()
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar el usuario porque tiene información relacionada.",
        )
        return redirect("consultar_usuarios")

    registrar_auditoria(
        request.user,
        "Usuarios",
        "Eliminación de usuario",
        f"Se eliminó el usuario {nombre_usuario}.",
    )
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
                "Su cuenta ha sido bloqueada por exceder los 3 intentos permitidos.",
            )
            return render(
                request,
                "usuarios/login.html",
                {"form": form},
            )

        if form.is_valid():
            usuario = form.get_user()

            if not usuario.estado:
                messages.error(request, "Este usuario se encuentra inactivo.")
            else:
                usuario.intentos_fallidos = 0
                usuario.save(update_fields=["intentos_fallidos"])
                login(request, usuario)

                registrar_auditoria(
                    usuario,
                    "Autenticación",
                    "Inicio de sesión",
                    "El usuario inició sesión correctamente.",
                )
                return redirect("dashboard")

        elif usuario_bd:
            usuario_bd.intentos_fallidos += 1

            if usuario_bd.intentos_fallidos >= 3:
                usuario_bd.bloqueado = True
                messages.error(
                    request,
                    "Su cuenta ha sido bloqueada por exceder los intentos permitidos.",
                )
            else:
                messages.error(
                    request,
                    "Correo o contraseña incorrectos. "
                    f"Intento {usuario_bd.intentos_fallidos} de 3.",
                )

            usuario_bd.save(
                update_fields=["intentos_fallidos", "bloqueado"]
            )
        else:
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(
        request,
        "usuarios/login.html",
        {"form": form},
    )


@require_POST
def logout_usuario(request):

    if request.user.is_authenticated:

        AuditoriaSesion.objects.create(
            usuario=request.user,
            modulo="Autenticación",
            accion="Cierre de sesión",
            descripcion="El usuario cerró sesión.",
        )


    logout(request)

    return redirect("login")


@login_required
def dashboard(request):

    permisos = []

    if request.user.rol:
        permisos = list(
            request.user.rol.permisos.filter(estado=True).values_list(
                "nombre",
                flat=True,
            )
        )

    return render(
        request,
        "usuarios/dashboard.html",
        {"permisos": permisos},
    )


def registrar_auditoria(usuario, modulo, accion=None, descripcion=""):
    """
    Registra un evento de auditoría.

    Mantiene compatibilidad con llamadas antiguas de dos argumentos:
    registrar_auditoria(usuario, accion).
    """
    if accion is None:
        accion = modulo
        modulo = "Usuarios"

    AuditoriaSesion.objects.create(
        usuario=usuario,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
    )


def obtener_auditorias_filtradas(request):
    auditorias = AuditoriaSesion.objects.select_related(
        "usuario"
    ).order_by("-fecha", "-pk")

    usuario_id = request.GET.get("usuario", "").strip()
    modulo = request.GET.get("modulo", "").strip()
    accion = request.GET.get("accion", "").strip()
    fecha_desde_texto = request.GET.get("fecha_desde", "").strip()
    fecha_hasta_texto = request.GET.get("fecha_hasta", "").strip()

    usuarios = Usuario.objects.order_by("username")
    modulos = list(
        AuditoriaSesion.objects.order_by("modulo")
        .values_list("modulo", flat=True)
        .distinct()
    )

    if usuario_id:
        if usuario_id.isdecimal() and usuarios.filter(pk=usuario_id).exists():
            auditorias = auditorias.filter(usuario_id=usuario_id)
        else:
            usuario_id = ""

    if modulo:
        if modulo in modulos:
            auditorias = auditorias.filter(modulo=modulo)
        else:
            modulo = ""

    if accion:
        auditorias = auditorias.filter(accion__icontains=accion)

    fecha_desde = parse_date(fecha_desde_texto) if fecha_desde_texto else None
    fecha_hasta = parse_date(fecha_hasta_texto) if fecha_hasta_texto else None

    if fecha_desde_texto and not fecha_desde:
        messages.error(request, "La fecha inicial no es válida.")
        fecha_desde_texto = ""

    if fecha_hasta_texto and not fecha_hasta:
        messages.error(request, "La fecha final no es válida.")
        fecha_hasta_texto = ""

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        messages.error(
            request,
            "La fecha inicial no puede ser posterior a la fecha final.",
        )
        fecha_desde = None
        fecha_hasta = None
        fecha_desde_texto = ""
        fecha_hasta_texto = ""

    if fecha_desde:
        auditorias = auditorias.filter(fecha__date__gte=fecha_desde)

    if fecha_hasta:
        auditorias = auditorias.filter(fecha__date__lte=fecha_hasta)

    filtros = {
        "usuarios": usuarios,
        "modulos": modulos,
        "usuario_id": usuario_id,
        "modulo_seleccionado": modulo,
        "accion": accion,
        "fecha_desde": fecha_desde_texto,
        "fecha_hasta": fecha_hasta_texto,
    }

    return auditorias, filtros


@login_required
def consultar_auditoria(request):
    permiso = validar_permiso(request, "Consultar auditoría")
    if permiso:
        return permiso

    auditorias, filtros = obtener_auditorias_filtradas(request)

    return render(
        request,
        "usuarios/consultar_auditoria.html",
        {
            "auditorias": auditorias,
            **filtros,
        },
    )


@login_required
def exportar_auditoria_csv(request):
    permiso = validar_permiso(request, "Consultar auditoría")
    if permiso:
        return permiso

    auditorias, _ = obtener_auditorias_filtradas(request)

    respuesta = HttpResponse(
        content_type="text/csv; charset=utf-8",
    )
    respuesta["Content-Disposition"] = (
        'attachment; filename="bitacora_auditoria.csv"'
    )
    respuesta.write("\ufeff")

    escritor = csv.writer(respuesta, delimiter=";")
    escritor.writerow(
        ["Usuario", "Fecha", "Módulo", "Acción", "Descripción"]
    )

    for evento in auditorias:
        escritor.writerow(
            [
                evento.usuario.username,
                evento.fecha.strftime("%d/%m/%Y %H:%M:%S"),
                evento.modulo,
                evento.accion,
                evento.descripcion,
            ]
        )

    return respuesta


class ConfirmarRecuperacionPasswordView(PasswordResetConfirmView):
    pass

@login_required
def exportar_auditoria_excel(request):
    permiso = validar_permiso(request, "Consultar auditoría")
    if permiso:
        return permiso

    auditorias, _ = obtener_auditorias_filtradas(request)

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Auditoría"

    encabezados = ["Usuario", "Fecha", "Módulo", "Acción", "Descripción"]
    hoja.append(encabezados)

    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="17365D")

    for evento in auditorias:
        fecha = timezone.localtime(evento.fecha)
        hoja.append([
            evento.usuario.username,
            fecha.strftime("%d/%m/%Y %H:%M:%S"),
            evento.modulo,
            evento.accion,
            evento.descripcion,
        ])

    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions

    anchos = {
        "A": 20,
        "B": 22,
        "C": 26,
        "D": 30,
        "E": 80,
    }
    for columna, ancho in anchos.items():
        hoja.column_dimensions[columna].width = ancho

    buffer = BytesIO()
    libro.save(buffer)

    respuesta = HttpResponse(
        buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    respuesta["Content-Disposition"] = (
        'attachment; filename="bitacora_auditoria.xlsx"'
    )
    return respuesta


@login_required
def exportar_auditoria_pdf(request):
    permiso = validar_permiso(request, "Consultar auditoría")
    if permiso:
        return permiso

    auditorias, _ = obtener_auditorias_filtradas(request)

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloAuditoria",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=15,
        leading=18,
        spaceAfter=12,
    )
    celda = ParagraphStyle(
        "CeldaAuditoria",
        parent=estilos["BodyText"],
        fontSize=7,
        leading=9,
        wordWrap="CJK",
    )

    filas = [[
        Paragraph("<b>Usuario</b>", celda),
        Paragraph("<b>Fecha</b>", celda),
        Paragraph("<b>Módulo</b>", celda),
        Paragraph("<b>Acción</b>", celda),
        Paragraph("<b>Descripción</b>", celda),
    ]]

    hay_eventos = False
    for evento in auditorias:
        hay_eventos = True
        fecha = timezone.localtime(evento.fecha)
        valores = [
            evento.usuario.username,
            fecha.strftime("%d/%m/%Y %H:%M:%S"),
            evento.modulo,
            evento.accion,
            evento.descripcion,
        ]
        filas.append([
            Paragraph(escape(str(valor or "")), celda)
            for valor in valores
        ])

    if not hay_eventos:
        filas.append([
            Paragraph("No hay eventos para los filtros seleccionados.", celda),
            "", "", "", "",
        ])

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(legal),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
        title="Bitácora de auditoría",
    )

    tabla = Table(
        filas,
        colWidths=[1.4 * inch, 1.55 * inch, 1.7 * inch, 2.0 * inch, 6.3 * inch],
        repeatRows=1,
        splitByRow=1,
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C9D6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F1F5F9"),
        ]),
        ("SPAN", (0, 1), (-1, 1)) if not hay_eventos
        else ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    documento.build([
        Paragraph("Bitácora de auditoría", titulo),
        Spacer(1, 4),
        tabla,
    ])

    respuesta = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    respuesta["Content-Disposition"] = (
        'attachment; filename="bitacora_auditoria.pdf"'
    )
    return respuesta

@login_required
def consultar_historial_cambios(request):
    permiso = validar_permiso(request, "Consultar auditoría")
    if permiso:
        return permiso

    historial = HistorialCambio.objects.select_related(
        "usuario"
    ).order_by("-fecha", "-pk")

    usuario_id = request.GET.get("usuario", "").strip()
    modulo = request.GET.get("modulo", "").strip()
    entidad = request.GET.get("entidad", "").strip()

    usuarios = Usuario.objects.order_by("username")
    modulos = list(
        HistorialCambio.objects.order_by("modulo")
        .values_list("modulo", flat=True)
        .distinct()
    )
    entidades = list(
        HistorialCambio.objects.order_by("entidad")
        .values_list("entidad", flat=True)
        .distinct()
    )

    if usuario_id and usuario_id.isdecimal():
        historial = historial.filter(usuario_id=usuario_id)
    else:
        usuario_id = ""

    if modulo in modulos:
        historial = historial.filter(modulo=modulo)
    else:
        modulo = ""

    if entidad in entidades:
        historial = historial.filter(entidad=entidad)
    else:
        entidad = ""

    return render(
        request,
        "usuarios/consultar_historial_cambios.html",
        {
            "historial": historial,
            "usuarios": usuarios,
            "modulos": modulos,
            "entidades": entidades,
            "usuario_id": usuario_id,
            "modulo_seleccionado": modulo,
            "entidad_seleccionada": entidad,
        },
    )
