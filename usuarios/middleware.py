
class AuditoriaAccionesMiddleware:
    MODULOS = {
        "usuarios": "Usuarios",
        "roles": "Roles",
        "entidades": "Entidades",
        "planificaciones": "Planificaciones",
        "configuracion": "Configuración",
        "proyectos": "Proyectos",
        "metas": "Seguimiento",
        "ods": "ODS",
        "objetivosI": "Objetivos institucionales",
        "objetivosE": "Objetivos estratégicos",
        "reportes": "Reportes",
        "inversiones": "Inversiones",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        es_redireccion_exitosa = response.status_code in (
            301, 302, 303, 307, 308
        )

        if (
            request.method == "POST"
            and es_redireccion_exitosa
            and request.user.is_authenticated
            and request.path != "/"
        ):
            segmento = request.path.strip("/").split("/")[0]
            modulo = self.MODULOS.get(
                segmento,
                segmento.replace("_", " ").title() or "Sistema"
            )
        
            from usuarios.models import AuditoriaSesion
            AuditoriaSesion.objects.create(
                usuario=request.user,
                modulo=modulo,
                accion="Operación registrada",
                descripcion=(
                    f"Solicitud POST exitosa en la ruta {request.path}"
                )
            )

        return response