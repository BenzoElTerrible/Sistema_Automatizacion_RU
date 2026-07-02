from django.utils import timezone
from urllib import request

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.generic import TemplateView, View
from django.http import HttpResponse

from .models import ResolucionUniversitaria, NombramientoDirector
from .serializers import ResolucionUniversitariaSerializer
from apps.base.models import TipoRU, CarreraPostgrado

import zipfile
from io import BytesIO


# ══════════════════════════════════════════════════════
# MÓDULO REPOSITORIO — Gestión del inventario de RU
# Modelos: ResolucionUniversitaria
# Templates: ru_gestion.html
# ══════════════════════════════════════════════════════

class ResolucionUniversitariaCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResolucionUniversitariaSerializer(data=request.data)

        if serializer.is_valid():
            ru = serializer.save()

            if not ru.archivo_esta_integro():
                ru.delete()
                return Response(
                    {"error": "El archivo no se guardó correctamente. Intenta subirlo nuevamente."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
            tipo_nombre = ru.tipo.nombre.lower()


            if "director" in tipo_nombre:
                nombre_director = request.data.get("nombre_director")
                fecha_inicio = request.data.get("fecha_inicio_director") or None
                fecha_vencimiento = request.data.get("fecha_vencimiento_director")

                if not nombre_director or not fecha_vencimiento:
                    ru.delete()
                    return Response(
                        {"error": "Para una RU de nombramiento de director debes ingresar nombre del director y fecha de vencimiento."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                NombramientoDirector.objects.create(
                    resolucion=ru,
                    nombre_director=nombre_director,
                    fecha_inicio=fecha_inicio,
                    fecha_vencimiento=fecha_vencimiento,
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("ERRORES SERIALIZER:", serializer.errors)
        print("DATA RECIBIDA:", request.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResolucionUniversitariaListView(APIView):
    def get(self, request):
        resoluciones = ResolucionUniversitaria.objects.all()
        serializer = ResolucionUniversitariaSerializer(resoluciones, many=True)
        return Response(serializer.data)


class ResolucionUniversitariaDetailView(APIView):
    def get(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response({"error": "La resolución no existe"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResolucionUniversitariaSerializer(resolucion)
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response({"error": "No existe"}, status=status.HTTP_404_NOT_FOUND)
        resolucion.delete()
        return Response({"message": "Eliminado."}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response({"error": "No existe"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResolucionUniversitariaSerializer(resolucion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResolucionGestionView(TemplateView):
    template_name = "repositorio/ru_gestion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resoluciones"] = ResolucionUniversitaria.objects.all().order_by("fecha_subida")
        context["tipos"] = TipoRU.objects.all()
        context["carreras"] = CarreraPostgrado.objects.all()
        return context


class RUHistoricasPorCarreraView(APIView):
    def get(self, request, carrera_id):
        resoluciones = ResolucionUniversitaria.objects.filter(
            carrera_asociada_id=carrera_id
        ).select_related(
            "tipo",
            "carrera_asociada",
            "nombramiento_director"
        ).order_by("-fecha_subida")

        data = []
        for ru in resoluciones:
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            fecha = ru.fecha_resolucion
            fecha_larga = f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"

            tipo_nombre = ru.tipo.nombre.lower()
            nombramiento = None

            if "director" in tipo_nombre:
                try:
                    nombramiento = ru.nombramiento_director
                except NombramientoDirector.DoesNotExist:
                    continue

                if nombramiento.fecha_vencimiento < timezone.localdate():
                    continue


            if "creación" in tipo_nombre or "creacion" in tipo_nombre:
                accion = "la creación"
            elif "modificación" in tipo_nombre or "modificacion" in tipo_nombre:
                accion = "la modificación"
            else:
                accion = tipo_nombre

            tipo_nombre = ru.tipo.nombre.lower()

            if "creación" in tipo_nombre or "creacion" in tipo_nombre:
                accion = "la creación"
            elif "ingreso" in tipo_nombre:
                accion = "el ingreso"
            elif "modificación" in tipo_nombre or "modificacion" in tipo_nombre:
                accion = "la modificación"
            elif "director" in tipo_nombre:
                accion = "el nombramiento de director"
            else:
                accion = tipo_nombre

            if "director" in tipo_nombre and hasattr(ru, "nombramiento_director"):
                nombramiento = ru.nombramiento_director

            if "director" in tipo_nombre and nombramiento is not None:
                considerando = (
                    f"Que, por la R.U. N° {ru.numero_ru} de fecha {fecha_larga}, "
                    f"se aprueba el nombramiento de {nombramiento.nombre_director} "
                    f"como Director/a del Programa de {ru.carrera_asociada.nombre}."
                )
            elif "modificación" in tipo_nombre or "modificacion" in tipo_nombre:
                considerando = (
                    f"Que, por la R.U. N° {ru.numero_ru} de fecha {fecha_larga}, "
                    f"se aprueba {accion} al Programa de {ru.carrera_asociada.nombre}."
                )
            else:
                considerando = (
                    f"Que, por la R.U. N° {ru.numero_ru} de fecha {fecha_larga}, "
                    f"se aprueba {accion} del Programa de {ru.carrera_asociada.nombre}."
                )

            data.append({
                "id": ru.id,
                "numero_ru": ru.numero_ru,
                "fecha": fecha_larga,
                "tipo": ru.tipo.nombre,
                "carrera": ru.carrera_asociada.nombre,
                "considerando": considerando,
                "archivo_pdf": ru.archivo_pdf.url if ru.archivo_pdf else None,
            })
        return Response(data, status=status.HTTP_200_OK)


class DescargarRespaldosRUZipView(View):
    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('ru_ids')
        if not ids:
            return HttpResponse("No se seleccionaron RU históricas.", status=400)

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            resoluciones = ResolucionUniversitaria.objects.filter(id__in=ids)
            for ru in resoluciones:
                if not ru.archivo_pdf:
                    continue
                nombre_archivo = f"RU_{ru.numero_ru}_{ru.anio}.pdf"
                try:
                    zip_file.write(ru.archivo_pdf.path, nombre_archivo)
                except FileNotFoundError:
                    continue

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="respaldos_ru.zip"'
        return response
    
def verificar_integridad(self):
    if not self.archivo_pdf or not self.hash_sha256:
        return False

    sha256 = hashlib.sha256()

    with self.archivo_pdf.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(8192), b""):
            sha256.update(bloque)

    return sha256.hexdigest() == self.hash_sha256