from rest_framework import serializers
from .models import ResolucionUniversitaria, TipoRU, CarreraPostgrado


class ResolucionUniversitariaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResolucionUniversitaria
        fields = [
            'id', 'anio', 'numero_ru', 'seccion_origen',
            'tipo', 'carrera_asociada', 'nombre_generado',
            'archivo_pdf', 'fecha_subida',
        ]
        read_only_fields = ['nombre_generado', 'fecha_subida']

    def validate_archivo_pdf(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("El archivo debe ser un PDF.")
        if value.content_type != 'application/pdf':
            raise serializers.ValidationError("El tipo de archivo debe ser application/pdf.")
        return value

    def create(self, validated_data):
        tipo = validated_data['tipo']
        carrera = validated_data['carrera_asociada']
        nombre_generado = (
            f"{validated_data['anio']}_"
            f"{validated_data['numero_ru']}_"
            f"{validated_data['seccion_origen']}_"
            f"{tipo.nombre}_"
            f"{carrera.nombre}"
        )
        validated_data['nombre_generado'] = nombre_generado
        return super().create(validated_data)