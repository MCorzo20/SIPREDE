
from django.test import TestCase
from django.urls import reverse
from django.db import connection

from .models import Usuario


class PruebasUsuarios(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Crear la tabla en la base de datos de pruebas.
        with connection.schema_editor() as schema:
            schema.create_model(Usuario)

    @classmethod
    def tearDownClass(cls):
        # Eliminar la tabla de la base de datos de pruebas.
        with connection.schema_editor() as schema:
            schema.delete_model(Usuario)

        super().tearDownClass()

    def datos_usuario(self, **cambios):
        datos = {
            "dni": "12345678",
            "nombres": "Juan Carlos",
            "apellidos": "Perez Gomez",
            "telefono": "987654321",
            "correo": "juan@example.com",
            "estado": "Tutor",
        }
        datos.update(cambios)
        return datos

    # ==========================================
    # PRUEBAS DEL REGISTRO
    # ==========================================

    def test_registrar_usuario_correctamente(self):
        respuesta = self.client.post(
            reverse("registrar_usuario"),
            self.datos_usuario()
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(
            Usuario.objects.filter(dni="12345678").exists()
        )

        usuario = Usuario.objects.get(dni="12345678")
        self.assertEqual(usuario.nombres, "Juan Carlos")
        self.assertEqual(usuario.estado, "Tutor")

    def test_no_permitir_dni_duplicado(self):
        Usuario.objects.create(**self.datos_usuario())

        respuesta = self.client.post(
            reverse("registrar_usuario"),
            self.datos_usuario(
                nombres="Maria",
                correo="maria@example.com"
            )
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertContains(respuesta, "DNI ya está registrado")

    def test_no_permitir_correo_duplicado(self):
        Usuario.objects.create(**self.datos_usuario())

        respuesta = self.client.post(
            reverse("registrar_usuario"),
            self.datos_usuario(
                dni="87654321"
            )
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertContains(respuesta, "correo ya está registrado")

    def test_rechazar_dni_invalido(self):
        respuesta = self.client.post(
            reverse("registrar_usuario"),
            self.datos_usuario(dni="123")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)
        self.assertContains(respuesta, "DNI debe tener 8 dígitos")

    def test_rechazar_telefono_invalido(self):
        respuesta = self.client.post(
            reverse("registrar_usuario"),
            self.datos_usuario(telefono="123")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)
        self.assertContains(respuesta, "teléfono debe tener 9 dígitos")

    def test_rechazar_rol_invalido(self):
        respuesta = self.client.post(
            reverse("registrar_usuario"),
            self.datos_usuario(estado="Administrador")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)
        self.assertContains(respuesta, "rol válido")

    # ==========================================
    # PRUEBAS DEL LISTADO
    # ==========================================

    def test_listado_carga_correctamente(self):
        Usuario.objects.create(**self.datos_usuario())

        respuesta = self.client.get(
            reverse("listado_usuarios")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta, "usuarios/listado.html"
        )
        self.assertContains(respuesta, "12345678")
        self.assertContains(respuesta, "Juan Carlos")
        self.assertContains(respuesta, "Perez Gomez")
        self.assertContains(respuesta, "987654321")
        self.assertContains(respuesta, "juan@example.com")
        self.assertContains(respuesta, "Tutor")

    def test_listado_sin_usuarios(self):
        respuesta = self.client.get(
            reverse("listado_usuarios")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta, "No hay usuarios registrados"
        )

    def test_listado_muestra_todos_los_roles(self):
        Usuario.objects.create(**self.datos_usuario())

        Usuario.objects.create(
            **self.datos_usuario(
                dni="87654321",
                nombres="Ana",
                apellidos="Lopez",
                correo="ana@example.com",
                estado="Director",
            )
        )

        respuesta = self.client.get(
            reverse("listado_usuarios")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Tutor")
        self.assertContains(respuesta, "Director")
        self.assertContains(respuesta, "Asignar Aula")

    def test_boton_asignar_aula_se_habilita_solo_para_tutor(self):
        Usuario.objects.create(**self.datos_usuario())

        Usuario.objects.create(
            **self.datos_usuario(
                dni="87654321",
                nombres="Ana",
                apellidos="Lopez",
                correo="ana@example.com",
                estado="Director",
            )
        )

        respuesta = self.client.get(
            reverse("listado_usuarios")
        )

        contenido = respuesta.content.decode()

        # El botón para Tutor debe estar habilitado.
        self.assertIn(
            'class="btn-asignar"',
            contenido
        )

        # El botón para Director debe estar deshabilitado.
        self.assertIn(
            'class="btn-asignar deshabilitado"',
            contenido
        )
        self.assertIn("disabled", contenido)
