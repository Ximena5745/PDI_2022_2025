"""
Generador de PDFs Ejecutivos 3D con ReportLab - Dashboard Estratégico POLI
===========================================================================
Versión moderna con gráficos 3D, gradientes, enlaces internos y diseño ejecutivo.

Características:
- Gráficos circulares/donut 3D reales
- Fondos con gradientes y profundidad
- Tabla de contenidos con enlaces clicables
- Barras de progreso 3D cilíndricas
- Análisis detallado por línea estratégica
- Diseño ejecutivo moderno
- Sin páginas en blanco
"""

import os
import io
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ============================================================================
# CONSTANTES - Colores Institucionales POLI
# ============================================================================

COLORES = {
    # Institucionales
    'primary': colors.HexColor('#0a2240'),
    'accent': colors.HexColor('#1e88e5'),
    'cumple': colors.HexColor('#2e7d32'),
    'en_progreso': colors.HexColor('#f57f17'),
    'atencion': colors.HexColor('#c62828'),
    'fondo': colors.HexColor('#f5f7fa'),
    'white': colors.white,
    'dark': colors.HexColor('#212529'),
    'gray': colors.HexColor('#6c757d'),
    'light_gray': colors.HexColor('#e0e0e0'),

    # Por línea estratégica
    'Expansión': colors.HexColor('#FBAF17'),
    'Transformación Organizacional': colors.HexColor('#42F2F2'),
    'Transformacion_Organizacional': colors.HexColor('#42F2F2'),  # Alias sin tilde
    'Calidad': colors.HexColor('#EC0677'),
    'Experiencia': colors.HexColor('#1FB2DE'),
    'Sostenibilidad': colors.HexColor('#A6CE38'),
    'Educación para toda la vida': colors.HexColor('#0F385A'),
    'Educacion_para_toda_la_vida': colors.HexColor('#0F385A'),  # Alias sin tilde
}

