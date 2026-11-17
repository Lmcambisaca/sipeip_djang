from io import BytesIO
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.utils.text import slugify
from django.urls import reverse
from openpyxl import Workbook

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from urllib.parse import urlencode
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,)

from entidades.models import Entidad
from ods.models import ObjetivoDesarrollo
from planificaciones.models import Planificacion
from proyectos.models import Proyecto
from seguimiento.models import AvanceIndicador, Indicador, Meta
from usuarios.models import Usuario
from inversiones.models import Inversion
from django.db.models import Q
from usuarios.permisos import validar_permiso

from .forms import ReporteForm
from .models import Reporte



REPORTES = {
    "Usuarios": Usuario,
    "Entidades": Entidad,
    "Planificaciones": Planificacion,
    "Proyectos": Proyecto,
    "ODS": ObjetivoDesarrollo,
    "Metas": Meta,
    "Indicadores": Indicador,
    "Avances": AvanceIndicador,
    "Inversiones": Inversion,
}

CAMPOS_REPORTE = {
    "Usuarios": ("username", "first_name", "last_name", "email", "rol", "estado"),
    "Entidades": ("codigo", "nombre", "descripcion", "responsable", "estado"),
    "Planificaciones": ("periodo", "nombre", "descripcion", "fecha_inicio", "fecha_fin","entidad", "estado", "validada", "aprobada", "observacion"),
    "Proyectos": ("codigo", "nombre", "descripcion", "responsable", "presupuesto","fecha_inicio", "fecha_fin", "planificacion", "estado"),
    "ODS": ("codigo", "descripcion", "eje_estrategico", "periodo_vigencia"),
    "Metas": ("proyecto", "descripcion", "periodo", "unidad_medida","valor_esperado", "estado"),
    "Indicadores": ("meta", "nombre", "formula", "unidad_medida", "frecuencia", "estado"),
    "Avances": ("indicador", "fecha", "valor", "porcentaje_cumplimiento"),
    "Inversiones": ("codigo", "nombre", "monto_asignado", "monto_ejecutado", "fuente_financiamiento", "proyecto", "periodo_fiscal", "estado",),
}


def _tiene_permiso(request):
    return validar_permiso(request, "Generar reportes")


def obtener_datos(tipo, filtros=None):
    filtros = filtros or {}

    if tipo == "Consolidado":
        encabezados = ["Módulo", "Registros"]
        filas = [
            ["Usuarios", Usuario.objects.count()],
            ["Entidades", Entidad.objects.count()],
            ["Planificaciones", Planificacion.objects.count()],
            ["Proyectos", Proyecto.objects.count()],
            ["ODS", ObjetivoDesarrollo.objects.count()],
            ["Metas", Meta.objects.count()],
            ["Indicadores", Indicador.objects.count()],
            ["Avances", AvanceIndicador.objects.count()],
            ["Inversiones", Inversion.objects.count()],
        ]
        return encabezados, filas

    modelo = REPORTES.get(tipo)
    if modelo is None:
        return [], []

    campos_disponibles = {
        campo.name: campo
        for campo in modelo._meta.concrete_fields
    }

    campos = [
        campos_disponibles[nombre]
        for nombre in CAMPOS_REPORTE.get(tipo, ())
        if nombre in campos_disponibles
    ]

    registros = modelo.objects.all()

    busqueda = filtros.get("busqueda", "").strip()
    if busqueda:
        consulta = Q()
        for campo in campos:
            if campo.get_internal_type() in ("CharField", "TextField"):
                consulta |= Q(**{f"{campo.name}__icontains": busqueda})
        if consulta:
            registros = registros.filter(consulta)

    periodo = filtros.get("periodo", "").strip()
    if periodo:
        for nombre in ("periodo", "periodo_fiscal", "periodo_vigencia"):
            if nombre in campos_disponibles:
                registros = registros.filter(
                    **{f"{nombre}__icontains": periodo}
                )
                break

    estado = filtros.get("estado", "").strip().lower()
    if estado in ("true", "false") and "estado" in campos_disponibles:
        registros = registros.filter(estado=(estado == "true"))

    relaciones = [
        campo.name
        for campo in campos
        if campo.is_relation and campo.many_to_one
    ]
    if relaciones:
        registros = registros.select_related(*relaciones)

    registros = registros.order_by("pk")
    encabezados = [campo.verbose_name.title() for campo in campos]
    filas = []

    for registro in registros:
        fila = []

        for campo in campos:
            valor = getattr(registro, campo.name)

            if valor is None:
                valor = ""
            elif campo.is_relation and campo.many_to_one:
                valor = str(valor)
            elif isinstance(valor, bool):
                valor = "Sí" if valor else "No"

            fila.append(valor)

        filas.append(fila)

    return encabezados, filas

