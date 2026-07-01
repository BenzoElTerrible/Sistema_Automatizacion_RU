from django.db import models
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
    seccion_origen = models.CharField(max_length=20, choices=SECCION_CHOICES)
    tipo = models.ForeignKey(TipoRU, on_delete=models.PROTECT, related_name='resoluciones')
    carrera_asociada = models.ForeignKey(CarreraPostgrado, on_delete=models.PROTECT, related_name='resoluciones')
    nombre_generado = models.CharField(max_length=300, blank=True)
    archivo_pdf = models.FileField(upload_to='resoluciones/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_generado

    def delete(self, *args, **kwargs):
        if self.archivo_pdf:
            self.archivo_pdf.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Resolución Universitaria"
        verbose_name_plural = "Resoluciones Universitarias"