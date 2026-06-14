from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from .models import (
    ResolucionUniversitaria,
    TipoRU,
    CarreraPostgrado
)


class ResolucionUniversitariaTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.tipo = TipoRU.objects.create(
            nombre="Decreto",
            sigla="DEC"
        )

        self.carrera = CarreraPostgrado.objects.create(
            nombre="Magister Salud",
            sigla="MS"
        )

    def crear_pdf(self):
        return SimpleUploadedFile(
            "archivo.pdf",
            b"%PDF-1.4 archivo pdf prueba",
            content_type="application/pdf"
        )

    def test_crear_modelo_ru(self):

        ru = ResolucionUniversitaria.objects.create(
            anio=2026,
            numero_ru=123,
            seccion_origen="Postgrado",
            tipo=self.tipo,
            carrera_asociada=self.carrera,
            nombre_generado="test",
            archivo_pdf=self.crear_pdf()
        )

        self.assertEqual(
            ResolucionUniversitaria.objects.count(),
            1
        )

        self.assertEqual(ru.anio, 2026)

    def test_post_ru(self):

        data = {
            "anio": 2026,
            "numero_ru": 555,
            "seccion_origen": "Postgrado",
            "tipo": self.tipo.id,
            "carrera_asociada": self.carrera.id,
            "archivo_pdf": self.crear_pdf()
        }

        response = self.client.post(
            "/ru/",
            data,
            format="multipart"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            ResolucionUniversitaria.objects.count(),
            1
        )

    def test_get_ru_list(self):

        ResolucionUniversitaria.objects.create(
            anio=2026,
            numero_ru=999,
            seccion_origen="Finanzas",
            tipo=self.tipo,
            carrera_asociada=self.carrera,
            nombre_generado="test",
            archivo_pdf=self.crear_pdf()
        )

        response = self.client.get("/ru/list/")

        self.assertEqual(response.status_code, 200)

    def test_delete_ru(self):

        ru = ResolucionUniversitaria.objects.create(
            anio=2026,
            numero_ru=888,
            seccion_origen="Otra",
            tipo=self.tipo,
            carrera_asociada=self.carrera,
            nombre_generado="test",
            archivo_pdf=self.crear_pdf()
        )

        response = self.client.delete(f"/ru/{ru.id}/")

        self.assertEqual(response.status_code, 204)

        self.assertEqual(
            ResolucionUniversitaria.objects.count(),
            0
        )