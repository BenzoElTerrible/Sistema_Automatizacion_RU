from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser
from .serializers import ResolucionUniversitariaSerializer
from .models import ResolucionUniversitaria, TipoRU, CarreraPostgrado, TipoPrograma, Visto

import os
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.staticfiles.finders import find
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin

class ResolucionUniversitariaCreateView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResolucionUniversitariaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResolucionUniversitariaListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        resoluciones = ResolucionUniversitaria.objects.all()
        serializer = ResolucionUniversitariaSerializer(resoluciones, many=True)
        return Response(serializer.data)


class ResolucionUniversitariaDetailView(APIView):
    permission_classes = [AllowAny]

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
        if not request.user.is_staff:
            return Response(
                {"error": "Solo un administrador puede eliminar archivos."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            resolucion = ResolucionUniversitaria.objects.get(pk=pk)
        except ResolucionUniversitaria.DoesNotExist:
            return Response(
                {"error": "No existe"},
                status=status.HTTP_404_NOT_FOUND
            )

        resolucion.delete()

        return Response(
            {"message": "Eliminado."},
            status=status.HTTP_204_NO_CONTENT
        )

    
def patch(self, request, pk):

    if not request.user.is_staff:
        return Response(
            {"error": "Solo un administrador puede editar."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        resolucion = ResolucionUniversitaria.objects.get(pk=pk)
    except ResolucionUniversitaria.DoesNotExist:
        return Response(
            {"error": "No existe"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ResolucionUniversitariaSerializer(
        resolucion,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


class ResolucionGestionView(LoginRequiredMixin, TemplateView):
    login_url = "/admin/login/"
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
        if not request.user.is_staff:
            return Response(
                {"error": "Solo un administrador puede editar."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            visto = Visto.objects.get(pk=pk)
        except Visto.DoesNotExist:
            return Response(
                {"error": "No existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        texto = request.data.get("texto")

        if texto:
            visto.texto = texto
            visto.save()

        return Response({
            "id": visto.id,
            "texto": visto.texto
        })

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "Solo un administrador puede eliminar."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            visto = Visto.objects.get(pk=pk)
        except Visto.DoesNotExist:
            return Response(
                {"error": "No existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        visto.delete()

        return Response(
            {"message": "Eliminado."},
            status=status.HTTP_204_NO_CONTENT
        )
class VistosPaginaView(TemplateView):
    template_name = "resoluciones/ru_vistos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_programa"] = TipoPrograma.objects.all()
        return context

class ResolucionCrearPaginaView(LoginRequiredMixin, TemplateView):
    login_url = "/admin/login/"
    template_name = "resoluciones/ru_crear.html"
   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos"] = TipoRU.objects.all()
        context["carreras"] = CarreraPostgrado.objects.all()
        return context
    

# Componentes de ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER


class ResolucionUniversitariaGenerarPDFView(View):
    def post(self, request, *args, **kwargs):
        # 1. Capturar la información enviada desde el formulario
        titulo = request.POST.get('titulo', '').strip().upper()
        anio = request.POST.get('anio', '2026')
        numero_ru = request.POST.get('numero_ru', '____')
        carrera = request.POST.get('carrera', 'No seleccionada')
        vistos_textos = request.POST.getlist('vistos_textos') # Lista de vistos
        considerandos_extra = request.POST.getlist('considerandos') # Solo recibe los dinámicos (c, d...)
        resuelvo_texto = request.POST.get('resuelvo', '').strip() 

        # 2. Configurar la respuesta HTTP para devolver un archivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="RU_{numero_ru}-{anio}.pdf"'

        # 3. Crear el lienzo del documento
        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            leftMargin=85,
            rightMargin=71,
            topMargin=71,
            bottomMargin=71
        )

        story = []
        styles = getSampleStyleSheet()

        # 4. Definición de estilos tipográficos
        style_normal = ParagraphStyle(
            'RU_Normal', 
            parent=styles['Normal'], 
            fontName='Helvetica', 
            fontSize=11, 
            leading=16, 
            alignment=TA_JUSTIFY
        )
        style_bold_label = ParagraphStyle(
            'RU_BoldLabel', 
            parent=style_normal, 
            fontName='Helvetica-Bold'
        )
        style_header_right = ParagraphStyle(
            'RU_HeaderRight', 
            parent=styles['Normal'], 
            fontName='Helvetica-Bold', 
            fontSize=11, 
            leading=15, 
            alignment=TA_RIGHT
        )
        style_footer_center = ParagraphStyle(
            'RU_FooterCenter', 
            parent=styles['Normal'], 
            fontName='Helvetica-Bold', 
            fontSize=11, 
            leading=16, 
            alignment=TA_CENTER
        )

        # 5. Logo Institucional
        logo_path = find('img/image_5e2339.png')
        if logo_path and os.path.exists(logo_path):
            img = Image(logo_path, width=145, height=85)
            img.hAlign = 'LEFT'
            story.append(img)
        else:
            story.append(Paragraph("<b>UNIVERSIDAD DE TALCA</b><br/>Dirección de Postgrado", style_normal))
        
        story.append(Spacer(1, 15))

        # 6. Título, Fecha y Número
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        fecha_actual = datetime.now()
        fecha_str = f"TALCA, {fecha_actual.day} de {meses[fecha_actual.month - 1]} de {anio}"

        texto_encabezado_derecho = f"{titulo}<br/><br/>{fecha_str}<br/>N° {numero_ru}"
        story.append(Paragraph(texto_encabezado_derecho, style_header_right))
        story.append(Spacer(1, 25))

        # 7. VISTOS
        story.append(Paragraph("<b>VISTOS:</b>", style_bold_label))
        if vistos_textos:
            parrafo_vistos = "; ".join([v.strip() for v in vistos_textos]) + "."
        else:
            parrafo_vistos = "[No se seleccionaron antecedentes normativos o vistos en el asistente]."
        story.append(Paragraph(parrafo_vistos, style_normal))
        story.append(Spacer(1, 15))

        # 8. CONSIDERANDO (Automáticos a/b + Dinámicos c/d...)
        story.append(Paragraph("<b>CONSIDERANDO:</b>", style_bold_label))
        
        # Preparamos la lista con los dos automáticos
        lista_considerandos = [
            f"Que, la Resolución Universitaria respectiva crea el programa de {carrera}.",
            "Que, los antecedentes presentados por la Dirección de Postgrado justifican la presente acción."
        ]
        
        # Agregamos los que vengan del formulario (si el usuario añadió extras)
        for cons in considerandos_extra:
            if cons.strip():
                lista_considerandos.append(cons.strip())

        # Imprimimos la lista asignando la letra de manera secuencial
        for idx, cons_texto in enumerate(lista_considerandos):
            letra = chr(97 + idx) # Genera a, b, c, d...
            texto_cons_final = f"{letra}) {cons_texto}"
            story.append(Paragraph(texto_cons_final, style_normal))
        
        story.append(Spacer(1, 15))

        # 9. RESUELVO
        story.append(Paragraph("<b>RESUELVO:</b>", style_bold_label))
        if resuelvo_texto:
            texto_formateado = resuelvo_texto.replace('\n', '<br/>')
            story.append(Paragraph(texto_formateado, style_normal))
        else:
            story.append(Paragraph("[Acción resolutiva principal no ingresada].", style_normal))
            
        story.append(Spacer(1, 45))

        # 10. Cierre del documento institucional
        story.append(Spacer(1, 30))
        story.append(Paragraph("ANÓTESE Y COMUNIQUESE", style_footer_center))
        story.append(Paragraph('"POR ORDEN DEL SR. RECTOR"', style_footer_center))

        # 11. Construir PDF
        doc.build(story)
        return response
