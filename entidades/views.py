from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Entidad
from .forms import EntidadForm


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

    buscar = request.GET.get("buscar", "")

    if buscar:

        entidades = Entidad.objects.filter(
            nombre__icontains=buscar
        )

    else:

        entidades = Entidad.objects.all()

    mensaje = ""

    if not entidades.exists():
        mensaje = "No existen entidades registradas."

    return render(
        request,
        "entidades/consultar_entidad.html",
        {
            "entidades": entidades,
            "mensaje": mensaje
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