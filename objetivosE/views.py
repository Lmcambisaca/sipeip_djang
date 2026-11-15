from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    ObjetivoEstrategico,
    HistorialObjetivoEstrategico
)

from .forms import ObjetivoEstrategicoForm

from usuarios.permisos import validar_permiso
@login_required
def registrar_objetivo_estrategico(request):

    permiso = validar_permiso(
        request,
        "Administrar objetivos estratégicos"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = ObjetivoEstrategicoForm(request.POST)

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

            elif ObjetivoEstrategico.objects.filter(
                codigo__iexact=codigo
            ).exists():

                messages.error(
                    request,
                    "Ya existe un objetivo estratégico con ese código."
                )

            else:
                
                objetivos = form.cleaned_data["objetivos_institucionales"]

                if not objetivos.exists():

                    messages.error(

                        request,

                        "Debe asociar al menos un objetivo institucional."

                    )

                else:

                    objetivo = form.save()

                    messages.success(

                        request,

                        "Objetivo estratégico registrado correctamente."

                    )

                    return redirect(
                        "consultar_objetivos_estrategicos"
                    )

    else:

        form = ObjetivoEstrategicoForm()

    return render(
        request,
        "objetivosE/registrar_objetivo_estrategico.html",
        {
            "form": form
        }
    )


@login_required
def consultar_objetivos_estrategicos(request):

    permiso = validar_permiso(
        request,
        "Consultar objetivos estratégicos"
    )

    if permiso:

        permiso = validar_permiso(
            request,
            "Administrar objetivos estratégicos"
        )

        if permiso:
            return permiso

    objetivos = ObjetivoEstrategico.objects.all()

    eje = request.GET.get("eje", "")

    periodo = request.GET.get("periodo", "")

    estado = request.GET.get("estado", "")

    if eje:

        objetivos = objetivos.filter(
            eje_estrategico__icontains=eje
        )

    if periodo:

        objetivos = objetivos.filter(
            periodo_vigencia__icontains=periodo
        )

    if estado != "":

        objetivos = objetivos.filter(
            estado=estado
        )

    mensaje = ""

    if not objetivos.exists():

        mensaje = "No existen objetivos estratégicos registrados."

    return render(

        request,

        "objetivosE/consultar_objetivos_estrategicos.html",

        {

            "objetivos": objetivos,

            "mensaje": mensaje

        }

    )


@login_required
def editar_objetivo_estrategico(request, id):
    permiso = validar_permiso(
        request,
        "Administrar objetivos estratégicos"
    )
    if permiso:
        return permiso

    objetivo = get_object_or_404(
        ObjetivoEstrategico,
        pk=id
    )

    if request.method == "POST":
        form = ObjetivoEstrategicoForm(
            request.POST,
            instance=objetivo
        )

        if form.is_valid():
            codigo = form.cleaned_data["codigo"].strip()
            descripcion = form.cleaned_data["descripcion"].strip()

            if not codigo:
                messages.error(request, "El código es obligatorio.")
            elif not descripcion:
                messages.error(request, "La descripción es obligatoria.")
            elif ObjetivoEstrategico.objects.filter(
                codigo__iexact=codigo
            ).exclude(
                pk=objetivo.pk
            ).exists():
                messages.error(
                    request,
                    "Ya existe otro objetivo estratégico con ese código."
                )
            else:
                cambios = []

                if objetivo.codigo != codigo:
                    cambios.append("Código actualizado")

                if objetivo.descripcion != descripcion:
                    cambios.append("Descripción actualizada")

                if objetivo.eje_estrategico != form.cleaned_data["eje_estrategico"]:
                    cambios.append("Eje estratégico actualizado")

                if objetivo.periodo_vigencia != form.cleaned_data["periodo_vigencia"]:
                    cambios.append("Período de vigencia actualizado")

                if objetivo.estado != form.cleaned_data["estado"]:
                    cambios.append("Estado actualizado")

                instituciones_anteriores = set(
                    objetivo.objetivos_institucionales.values_list(
                        "pk",
                        flat=True
                    )
                )
                instituciones_nuevas = set(
                    form.cleaned_data[
                        "objetivos_institucionales"
                    ].values_list("pk", flat=True)
                )

                if instituciones_anteriores != instituciones_nuevas:
                    cambios.append(
                        "Objetivos institucionales asociados actualizados"
                    )

                objetivo = form.save()

                if cambios:
                    HistorialObjetivoEstrategico.objects.create(
                        objetivo=objetivo,
                        usuario=request.user,
                        accion="; ".join(cambios)
                    )

                messages.success(
                    request,
                    "Objetivo estratégico actualizado correctamente."
                )
                return redirect("consultar_objetivos_estrategicos")
    else:
        form = ObjetivoEstrategicoForm(instance=objetivo)

    return render(
        request,
        "objetivosE/editar_objetivo_estrategico.html",
        {"form": form}
    )
    
@login_required
def seguimiento_objetivo_estrategico(request,id):

    permiso = validar_permiso(
        request,
        "Consultar objetivos estratégicos"
    )

    if permiso:

        permiso = validar_permiso(
            request,
            "Administrar objetivos estratégicos"
        )

        if permiso:
            return permiso

    objetivo = get_object_or_404(
        ObjetivoEstrategico,
        pk=id
    )

    registros = []

    total = 0
    cantidad = 0

    for oi in objetivo.objetivos_institucionales.all():

        for proyecto in oi.proyectos.all():

            metas = proyecto.metas.all()

            cantidad_metas = metas.count()

            cantidad_indicadores = 0

            suma = 0
            contador = 0

            for meta in metas:

                indicadores = meta.indicadores.all()

                cantidad_indicadores += indicadores.count()

                for indicador in indicadores:

                    avances = indicador.avances.all()

                    for avance in avances:

                        suma += avance.porcentaje_cumplimiento
                        contador += 1

            porcentaje = 0

            if contador > 0:

                porcentaje = round(suma / contador)

                total += porcentaje

                cantidad += 1

            registros.append({

                "objetivo": oi,

                "proyecto": proyecto,

                "metas": cantidad_metas,

                "indicadores": cantidad_indicadores,

                "porcentaje": porcentaje

            })

    porcentaje_general = 0

    if cantidad > 0:

        porcentaje_general = round(total / cantidad)

    return render(

        request,

        "objetivosE/seguimiento_objetivo_estrategico.html",

        {

            "objetivo": objetivo,

            "registros": registros,

            "porcentaje": porcentaje_general

        }

    )


@login_required
def dashboard_objetivos_estrategicos(request):

    permiso = validar_permiso(
        request,
        "Consultar objetivos estratégicos"
    )

    if permiso:

        permiso = validar_permiso(
            request,
            "Administrar objetivos estratégicos"
        )

        if permiso:
            return permiso

    datos = []

    objetivos = ObjetivoEstrategico.objects.all()

    for objetivo in objetivos:

        total = 0

        cantidad = 0

        for oi in objetivo.objetivos_institucionales.all():

            suma = 0

            contador = 0

            for proyecto in oi.proyectos.all():

                for cronograma in proyecto.cronogramas.all():

                    suma += cronograma.porcentaje_avance

                    contador += 1

            if contador > 0:

                total += round(suma / contador)

                cantidad += 1

        porcentaje = 0

        if cantidad > 0:

            porcentaje = round(total / cantidad)

        datos.append({

            "objetivo": objetivo,

            "porcentaje": porcentaje

        })

    return render(

        request,

        "objetivosE/dashboard_objetivos_estrategicos.html",

        {

            "datos": datos

        }

    )