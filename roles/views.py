from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .decorators import permiso_requerido
from .models import Rol, Permiso
from .forms import RolForm
from usuarios.permisos import validar_permiso

from django.contrib.auth.decorators import login_required
@login_required
def registrar_rol(request):
    
    permiso = validar_permiso(
    request,
    "Administrar roles"
    )

    if permiso:
        return permiso

    if request.method == "POST":

        form = RolForm(request.POST)

        if form.is_valid():

            nombre = form.cleaned_data["nombre"].strip()
            descripcion = form.cleaned_data["descripcion"].strip()

            # Validar nombre obligatorio
            if not nombre:
                messages.error(request, "El nombre es obligatorio.")
                return render(request, "roles/registrar_rol.html", {"form": form})

            # Validar descripción obligatoria
            if not descripcion:
                messages.error(request, "La descripción es obligatoria.")
                return render(request, "roles/registrar_rol.html", {"form": form})

            # Validar nombre duplicado
            if Rol.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, "Ya existe un rol con ese nombre.")
                return render(request, "roles/registrar_rol.html", {"form": form})

            form.save()

            messages.success(request, "Rol registrado correctamente.")

            return redirect("consultar_roles")

    else:

        form = RolForm()

    return render(request, "roles/registrar_rol.html", {
        "form": form
    })

@login_required
def consultar_roles(request):
    
    permiso = validar_permiso(
    request,
    "Administrar roles"
    )

    if permiso:
        return permiso

    buscar = request.GET.get("buscar", "")

    if buscar:

        roles = Rol.objects.filter(nombre__icontains=buscar)

    else:

        roles = Rol.objects.all()

    return render(request, "roles/consultar_rol.html", {
        "roles": roles
    })

@login_required
def editar_rol(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar roles"
    )

    if permiso:
        return permiso

    rol = Rol.objects.filter(id=id).first()

    if not rol:
        messages.error(request, "El rol solicitado no existe.")
        return redirect("consultar_roles")

    if request.method == "POST":

        form = RolForm(request.POST, instance=rol)

        if form.is_valid():

            nombre = form.cleaned_data["nombre"].strip()
            descripcion = form.cleaned_data["descripcion"].strip()

            if not nombre:
                messages.error(request, "El nombre es obligatorio.")
                return render(request, "roles/editar_rol.html", {
                    "form": form,
                    "rol": rol
                })

            if not descripcion:
                messages.error(request, "La descripción es obligatoria.")
                return render(request, "roles/editar_rol.html", {
                    "form": form,
                    "rol": rol
                })

            existe = Rol.objects.filter(
                nombre__iexact=nombre
            ).exclude(id=id)

            if existe.exists():

                messages.error(request, "Ya existe otro rol con ese nombre.")

            else:

                form.save()

                messages.success(request, "Rol actualizado correctamente.")

                return redirect("consultar_roles")

    else:

        form = RolForm(instance=rol)

    return render(request, "roles/editar_rol.html", {
        "form": form,
        "rol": rol
    })
    
@login_required
@permiso_requerido("Eliminar Rol")
def eliminar_rol(request, id):
    
    permiso = validar_permiso(
    request,
    "Administrar roles"
    )

    if permiso:
        return permiso

    rol = Rol.objects.filter(id=id).first()

    if not rol:
        messages.error(request, "El rol solicitado no existe.")
        return redirect("consultar_roles")

    if rol.usuarios.filter(estado=True).exists():

        messages.error(
            request,
            "No se puede eliminar el rol porque está asignado a usuarios activos."
        )

        return redirect("consultar_roles")
    else:

        rol.delete()

        messages.success(
            request,
            "Rol eliminado correctamente."
        )

    return redirect("consultar_roles")

@login_required
def asignar_permiso(request, id):
    
    permiso = validar_permiso(
    request,
    "Asignar permisos"
    )

    if permiso:
        return permiso

    rol = Rol.objects.filter(id=id).first()

    if not rol:
        messages.error(request, "El rol solicitado no existe.")
        return redirect("consultar_roles")

    permisos = Permiso.objects.filter(estado=True)

    if request.method == "POST":

        seleccionados = request.POST.getlist("permisos")

        if not seleccionados:

            messages.error(
                request,
                "Debe seleccionar al menos un permiso."
            )

            return redirect(
                "asignar_permiso",
                id=id
            )

        permisos_actuales = list(
            rol.permisos.values_list("id", flat=True)
        )

        nuevos = list(map(int, seleccionados))

        if permisos_actuales == nuevos:

            messages.info(
                request,
                "El rol ya posee esos permisos."
            )

        else:

            rol.permisos.set(seleccionados)

            messages.success(
                request,
                "Permisos actualizados correctamente."
            )

        return redirect("consultar_roles")

    return render(
        request,
        "roles/asignar_permiso.html",
        {
            "rol": rol,
            "permisos": permisos
        }
    )

