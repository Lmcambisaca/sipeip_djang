from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.db import connection
from .forms import ReporteForm
from .models import Reporte

import io

from reportlab.pdfgen import canvas
from openpyxl import Workbook


from usuarios.models import Usuario
from entidades.models import Entidad
from proyectos.models import Proyecto
from planificaciones.models import Planificacion
from proyectos.models import Proyecto
from ods.models import ObjetivoDesarrollo
from seguimiento.models import Meta, Indicador, AvanceIndicador
from seguimiento.models import Meta
from seguimiento.models import Indicador
from usuarios.permisos import validar_permiso

@login_required
def generar_reporte(request):

    if request.method == "POST":
        
        if Proyecto.objects.count() == 0:
            messages.warning(
                request,
                "No existe información disponible para generar el reporte"
            )

            return redirect("generar_reporte")

        form = ReporteForm(request.POST)

        if form.is_valid():

            tipo = form.cleaned_data["tipo"]

            Reporte.objects.create(

                tipo=tipo,

                usuario=request.user

            )

            if request.POST["accion"] == "pdf":

                return redirect(
                    "reporte_pdf",
                    tipo=tipo
                )

            return redirect(
                "reporte_excel",
                tipo=tipo
            )

    else:

        form = ReporteForm()

    return render(

        request,

        "reportes/generar_reporte.html",

        {

            "form": form

        }

    )
    
@login_required
def consultar_reportes(request):
    permiso = _tiene_permiso(request)
    if permiso:
        return permiso

    reportes = Reporte.objects.select_related("usuario").order_by(
        "-fecha_generacion", "-pk"
    )

    tipo = request.GET.get("tipo", "").strip()
    fecha = request.GET.get("fecha", "").strip()
    usuario_id = request.GET.get("usuario", "").strip()

    tipos_validos = {valor for valor, _ in Reporte.TIPO_REPORTE}
    if tipo in tipos_validos:
        reportes = reportes.filter(tipo=tipo)
    else:
        tipo = ""

    fecha_valida = parse_date(fecha) if fecha else None
    if fecha_valida:
        reportes = reportes.filter(fecha_generacion__date=fecha_valida)
    else:
        fecha = ""

    usuarios = Usuario.objects.order_by("username")
    if usuario_id.isdecimal() and usuarios.filter(pk=usuario_id).exists():
        reportes = reportes.filter(usuario_id=usuario_id)
    else:
        usuario_id = ""

    return render(
        request,
        "reportes/consultar_reportes.html",
        {
            "reportes": reportes,
            "tipo": tipo,
            "fecha": fecha,
            "usuario_id": usuario_id,
            "usuarios": usuarios,
        },
    )
    
@login_required
def reporte_pdf(request, tipo):
    
    permiso = validar_permiso(

        request,

        "Generar reportes"

    )


    if permiso:

        return permiso

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.drawString(50,800,f"Reporte: {tipo}")

    y = 770

    for dato in obtener_datos(tipo):

        pdf.drawString(50,y,str(dato))

        y -= 20

        if y < 40:

            pdf.showPage()

            y = 800

    pdf.save()

    buffer.seek(0)

    return FileResponse(

        buffer,

        as_attachment=True,

        filename=f"{tipo}.pdf"

    )
    
@login_required
def reporte_excel(request, tipo):
    
    permiso = validar_permiso(
    request,
    "Generar reportes"
    )

    if permiso:
        return permiso

    libro = Workbook()

    hoja = libro.active

    hoja.append(["Reporte", tipo])

    hoja.append([""])

    for dato in obtener_datos(tipo):

        hoja.append([str(dato)])

    respuesta = FileResponse(

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    respuesta["Content-Disposition"] = (

        f'attachment; filename="{tipo}.xlsx"'

    )

    libro.save(respuesta)

    return respuesta

@login_required
def reporte_consolidado(request):


    informacion = {

        "usuarios": Usuario.objects.count(),

        "entidades": Entidad.objects.count(),

        "proyectos": Proyecto.objects.count(),

        "metas": Meta.objects.count(),

        "indicadores": Indicador.objects.count(),

    }


    return render(

        request,

        "reportes/reporte_consolidado.html",

        {

            "informacion": informacion

        }

    )