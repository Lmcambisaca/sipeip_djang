from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from .models import (
    Meta,
    HistorialMeta,
    Indicador,
    AvanceIndicador,
)

from .forms import (
    MetaForm,
    IndicadorForm,
    AvanceIndicadorForm,
)

from usuarios.permisos import validar_permiso

@login_required
def registrar_meta(request):
    
    permiso = validar_permiso(
    request,
    "Administrar metas"
    )

    if permiso:
        return permiso

    if request.method=="POST":

        form=MetaForm(request.POST)

        if form.is_valid():

            descripcion=form.cleaned_data["descripcion"].strip()

            periodo=form.cleaned_data["periodo"].strip()

            unidad=form.cleaned_data["unidad_medida"].strip()

            valor=form.cleaned_data["valor_esperado"]

            if not descripcion:

                messages.error(
                    request,
                    "La descripción es obligatoria."
                )

            elif not periodo:

                messages.error(
                    request,
                    "El período es obligatorio."
                )

            elif not unidad:

                messages.error(
                    request,
                    "La unidad de medida es obligatoria."
                )

            elif valor<=0:

                messages.error(
                    request,
                    "El valor esperado debe ser mayor que cero."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Meta registrada correctamente."
                )

                return redirect("consultar_metas")

    else:

        form=MetaForm()

    return render(

        request,

        "seguimiento/registrar_meta.html",

        {

            "form":form

        }

    )
    
@login_required
def consultar_metas(request):
    
    permiso = validar_permiso(
    request,
    "Administrar metas"
    )

    if permiso:
        return permiso

    buscar = request.GET.get("buscar", "")

    metas = Meta.objects.select_related("proyecto")

    if buscar:

        metas = metas.filter(
            descripcion__icontains=buscar
        )

    mensaje = ""

    if not metas.exists():

        mensaje = "No existen metas registradas."

    return render(

        request,

        "seguimiento/consultar_metas.html",

        {

            "metas": metas,

            "mensaje": mensaje,

            "buscar": buscar

        }

    )
    
@login_required
def editar_meta(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar metas"
    )

    if permiso:
        return permiso

    meta = get_object_or_404(
        Meta,
        pk=id
    )

    if request.method == "POST":

        form = MetaForm(
            request.POST,
            instance=meta
        )

        if form.is_valid():

            descripcion = form.cleaned_data["descripcion"].strip()

            periodo = form.cleaned_data["periodo"].strip()

            unidad = form.cleaned_data["unidad_medida"].strip()

            valor = form.cleaned_data["valor_esperado"]

            if not descripcion:

                messages.error(
                    request,
                    "La descripción es obligatoria."
                )

            elif not periodo:

                messages.error(
                    request,
                    "El período es obligatorio."
                )

            elif not unidad:

                messages.error(
                    request,
                    "La unidad es obligatoria."
                )

            elif valor <= 0:

                messages.error(
                    request,
                    "El valor esperado debe ser mayor que cero."
                )

            else:
                
                HistorialMeta.objects.create(

                    meta=meta,

                    descripcion="Actualización de la meta."

                )
                
                proyecto = form.cleaned_data["proyecto"]

                if not proyecto.objetivos_desarrollo.exists():

                    messages.error(

                        request,

                        "El proyecto seleccionado no está asociado a ningún Objetivo de Desarrollo."

                    )

                    return render(

                        request,

                        "seguimiento/registrar_meta.html",

                        {

                            "form": form

                        }

                    )

                form.save()

                messages.success(
                    request,
                    "Meta actualizada correctamente."
                )

                return redirect(
                    "consultar_metas"
                )

    else:

        form = MetaForm(instance=meta)

    return render(

        request,

        "seguimiento/editar_meta.html",

        {

            "form": form

        }

    )
    
@login_required
def registrar_indicador(request):
    
    permiso = validar_permiso(
    request,
    "Administrar indicadores"
    )

    if permiso:
        return permiso

    if request.method=="POST":

        form=IndicadorForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Indicador registrado correctamente."
            )

            return redirect(
                "consultar_indicadores"
            )

    else:

        form=IndicadorForm()

    return render(

        request,

        "seguimiento/registrar_indicador.html",

        {

            "form":form

        }

    )
    
