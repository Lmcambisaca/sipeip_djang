from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def tiene_permiso(context, nombre_permiso):

    request = context["request"]

    if not request.user.is_authenticated:
        return False

    if (
        request.user.rol
        and request.user.rol.nombre == "Administrador del Sistema"
    ):
        return True

    if not request.user.rol:
        return False

    return request.user.rol.permisos.filter(
        nombre__iexact=nombre_permiso.strip(),
        estado=True
    ).exists()