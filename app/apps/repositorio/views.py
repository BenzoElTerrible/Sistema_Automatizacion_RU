from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.generic import TemplateView, View
from django.http import HttpResponse

from .models import ResolucionUniversitaria
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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        ).select_related("tipo", "carrera_asociada").order_by("-fecha_subida")

        data = []
        for ru in resoluciones:
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            fecha = ru.fecha_subida
            fecha_larga = f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"
            considerando = (
                f"Que, por la R.U. N° {ru.numero_ru} de fecha {fecha_larga}, "
                f"se aprueba {ru.tipo.nombre.lower()} del Programa de {ru.carrera_asociada.nombre}."
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