
from django.db import models


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)

    dni = models.CharField(
        max_length=8,
        unique=True
    )

    nombres = models.CharField(max_length=100)

    apellidos = models.CharField(max_length=100)

    telefono = models.CharField(max_length=9)

    correo = models.CharField(
        max_length=254,
        unique=True
    )

    ESTADOS = [
        ("Director", "Director"),
        ("Tutor", "Tutor"),
    ]

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS
    )

    class Meta:
        db_table = "usuario"
        managed = False

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.dni}"


    
class Aula(models.Model):
    idaula = models.AutoField(primary_key=True)
    grado = models.CharField(max_length=45)
    seccion = models.CharField(max_length=45)
    id_usuario = models.IntegerField(null=True, blank=True)

    @property
    def tutor(self):
        if self.id_usuario is None:
            return None

        return Usuario.objects.filter(
            id_usuario=self.id_usuario
        ).first()

    class Meta:
        db_table = "aula"
        managed = False

    def __str__(self):
        return f"{self.grado} - {self.seccion}"


