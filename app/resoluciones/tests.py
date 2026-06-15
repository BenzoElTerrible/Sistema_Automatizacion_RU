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

class VistoDeResolucionTests(TestCase):

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

        def crear_pdf(nombre):
            return SimpleUploadedFile(
                nombre,
                b"%PDF-1.4 archivo pdf prueba",
                content_type="application/pdf"
            )

        self.ru_principal = ResolucionUniversitaria.objects.create(
            anio=2026, numero_ru=200, seccion_origen="Postgrado",
            tipo=self.tipo, carrera_asociada=self.carrera,
            nombre_generado="test_principal", archivo_pdf=crear_pdf("principal.pdf")
        )

        self.ru_visto_1 = ResolucionUniversitaria.objects.create(
            anio=2024, numero_ru=150, seccion_origen="Finanzas",
            tipo=self.tipo, carrera_asociada=self.carrera,
            nombre_generado="test_visto_1", archivo_pdf=crear_pdf("visto1.pdf")
        )

        self.ru_visto_2 = ResolucionUniversitaria.objects.create(
            anio=2025, numero_ru=180, seccion_origen="Rectoria",
            tipo=self.tipo, carrera_asociada=self.carrera,
            nombre_generado="test_visto_2", archivo_pdf=crear_pdf("visto2.pdf")
        )

    # --- HU: Visualizar vistos ---

    def test_get_vistos_existentes(self):
        self.ru_principal.vistos.set([self.ru_visto_1, self.ru_visto_2])
        response = self.client.get(f"/ru/{self.ru_principal.id}/visto/")
        self.assertEqual(response.status_code, 200)
        ids_retornados = [v["id"] for v in response.data]
        self.assertIn(self.ru_visto_1.id, ids_retornados)
        self.assertIn(self.ru_visto_2.id, ids_retornados)

    def test_get_vistos_sin_vistos_registrados(self):
        response = self.client.get(f"/ru/{self.ru_principal.id}/visto/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_get_vistos_resolucion_no_existente(self):
        response = self.client.get("/ru/9999/visto/")
        self.assertEqual(response.status_code, 404)

    # --- HU: Editar vistos ---

    def test_patch_vistos_exitoso(self):
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {"vistos": [self.ru_visto_1.id, self.ru_visto_2.id]},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(self.ru_principal.vistos.count(), 2)

    def test_patch_vistos_reemplaza_anteriores(self):
        self.ru_principal.vistos.set([self.ru_visto_1, self.ru_visto_2])
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {"vistos": [self.ru_visto_1.id]},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ru_principal.vistos.count(), 1)

    def test_patch_vistos_sin_campo_vistos(self):
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {},
            format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_vistos_ru_no_existente(self):
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {"vistos": [9999]},
            format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_patch_vistos_resolucion_no_existente(self):
        response = self.client.patch(
            "/ru/9999/visto/",
            {"vistos": [self.ru_visto_1.id]},
            format="json"
        )
        self.assertEqual(response.status_code, 404)

class VistoDeResolucionTests(TestCase):

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

        def crear_pdf(nombre):
            return SimpleUploadedFile(
                nombre,
                b"%PDF-1.4 archivo pdf prueba",
                content_type="application/pdf"
            )

        self.ru_principal = ResolucionUniversitaria.objects.create(
            anio=2026, numero_ru=200, seccion_origen="Postgrado",
            tipo=self.tipo, carrera_asociada=self.carrera,
            nombre_generado="test_principal", archivo_pdf=crear_pdf("principal.pdf")
        )

        self.ru_visto_1 = ResolucionUniversitaria.objects.create(
            anio=2024, numero_ru=150, seccion_origen="Finanzas",
            tipo=self.tipo, carrera_asociada=self.carrera,
            nombre_generado="test_visto_1", archivo_pdf=crear_pdf("visto1.pdf")
        )

        self.ru_visto_2 = ResolucionUniversitaria.objects.create(
            anio=2025, numero_ru=180, seccion_origen="Rectoria",
            tipo=self.tipo, carrera_asociada=self.carrera,
            nombre_generado="test_visto_2", archivo_pdf=crear_pdf("visto2.pdf")
        )

    # --- HU: Visualizar vistos ---

    def test_get_vistos_existentes(self):
        self.ru_principal.vistos.set([self.ru_visto_1, self.ru_visto_2])
        response = self.client.get(f"/ru/{self.ru_principal.id}/visto/")
        self.assertEqual(response.status_code, 200)
        ids_retornados = [v["id"] for v in response.data]
        self.assertIn(self.ru_visto_1.id, ids_retornados)
        self.assertIn(self.ru_visto_2.id, ids_retornados)

    def test_get_vistos_sin_vistos_registrados(self):
        response = self.client.get(f"/ru/{self.ru_principal.id}/visto/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_get_vistos_resolucion_no_existente(self):
        response = self.client.get("/ru/9999/visto/")
        self.assertEqual(response.status_code, 404)

    # --- HU: Editar vistos ---

    def test_patch_vistos_exitoso(self):
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {"vistos": [self.ru_visto_1.id, self.ru_visto_2.id]},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(self.ru_principal.vistos.count(), 2)

    def test_patch_vistos_reemplaza_anteriores(self):
        self.ru_principal.vistos.set([self.ru_visto_1, self.ru_visto_2])
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {"vistos": [self.ru_visto_1.id]},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ru_principal.vistos.count(), 1)

    def test_patch_vistos_sin_campo_vistos(self):
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {},
            format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_vistos_ru_no_existente(self):
        response = self.client.patch(
            f"/ru/{self.ru_principal.id}/visto/",
            {"vistos": [9999]},
            format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_patch_vistos_resolucion_no_existente(self):
        response = self.client.patch(
            "/ru/9999/visto/",
            {"vistos": [self.ru_visto_1.id]},
            format="json"
        )
        self.assertEqual(response.status_code, 404)