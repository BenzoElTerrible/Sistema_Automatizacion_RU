import os
from datetime import datetime
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.contrib.staticfiles.finders import find

from apps.base.models import TipoRU, CarreraPostgrado

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib import colors


# ══════════════════════════════════════════════════════
# MÓDULO GENERADOR — Creación asistida de RU con ReportLab
# Templates: ru_crear.html
# ══════════════════════════════════════════════════════

class ResolucionCrearPaginaView(TemplateView):
    template_name = "generador/ru_crear.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos"] = TipoRU.objects.all()
        context["carreras"] = CarreraPostgrado.objects.all()
        return context


class ResolucionUniversitariaGenerarPDFView(View):
    def post(self, request, *args, **kwargs):
        titulo = request.POST.get('titulo', '').strip().upper()
        anio = request.POST.get('anio', '2026')
        numero_ru = request.POST.get('numero_ru', '____')
        vistos_textos = request.POST.getlist('vistos_textos')
        considerandos_extra = request.POST.getlist('considerandos')
        resuelvo_texto = request.POST.get('resuelvo', '').strip()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="RU_{numero_ru}-{anio}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter, leftMargin=85, rightMargin=71, topMargin=80, bottomMargin=80)
        story = []
        styles = getSampleStyleSheet()

        style_normal = ParagraphStyle('RU_Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=16, alignment=TA_JUSTIFY, firstLineIndent=0, leftIndent=0)
        style_section_title = ParagraphStyle('RU_SectionTitle', parent=styles['Normal'], fontName='Times-Bold', fontSize=12, leading=16, alignment=TA_CENTER, spaceBefore=10, spaceAfter=8)
        style_considerando = ParagraphStyle('RU_Considerando', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=16, alignment=TA_JUSTIFY, firstLineIndent=190, spaceAfter=10)
        style_footer_center = ParagraphStyle('RU_FooterCenter', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=14, alignment=TA_CENTER)
        style_epigrafe = ParagraphStyle('RU_Epigrafe', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=14, alignment=TA_JUSTIFY)
        style_fecha_numero = ParagraphStyle('RU_FechaNumero', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=16, alignment=TA_LEFT)

        logo_path = find('img/image_5e2339.png')
        if logo_path and os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.drawWidth = 160
            logo.drawHeight = 160
        else:
            logo = Paragraph("<b>UNIVERSIDAD DE TALCA</b><br/>Dirección de Postgrado", style_normal)

        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        fecha_actual = datetime.now()
        fecha_str = f"TALCA, {fecha_actual.day} de {meses[fecha_actual.month - 1]} de {anio}"

        epigrafe_box = Table(
            [[Paragraph(titulo, style_epigrafe)], [Spacer(1, 18)], [Paragraph(fecha_str, style_fecha_numero)], [Spacer(1, 16)], [Paragraph(f"<b>N° {numero_ru}</b>", style_fecha_numero)]],
            colWidths=[250]
        )
        epigrafe_box.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (0, 0), 0.6, colors.black),
            ('LINEBELOW', (0, 0), (0, 0), 0.6, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))

        header_table = Table([[logo, epigrafe_box]], colWidths=[250, 250])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0)]))

        story.append(header_table)
        story.append(Spacer(1, 22))

        story.append(Paragraph("<b>VISTOS:</b>", style_section_title))
        parrafo_vistos = "; ".join([v.strip() for v in vistos_textos]) + "." if vistos_textos else "[No se seleccionaron antecedentes normativos o vistos en el asistente]."
        story.append(Paragraph(parrafo_vistos, style_normal))
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>CONSIDERANDO:</b>", style_section_title))
        lista_considerandos = [c.strip() for c in considerandos_extra if c.strip()]
        for idx, cons_texto in enumerate(lista_considerandos):
            letra = chr(97 + idx)
            cons_limpio = " ".join(cons_texto.split())
            story.append(Paragraph(f"{letra}) {cons_limpio}", style_considerando))
            story.append(Spacer(1, 8))
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>RESUELVO:</b>", style_section_title))
        if resuelvo_texto:
            story.append(Paragraph(resuelvo_texto.strip().replace('\n', '<br/>'), style_normal))
        else:
            story.append(Paragraph("[Acción resolutiva principal no ingresada].", style_normal))

        story.append(Spacer(1, 80))
        story.append(Paragraph("ANÓTESE Y COMUNÍQUESE", style_footer_center))
        story.append(Paragraph('"POR ORDEN DEL SR. RECTOR"', style_footer_center))
        story.append(Spacer(1, 45))
        story.append(Paragraph("SWW/pgc", style_normal))

        doc.build(story)
        return response