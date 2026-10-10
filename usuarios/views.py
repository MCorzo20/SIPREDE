
import re

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError, transaction

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
