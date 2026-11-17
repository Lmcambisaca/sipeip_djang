from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.permisos import validar_permiso
from .forms import (InversionForm, ConsultaInversionForm, EditarInversionForm,)
from .models import Inversion, HistorialInversion
import json
import csv
from decimal import Decimal
from django.db.models import Sum
from decimal import Decimal

from django.http import HttpResponse

@login_required
def registrar_inversion(request):
    permiso = validar_permiso(request, "Administrar inversiones")
    if permiso:
        return permiso

    form = InversionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Inversión registrada correctamente.")
        return redirect("consultar_inversiones")

    return render(
        request,
        "inversiones/registrar_inversion.html",
        {"form": form}
    )


@login_required
def consultar_inversiones(request):
    permiso = validar_permiso(request, "Consultar inversiones")
    if permiso:
        return permiso

    formulario = ConsultaInversionForm(request.GET or None)
    inversiones = Inversion.objects.select_related("proyecto").all()

    if formulario.is_valid():
        datos = formulario.cleaned_data

        if datos.get("periodo_fiscal"):
            inversiones = inversiones.filter(
                periodo_fiscal=datos["periodo_fiscal"]
            )

        if datos.get("fuente_financiamiento"):
            inversiones = inversiones.filter(
                fuente_financiamiento__icontains=(
                    datos["fuente_financiamiento"].strip()
                )
            )

        if datos.get("estado") == "true":
            inversiones = inversiones.filter(estado=True)
        elif datos.get("estado") == "false":
            inversiones = inversiones.filter(estado=False)

        if datos.get("proyecto"):
            inversiones = inversiones.filter(proyecto=datos["proyecto"])

        if datos.get("monto_minimo") is not None:
            inversiones = inversiones.filter(
                monto_asignado__gte=datos["monto_minimo"]
            )

        if datos.get("monto_maximo") is not None:
            inversiones = inversiones.filter(
                monto_asignado__lte=datos["monto_maximo"]
            )

    return render(
        request,
        "inversiones/consultar_inversiones.html",
        {
            "formulario": formulario,
            "inversiones": inversiones,
        }
    )
    
@login_required
def editar_inversion(request, id):
    permiso = validar_permiso(request, "Administrar inversiones")
    if permiso:
        return permiso

    inversion = get_object_or_404(
        Inversion.objects.select_related("proyecto"),
        pk=id
    )

    if request.method == "POST":
        valores_anteriores = {
            "monto_asignado": inversion.monto_asignado,
            "fuente_financiamiento": inversion.fuente_financiamiento,
            "estado": inversion.estado,
            "monto_ejecutado": inversion.monto_ejecutado,
        }

        form = EditarInversionForm(
            request.POST,
            instance=inversion
        )

        if form.is_valid():
            cambios = []

            if valores_anteriores["monto_asignado"] != form.cleaned_data["monto_asignado"]:
                cambios.append("Monto asignado actualizado")
                
            if valores_anteriores["monto_ejecutado"] != form.cleaned_data["monto_ejecutado"]:
                cambios.append("Monto ejecutado actualizado")

            if valores_anteriores["fuente_financiamiento"] != form.cleaned_data["fuente_financiamiento"]:
                cambios.append("Fuente de financiamiento actualizada")

            if valores_anteriores["estado"] != form.cleaned_data["estado"]:
                cambios.append("Estado actualizado")

            inversion = form.save()

            if cambios:
                HistorialInversion.objects.create(
                    inversion=inversion,
                    usuario=request.user,
                    accion="; ".join(cambios)
                )

            messages.success(
                request,
                "Inversión actualizada correctamente."
            )
            return redirect("consultar_inversiones")
    else:
        form = EditarInversionForm(instance=inversion)

    return render(
        request,
        "inversiones/editar_inversion.html",
        {
            "form": form,
            "inversion": inversion,
        }
    )
    
