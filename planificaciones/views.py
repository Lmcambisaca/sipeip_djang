from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from .models import Planificacion
from .forms import PlanificacionForm
from entidades.models import Entidad
from usuarios.permisos import validar_permiso
from django.views.decorators.http import require_POST

@login_required
def registrar_planificacion(request):

    permiso = validar_permiso(
        request,
        "Administrar planificación"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = PlanificacionForm(request.POST)

        if form.is_valid():

            periodo = form.cleaned_data["periodo"].strip()
            nombre = form.cleaned_data["nombre"].strip()
            descripcion = form.cleaned_data["descripcion"].strip()
            fecha_inicio = form.cleaned_data["fecha_inicio"]
            fecha_fin = form.cleaned_data["fecha_fin"]

            if not periodo:

                messages.error(
                    request,
                    "El período es obligatorio."
                )

                return render(
                    request,
                    "planificaciones/registrar_planificacion.html",
                    {"form": form}
                )

            if not nombre:

                messages.error(
                    request,
                    "El nombre es obligatorio."
                )

                return render(
                    request,
                    "planificaciones/registrar_planificacion.html",
                    {"form": form}
                )

            if not descripcion:

                messages.error(
                    request,
                    "La descripción es obligatoria."
                )

                return render(
                    request,
                    "planificaciones/registrar_planificacion.html",
                    {"form": form}
                )

            if fecha_inicio > fecha_fin:

                messages.error(
                    request,
                    "La fecha de inicio no puede ser mayor que la fecha final."
                )

                return render(
                    request,
                    "planificaciones/registrar_planificacion.html",
                    {"form": form}
                )

            form.save()

            messages.success(
                request,
                "Planificación registrada correctamente."
            )

            return redirect("consultar_planificaciones")

    else:

        form = PlanificacionForm()

    return render(
        request,
        "planificaciones/registrar_planificacion.html",
        {
            "form": form
        }
    )
    
@login_required
def consultar_planificaciones(request):

    permiso = validar_permiso(
        request,
        "Consultar planificación"
    )

    if permiso:
        return permiso

    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "")
    entidad = request.GET.get("entidad", "")

    planificaciones = Planificacion.objects.select_related(
        "entidad"
    ).all()

    if buscar:

        planificaciones = planificaciones.filter(

            Q(periodo__icontains=buscar)
            | Q(nombre__icontains=buscar)
            | Q(descripcion__icontains=buscar)

        )

    if estado != "":

        planificaciones = planificaciones.filter(
            estado=(estado == "1")
        )

    if entidad:

        planificaciones = planificaciones.filter(
            entidad_id=entidad
        )

    entidades = Entidad.objects.filter(
        estado=True
    ).order_by("nombre")

    mensaje = ""

    if not planificaciones.exists():

        mensaje = "No existen planificaciones registradas."

    return render(

        request,

        "planificaciones/consultar_planificacion.html",

        {

            "planificaciones": planificaciones,

            "entidades": entidades,

            "mensaje": mensaje,

            "buscar": buscar,

            "estado": estado,

            "entidad": entidad,

        }

    )

@login_required
def editar_planificacion(request, id):

    permiso = validar_permiso(
        request,
        "Editar planificación"
    )

    if permiso:
        return permiso

    planificacion = get_object_or_404(
        Planificacion,
        pk=id
    )

    if request.method == "POST":

        form = PlanificacionForm(
            request.POST,
            instance=planificacion
        )

        if form.is_valid():

            periodo = form.cleaned_data["periodo"].strip()
            nombre = form.cleaned_data["nombre"].strip()

            if not periodo:

                messages.error(
                    request,
                    "El período es obligatorio."
                )

            elif not nombre:

                messages.error(
                    request,
                    "El nombre es obligatorio."
                )

            elif form.cleaned_data["fecha_inicio"] > form.cleaned_data["fecha_fin"]:

                messages.error(
                    request,
                    "La fecha de inicio no puede ser mayor que la fecha final."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Planificación actualizada correctamente."
                )

                return redirect(
                    "consultar_planificaciones"
                )

    else:

        form = PlanificacionForm(
            instance=planificacion
        )

    return render(
        request,
        "planificaciones/editar_planificacion.html",
        {
            "form": form,
            "planificacion": planificacion
        }
    )

