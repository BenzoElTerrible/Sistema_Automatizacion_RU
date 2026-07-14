from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date, timedelta

from apps.base.models import TipoRU, TipoPrograma, CarreraPostgrado
from apps.repositorio.models import ResolucionUniversitaria, NombramientoDirector
from apps.repositorio.serializers import obtener_etiqueta, ResolucionUniversitariaSerializer

"""
    En este test, se evaluará potencialmente tres cosas y de ahi decidir cual es mejor.
    1. (funcion) obtener_etiqueta() que esta en repositorio/serializers.py la cual genera el nombre descriptivo de una RU creada
    
    2. (funcion) validate_archivo_pdf(), osea, que el pdf que se ingrese sea efectivamente un pdf apartir de tres "filtros", 
    el primero, que tenga extension .pdf; el segundo, que tenga un content-type de application/pdf; tercero, que el archivo 
    tenga un header que empieze con %PDF
    
    3. (funcion) esta_vigente() en repositorio/models.py. CUando subes RU de tipo "NOmbramientoDIrector" el sistema guarda el nombre
    del director y su fecha dew vencimiento en NOmbramientoDirector y esta_vigente() compara la fecha de vencimiento con la fecha actual. 

    Creo que los dos primeros ya estaban en el sprint 1 con los avances posteriores quedaron obsoletos. Pero el tercero es un 
    test nuevo por si la condición para este sprint 3 era testear una funcion nunca antes testeada y por eso escogi la funcion
    (3) "esta_vigente()" que se creo en el sprint 3.

"""


# ===============================================================================
# Test para la funcion: obtener_etiqueta()
# esta en serializers.py y su funcion es generar el nombre estandarizado de
# cada RU. Un error aqui afectaria la identificacion de todos los
# documentos del sistema por lo cual es importante testearlo.
# ===============================================================================

class ObtenerEtiquetaTests(TestCase):

    def test_retorna_sigla_cuando_existe(self):
        """Caso esperado: si el objeto tiene sigla, la retorna directamente."""
        tipo = TipoRU(nombre="Nombramiento de Director", sigla="ND")
        self.assertEqual(obtener_etiqueta(tipo), "ND")

    def test_genera_etiqueta_desde_nombre_sin_sigla(self):
        """Caso esperado: sin sigla, genera etiqueta normalizando el nombre."""
        tipo = TipoRU(nombre="Creacion de Programa", sigla="")
        resultado = obtener_etiqueta(tipo)
        self.assertEqual(resultado, "Creacion_de_Programa")

    def test_elimina_tildes_del_nombre(self):
        """Caso límite: nombres con tildes deben normalizarse correctamente."""
        tipo = TipoRU(nombre="Modificación de Programa", sigla="")
        resultado = obtener_etiqueta(tipo)
        self.assertNotIn("ó", resultado)
        self.assertIn("Modificacion", resultado)

    def test_sigla_vacia_usa_nombre(self):
        """Caso límite: sigla vacía debe usar nombre como fallback."""
        tipo = TipoRU(nombre="Ingreso de Estudiantes", sigla="")
        resultado = obtener_etiqueta(tipo)
        self.assertIsNotNone(resultado)
        self.assertGreater(len(resultado), 0)

    def test_nombre_con_espacios_usa_guion_bajo(self):
        """Caso límite: los espacios del nombre deben convertirse en _"""
        tipo = TipoRU(nombre="Otro Tipo", sigla="")
        resultado = obtener_etiqueta(tipo)
        self.assertNotIn(" ", resultado)
        self.assertIn("_", resultado)

# ===============================================================================
# testear la funcion validate_archivo_pdf()
# Metodo en el serializer que valida que el archivo subido sea un
# PDF real. Una validacion incorrecta permitiria subir archivos
# corruptos o maliciosos disfrazados de PDF. seguridad y calidad
# ===============================================================================

