from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    ObjetivoInstitucional,
    HistorialObjetivoInstitucional
)

from .forms import ObjetivoInstitucionalForm

from usuarios.permisos import validar_permiso
@login_required
def registrar_objetivo_institucional(request):

    permiso = validar_permiso(
        request,
        "Administrar objetivos institucionales"
    )

    if permiso:
        return permiso


    if request.method == "POST":

        form = ObjetivoInstitucionalForm(request.POST)

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

            elif ObjetivoInstitucional.objects.filter(
                codigo__iexact=codigo
            ).exists():

                messages.error(
                    request,
                    "Ya existe un objetivo institucional con ese código."
                )

            else:

                objetivo = form.save()


                HistorialObjetivoInstitucional.objects.create(
                    objetivo=objetivo,
                    usuario=request.user,
                    accion="Registro"
                )


                messages.success(
                    request,
                    "Objetivo institucional registrado correctamente."
                )

                return redirect(
                    "consultar_objetivos_institucionales"
                )


    else:

        form = ObjetivoInstitucionalForm()


    return render(
        request,
        "objetivosI/registrar_objetivo.html",
        {
            "form":form
        }
    )

@login_required
def consultar_objetivos_institucionales(request):

    permiso = validar_permiso(
        request,
        "Consultar objetivos institucionales"
    )

    if permiso:

        permiso = validar_permiso(
            request,
            "Administrar objetivos institucionales"
        )

        if permiso:
            return permiso


    objetivos = ObjetivoInstitucional.objects.all()


    periodo = request.GET.get(
        "periodo",
        ""
    )

    responsable = request.GET.get(
        "responsable",
        ""
    )

    estado = request.GET.get(
        "estado",
        ""
    )


    if periodo:

        objetivos = objetivos.filter(
            periodo_vigencia__icontains=periodo
        )


    if responsable:

        objetivos = objetivos.filter(
            responsable_id=responsable
        )


    if estado != "":

        objetivos = objetivos.filter(
            estado=estado
        )


    mensaje=""


    if not objetivos.exists():

        mensaje="No existen objetivos institucionales registrados."


    return render(
        request,
        "objetivosI/consultar_objetivo.html",
        {
            "objetivos":objetivos,
            "mensaje":mensaje
        }
    )


@login_required
def editar_objetivo_institucional(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar objetivos institucionales"
    )

    if permiso:
        return permiso

    objetivo = get_object_or_404(
        ObjetivoInstitucional,
        pk=id
    )


    if request.method == "POST":


        form = ObjetivoInstitucionalForm(
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


            elif ObjetivoInstitucional.objects.filter(

                codigo__iexact=codigo

            ).exclude(

                pk=objetivo.pk

            ).exists():


                messages.error(
                    request,
                    "Ya existe otro objetivo con ese código."
                )


            else:


                cambios = []


                if objetivo.descripcion != descripcion:

                    cambios.append(
                        "Descripción modificada"
                    )


                if objetivo.periodo_vigencia != form.cleaned_data["periodo_vigencia"]:

                    cambios.append(
                        "Periodo actualizado"
                    )


                if objetivo.responsable != form.cleaned_data["responsable"]:

                    cambios.append(
                        "Responsable actualizado"
                    )


                if objetivo.estado != form.cleaned_data["estado"]:

                    cambios.append(
                        "Estado actualizado"
                    )


                objetivo = form.save()


                if cambios:


                    HistorialObjetivoInstitucional.objects.create(

                        objetivo=objetivo,

                        usuario=request.user,

                        accion=", ".join(cambios)

                    )


                messages.success(

                    request,

                    "Objetivo institucional actualizado correctamente."

                )


                return redirect(

                    "consultar_objetivos_institucionales"

                )


    else:


        form = ObjetivoInstitucionalForm(

            instance=objetivo

        )


    return render(

        request,

        "objetivosI/editar_objetivo.html",

        {

            "form":form

        }

    )
    
@login_required
def seguimiento_objetivo_institucional(request,id):

    permiso = validar_permiso(
        request,
        "Consultar objetivos institucionales"
    )

    if permiso:
        
        permiso = validar_permiso(
            request,
            "Administrar objetivos institucionales"
        )

        if permiso:
            return permiso

    objetivo = get_object_or_404(
        ObjetivoInstitucional,
        pk=id
    )

    proyectos = objetivo.proyectos.all()

    indicadores = []

    total = 0

    cantidad = 0


    for proyecto in proyectos:

        for cronograma in proyecto.cronogramas.all():

            indicadores.append(cronograma)

            total += cronograma.porcentaje_avance

            cantidad += 1


    porcentaje = 0

    if cantidad > 0:

        porcentaje = round(total / cantidad)


    return render(

        request,

        "objetivosI/seguimiento_objetivo.html",

        {

            "objetivo": objetivo,

            "indicadores": indicadores,

            "porcentaje": porcentaje

        }

    )
    
@login_required
def dashboard_objetivos_institucionales(request):

    permiso = validar_permiso(
        request,
        "Consultar objetivos institucionales"
    )

    if permiso:

        permiso = validar_permiso(
            request,
            "Administrar objetivos institucionales"
        )

        if permiso:
            return permiso

    datos = []

    objetivos = ObjetivoInstitucional.objects.all()

    for objetivo in objetivos:

        total = 0

        cantidad = 0

        for proyecto in objetivo.proyectos.all():

            for cronograma in proyecto.cronogramas.all():

                total += cronograma.porcentaje_avance

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

        "objetivosI/dashboard_objetivos.html",

        {

            "datos": datos

        }

    )