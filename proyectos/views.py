from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import (
    Proyecto,
    AuditoriaProyecto,
    Cronograma, 
    Documento
)

from .forms import (ProyectoForm, CronogramaForm, DocumentoForm)

@login_required
def registrar_proyecto(request):

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

    buscar = request.GET.get(
        "buscar",
        ""
    )

    proyectos = Proyecto.objects.filter(
    eliminado=False
    ).select_related(
        "responsable",
        "planificacion"
    )

    if buscar:

        proyectos = proyectos.filter(

            Q(nombre__icontains=buscar)

            | Q(codigo__icontains=buscar)

            | Q(responsable__first_name__icontains=buscar)

        )

    mensaje = ""

    if not proyectos.exists():

        mensaje = "No existen proyectos registrados."

    return render(

        request,

        "proyectos/consultar_proyecto.html",

        {

            "proyectos": proyectos,

            "mensaje": mensaje,

            "buscar": buscar

        }

    )
    
@login_required
def editar_proyecto(request, id):

    proyecto = get_object_or_404(
        Proyecto,
        pk=id,
        eliminado=False
    )

    if request.method == "POST":

        form = ProyectoForm(
            request.POST,
            instance=proyecto
        )

        if form.is_valid():

            presupuesto = form.cleaned_data["presupuesto"]

            fecha_inicio = form.cleaned_data["fecha_inicio"]

            fecha_fin = form.cleaned_data["fecha_fin"]

            if presupuesto <= 0:

                messages.error(
                    request,
                    "El presupuesto debe ser mayor a cero."
                )

            elif fecha_inicio > fecha_fin:

                messages.error(
                    request,
                    "La fecha inicial no puede ser mayor que la final."
                )

            else:

                proyecto = form.save()

                AuditoriaProyecto.objects.create(

                    proyecto=proyecto,

                    accion="Actualización",

                    usuario=request.user

                )

                messages.success(

                    request,

                    "Proyecto actualizado correctamente."

                )

                return redirect(
                    "consultar_proyectos"
                )

    else:

        form = ProyectoForm(
            instance=proyecto
        )

    return render(

        request,

        "proyectos/editar_proyecto.html",

        {

            "form": form

        }

    )


@login_required
def eliminar_proyecto(request, id):

    proyecto = get_object_or_404(

        Proyecto,

        pk=id,

        eliminado=False

    )
    
    # TAR-116, TAR-118 y TAR-119

    if proyecto.cronogramas.exists():

        messages.error(

            request,

            "No puede eliminar este proyecto porque tiene actividades registradas en el cronograma."

        )

        return redirect("consultar_proyectos")


    proyecto.eliminado = True

    proyecto.save()

    AuditoriaProyecto.objects.create(

        proyecto=proyecto,

        accion="Eliminación lógica",

        usuario=request.user

    )

    messages.success(

        request,

        "Proyecto eliminado correctamente."

    )

    return redirect(
        "consultar_proyectos"
    )
    
@login_required
def registrar_cronograma(request):

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
    
    if not request.user.is_authenticated:

        return redirect("login")
    
    if request.user.rol and request.user.rol.nombre not in [
        "Administrador",
        "Planificador"
    ]:

        messages.error(
            request,
            "No tiene permisos para registrar documentos."
        )

        return redirect("dashboard")

    if request.method == "POST":

        form = DocumentoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            archivo = request.FILES["archivo"]

            if archivo.size > 5 * 1024 * 1024:

                messages.error(
                    request,
                    "El archivo supera el tamaño permitido (5 MB)."
                )

            else:

                extension = archivo.name.split(".")[-1].lower()

                permitidos = [

                    "pdf",

                    "doc",

                    "docx",

                    "xls",

                    "xlsx",

                    "png",

                    "jpg",

                    "jpeg"

                ]

                if extension not in permitidos:

                    messages.error(
                        request,
                        "Formato de archivo no permitido."
                    )

                else:

                    form.save()

                    messages.success(
                        request,
                        "Documento cargado correctamente."
                    )

                    return redirect(
                        "consultar_documentos"
                    )

    else:

        form = DocumentoForm()

    return render(

        request,

        "proyectos/registrar_documento.html",

        {

            "form": form

        }

    )
    
@login_required
def consultar_documentos(request):

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