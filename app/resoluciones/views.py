from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import ResolucionUniversitariaSerializer
from .models import ResolucionUniversitaria


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