@login_required
def consultar_indicadores(request):
    
    permiso = validar_permiso(
    request,
    "Administrar indicadores"
    )

    if permiso:
        return permiso

    indicadores=Indicador.objects.select_related(
        "meta"
    )

    return render(

        request,

        "seguimiento/consultar_indicadores.html",

        {

            "indicadores":indicadores

        }

    )
    
@login_required
def editar_indicador(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar indicadores"
    )

    if permiso:
        return permiso

    indicador = get_object_or_404(
        Indicador,
        pk=id
    )

    if request.method == "POST":

        form = IndicadorForm(
            request.POST,
            instance=indicador
        )

        if form.is_valid():

            meta = form.cleaned_data["meta"]

            if not meta:

                messages.error(
                    request,
                    "Debe seleccionar una meta."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Indicador actualizado correctamente."
                )

                return redirect(
                    "consultar_indicadores"
                )

    else:

        form = IndicadorForm(
            instance=indicador
        )

    return render(

        request,

        "seguimiento/editar_indicador.html",

        {

            "form": form

        }

    )


@login_required
def registrar_avance(request):
    
    permiso = validar_permiso(
    request,
    "Registrar avances"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = AvanceIndicadorForm(
            request.POST
        )

        if form.is_valid():

            avance = form.save(commit=False)

            meta = avance.indicador.meta

            porcentaje = (
                float(avance.valor) /
                float(meta.valor_esperado)
            ) * 100

            if porcentaje > 100:
                porcentaje = 100

            avance.porcentaje_cumplimiento = porcentaje

            avance.save()

            messages.success(
                request,
                "Avance registrado correctamente."
            )

            return redirect(
                "consultar_avances"
            )

    else:

        form = AvanceIndicadorForm()

    return render(

        request,

        "seguimiento/registrar_avance.html",

        {

            "form": form

        }

    )
    
@login_required
def consultar_avances(request):
    
    permiso = validar_permiso(
    request,
    "Registrar avances"
    )

    if permiso:
        return permiso

    avances = AvanceIndicador.objects.select_related(
        "indicador",
        "indicador__meta"
    )

    return render(

        request,

        "seguimiento/consultar_avances.html",

        {

            "avances": avances

        }

    )
    
@login_required
def editar_avance(request, id):
    
    permiso = validar_permiso(
    request,
    "Registrar avances"
    )

    if permiso:
        return permiso

    avance = get_object_or_404(
        AvanceIndicador,
        pk=id
    )

    if request.method == "POST":

        form = AvanceIndicadorForm(
            request.POST,
            instance=avance
        )

        if form.is_valid():

            avance = form.save(commit=False)

            meta = avance.indicador.meta

            porcentaje = (
                float(avance.valor) /
                float(meta.valor_esperado)
            ) * 100

            if porcentaje > 100:

                porcentaje = 100

            avance.porcentaje_cumplimiento = porcentaje

            avance.save()

            messages.success(

                request,

                "Avance actualizado correctamente."

            )

            return redirect(
                "consultar_avances"
            )

    else:

        form = AvanceIndicadorForm(
            instance=avance
        )

    return render(

        request,

        "seguimiento/editar_avance.html",

        {

            "form": form

        }

    )

@login_required
def grafico_indicador(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar indicadores"
    )

    if permiso:
        return permiso

    indicador = get_object_or_404(
        Indicador,
        pk=id
    )

    avances = AvanceIndicador.objects.filter(
        indicador=indicador
    ).order_by("fecha")

    fechas = []
    valores = []

    for avance in avances:

        fechas.append(
            avance.fecha.strftime("%d/%m/%Y")
        )

        valores.append(
            float(avance.valor)
        )

    return render(

        request,

        "seguimiento/grafico_indicador.html",

        {

            "indicador": indicador,

            "fechas": json.dumps(fechas),

            "valores": json.dumps(valores),

        }

    )
    
    

