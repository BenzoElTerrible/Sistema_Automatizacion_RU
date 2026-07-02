import hashlib
from django.db import models
from django.utils import timezone
from apps.base.models import TipoRU, CarreraPostgrado


class ResolucionUniversitaria(models.Model):
    SECCION_CHOICES = [
        ('Rectoria', 'Rectoría'),
        ('Postgrado', 'Postgrado'),
        ('Finanzas', 'Finanzas'),
        ('Otra', 'Otra'),
    ]

    anio = models.IntegerField()
    numero_ru = models.IntegerField()
    fecha_resolucion = models.DateField(null=True, blank=True)
    seccion_origen = models.CharField(max_length=20, choices=SECCION_CHOICES)
    tipo = models.ForeignKey(TipoRU, on_delete=models.PROTECT, related_name='resoluciones')
    carrera_asociada = models.ForeignKey(CarreraPostgrado, on_delete=models.PROTECT, related_name='resoluciones')
    nombre_generado = models.CharField(max_length=300, blank=True)
    archivo_pdf = models.FileField(upload_to='resoluciones/')
    hash_sha256 = models.CharField(max_length=64, blank=True)
    tamanio_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_generado

    def delete(self, *args, **kwargs):
        if self.archivo_pdf:
            self.archivo_pdf.delete(save=False)
        super().delete(*args, **kwargs)

    def calcular_hash_archivo_guardado(self):
        sha256 = hashlib.sha256()

        with self.archivo_pdf.open("rb") as archivo:
            for bloque in iter(lambda: archivo.read(8192), b""):
                sha256.update(bloque)

        return sha256.hexdigest()

    def archivo_esta_integro(self):
        if not self.archivo_pdf or not self.hash_sha256:
            return False

        mismo_hash = self.calcular_hash_archivo_guardado() == self.hash_sha256
        mismo_tamanio = self.archivo_pdf.size == self.tamanio_bytes

        return mismo_hash and mismo_tamanio
    class Meta:
        verbose_name = "Resolución Universitaria"
        verbose_name_plural = "Resoluciones Universitarias"


class NombramientoDirector(models.Model):
    resolucion = models.OneToOneField(
        ResolucionUniversitaria,
        on_delete=models.CASCADE,
        related_name="nombramiento_director"
    )
    nombre_director = models.CharField(max_length=200)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField()

    def esta_vigente(self):
        return self.fecha_vencimiento >= timezone.localdate()

    def __str__(self):
        return f"{self.nombre_director} - vence {self.fecha_vencimiento}"

    class Meta:
        verbose_name = "Nombramiento de Director"
        verbose_name_plural = "Nombramientos de Directores"