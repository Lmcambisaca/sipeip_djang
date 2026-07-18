def rol_usuario(request):

    rol = ""

    if request.user.is_authenticated:

        if hasattr(request.user, "rol") and request.user.rol:

            rol = request.user.rol.nombre

    return {

        "rol": rol

    }