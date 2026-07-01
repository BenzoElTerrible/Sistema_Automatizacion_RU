from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView

from .models import TipoPrograma, Visto


# ══════════════════════════════════════════════════════
# MÓDULO BASE — Gestión de datos maestros
# Modelos: TipoPrograma, TipoRU, CarreraPostgrado, Visto
# Templates: ru_vistos.html
# ══════════════════════════════════════════════════════

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
    template_name = "base/ru_vistos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_programa"] = TipoPrograma.objects.all()
        return context