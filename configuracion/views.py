from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Configuracion
from .forms import ConfiguracionForm


def registrar_configuracion(request):

    if request.method == "POST":

        form = ConfiguracionForm(request.POST)

        if form.is_valid():

            nombre = form.cleaned_data["nombre"].strip()

            if Configuracion.objects.filter(
                nombre__iexact=nombre
            ).exists():

                messages.error(
                    request,
                    "Ya existe este parámetro."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Configuración registrada correctamente."
                )

                return redirect("consultar_configuracion")

    else:

        form = ConfiguracionForm()

    return render(
        request,
        "configuracion/registrar_configuracion.html",
        {
            "form": form
        }
    )


def consultar_configuracion(request):

    configuraciones = Configuracion.objects.all()

    return render(
        request,
        "configuracion/consultar_configuracion.html",
        {
            "configuraciones": configuraciones
        }
    )


def editar_configuracion(request, id):

    configuracion = get_object_or_404(
        Configuracion,
        pk=id
    )

    if request.method == "POST":

        form = ConfiguracionForm(
            request.POST,
            instance=configuracion
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Configuración actualizada correctamente."
            )

            return redirect(
                "consultar_configuracion"
            )

    else:

        form = ConfiguracionForm(
            instance=configuracion
        )

    return render(
        request,
        "configuracion/editar_configuracion.html",
        {
            "form": form
        }
    )
