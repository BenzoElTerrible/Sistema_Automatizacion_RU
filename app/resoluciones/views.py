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