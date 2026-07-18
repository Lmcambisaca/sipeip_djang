from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from .models import Planificacion
from .forms import PlanificacionForm
from entidades.models import Entidad
from usuarios.permisos import validar_permiso

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
def eliminar_planificacion(request, id):

    permiso = validar_permiso(
        request,
        "Eliminar planificación"
    )

    if permiso:
        return permiso

    planificacion = get_object_or_404(
        Planificacion,
        pk=id
    )

    # TAR-81
    if planificacion.proyectos.exists():

        messages.error(

            request,

            "No es posible eliminar la planificación porque tiene proyectos asociados."

        )

        return redirect(
            "consultar_planificaciones"
        )

    planificacion.delete()

    messages.success(

        request,

        "Planificación eliminada correctamente."

    )

    return redirect(
        "consultar_planificaciones"
    )

@login_required
def validar_planificacion(request, id):

    permiso = validar_permiso(
        request,
        "Validar planificación"
    )

    if permiso:
        return permiso

    planificacion = get_object_or_404(
        Planificacion,
        pk=id
    )

    errores = []

    if not planificacion.periodo.strip():
        errores.append("No tiene período.")

    if not planificacion.nombre.strip():
        errores.append("No tiene nombre.")

    if not planificacion.descripcion.strip():
        errores.append("No tiene descripción.")

    if planificacion.fecha_inicio > planificacion.fecha_fin:
        errores.append("Las fechas son inconsistentes.")

    if planificacion.entidad is None:
        errores.append("No tiene entidad asignada.")

    if errores:

        planificacion.validada = False
        planificacion.observacion = "\n".join(errores)
        planificacion.save()

        messages.error(
            request,
            "La planificación no puede validarse."
        )

    else:

        planificacion.validada = True
        planificacion.observacion = "Planificación validada correctamente."
        planificacion.save()

        messages.success(
            request,
            "Planificación validada correctamente."
        )

    return redirect("consultar_planificaciones")

@login_required
def aprobar_planificacion(request, id):

    permiso = validar_permiso(
        request,
        "Aprobar planificación"
    )

    if permiso:
        return permiso

    planificacion = get_object_or_404(
        Planificacion,
        pk=id
    )

    if not planificacion.validada:

        messages.error(
            request,
            "Primero debe validar la planificación."
        )

    elif planificacion.aprobada:

        messages.warning(
            request,
            "La planificación ya fue aprobada."
        )

    else:

        planificacion.aprobada = True
        planificacion.aprobada_por = request.user
        planificacion.fecha_aprobacion = timezone.now()

        planificacion.save()

        messages.success(
            request,
            "Planificación aprobada correctamente."
        )

    return redirect(
        "consultar_planificaciones"
    )

@login_required
def rechazar_planificacion(request, id):

    permiso = validar_permiso(
        request,
        "Aprobar planificación"
    )

    if permiso:
        return permiso

    planificacion = get_object_or_404(
        Planificacion,
        pk=id
    )

    planificacion.aprobada = False
    planificacion.validada = False

    planificacion.save()

    messages.success(
        request,
        "Planificación rechazada."
    )

    return redirect(
        "consultar_planificaciones"
    )