@login_required
def generar_reporte(request):
    permiso = _tiene_permiso(request)
    if permiso:
        return permiso

    if request.method == "POST":
        form = ReporteForm(request.POST)
        accion = request.POST.get("accion")

        if accion not in ("pdf", "excel"):
            return HttpResponseBadRequest(
                "Seleccione PDF o Excel para generar el reporte."
            )
            
        if form.is_valid():
         
            tipo = form.cleaned_data["tipo"]
            parametros = {
                "busqueda": form.cleaned_data["busqueda"],
                "periodo": form.cleaned_data["periodo"],
                "estado": form.cleaned_data["estado"],
            }

            encabezados, filas = obtener_datos(tipo, parametros)

            if not filas:
                messages.warning(
                    request,
                    "No existe información para los criterios seleccionados."
                )
            else:
                Reporte.objects.create(
                    tipo=tipo,
                    usuario=request.user,
                    parametros=parametros,
                )

                nombre_vista = (
                    "reporte_pdf" if accion == "pdf" else "reporte_excel"
                )
                return redirect(
                    f"{reverse(nombre_vista, kwargs={'tipo': tipo})}"
                    f"?{urlencode(parametros)}"
         
                )
    else:
        
        form = ReporteForm()

    return render(
        
        request,
        
        "reportes/generar_reporte.html",
        {"form": form}
    )


@login_required
def consultar_reportes(request):
    permiso = _tiene_permiso(request)
    if permiso:
        return permiso

    reportes = Reporte.objects.select_related(
        "usuario"
    ).order_by("-fecha_generacion", "-pk")

    tipo = request.GET.get("tipo", "").strip()
    fecha = request.GET.get("fecha", "").strip()
    usuario_id = request.GET.get("usuario", "").strip()

    tipos_validos = {valor for valor, etiqueta in Reporte.TIPO_REPORTE}

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
        }
    )


@login_required
def reporte_pdf(request, tipo):
    permiso = _tiene_permiso(request)
    if permiso:
        
        return permiso

    encabezados, filas = obtener_datos(tipo, request.GET)
    if tipo not in REPORTES and tipo != "Consolidado":
        return HttpResponseBadRequest("El tipo de reporte no es válido.")

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloReporte",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=15,
        leading=18,
        spaceAfter=12,
    )
    estilo_celda = ParagraphStyle(
        "CeldaReporte",
        parent=estilos["BodyText"],
        fontSize=7,
        leading=9,
        wordWrap="CJK",
    )

    tabla_datos = [
        [
            Paragraph(f"<b>{escape(str(valor))}</b>", estilo_celda)
            for valor in encabezados
        ]
    ]

    for fila in filas:
        tabla_datos.append([
            Paragraph(escape(str(valor)), estilo_celda)
            for valor in fila
        ])

    ancho_util = landscape(letter)[0] - 0.7 * inch
    numero_columnas = max(len(encabezados), 1)
    anchos = [ancho_util / numero_columnas] * numero_columnas

    tabla = Table(
        tabla_datos,
        colWidths=anchos,
        repeatRows=1,
        hAlign="LEFT"
    )
    tabla.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C9D6")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#F1F5F9")
            ]),
        ])
    )

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.4 * inch,
        title=f"Reporte de {tipo}",
    )
    documento.build([
        Paragraph(f"Reporte de {escape(tipo)}", estilo_titulo),
        Spacer(1, 4),
        tabla,
    ])

    buffer.seek(0)
    
    return FileResponse(
    
        buffer,
    
        as_attachment=True,
        filename=f"{slugify(tipo)}.pdf",
        content_type="application/pdf",
    )


@login_required
def reporte_excel(request, tipo):
    permiso = _tiene_permiso(request)
    if permiso:
        return permiso

    if tipo not in REPORTES:
        return HttpResponseBadRequest("El tipo de reporte no es válido.")

    encabezados, filas = obtener_datos(tipo, request.GET)

    libro = Workbook(write_only=True)
    hoja = libro.create_sheet(title="Reporte")
    hoja.append(encabezados)

    for fila in filas:
        hoja.append([
            str(valor) if valor is not None else ""
            for valor in fila
        ])

    buffer = BytesIO()
    libro.save(buffer)
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"{slugify(tipo)}.xlsx",
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@login_required
def reporte_consolidado(request):
    permiso = _tiene_permiso(request)
    if permiso:
        return permiso

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
        {"informacion": informacion}
        
    )