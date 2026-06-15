from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import ResolucionUniversitariaSerializer
from .models import ResolucionUniversitaria, TipoRU, CarreraPostgrado

from django.shortcuts import render
from django.views.generic import TemplateView

from django.core.paginator import Paginator

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
        serializer = ResolucionUniversitariaSerializer(
            resoluciones,
            many=True
        )
        return Response(serializer.data)


class ResolucionUniversitariaDetailView(APIView):

    def get(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response(
                {"error": "La resolución no existe"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResolucionUniversitariaSerializer(resolucion)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response(
                {"error": "La resolucion que intenta eliminar no existe"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        resolucion.delete()
        return Response(
            {"message": "Resolución y archivo PDF eliminados con exito."},
            status=status.HTTP_204_NO_CONTENT
        )
    
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

        todas = ResolucionUniversitaria.objects.all().order_by("fecha_subida")
        paginator = Paginator(todas, 5)  
        page = self.request.GET.get('page', 1)
        resoluciones = paginator.get_page(page)

        context["resoluciones"] = resoluciones
        context["tipos"] = TipoRU.objects.all() # OJO para el formulario
        context["carreras"] = CarreraPostgrado.objects.all() # OJO para el formulario
        return context
    
class VistoDeResolucionView(APIView):
    def get(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response(
                {"error": "La resolución no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        vistos = resolucion.vistos.all()
        if not vistos.exists():
            return Response(
                {"message": "Esta resolución no tiene vistos registrados."},
                status=status.HTTP_200_OK
            )

        serializer = ResolucionUniversitariaSerializer(vistos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response(
                {"error": "La resolución no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        vistos_ids = request.data.get('vistos')
        if not vistos_ids or not isinstance(vistos_ids, list):
            return Response(
                {"error": "Debe proporcionar una lista en el campo 'vistos'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        nuevos_vistos = ResolucionUniversitaria.objects.filter(pk__in=vistos_ids)
        if nuevos_vistos.count() != len(vistos_ids):
            return Response(
                {"error": "Una o más resoluciones indicadas no existen."},
                status=status.HTTP_404_NOT_FOUND
            )

        resolucion.vistos.set(nuevos_vistos)
        serializer = ResolucionUniversitariaSerializer(resolucion.vistos.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)