@login_required
def seguimiento_inversiones(request):
    permiso = validar_permiso(request, "Consultar inversiones")
    if permiso:
        return permiso

    inversiones = Inversion.objects.select_related(
        "proyecto"
    ).order_by("codigo")

    resumen = inversiones.aggregate(
        total_asignado=Sum("monto_asignado"),
        total_ejecutado=Sum("monto_ejecutado"),
    )

    total_asignado = resumen["total_asignado"] or Decimal("0.00")
    total_ejecutado = resumen["total_ejecutado"] or Decimal("0.00")
    total_pendiente = total_asignado - total_ejecutado

    if total_asignado > 0:
        porcentaje_general = round(
            total_ejecutado / total_asignado * 100,
            2
        )
    else:
        porcentaje_general = 0

    datos_grafico = {
        "etiquetas": [inversion.codigo for inversion in inversiones],
        "asignados": [float(inversion.monto_asignado) for inversion in inversiones],
        "ejecutados": [float(inversion.monto_ejecutado) for inversion in inversiones],
        "pendientes": [float(inversion.monto_pendiente) for inversion in inversiones],
    }

    return render(
        request,
        "inversiones/seguimiento_inversiones.html",
        {
            "inversiones": inversiones,
            "total_asignado": total_asignado,
            "total_ejecutado": total_ejecutado,
            "total_pendiente": total_pendiente,
            "porcentaje_general": porcentaje_general,
            "datos_grafico": datos_grafico,
        }
    )
    
@login_required
def reporte_inversiones(request):
    permiso = validar_permiso(request, "Consultar inversiones")
    if permiso:
        return permiso

    inversiones = Inversion.objects.select_related("proyecto")

    periodo = request.GET.get("periodo", "").strip()
    if periodo.isdigit():
        inversiones = inversiones.filter(periodo_fiscal=int(periodo))
    else:
        periodo = ""

    filas = list(
        inversiones.values(
            "periodo_fiscal",
            "fuente_financiamiento",
            "proyecto__codigo",
            "proyecto__nombre",
        )
        .annotate(
            total_asignado=Sum("monto_asignado"),
            total_ejecutado=Sum("monto_ejecutado"),
        )
        .order_by(
            "periodo_fiscal",
            "fuente_financiamiento",
            "proyecto__nombre",
        )
    )

    for fila in filas:
        asignado = fila["total_asignado"] or Decimal("0.00")
        ejecutado = fila["total_ejecutado"] or Decimal("0.00")

        fila["total_asignado"] = asignado
        fila["total_ejecutado"] = ejecutado
        fila["pendiente"] = asignado - ejecutado
        fila["porcentaje"] = (
            round(ejecutado / asignado * 100, 2)
            if asignado > 0
            else 0
        )

    if request.GET.get("formato") == "csv":
        respuesta = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )
        respuesta["Content-Disposition"] = (
            'attachment; filename="reporte_ejecucion_inversiones.csv"'
        )
        respuesta.write("\ufeff")

        escritor = csv.writer(respuesta, delimiter=";")
        escritor.writerow([
            "Período fiscal",
            "Fuente de financiamiento",
            "Código del proyecto",
            "Proyecto",
            "Monto asignado",
            "Monto ejecutado",
            "Monto pendiente",
            "Porcentaje de ejecución",
        ])

        for fila in filas:
            escritor.writerow([
                fila["periodo_fiscal"],
                fila["fuente_financiamiento"],
                fila["proyecto__codigo"],
                fila["proyecto__nombre"],
                fila["total_asignado"],
                fila["total_ejecutado"],
                fila["pendiente"],
                fila["porcentaje"],
            ])

        return respuesta

    resumen = inversiones.aggregate(
        total_asignado=Sum("monto_asignado"),
        total_ejecutado=Sum("monto_ejecutado"),
    )

    total_asignado = resumen["total_asignado"] or Decimal("0.00")
    total_ejecutado = resumen["total_ejecutado"] or Decimal("0.00")

    return render(
        request,
        "inversiones/reporte_inversiones.html",
        {
            "filas": filas,
            "periodo": periodo,
            "total_asignado": total_asignado,
            "total_ejecutado": total_ejecutado,
            "total_pendiente": total_asignado - total_ejecutado,
        }
    )