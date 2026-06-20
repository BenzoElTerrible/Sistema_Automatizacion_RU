from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import ResolucionUniversitariaSerializer
from .models import ResolucionUniversitaria, TipoRU, CarreraPostgrado, TipoPrograma, Visto

from django.views.generic import TemplateView


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
    template_name = "resoluciones/ru_gestion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resoluciones"] = ResolucionUniversitaria.objects.all().order_by("fecha_subida")
        context["tipos"] = TipoRU.objects.all()
        context["carreras"] = CarreraPostgrado.objects.all()
        return context


""" S2.1 para devolver los vistos (textos) asociados a una resolución específica, 
a través de su carrera → tipo_programa → vistos. Solamente lo pongo porque lo pide
en una historia de usuario. Es el icono de ojo para ver los vistos en GestionRU y 
el unico que se relaciona con (ru_gestion.html) de los views relacionados a vistos.
"""
class VistosDeRUView(APIView):
    def get(self, request, pk):
        try:
            ru = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response({"error": "No existe"}, status=status.HTTP_404_NOT_FOUND)

        tipo_programa = ru.carrera_asociada.tipo_programa
        if not tipo_programa:
            return Response([], status=status.HTTP_200_OK)

        vistos = tipo_programa.vistos.all().values('id', 'texto', 'tipo_programa__nombre')
        return Response(list(vistos), status=status.HTTP_200_OK)


# CRUD de Vistos (para ru_vistos.html)
class VistoListCreateView(APIView):
    def get(self, request):
        tipo_programa_id = request.query_params.get('tipo_programa')
        if tipo_programa_id:
            vistos = Visto.objects.filter(tipo_programa_id=tipo_programa_id).values('id', 'texto', 'tipo_programa_id', 'tipo_programa__nombre')
        else:
            vistos = Visto.objects.all().values('id', 'texto', 'tipo_programa_id', 'tipo_programa__nombre')
        return Response(list(vistos))

    def post(self, request):
        texto = request.data.get('texto')
        tipo_programa_id = request.data.get('tipo_programa')
        if not texto or not tipo_programa_id:
            return Response({"error": "Faltan campos."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tp = TipoPrograma.objects.get(pk=tipo_programa_id)
        except TipoPrograma.DoesNotExist:
            return Response({"error": "TipoPrograma no existe."}, status=status.HTTP_404_NOT_FOUND)
        visto = Visto.objects.create(texto=texto, tipo_programa=tp)
        return Response({'id': visto.id, 'texto': visto.texto, 'tipo_programa_id': tp.id, 'tipo_programa__nombre': tp.nombre}, status=status.HTTP_201_CREATED)


class VistoDetailView(APIView):
    def patch(self, request, pk):
        try:
            visto = Visto.objects.get(pk=pk)
        except Visto.DoesNotExist:
            return Response({"error": "No existe."}, status=status.HTTP_404_NOT_FOUND)
        texto = request.data.get('texto')
        if texto:
            visto.texto = texto
            visto.save()
        return Response({'id': visto.id, 'texto': visto.texto})

    def delete(self, request, pk):
        try:
            visto = Visto.objects.get(pk=pk)
        except Visto.DoesNotExist:
            return Response({"error": "No existe."}, status=status.HTTP_404_NOT_FOUND)
        visto.delete()
        return Response({"message": "Eliminado."}, status=status.HTTP_204_NO_CONTENT)


class VistosPaginaView(TemplateView):
    template_name = "resoluciones/ru_vistos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_programa"] = TipoPrograma.objects.all()
        return context