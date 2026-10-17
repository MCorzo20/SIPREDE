
from django.urls import path
from . import views

urlpatterns = [
    path("", views.registrar_usuario, name="registrar_usuario"),
    path(
        "usuarios/listado/",
        views.listado_usuarios,
        name="listado_usuarios"
    ),
    path(
        "usuarios/asignar-aula/",
        views.asignar_aula,
        name="asignar_aula"
    ),
    path(
    "usuarios/aulas/",
    views.listado_aulas,
    name="listado_aulas"
),
]