class ValidacionPDFTests(TestCase):

    """ 
        crear/instancia el TipoRU, TipoPrograma y CarreraPostgrado
    """
    def setUp(self):
        self.tipo = TipoRU.objects.create(nombre="Nombramiento de Director", sigla="ND")
        self.tipo_programa = TipoPrograma.objects.create(nombre="Magíster")
        self.carrera = CarreraPostgrado.objects.create(
            nombre="Magíster en Derecho",
            sigla="MD",
            tipo_programa=self.tipo_programa
        )

    """
        arma el diccionario con todos los campos que el serializer necesita ¿hace todos los del modelo o solo los que el serializer necesita?
    """
    def crear_data(self, archivo):
        return {
            "anio": 2026,
            "numero_ru": 1,
            "fecha_resolucion": "2026-01-15",
            "seccion_origen": "Postgrado",
            "tipo": self.tipo.id,
            "carrera_asociada": self.carrera.id,
            "archivo_pdf": archivo,
        }


    def test_pdf_valido_es_aceptado(self):
        archivo = SimpleUploadedFile("archivo.pdf", b"%PDF-1.4 contenido", content_type="application/pdf")
        serializer = ResolucionUniversitariaSerializer(data=self.crear_data(archivo))
        self.assertTrue(serializer.is_valid())

    def test_archivo_sin_extension_pdf_es_rechazado(self):
        """Entrada inválida: archivo con extensión .txt debe ser rechazado."""
        archivo = SimpleUploadedFile("documento.txt", b"%PDF-1.4 contenido", content_type="application/pdf")
        serializer = ResolucionUniversitariaSerializer(data=self.crear_data(archivo))
        self.assertFalse(serializer.is_valid())
        self.assertIn("archivo_pdf", serializer.errors)

    def test_archivo_con_content_type_incorrecto_es_rechazado(self):
        """Entrada inválida: content-type que no sea application/pdf debe ser rechazado."""
        archivo = SimpleUploadedFile("archivo.pdf", b"%PDF-1.4 contenido", content_type="text/plain")
        serializer = ResolucionUniversitariaSerializer(data=self.crear_data(archivo))
        self.assertFalse(serializer.is_valid())
        self.assertIn("archivo_pdf", serializer.errors)

    def test_archivo_sin_header_pdf_es_rechazado(self):
        """Entrada inválida: archivo .pdf pero sin header %PDF debe ser rechazado."""
        archivo = SimpleUploadedFile("falso.pdf", b"esto no es un pdf real", content_type="application/pdf")
        serializer = ResolucionUniversitariaSerializer(data=self.crear_data(archivo))
        self.assertFalse(serializer.is_valid())
        self.assertIn("archivo_pdf", serializer.errors)


# ===============================================================================
# test para esta_vigente() en NombramientoDIrector
# Metodo que esta en models.py de repositorio. Determina si un director esta vigente
# segun su fecha de vencimiento. Un error aqui mostraria directores
# vencidos como activos en el sistema.
# ===============================================================================

class VigenciaDirectorTests(TestCase):

    def setUp(self):
        self.tipo = TipoRU.objects.create(nombre="Nombramiento de Director", sigla="ND")
        self.tipo_programa = TipoPrograma.objects.create(nombre="Doctorado")
        self.carrera = CarreraPostgrado.objects.create(
            nombre="Doctorado en Ingeniería",
            sigla="DI",
            tipo_programa=self.tipo_programa
        )
        self.ru = ResolucionUniversitaria.objects.create(
            anio=2026,
            numero_ru=100,
            fecha_resolucion=date(2026, 1, 1),
            seccion_origen="Postgrado",
            tipo=self.tipo,
            carrera_asociada=self.carrera,
            nombre_generado="test_ru",
            archivo_pdf=SimpleUploadedFile("test.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        )

    def test_director_con_vencimiento_futuro_esta_vigente(self):
        """Caso esperado: director que vence en el futuro debe estar vigente."""
        nombramiento = NombramientoDirector.objects.create(
            resolucion=self.ru,
            nombre_director="Dr. Juan Pérez",
            fecha_inicio=date(2026, 1, 1),
            fecha_vencimiento=timezone.localdate() + timedelta(days=365)
        )
        self.assertTrue(nombramiento.esta_vigente())

    def test_director_con_vencimiento_hoy_esta_vigente(self):
        """Caso límite: director que vence hoy debe considerarse vigente."""
        nombramiento = NombramientoDirector.objects.create(
            resolucion=self.ru,
            nombre_director="Dra. María González",
            fecha_inicio=date(2026, 1, 1),
            fecha_vencimiento=timezone.localdate()
        )
        self.assertTrue(nombramiento.esta_vigente())

    def test_director_con_vencimiento_pasado_no_esta_vigente(self):
        """Caso esperado: director cuyo vencimiento ya pasó no debe estar vigente."""
        nombramiento = NombramientoDirector.objects.create(
            resolucion=self.ru,
            nombre_director="Dr. Carlos López",
            fecha_inicio=date(2023, 1, 1),
            fecha_vencimiento=date(2024, 12, 31)
        )
        self.assertFalse(nombramiento.esta_vigente())

    def test_director_que_vence_maniana_esta_vigente(self):
        """Caso límite: director que vence mañana debe estar vigente."""
        nombramiento = NombramientoDirector.objects.create(
            resolucion=self.ru,
            nombre_director="Dr. Pedro Soto",
            fecha_inicio=date(2026, 1, 1),
            fecha_vencimiento=timezone.localdate() + timedelta(days=1)
        )
        self.assertTrue(nombramiento.esta_vigente())

    def test_director_que_vencio_ayer_no_esta_vigente(self):
        """Caso límite: director que venció ayer no debe estar vigente."""
        nombramiento = NombramientoDirector.objects.create(
            resolucion=self.ru,
            nombre_director="Dra. Ana Muñoz",
            fecha_inicio=date(2023, 1, 1),
            fecha_vencimiento=timezone.localdate() - timedelta(days=1)
        )
        self.assertFalse(nombramiento.esta_vigente())