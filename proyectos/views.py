from django.shortcuts import render, redirect, get_object_or_404
from usuarios.models import Usuario
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST
from .models import (Proyecto, AuditoriaProyecto, Cronograma, Documento)
from .forms import (ProyectoForm, CronogramaForm, DocumentoForm)
from usuarios.permisos import validar_permiso
import mimetypes
from pathlib import Path
from django.http import FileResponse, Http404
from planificaciones.models import Planificacion

@login_required
def registrar_proyecto(request):
    
    permiso = validar_permiso(
    request,
    "Administrar proyectos"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = ProyectoForm(request.POST)

        if form.is_valid():

            codigo = form.cleaned_data["codigo"].strip()
            nombre = form.cleaned_data["nombre"].strip()
            descripcion = form.cleaned_data["descripcion"].strip()
            responsable = form.cleaned_data["responsable"]
            presupuesto = form.cleaned_data["presupuesto"]
            fecha_inicio = form.cleaned_data["fecha_inicio"]
            fecha_fin = form.cleaned_data["fecha_fin"]
            planificacion = form.cleaned_data["planificacion"]

            if not codigo or not nombre or not descripcion:

                messages.error(
                    request,
                    "Todos los campos son obligatorios."
                )

            elif presupuesto <= 0:

                messages.error(
                    request,
                    "El presupuesto debe ser mayor a cero."
                )

            elif fecha_inicio > fecha_fin:

                messages.error(
                    request,
                    "La fecha de inicio no puede ser mayor que la fecha de fin."
                )

            elif Proyecto.objects.filter(
                codigo__iexact=codigo
            ).exists():

                messages.error(
                    request,
                    "Ya existe un proyecto con ese código."
                )

            else:

                proyecto = form.save()

                AuditoriaProyecto.objects.create(
                    proyecto=proyecto,
                    accion="Registro",
                    usuario=request.user
                )

                messages.success(
                    request,
                    "Proyecto registrado correctamente."
                )

                return redirect(
                    "consultar_proyectos"
                )

    else:

        form = ProyectoForm()

    return render(
        request,
        "proyectos/registrar_proyecto.html",
        {
            "form": form
        }
    )


@login_required
def consultar_proyectos(request):
    permiso = validar_permiso(request, "Administrar proyectos")
    if permiso:
        return permiso

    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "")
    responsable_id = request.GET.get("responsable", "")
    planificacion_id = request.GET.get("planificacion", "")
    periodo = request.GET.get("periodo", "")
    presupuesto_min = request.GET.get("presupuesto_min", "").strip()
    presupuesto_max = request.GET.get("presupuesto_max", "").strip()

    proyectos = Proyecto.objects.filter(
        eliminado=False
    ).select_related(
        "responsable",
        "planificacion",
    )

    if buscar:

        proyectos = proyectos.filter(

            Q(nombre__icontains=buscar)

            | Q(codigo__icontains=buscar)

            | Q(responsable__first_name__icontains=buscar)

            | Q(responsable__last_name__icontains=buscar)
        )

    if estado in {"0", "1"}:
        proyectos = proyectos.filter(estado=(estado == "1"))
    else:
        estado = ""

    if responsable_id.isdecimal():
        proyectos = proyectos.filter(responsable_id=responsable_id)
    else:
        responsable_id = ""

    if planificacion_id.isdecimal():
        proyectos = proyectos.filter(planificacion_id=planificacion_id)
    else:
        planificacion_id = ""

    if periodo:
        proyectos = proyectos.filter(planificacion__periodo=periodo)

    try:
        if presupuesto_min:
            proyectos = proyectos.filter(
                presupuesto__gte=Decimal(presupuesto_min)
            )
    except InvalidOperation:
        presupuesto_min = ""
        messages.error(request, "El presupuesto mínimo no es válido.")

    try:
        if presupuesto_max:
            proyectos = proyectos.filter(
                presupuesto__lte=Decimal(presupuesto_max)
            )
    except InvalidOperation:
        presupuesto_max = ""
        messages.error(request, "El presupuesto máximo no es válido.")

    proyectos = proyectos.order_by("codigo")
    responsables = Usuario.objects.filter(
        estado=True,
        is_active=True,
    ).order_by("last_name", "first_name")
    planificaciones = Planificacion.objects.order_by("-periodo", "nombre")
    periodos = (
        Planificacion.objects.order_by("-periodo")
        .values_list("periodo", flat=True)
        .distinct()
    )

    mensaje = ""

    if not proyectos.exists():
        mensaje = "No existen proyectos que coincidan con la búsqueda."

    return render(

        request,

        "proyectos/consultar_proyecto.html",

        {

            "proyectos": proyectos,
            "responsables": responsables,
            "planificaciones": planificaciones,
            "periodos": periodos,
            "mensaje": mensaje,
            "buscar": buscar,
            "estado": estado,
            "responsable_id": responsable_id,
            "planificacion_id": planificacion_id,
            "periodo": periodo,
            "presupuesto_min": presupuesto_min,
            "presupuesto_max": presupuesto_max,
        },
    )
    
