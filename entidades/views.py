from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Entidad
from .forms import EntidadForm
from django.db.models import Q


def registrar_entidad(request):

    if request.method == "POST":

        form = EntidadForm(request.POST)

        if form.is_valid():

            codigo = form.cleaned_data["codigo"].strip()
            nombre = form.cleaned_data["nombre"].strip()
            descripcion = form.cleaned_data["descripcion"].strip()
            responsable = form.cleaned_data["responsable"].strip()

            if not codigo:
                messages.error(request, "El código es obligatorio.")
                return render(request, "entidades/registrar_entidad.html", {"form": form})

            if not nombre:
                messages.error(request, "El nombre es obligatorio.")
                return render(request, "entidades/registrar_entidad.html", {"form": form})

            if not descripcion:
                messages.error(request, "La descripción es obligatoria.")
                return render(request, "entidades/registrar_entidad.html", {"form": form})

            if not responsable:
                messages.error(request, "El responsable es obligatorio.")
                return render(request, "entidades/registrar_entidad.html", {"form": form})

            if Entidad.objects.filter(codigo__iexact=codigo).exists():
                messages.error(request, "Ya existe una entidad con ese código.")
                return render(request, "entidades/registrar_entidad.html", {"form": form})

            form.save()

            messages.success(request, "Entidad registrada correctamente.")

            return redirect("consultar_entidades")

    else:

        form = EntidadForm()

    return render(
        request,
        "entidades/registrar_entidad.html",
        {
            "form": form
        }
    )

def consultar_entidades(request):

    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "")

    entidades = Entidad.objects.all()

    # Buscar por código, nombre o responsable
    if buscar != "":

        entidades = entidades.filter(
            Q(codigo__icontains=buscar) |
            Q(nombre__icontains=buscar) |
            Q(responsable__icontains=buscar)
        )

    # Filtrar por estado
    if estado == "1":
        entidades = entidades.filter(estado=True)

    elif estado == "0":
        entidades = entidades.filter(estado=False)

    mensaje = ""

    if entidades.count() == 0:
        mensaje = "No existen entidades que coincidan con la búsqueda."

    return render(
        request,
        "entidades/consultar_entidad.html",
        {
            "entidades": entidades,
            "mensaje": mensaje,
            "buscar": buscar,
            "estado": estado,
        }
    )

def editar_entidad(request, id):

    entidad = get_object_or_404(
        Entidad,
        id=id
    )

    if request.method == "POST":

        form = EntidadForm(
            request.POST,
            instance=entidad
        )

        if form.is_valid():

            codigo = form.cleaned_data["codigo"]

            existe = Entidad.objects.filter(
                codigo__iexact=codigo
            ).exclude(id=id)

            if existe.exists():

                messages.error(
                    request,
                    "Ya existe otra entidad con ese código."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Entidad actualizada correctamente."
                )

                return redirect("consultar_entidades")

    else:

        form = EntidadForm(
            instance=entidad
        )

    return render(
        request,
        "entidades/editar_entidad.html",
        {
            "form": form,
            "entidad": entidad
        }
    )


def eliminar_entidad(request, id):

    entidad = get_object_or_404(
        Entidad,
        id=id
    )

    entidad.delete()

    messages.success(
        request,
        "Entidad eliminada correctamente."
    )

    return redirect("consultar_entidades")

def cambiar_estado_entidad(request, id):

    entidad = get_object_or_404(
        Entidad,
        id=id
    )

    # En el futuro aquí validaremos dependencias
    # cuando exista el módulo Planificación.

    entidad.estado = not entidad.estado

    entidad.save()

    if entidad.estado:

        messages.success(
            request,
            "Entidad activada correctamente."
        )

    else:

        messages.success(
            request,
            "Entidad desactivada correctamente."
        )

    return redirect(
        "consultar_entidades"
    )