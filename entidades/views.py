from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Entidad
from .forms import EntidadForm
from planificaciones.models import Planificacion
from django.views.decorators.http import require_POST
from django.db.models.deletion import ProtectedError

from usuarios.permisos import validar_permiso

@login_required
def registrar_entidad(request):
    permiso = validar_permiso(request, "Administrar entidades")
    if permiso:
        return permiso

    if request.method == "POST":
        form = EntidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Entidad registrada correctamente.")
            return redirect("consultar_entidades")
    else:
        form = EntidadForm()

    return render(
        request,
        "entidades/registrar_entidad.html",
        {"form": form},
    )


@login_required
def consultar_entidades(request):
    permiso = validar_permiso(request, "Administrar entidades")
    if permiso:
        return permiso

    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "")

    entidades = Entidad.objects.all()

    if buscar:
        entidades = entidades.filter(
            Q(codigo__icontains=buscar)
            | Q(nombre__icontains=buscar)
            | Q(responsable__icontains=buscar)
        )

    if estado in {"0", "1"}:
        entidades = entidades.filter(estado=(estado == "1"))
    else:
        estado = ""

    entidades = entidades.order_by("nombre", "codigo")
    mensaje = ""

    if not entidades.exists():
        mensaje = "No existen entidades que coincidan con la búsqueda."

    return render(
        request,
        "entidades/consultar_entidad.html",
        {
            "entidades": entidades,
            "mensaje": mensaje,
            "buscar": buscar,
            "estado": estado,
        },
    )


@login_required
def editar_entidad(request, id):
    permiso = validar_permiso(request, "Administrar entidades")
    if permiso:
        return permiso

    entidad = get_object_or_404(Entidad, pk=id)

    if request.method == "POST":
        form = EntidadForm(request.POST, instance=entidad)
        if form.is_valid():
            form.save()
            messages.success(request, "Entidad actualizada correctamente.")
            return redirect("consultar_entidades")
    else:
        form = EntidadForm(instance=entidad)

    return render(
        request,
        "entidades/editar_entidad.html",
        {
            "form": form,
            "entidad": entidad,
        },
    )


@login_required
@require_POST
def eliminar_entidad(request, id):
    permiso = validar_permiso(request, "Administrar entidades")
    if permiso:
        return permiso

    entidad = get_object_or_404(Entidad, pk=id)

    if Planificacion.objects.filter(entidad=entidad).exists():
        messages.error(
            request,
            "No se puede eliminar la entidad porque tiene planificaciones relacionadas.",
        )
        return redirect("consultar_entidades")

    try:
        entidad.delete()
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar la entidad porque tiene información relacionada.",
        )
        return redirect("consultar_entidades")

    messages.success(request, "Entidad eliminada correctamente.")
    return redirect("consultar_entidades")


@login_required
@require_POST
def cambiar_estado_entidad(request, id):
    permiso = validar_permiso(request, "Administrar entidades")
    if permiso:
        return permiso

    entidad = get_object_or_404(Entidad, pk=id)
    accion = request.POST.get("accion")

    if accion not in {"activar", "desactivar"}:
        messages.error(request, "La acción solicitada no es válida.")
        return redirect("consultar_entidades")

    nuevo_estado = accion == "activar"

    if entidad.estado == nuevo_estado:
        messages.info(request, "La entidad ya se encuentra en ese estado.")
        return redirect("consultar_entidades")

    if (
        not nuevo_estado
        and Planificacion.objects.filter(
            entidad=entidad,
            estado=True,
        ).exists()
    ):
        messages.error(
            request,
            "No se puede desactivar la entidad porque tiene planificaciones activas.",
        )
        return redirect("consultar_entidades")

    entidad.estado = nuevo_estado
    entidad.save(update_fields=["estado"])

    if nuevo_estado:
        messages.success(request, "Entidad activada correctamente.")
    else:
        messages.success(request, "Entidad desactivada correctamente.")

    return redirect("consultar_entidades")