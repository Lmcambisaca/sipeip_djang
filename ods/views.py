from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    ObjetivoDesarrollo,
    HistorialObjetivo,
)

from .forms import ObjetivoDesarrolloForm

from seguimiento.models import (
    Meta,
    Indicador,
)

from usuarios.permisos import validar_permiso


@login_required
def registrar_objetivo(request):
    
    permiso = validar_permiso(
    request,
    "Administrar ODS"
    )

    if permiso:
        return permiso
    
    if request.method == "POST":

        form = ObjetivoDesarrolloForm(request.POST)

        if form.is_valid():

            codigo = form.cleaned_data["codigo"].strip()

            descripcion = form.cleaned_data["descripcion"].strip()

            if not codigo:

                messages.error(
                    request,
                    "El código es obligatorio."
                )

            elif not descripcion:

                messages.error(
                    request,
                    "La descripción es obligatoria."
                )

            elif ObjetivoDesarrollo.objects.filter(
                codigo__iexact=codigo
            ).exists():

                messages.error(
                    request,
                    "Ya existe un objetivo con ese código."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Objetivo registrado correctamente."
                )

                return redirect("consultar_objetivos")

    else:

        form = ObjetivoDesarrolloForm()

    return render(
        request,
        "ods/registrar_objetivo.html",
        {
            "form": form
        }
    )
    
@login_required
def consultar_objetivos(request):
    
    permiso = validar_permiso(
    request,
    "Consultar ODS"
    )

    if permiso:
        return permiso
    
    objetivos = ObjetivoDesarrollo.objects.all()


    buscar = request.GET.get(
        "buscar",
        ""
    )


    eje = request.GET.get(
        "eje",
        ""
    )


    if buscar:

        objetivos = objetivos.filter(

            descripcion__icontains=buscar

        )


    if eje:

        objetivos = objetivos.filter(

            eje_estrategico__icontains=eje

        )


    mensaje = ""


    if not objetivos.exists():

        mensaje = "No existen objetivos registrados."


    return render(

        request,

        "ods/consultar_objetivos.html",

        {

            "objetivos": objetivos,

            "mensaje": mensaje

        }

    )
    
@login_required
def editar_objetivo(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar ODS"
    )

    if permiso:
        return permiso
    
    objetivo = get_object_or_404(
        ObjetivoDesarrollo,
        pk=id
    )

    if request.method == "POST":

        form = ObjetivoDesarrolloForm(
            request.POST,
            instance=objetivo
        )

        if form.is_valid():

            codigo = form.cleaned_data["codigo"].strip()

            descripcion = form.cleaned_data["descripcion"].strip()

            if not codigo:

                messages.error(
                    request,
                    "El código es obligatorio."
                )

            elif not descripcion:

                messages.error(
                    request,
                    "La descripción es obligatoria."
                )

            elif ObjetivoDesarrollo.objects.filter(
                codigo__iexact=codigo
            ).exclude(
                pk=objetivo.pk
            ).exists():

                messages.error(
                    request,
                    "Ya existe un objetivo con ese código."
                )

            else:

                form.save()
                
                HistorialObjetivo.objects.create(

                    objetivo=objetivo,

                    usuario=request.user,

                    descripcion="Se actualizó la información del objetivo."

                )

                messages.success(
                    request,
                    "Objetivo actualizado correctamente."
                )

                return redirect("consultar_objetivos")

    else:

        form = ObjetivoDesarrolloForm(
            instance=objetivo
        )

    return render(
        request,
        "ods/editar_objetivo.html",
        {
            "form": form
        }
    )
        
@login_required
def seguimiento_objetivo(request, id):
    
    permiso = validar_permiso(
    request,
    "Consultar ODS"
    )

    if permiso:
        return permiso
    
    objetivo = get_object_or_404(
        ObjetivoDesarrollo,
        pk=id
    )

    proyectos = objetivo.proyectos.all()

    metas = Meta.objects.filter(
        proyecto__in=proyectos
    )

    indicadores = Indicador.objects.filter(
        meta__in=metas
    )

    indicadores_activos = indicadores.filter(
    estado=True
).count()

    total_indicadores = indicadores.count()

    if total_indicadores > 0:

        promedio = round(
            (indicadores_activos / total_indicadores) * 100,
            2
        )

    else:

        promedio = 0

    return render(

        request,

        "ods/seguimiento_objetivo.html",

        {

            "objetivo": objetivo,

            "proyectos": proyectos,

            "metas": metas,

            "indicadores": indicadores,

            "promedio": promedio

        }

    )

@login_required
def dashboard_ods(request):
    
    permiso = validar_permiso(
    request,
    "Consultar ODS"
    )

    if permiso:
        return permiso
    
    objetivos = ObjetivoDesarrollo.objects.all()

    datos = []

    for objetivo in objetivos:

        proyectos = objetivo.proyectos.all()

        metas = Meta.objects.filter(
            proyecto__in=proyectos
        )

        indicadores = Indicador.objects.filter(
            meta__in=metas
        )

        total = indicadores.count()

        activos = indicadores.filter(
            estado=True
        ).count()

        if total > 0:

            porcentaje = round(
                (activos / total) * 100,
                2
            )

        else:

            porcentaje = 0

        if porcentaje >= 80:

            color = "success"

        elif porcentaje >= 50:

            color = "warning"

        else:

            color = "danger"

        datos.append({

            "codigo": objetivo.codigo,

            "descripcion": objetivo.descripcion,

            "porcentaje": porcentaje,

            "color": color

        })

    return render(

        request,

        "ods/dashboard_ods.html",

        {

            "datos": datos

        }

    )