from django.db import models


class TipoPrograma(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Programa"
        verbose_name_plural = "Tipos de Programa"


class TipoRU(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Resolución"
        verbose_name_plural = "Tipos de Resolución"


class CarreraPostgrado(models.Model):
    nombre = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, blank=True)
    tipo_programa = models.ForeignKey(
        TipoPrograma, on_delete=models.PROTECT,
        related_name='carreras', null=True, blank=True
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Carrera de Postgrado"
        verbose_name_plural = "Carreras de Postgrado"


class Visto(models.Model):
    texto = models.TextField()
    tipo_programa = models.ForeignKey(
        TipoPrograma, on_delete=models.CASCADE,
        related_name='vistos'
    )

    def __str__(self):
        return f"Visto [{self.tipo_programa.nombre}]: {self.texto[:50]}"

    class Meta:
        verbose_name = "Visto"
        verbose_name_plural = "Vistos"