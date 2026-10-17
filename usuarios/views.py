
import re

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import Usuario, Aula
from .models import Usuario


def registrar_usuario(request):
    if request.method == "POST":
        dni = request.POST.get("dni", "").strip()
        nombres = request.POST.get("nombres", "").strip()
        apellidos = request.POST.get("apellidos", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        correo = request.POST.get("correo", "").strip()
        estado = request.POST.get("estado", "").strip()

        # Validar los datos en el servidor.
        if not re.fullmatch(r"[0-9]{8}", dni):
            messages.error(request, "El DNI debe tener 8 dígitos.")

        elif not re.fullmatch(r"[0-9]{9}", telefono):
            messages.error(request, "El teléfono debe tener 9 dígitos.")

        elif not all([nombres, apellidos, correo]):
            messages.error(request, "Completa todos los campos.")

        elif estado not in ("Director", "Tutor"):
            messages.error(request, "Selecciona un rol válido.")

        elif Usuario.objects.filter(dni=dni).exists():
            messages.error(request, "Este DNI ya está registrado.")

        elif Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya está registrado.")

        else:
            try:
                with transaction.atomic():
                    Usuario.objects.create(
                        dni=dni,
                        nombres=nombres,
                        apellidos=apellidos,
                        telefono=telefono,
                        correo=correo,
                        estado=estado,
                    )

                messages.success(
                    request,
                    "Usuario registrado correctamente."
                )

                return redirect("registrar_usuario")

            except IntegrityError:
                messages.error(
                    request,
                    "El DNI o el correo ya están registrados."
                )

    return render(request, "usuarios/registro.html")


def listado_usuarios(request):
    usuarios = Usuario.objects.all().order_by("apellidos", "nombres")
    aulas = Aula.objects.all().order_by("grado", "seccion")

    aulas_por_usuario = {
        aula.id_usuario: aula
        for aula in aulas
        if aula.id_usuario is not None
    }

    aulas_disponibles = [
        aula for aula in aulas
        if aula.id_usuario is None
    ]

    return render(
        request,
        "usuarios/listado.html",
        {
            "usuarios": usuarios,
            "aulas": aulas,
            "aulas_por_usuario": aulas_por_usuario,
            "aulas_disponibles": aulas_disponibles,
        }
    )

@require_POST
def asignar_aula(request):
    tutor_id = request.POST.get("tutor_id", "").strip()
    aula_id = request.POST.get("aula_id", "").strip()

    if not tutor_id.isdigit() or not aula_id.isdigit():
        messages.error(request, "Selecciona un tutor y un aula válidos.")
        return redirect("listado_usuarios")

    try:
        with transaction.atomic():
            # Bloquear al tutor para evitar asignaciones simultáneas.
            tutor = Usuario.objects.select_for_update().get(
                id_usuario=int(tutor_id)
            )

            if tutor.estado != "Tutor":
                messages.error(
                    request,
                    "Solo los usuarios con rol Tutor pueden tener un aula."
                )
                return redirect("listado_usuarios")

            # Bloquear el aula elegida mientras se valida y asigna.
            aula = Aula.objects.select_for_update().get(
                idaula=int(aula_id)
            )

            # Si pertenece a otro tutor, no permitir la asignación.
            if (
                aula.id_usuario is not None
                and aula.id_usuario != tutor.id_usuario
            ):
                messages.error(
                    request,
                    "Esta aula ya fue asignada a otro tutor."
                )
                return redirect("listado_usuarios")

            # Liberar cualquier aula que tuviera asignada este tutor.
            Aula.objects.filter(
                id_usuario=tutor.id_usuario
            ).exclude(
                idaula=aula.idaula
            ).update(id_usuario=None)

            # Asignar el aula seleccionada.
            Aula.objects.filter(
                idaula=aula.idaula
            ).update(id_usuario=tutor.id_usuario)

        messages.success(
            request,
            f"Se asignó {aula.grado} - {aula.seccion} "
            f"a {tutor.nombres} {tutor.apellidos}."
        )

    except Usuario.DoesNotExist:
        messages.error(request, "El usuario seleccionado no existe.")
    except Aula.DoesNotExist:
        messages.error(request, "El aula seleccionada no existe.")

    return redirect("listado_usuarios")

def listado_aulas(request):
    aulas = Aula.objects.all().order_by("grado", "seccion")

    return render(request, "usuarios/listado_aulas.html", {
        "aulas": aulas,
    })