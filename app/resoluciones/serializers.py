from rest_framework import serializers
from .models import ResolucionUniversitaria, TipoRU, CarreraPostgrado
import unicodedata

def obtener_etiqueta(obj):
    if obj.sigla:
        return obj.sigla

    nombre = unicodedata.normalize('NFD', obj.nombre)
    nombre = ''.join(c for c in nombre if unicodedata.category(c) != 'Mn') 
    nombre = nombre.replace(' ', '_')
    return nombre

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
        header = value.read(4)
        value.seek(0)
        if header != b'%PDF':
            raise serializers.ValidationError("El archivo no es un PDF valido.")
        return value

    def create(self, validated_data):
        tipo = validated_data['tipo']
        carrera = validated_data['carrera_asociada']
        nombre_generado = (
            f"{validated_data['anio']}_"
            f"{validated_data['numero_ru']}_"
            f"{validated_data['seccion_origen']}_"
            f"{obtener_etiqueta(tipo)}_"
            f"{obtener_etiqueta(carrera)}"
        )
        validated_data['nombre_generado'] = nombre_generado
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.nombre_generado = (
            f"{instance.anio}_"
            f"{instance.numero_ru}_"
            f"{instance.seccion_origen}_"
            f"{obtener_etiqueta(instance.tipo)}_"
            f"{obtener_etiqueta(instance.carrera_asociada)}"
        )

        instance.save()
        return instance
    