@login_required
@require_POST
def eliminar_planificacion(request, id):
    permiso = validar_permiso(request, "Eliminar planificación")
    if permiso:
        return permiso

    planificacion = get_object_or_404(Planificacion, pk=id)
    accion = request.POST.get("accion")

    if accion not in {"activar", "desactivar"}:
        messages.error(request, "La acción solicitada no es válida.")
        return redirect("consultar_planificaciones")

    nuevo_estado = accion == "activar"

    if planificacion.estado == nuevo_estado:
        messages.info(request, "La planificación ya se encuentra en ese estado.")
        return redirect("consultar_planificaciones")

    planificacion.estado = nuevo_estado
    planificacion.save(update_fields=["estado"])

    if nuevo_estado:
        messages.success(request, "Planificación activada correctamente.")
    else:
        messages.success(request, "Planificación desactivada correctamente.")

    return redirect("consultar_planificaciones")

@login_required
@require_POST
def validar_planificacion(request, id):
    permiso = validar_permiso(request, "Validar planificación")
    if permiso:
        return permiso

    planificacion = get_object_or_404(Planificacion, pk=id)

    errores = []

    if not planificacion.periodo.strip():
        errores.append("No tiene período.")

    if not planificacion.nombre.strip():
        errores.append("No tiene nombre.")

    if not planificacion.descripcion.strip():
        errores.append("No tiene descripción.")

    if (
        planificacion.fecha_inicio
        and planificacion.fecha_fin
        and planificacion.fecha_inicio > planificacion.fecha_fin
    ):
        errores.append("La fecha de inicio es posterior a la fecha de fin.")

    if not planificacion.entidad_id:
        errores.append("No tiene entidad asignada.")

    planificacion.validada = not errores
    planificacion.observacion = (
        "\n".join(errores)
        if errores
        else "Planificación validada correctamente."
    )
    planificacion.save(update_fields=["validada", "observacion"])

    if errores:
        messages.error(request, "La planificación no puede validarse.")
    else:
        messages.success(request, "Planificación validada correctamente.")

    return redirect("consultar_planificaciones")


@login_required
@require_POST
def aprobar_planificacion(request, id):
    permiso = validar_permiso(request, "Aprobar planificación")
    if permiso:
        return permiso

    planificacion = get_object_or_404(Planificacion, pk=id)

    if not planificacion.estado:
        messages.error(request, "No se puede aprobar una planificación inactiva.")
    elif not planificacion.validada:
        messages.error(request, "Primero debe validar la planificación.")
    elif planificacion.aprobada:
        messages.warning(request, "La planificación ya fue aprobada.")
    else:
        planificacion.aprobada = True
        planificacion.aprobada_por = request.user
        planificacion.fecha_aprobacion = timezone.now()
        planificacion.save(
            update_fields=[
                "aprobada",
                "aprobada_por",
                "fecha_aprobacion",
            ]
        )
        messages.success(request, "Planificación aprobada correctamente.")

    return redirect("consultar_planificaciones")


@login_required
@require_POST
def rechazar_planificacion(request, id):
    permiso = validar_permiso(request, "Aprobar planificación")
    if permiso:
        return permiso

    planificacion = get_object_or_404(Planificacion, pk=id)
    observacion = request.POST.get("observacion", "").strip()

    if not (planificacion.validada or planificacion.aprobada):
        messages.error(
            request,
            "Solo se puede rechazar una planificación que haya sido validada o aprobada.",
        )
    elif not observacion:
        messages.error(request, "Escribe el motivo del rechazo.")
    else:
        planificacion.validada = False
        planificacion.aprobada = False
        planificacion.aprobada_por = None
        planificacion.fecha_aprobacion = None
        planificacion.observacion = observacion
        planificacion.save(
            update_fields=[
                "validada",
                "aprobada",
                "aprobada_por",
                "fecha_aprobacion",
                "observacion",
            ]
        )
        messages.success(request, "Planificación rechazada.")

    return redirect("consultar_planificaciones")