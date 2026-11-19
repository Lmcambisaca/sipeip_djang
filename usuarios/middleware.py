import inspect
import json

from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import Resolver404, resolve


class AuditoriaAccionesMiddleware:
    MODULOS = {
        "usuarios": "Usuarios",
        "roles": "Roles",
        "entidades": "Entidades",
        "planificaciones": "Planificaciones",
        "configuracion": "Configuración",
        "proyectos": "Proyectos",
        "metas": "Seguimiento",
        "seguimiento": "Seguimiento",
        "ods": "ODS",
        "objetivosI": "Objetivos institucionales",
        "objetivosE": "Objetivos estratégicos",
        "reportes": "Reportes",
        "inversiones": "Inversiones",
    }

    MODELOS_EDITABLES = {
        "editar_configuracion": ("configuracion", "Configuracion"),
        "editar_entidad": ("entidades", "Entidad"),
        "editar_inversion": ("inversiones", "Inversion"),
        "editar_objetivo_estrategico": (
            "objetivosE",
            "ObjetivoEstrategico",
        ),
        "editar_objetivo_institucional": (
            "objetivosI",
            "ObjetivoInstitucional",
        ),
        "editar_objetivo": ("ods", "ObjetivoDesarrollo"),
        "editar_planificacion": ("planificaciones", "Planificacion"),
        "editar_proyecto": ("proyectos", "Proyecto"),
        "editar_cronograma": ("proyectos", "Cronograma"),
        "editar_rol": ("roles", "Rol"),
        "editar_meta": ("seguimiento", "Meta"),
        "editar_indicador": ("seguimiento", "Indicador"),
        "editar_avance": ("seguimiento", "AvanceIndicador"),
        "editar_usuario": ("usuarios", "Usuario"),
    }

    CAMPOS_SENSIBLES = {
        "password",
        "token",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        datos_cambio = self._capturar_estado_anterior(request)
        response = self.get_response(request)

        if (
            request.method == "POST"
            and response.status_code < 400
            and request.user.is_authenticated
            and request.path != "/"
        ):
            self._guardar_historial_cambio(request, datos_cambio)

            if response.status_code in (301, 302, 303, 307, 308):
                from usuarios.models import AuditoriaSesion

                segmento = request.path.strip("/").split("/")[0]
                modulo = self.MODULOS.get(
                    segmento,
                    segmento.replace("_", " ").title() or "Sistema",
                )

                AuditoriaSesion.objects.create(
                    usuario=request.user,
                    modulo=modulo,
                    accion="Operación registrada",
                    descripcion=(
                        f"Solicitud POST exitosa en la ruta {request.path}"
                    ),
                )

        return response

    def _capturar_estado_anterior(self, request):
        if request.method != "POST" or not request.user.is_authenticated:
            return None

        try:
            coincidencia = resolve(request.path_info)
        except Resolver404:
            return None

        nombre_vista = inspect.unwrap(coincidencia.func).__name__
        configuracion_modelo = self.MODELOS_EDITABLES.get(nombre_vista)

        if not configuracion_modelo:
            return None

        app_label, nombre_modelo = configuracion_modelo
        identificador = (
            coincidencia.kwargs.get("id")
            or coincidencia.kwargs.get("pk")
        )

        if not identificador:
            return None

        modelo = apps.get_model(app_label, nombre_modelo)
        instancia = modelo.objects.filter(pk=identificador).first()

        if instancia is None:
            return None

        return {
            "app_label": app_label,
            "nombre_modelo": nombre_modelo,
            "registro_id": str(instancia.pk),
            "valores_anteriores": self._obtener_valores(instancia),
        }

    def _obtener_valores(self, instancia):
        valores = {}

        for campo in instancia._meta.concrete_fields:
            if campo.primary_key or not campo.editable:
                continue

            if campo.name.lower() in self.CAMPOS_SENSIBLES:
                continue

            valor = getattr(instancia, campo.attname)

            try:
                valor = json.loads(
                    json.dumps(valor, cls=DjangoJSONEncoder)
                )
            except (TypeError, ValueError):
                valor = str(valor) if valor is not None else None

            valores[campo.name] = valor

        return valores

    def _guardar_historial_cambio(self, request, datos_cambio):
        if not datos_cambio:
            return

        app_label = datos_cambio["app_label"]
        nombre_modelo = datos_cambio["nombre_modelo"]
        registro_id = datos_cambio["registro_id"]

        modelo = apps.get_model(app_label, nombre_modelo)
        instancia = modelo.objects.filter(pk=registro_id).first()

        if instancia is None:
            return

        valores_anteriores_completos = datos_cambio["valores_anteriores"]
        valores_nuevos_completos = self._obtener_valores(instancia)

        campos_modificados = [
            campo
            for campo in valores_anteriores_completos
            if valores_anteriores_completos.get(campo)
            != valores_nuevos_completos.get(campo)
        ]

        if not campos_modificados:
            return

        valores_anteriores = {
            campo: valores_anteriores_completos.get(campo)
            for campo in campos_modificados
        }
        valores_nuevos = {
            campo: valores_nuevos_completos.get(campo)
            for campo in campos_modificados
        }

        from usuarios.models import HistorialCambio

        HistorialCambio.objects.create(
            usuario=request.user,
            modulo=self.MODULOS.get(app_label, app_label),
            entidad=nombre_modelo,
            registro_id=registro_id,
            accion="Actualización",
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos,
        )