@login_required
def editar_proyecto(request, id):
    permiso = validar_permiso(request, "Administrar proyectos")
    if permiso:
        return permiso

    proyecto = get_object_or_404(
        Proyecto,
        pk=id,
        eliminado=False,
    )

    if request.method == "POST":
        form = ProyectoForm(request.POST, instance=proyecto)

        if form.is_valid():
            cambios = []

            for campo in form.changed_data:
                valor_anterior = getattr(proyecto, campo)
                valor_nuevo = form.cleaned_data[campo]
                etiqueta = form.fields[campo].label

                cambios.append(

                    f"{etiqueta}: {valor_anterior} → {valor_nuevo}"

                )

            proyecto = form.save()

            if cambios:
                AuditoriaProyecto.objects.create(
    
                    proyecto=proyecto,
    
                    accion="Actualización",
                    detalle="\n".join(cambios),
                    usuario=request.user,
                )

            messages.success(request, "Proyecto actualizado correctamente.")
            return redirect("consultar_proyectos")
    else:
        form = ProyectoForm(instance=proyecto)

    return render(
    
        request,
    
        "proyectos/editar_proyecto.html",
        {"form": form},
    )


@login_required
@require_POST
def eliminar_proyecto(request, id):
    permiso = validar_permiso(request, "Administrar proyectos")
    if permiso:
        return permiso

    proyecto = get_object_or_404(
    
        Proyecto,
    
        pk=id,
        eliminado=False,
    )

    tiene_dependencias = (
        proyecto.cronogramas.exists()
        or proyecto.metas.exists()
        or proyecto.objetivos_desarrollo.exists()
        or proyecto.objetivos_institucionales.exists()
    )

    if tiene_dependencias:
        messages.error(
    
            request,
            "No se puede eliminar el proyecto porque tiene cronogramas, metas u objetivos asociados.",
        )
    
        return redirect("consultar_proyectos")

    
    proyecto.eliminado = True
    proyecto.save(update_fields=["eliminado"])

    AuditoriaProyecto.objects.create(
       
        proyecto=proyecto,
       
        accion="Eliminación lógica",
        detalle="El proyecto fue marcado como eliminado.",
        usuario=request.user,
    )

    messages.success(request, "Proyecto eliminado correctamente.")
    return redirect("consultar_proyectos")
    
@login_required
def registrar_cronograma(request):
    
    permiso = validar_permiso(
    request,
    "Administrar proyectos"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = CronogramaForm(request.POST)

        if form.is_valid():

            fecha_inicio = form.cleaned_data["fecha_inicio"]
            fecha_fin = form.cleaned_data["fecha_fin"]
            
            if fecha_inicio > fecha_fin:

                messages.error(
                    request,
                    "La fecha inicial no puede ser mayor que la final."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Actividad registrada correctamente."
                )

                return redirect("consultar_cronogramas")

    else:

        form = CronogramaForm()

    return render(
        request,
        "proyectos/registrar_cronograma.html",
        {
            "form": form
        }
    )


@login_required
def consultar_cronogramas(request):
    
    permiso = validar_permiso(
    request,
    "Administrar proyectos"
    )

    if permiso:
        return permiso

    cronogramas = Cronograma.objects.select_related(
        "proyecto",
        "responsable"
    )

    return render(

        request,

        "proyectos/consultar_cronograma.html",

        {

            "cronogramas": cronogramas

        }

    )
    
@login_required
def editar_cronograma(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar proyectos"
    )

    if permiso:
        return permiso

    cronograma = get_object_or_404(
        Cronograma,
        pk=id
    )

    if request.method == "POST":

        form = CronogramaForm(
            request.POST,
            instance=cronograma
        )

        if form.is_valid():

            fecha_inicio = form.cleaned_data["fecha_inicio"]
            fecha_fin = form.cleaned_data["fecha_fin"]

            if fecha_inicio > fecha_fin:

                messages.error(
                    request,
                    "La fecha de inicio no puede ser mayor que la fecha de fin."
                )

            else:

                form.save()

                messages.success(
                    request,
                    "Cronograma actualizado correctamente."
                )

                return redirect(
                    "consultar_cronogramas"
                )

    else:

        form = CronogramaForm(
            instance=cronograma
        )

    return render(

        request,

        "proyectos/registrar_cronograma.html",

        {

            "form": form

        }

    )
    
@login_required
def registrar_documento(request):
    permiso = validar_permiso(request, "Administrar documentos")
    if permiso:
        return permiso

    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento cargado correctamente.")
            return redirect("consultar_documentos")
    else:
       
        form = DocumentoForm()

    return render(
       
        request,
       
        "proyectos/registrar_documento.html",
        {"form": form},
    )
    
@login_required
def consultar_documentos(request):
    
    permiso = validar_permiso(
    request,
    "Administrar documentos"
    )

    if permiso:
        return permiso

    documentos = Documento.objects.select_related(
        "proyecto"
    )

    return render(

        request,

        "proyectos/consultar_documentos.html",

        {

            "documentos": documentos

        }

    )
    
@login_required
def descargar_documento(request, id):
    permiso = validar_permiso(request, "Administrar documentos")
    if permiso:
        return permiso

    documento = get_object_or_404(
        Documento.objects.select_related("proyecto"),
        pk=id,
        proyecto__eliminado=False,
    )

    try:
        archivo = documento.archivo.open("rb")
    except (FileNotFoundError, ValueError):
        raise Http404("El archivo solicitado no está disponible.")

    tipo = mimetypes.guess_type(documento.archivo.name)[0]
    nombre = Path(documento.archivo.name).name

    return FileResponse(
        archivo,
        as_attachment=True,
        filename=nombre,
        content_type=tipo or "application/octet-stream",
    )