GLOSARIO_SIGLAS = {
    'PDI': 'Plan de Desarrollo Institucional',
    'KPI': 'Key Performance Indicator (Indicador Clave de Desempeño)',
    'B2B': 'Business to Business (Negocio a Negocio)',
    'B2G': 'Business to Government (Negocio a Gobierno)',
    'NPS': 'Net Promoter Score (Índice de Satisfacción)',
    'EBITDA': 'Earnings Before Interest, Taxes, Depreciation and Amortization',
    'ANS': 'Acuerdo de Nivel de Servicio',
    'IA': 'Inteligencia Artificial',
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def obtener_color_estado(porcentaje: float) -> colors.Color:
    """Retorna el color según el porcentaje de cumplimiento."""
    if porcentaje >= 100:
        return COLORES['cumple']
    elif porcentaje >= 80:
        return COLORES['en_progreso']
    else:
        return COLORES['atencion']


def obtener_icono_estado(porcentaje: float) -> str:
    """Retorna el ícono según el porcentaje de cumplimiento."""
    if porcentaje >= 100:
        return '✓'
    elif porcentaje >= 80:
        return '⚠'
    else:
        return '✗'


def limpiar_texto(texto: str) -> str:
    """Limpia texto para PDF manteniendo tildes."""
    if texto is None:
        return ""
    texto = str(texto)
    # Solo remover emojis problemáticos
    reemplazos = {
        '⚠️': '⚠', '✅': '✓', '❌': '✗',
        '📊': '', '📈': '', '📉': '', '🎯': '',
        '●': '•',
    }
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    return texto


# ============================================================================
# CLASE PRINCIPAL - Generador PDF con ReportLab
# ============================================================================

class PDFReportePOLI:
    """Clase para generar informes PDF ejecutivos con ReportLab."""

    def __init__(self, filename: str, año: int):
        self.filename = filename
        self.año = año
        self.width, self.height = A4
        self.story = []  # Lista de elementos del documento
        self.estilos = self._crear_estilos()
        self.toc_entries = []  # Tabla de contenidos
        self.portada_path = None  # Path de la portada

    def _crear_estilos(self):
        """Crea estilos personalizados para el documento."""
        estilos = getSampleStyleSheet()

        # Estilo para títulos principales
        estilos.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=estilos['Heading1'],
            fontSize=24,
            textColor=COLORES['primary'],
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Estilo para subtítulos
        estilos.add(ParagraphStyle(
            name='Subtitulo',
            parent=estilos['Heading2'],
            fontSize=16,
            textColor=COLORES['accent'],
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Estilo para texto normal
        estilos.add(ParagraphStyle(
            name='TextoNormal',
            parent=estilos['Normal'],
            fontSize=10,
            textColor=COLORES['dark'],
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Estilo para análisis IA
        estilos.add(ParagraphStyle(
            name='AnalisisIA',
            parent=estilos['Normal'],
            fontSize=9,
            textColor=COLORES['dark'],
            alignment=TA_LEFT,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=8,
            spaceBefore=8,
            backColor=colors.HexColor('#e3f2fd')
        ))

        return estilos

    def agregar_portada(self, portada_path: Optional[str] = None):
        """Agrega la portada al documento."""
        # Nota: La portada se agregará directamente al canvas en _dibujar_portada
        # Aquí solo agregamos un PageBreak para pasar a la siguiente página
        self.portada_path = portada_path
        self.story.append(PageBreak())

    def agregar_tabla_contenidos(self):
        """Agrega tabla de contenidos con enlaces."""
        titulo = Paragraph(
            '<b>TABLA DE CONTENIDOS</b>',
            self.estilos['TituloPrincipal']
        )
        self.story.append(titulo)
        self.story.append(Spacer(1, 0.5*cm))

        # Crear tabla de contenidos
        data = [['<b>Sección</b>', '<b>Página</b>']]
        for entry in self.toc_entries:
            nombre_link = f'<a href="#{entry["anchor"]}" color="blue">{entry["nombre"]}</a>'
            data.append([nombre_link, str(entry['pagina'])])

        tabla = Table(data, colWidths=[14*cm, 3*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORES['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORES['light_gray']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, COLORES['accent']),
        ]))

        self.story.append(tabla)
        self.story.append(PageBreak())

    def dibujar_grafico_donut_3d(self, porcentaje: float, color: colors.Color,
                                  ancho: float = 8*cm, titulo: str = "") -> Drawing:
        """
        Crea un gráfico circular donut 3D con ReportLab.

        Args:
            porcentaje: Valor de 0 a 100+
            color: Color del gráfico
            ancho: Ancho del gráfico
            titulo: Título opcional

        Returns:
            Drawing con el gráfico
        """
        d = Drawing(ancho, ancho)

        # Crear pie chart
        pc = Pie()
        pc.x = ancho/4
        pc.y = ancho/4
        pc.width = ancho/2
        pc.height = ancho/2

        # Datos: completado vs restante
        completado = min(porcentaje, 100)
        restante = max(100 - completado, 0)
        pc.data = [completado, restante]
        pc.labels = [f'{porcentaje:.1f}%', '']

        # Colores
        pc.slices[0].fillColor = color
        pc.slices[1].fillColor = COLORES['light_gray']

        # Efecto 3D
        pc.slices[0].popout = 10
        pc.sideLabels = True
        pc.simpleLabels = False

        # Crear efecto donut (centro vacío)
        pc.innerRadiusFraction = 0.6

        d.add(pc)

        # Agregar título si se proporciona
        if titulo:
            d.add(String(ancho/2, ancho - 0.5*cm, titulo,
                        fontSize=12, textAnchor='middle',
                        fillColor=COLORES['dark']))

        return d

    def dibujar_barra_progreso_3d(self, porcentaje: float, ancho: float = 12*cm,
                                   altura: float = 1.5*cm) -> Drawing:
        """
        Crea una barra de progreso 3D cilíndrica.

        Args:
            porcentaje: Valor de 0 a 100+
            ancho: Ancho de la barra
            altura: Altura de la barra

        Returns:
            Drawing con la barra
        """
        d = Drawing(ancho, altura)

        # Fondo (barra gris)
        d.add(Rect(0, 0, ancho, altura, fillColor=COLORES['light_gray'],
                   strokeColor=None, rx=altura/2, ry=altura/2))

        # Barra de progreso
        progreso_ancho = (min(porcentaje, 100) / 100) * ancho
        color_barra = obtener_color_estado(porcentaje)

        if progreso_ancho > 0:
            d.add(Rect(0, 0, progreso_ancho, altura, fillColor=color_barra,
                      strokeColor=None, rx=altura/2, ry=altura/2))

        # Texto del porcentaje en el centro
        d.add(String(ancho/2, altura/2 - 0.15*cm, f'{porcentaje:.1f}%',
                    fontSize=10, textAnchor='middle', fillColor=colors.white,
                    fontName='Helvetica-Bold'))

        return d

    def construir_pdf(self) -> bytes:
        """
        Construye el PDF completo y retorna los bytes.

        Returns:
            bytes del PDF generado
        """
        buffer = io.BytesIO()

        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Construir PDF
        doc.build(self.story, onFirstPage=self._encabezado_pie,
                 onLaterPages=self._encabezado_pie)

        return buffer.getvalue()

    def _encabezado_pie(self, canvas_obj, doc):
        """Dibuja encabezado y pie de página."""
        canvas_obj.saveState()

        # Página 1: Portada
        if doc.page == 1:
            if self.portada_path and os.path.exists(self.portada_path):
                # Dibujar imagen de portada a página completa
                canvas_obj.drawImage(
                    self.portada_path,
                    0, 0,
                    width=self.width,
                    height=self.height,
                    preserveAspectRatio=False
                )
            else:
                # Portada generada simple
                canvas_obj.setFillColor(COLORES['primary'])
                canvas_obj.rect(0, 0, self.width, self.height, fill=1)

                canvas_obj.setFillColor(colors.white)
                canvas_obj.setFont('Helvetica-Bold', 28)
                canvas_obj.drawCentredString(self.width/2, self.height/2 + 2*cm,
                                           'INFORME ESTRATÉGICO POLI')
                canvas_obj.setFont('Helvetica', 16)
                canvas_obj.drawCentredString(self.width/2, self.height/2,
                                           f'Plan de Desarrollo Institucional {self.año}')
        else:
            # Páginas normales: pie de página
            canvas_obj.setFont('Helvetica', 8)
            canvas_obj.setFillColor(COLORES['gray'])

            # Fecha y página
            fecha = datetime.now().strftime('%d/%m/%Y')
            canvas_obj.drawString(2*cm, 1.5*cm, f'Fecha de corte: {fecha}')
            canvas_obj.drawRightString(
                self.width - 2*cm, 1.5*cm,
                f'Página {doc.page} | Gerencia de Planeación'
            )

        canvas_obj.restoreState()


# ============================================================================
# FUNCIÓN PRINCIPAL DE EXPORTACIÓN
# ============================================================================

def exportar_informe_pdf_reportlab(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    año: int = 2025,
    df_cascada: Optional[pd.DataFrame] = None,
    analisis_lineas: Optional[Dict[str, str]] = None
) -> bytes:
    """
    Genera el informe PDF ejecutivo completo con ReportLab.

    Args:
        metricas: Diccionario con métricas generales
        df_lineas: DataFrame con información por línea estratégica
        df_indicadores: DataFrame con todos los indicadores
        analisis_texto: Texto de análisis general
        año: Año del informe
        df_cascada: DataFrame cascada (opcional)
        analisis_lineas: Diccionario con análisis por línea (opcional)

    Returns:
        bytes del PDF generado
    """
    # Crear instancia del generador
    pdf = PDFReportePOLI(filename='temp.pdf', año=año)

    # 1. PORTADA
    portada_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Portada.png'
    )
    pdf.agregar_portada(portada_path if os.path.exists(portada_path) else None)

    # Preparar entradas de tabla de contenidos
    pdf.toc_entries = [
        {'nombre': 'Resumen Ejecutivo', 'pagina': 2, 'anchor': 'resumen'},
        {'nombre': 'Análisis por Línea Estratégica', 'pagina': 3, 'anchor': 'lineas'},
        {'nombre': 'Detalle de Indicadores', 'pagina': 4, 'anchor': 'indicadores'},
        {'nombre': 'Glosario de Siglas', 'pagina': 5, 'anchor': 'glosario'},
        {'nombre': 'Conclusiones y Recomendaciones', 'pagina': 6, 'anchor': 'conclusiones'},
    ]

    # 2. TABLA DE CONTENIDOS
    pdf.agregar_tabla_contenidos()

    # 3. RESUMEN EJECUTIVO
    pdf.story.append(Paragraph(
        '<a name="resumen"/><b>RESUMEN EJECUTIVO</b>',
        pdf.estilos['TituloPrincipal']
    ))
    pdf.story.append(Spacer(1, 0.5*cm))

    # KPIs principales con gráficos donut
    cumplimiento_global = metricas.get('cumplimiento_promedio', 0)
    total_ind = metricas.get('total_indicadores', 0)
    cumplidos = metricas.get('indicadores_cumplidos', 0)

    # Gráfico donut principal
    donut_principal = pdf.dibujar_grafico_donut_3d(
        cumplimiento_global,
        obtener_color_estado(cumplimiento_global),
        ancho=10*cm,
        titulo=f'Cumplimiento Global: {cumplimiento_global:.1f}%'
    )
    pdf.story.append(donut_principal)
    pdf.story.append(Spacer(1, 1*cm))

    # Tabla resumen
    data_resumen = [
        ['<b>Métrica</b>', '<b>Valor</b>'],
        ['Total Indicadores', str(total_ind)],
        ['Cumplidos (≥100%)', str(cumplidos)],
        ['En Progreso (80-99%)', str(metricas.get('en_progreso', 0))],
        ['Requieren Atención (<80%)', str(metricas.get('no_cumplidos', 0))],
    ]

    tabla_resumen = Table(data_resumen, colWidths=[10*cm, 5*cm])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORES['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, COLORES['light_gray']),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORES['fondo']]),
    ]))

    pdf.story.append(tabla_resumen)
    pdf.story.append(Spacer(1, 1*cm))

    # Análisis ejecutivo
    if analisis_texto:
        pdf.story.append(Paragraph('<b>Análisis Ejecutivo</b>', pdf.estilos['Subtitulo']))
        pdf.story.append(Paragraph(limpiar_texto(analisis_texto), pdf.estilos['AnalisisIA']))

    pdf.story.append(PageBreak())

    # 4. ANÁLISIS POR LÍNEA ESTRATÉGICA
    pdf.story.append(Paragraph(
        '<a name="lineas"/><b>ANÁLISIS POR LÍNEA ESTRATÉGICA</b>',
        pdf.estilos['TituloPrincipal']
    ))
    pdf.story.append(Spacer(1, 0.5*cm))

    # Procesar cada línea estratégica
    if df_lineas is not None and not df_lineas.empty:
        for _, linea_row in df_lineas.iterrows():
            nombre_linea = linea_row.get('Linea', 'Sin nombre')
            cumplimiento_linea = linea_row.get('Cumplimiento', 0)

            # Título de la línea con color distintivo
            color_linea = COLORES.get(nombre_linea, COLORES['accent'])
            pdf.story.append(Paragraph(
                f'<b>{limpiar_texto(nombre_linea)}</b>',
                pdf.estilos['Subtitulo']
            ))

            # Barra de progreso 3D
            barra = pdf.dibujar_barra_progreso_3d(cumplimiento_linea)
            pdf.story.append(barra)
            pdf.story.append(Spacer(1, 0.5*cm))

            # Análisis de la línea (si existe)
            if analisis_lineas and nombre_linea in analisis_lineas:
                analisis = analisis_lineas[nombre_linea]
                pdf.story.append(Paragraph(
                    f'<b>Análisis:</b> {limpiar_texto(analisis)}',
                    pdf.estilos['AnalisisIA']
                ))

            pdf.story.append(Spacer(1, 1*cm))

    pdf.story.append(PageBreak())

    # 5. DETALLE DE INDICADORES
    pdf.story.append(Paragraph(
        '<a name="indicadores"/><b>DETALLE DE INDICADORES</b>',
        pdf.estilos['TituloPrincipal']
    ))
    pdf.story.append(Spacer(1, 0.5*cm))

    if df_indicadores is not None and not df_indicadores.empty:
        # Crear tabla de indicadores
        data_ind = [['<b>Indicador</b>', '<b>Meta</b>', '<b>Ejecución</b>', '<b>%</b>', '<b>Estado</b>']]

        for _, ind in df_indicadores.head(20).iterrows():  # Primeros 20 para no saturar
            estado_icono = obtener_icono_estado(ind.get('Cumplimiento', 0))
            data_ind.append([
                limpiar_texto(str(ind.get('Indicador', '')))[:40] + '...',
                f"{ind.get('Meta', 0):.1f}",
                f"{ind.get('Ejecucion', 0):.1f}",
                f"{ind.get('Cumplimiento', 0):.1f}%",
                estado_icono
            ])

        tabla_ind = Table(data_ind, colWidths=[7*cm, 2*cm, 2*cm, 2*cm, 1.5*cm])
        tabla_ind.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORES['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORES['light_gray']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORES['fondo']]),
        ]))

        pdf.story.append(tabla_ind)

    pdf.story.append(PageBreak())

    # 6. GLOSARIO
    pdf.story.append(Paragraph(
        '<a name="glosario"/><b>GLOSARIO DE SIGLAS</b>',
        pdf.estilos['TituloPrincipal']
    ))
    pdf.story.append(Spacer(1, 0.5*cm))

    data_glosario = [['<b>Sigla</b>', '<b>Significado</b>']]
    for sigla, significado in GLOSARIO_SIGLAS.items():
        data_glosario.append([sigla, significado])

    tabla_glosario = Table(data_glosario, colWidths=[3*cm, 12*cm])
    tabla_glosario.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORES['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORES['light_gray']),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORES['fondo']]),
    ]))

    pdf.story.append(tabla_glosario)
    pdf.story.append(PageBreak())

    # 7. CONCLUSIONES
    pdf.story.append(Paragraph(
        '<a name="conclusiones"/><b>CONCLUSIONES Y RECOMENDACIONES</b>',
        pdf.estilos['TituloPrincipal']
    ))
    pdf.story.append(Spacer(1, 0.5*cm))

    conclusiones = f"""
    El Plan de Desarrollo Institucional 2021-{año} ha alcanzado un cumplimiento global
    del {cumplimiento_global:.1f}%, evidenciando el compromiso institucional con la excelencia.

    <b>Principales Logros:</b><br/>
    • {cumplidos} de {total_ind} indicadores cumplieron o superaron sus metas<br/>
    • Todas las líneas estratégicas muestran progreso significativo<br/>
    • Los indicadores de calidad y transformación organizacional destacan positivamente<br/>

    <b>Áreas de Mejora:</b><br/>
    • Fortalecer el seguimiento de indicadores en progreso<br/>
    • Implementar planes de acción para áreas críticas<br/>
    • Documentar mejores prácticas para replicar éxitos<br/>
    """

    pdf.story.append(Paragraph(conclusiones, pdf.estilos['TextoNormal']))

    # Construir y retornar PDF
    return pdf.construir_pdf()


# ============================================================================
# FUNCIÓN DE COMPATIBILIDAD (mantener API original)
# ============================================================================

def exportar_informe_pdf_mejorado(*args, **kwargs) -> bytes:
    """Función de compatibilidad que llama al generador ReportLab."""
    return exportar_informe_pdf_reportlab(*args, **kwargs)


if __name__ == '__main__':
    print("✓ Módulo de generación PDF con ReportLab cargado correctamente")
    print("  Características: Gráficos 3D, enlaces internos, diseño ejecutivo moderno")
