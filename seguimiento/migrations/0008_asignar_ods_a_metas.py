import re

from django.db import migrations


PATRON_META = re.compile(
    r"^\s*(\d{1,2})\s*\.\s*(?:\d+|[a-z])",
    re.IGNORECASE,
)
PATRON_CODIGO_ODS = re.compile(r"(\d+)$")


def asignar_ods_a_metas(apps, schema_editor):
    Meta = apps.get_model("seguimiento", "Meta")
    ObjetivoDesarrollo = apps.get_model("ods", "ObjetivoDesarrollo")
    db_alias = schema_editor.connection.alias

    ods_por_numero = {}
    errores = []

    objetivos = ObjetivoDesarrollo.objects.using(db_alias).only(
        "pk",
        "codigo",
    )

    for objetivo in objetivos.iterator():
        coincidencia = PATRON_CODIGO_ODS.search(objetivo.codigo or "")

        if not coincidencia:
            continue

        numero = int(coincidencia.group(1))

        if numero in ods_por_numero:
            errores.append(
                f"Hay más de un ODS con el número {numero:03d}."
            )
        else:
            ods_por_numero[numero] = objetivo.pk

    asignaciones = []

    metas = Meta.objects.using(db_alias).filter(
        objetivo_desarrollo__isnull=True
    ).only(
        "pk",
        "descripcion",
        "proyecto_id",
    )

    for meta in metas.iterator():
        coincidencia = PATRON_META.match(meta.descripcion or "")

        if not coincidencia:
            errores.append(
                f"Meta {meta.pk}: la descripción no empieza con un "
                "código como 1.1 o 1.a."
            )
            continue

        numero_ods = int(coincidencia.group(1))
        objetivo_id = ods_por_numero.get(numero_ods)

        if objetivo_id is None:
            errores.append(
                f"Meta {meta.pk}: no se encontró el ODS-{numero_ods:03d}."
            )
            continue

        asignaciones.append(
            (meta.pk, objetivo_id, meta.proyecto_id)
        )

    if errores:
        detalle = "\n".join(errores[:30])
        raise RuntimeError(
            "No se pudieron asociar todas las metas a sus ODS. "
            "No se guardaron asignaciones. Detalles:\n"
            f"{detalle}"
        )

    for meta_id, objetivo_id, proyecto_id in asignaciones:
        Meta.objects.using(db_alias).filter(pk=meta_id).update(
            objetivo_desarrollo_id=objetivo_id
        )

        objetivo = ObjetivoDesarrollo.objects.using(db_alias).get(
            pk=objetivo_id
        )
        objetivo.proyectos.add(proyecto_id)


class Migration(migrations.Migration):
    dependencies = [
        ("ods", "0004_historialobjetivo"),
        ("seguimiento", "0007_meta_objetivo_desarrollo"),
    ]

    operations = [
        migrations.RunPython(
            asignar_ods_a_metas,
            migrations.RunPython.noop,
        ),
    ]