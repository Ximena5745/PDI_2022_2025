"""
Generador de PDFs Ejecutivos con ReportLab - Dashboard Estratégico POLI
=======================================================================
Diseño ejecutivo profesional con:
- Fichas 3D con sombras y bordes redondeados
- Colores semáforo (verde/naranja/rojo) para cumplimiento
- Barras de progreso redondeadas
- Análisis IA por línea estratégica
- Tabla detallada de indicadores (todos, paginada)
- Portada institucional
- Sin páginas en blanco
"""

import os
import io
import unicodedata
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF


# ============================================================
# PALETA DE COLORES
# ============================================================

# Semáforo
C_VERDE   = colors.HexColor('#2e7d32')
C_NARANJA = colors.HexColor('#e65100')
C_ROJO    = colors.HexColor('#b71c1c')

# Institucionales
C_NAVY    = colors.HexColor('#0a2240')
C_ACCENT  = colors.HexColor('#1e88e5')
C_WHITE   = colors.white
C_BG      = colors.HexColor('#f5f7fa')
C_DARK    = colors.HexColor('#212529')
C_GRAY    = colors.HexColor('#6c757d')
C_LIGHT   = colors.HexColor('#dee2e6')
C_SHADOW  = colors.HexColor('#c8cdd3')
C_RING_BG = colors.HexColor('#e8ecef')

# Por línea estratégica (con y sin tilde)
COLOR_LINEAS: Dict[str, colors.Color] = {
    'Expansión':                         colors.HexColor('#FBAF17'),
    'Expansion':                         colors.HexColor('#FBAF17'),
    'Transformación Organizacional':     colors.HexColor('#00A8A8'),
    'Transformacion Organizacional':     colors.HexColor('#00A8A8'),
    'Calidad':                           colors.HexColor('#EC0677'),
    'Experiencia':                       colors.HexColor('#1FB2DE'),
    'Sostenibilidad':                    colors.HexColor('#5A9E1A'),
    'Educación para toda la vida':       colors.HexColor('#0F385A'),
    'Educacion para toda la vida':       colors.HexColor('#0F385A'),
}

GLOSARIO = {
    'PDI':    'Plan de Desarrollo Institucional',
    'KPI':    'Key Performance Indicator (Indicador Clave de Desempeño)',
    'B2B':    'Business to Business (Negocio a Negocio)',
    'B2G':    'Business to Government (Negocio a Gobierno)',
    'NPS':    'Net Promoter Score (Índice de Satisfacción)',
    'EBITDA': 'Earnings Before Interest, Taxes, Depreciation and Amortization',
    'ANS':    'Acuerdo de Nivel de Servicio',
    'IA':     'Inteligencia Artificial',
}


# ============================================================
# HELPERS
# ============================================================

def _norm(s: str) -> str:
    """Normalize string: remove accents, lowercase, strip."""
    return unicodedata.normalize('NFD', str(s)).encode('ascii', 'ignore').decode().lower().strip()


def color_semaforo(pct: float) -> colors.Color:
    if pct >= 100:
        return C_VERDE
    if pct >= 80:
        return C_NARANJA
    return C_ROJO


def texto_estado(pct: float) -> str:
    if pct >= 100:
        return 'CUMPLIDO'
    if pct >= 80:
        return 'EN PROGRESO'
    return 'ATENCION'


def color_linea(nombre: str) -> colors.Color:
    """Return brand color for a strategic line (accent-insensitive)."""
    n = _norm(nombre)
    for key, col in COLOR_LINEAS.items():
        if _norm(key) == n:
            return col
    for key, col in COLOR_LINEAS.items():
        if _norm(key) in n or n in _norm(key):
            return col
    return C_ACCENT


def limpiar(txt: str) -> str:
    """Clean text for PDF (keep accents, strip problematic characters)."""
    if not txt:
        return ""
    txt = str(txt)
    for orig, rep in [('⚠️', '⚠'), ('✅', '✓'), ('❌', '✗'),
                      ('📊', ''), ('📈', ''), ('📉', ''), ('🎯', ''),
                      ('●', '•'), ('**', ''), ('*', '')]:
        txt = txt.replace(orig, rep)
    return txt.strip()


def nombre_display(nombre: str) -> str:
    """Convierte nombres internos (con _) a forma legible con espacios."""
    return limpiar(nombre.replace('_', ' '))


def _light_color(c: colors.Color, factor: float = 0.82) -> colors.Color:
    """Mix color with white to get a lighter tint."""
    r = min(1.0, c.red   + (1 - c.red)   * factor)
    g = min(1.0, c.green + (1 - c.green) * factor)
    b = min(1.0, c.blue  + (1 - c.blue)  * factor)
    return colors.Color(r, g, b)


# ============================================================
# CLASE PRINCIPAL
# ============================================================

class PDFReportePOLI:
    """Genera informes PDF ejecutivos con canvas ReportLab."""

    # Margen horizontal estándar
    MX = 18 * mm
    # Alturas de banda
    H_HEADER = 22 * mm
    H_FOOTER = 14 * mm

    def __init__(self, año: int):
        self.buffer = io.BytesIO()
        self.c = rl_canvas.Canvas(self.buffer, pagesize=A4)
        self.W, self.H = A4
        self.año = año
        self._page = 0          # current page number (1-based after portada)

    # ----------------------------------------------------------
    # Utilidades de página
    # ----------------------------------------------------------

    def _new_page(self):
        self.c.showPage()
        self._page += 1

    def _footer(self, subtitulo: str = "Informe Estratégico POLI"):
        """Dibuja pie de página estándar."""
        y = self.H_FOOTER - 4 * mm
        # Línea separadora
        self.c.setStrokeColor(C_LIGHT)
        self.c.setLineWidth(0.4)
        self.c.line(self.MX, y + 3 * mm, self.W - self.MX, y + 3 * mm)
        # Textos
        self.c.setFont('Helvetica', 6.5)
        self.c.setFillColor(C_GRAY)
        fecha = datetime.now().strftime('%d/%m/%Y')
        self.c.drawString(self.MX, y, f'PDI {self.año} | {limpiar(subtitulo)}')
        self.c.drawRightString(
            self.W - self.MX, y,
            f'Página {self._page} | Gerencia de Planeación | {fecha}'
        )

    def _header_band(self, color: colors.Color, titulo: str, subtitulo: str = "") -> float:
        """
        Dibuja banda de encabezado con sombra.
        Retorna la coordenada Y inferior de la banda (inicio del contenido).
        """
        y0 = self.H - self.H_HEADER
        # Sombra
        self.c.setFillColor(C_SHADOW)
        self.c.rect(0, y0 - 2 * mm, self.W, self.H_HEADER, fill=1, stroke=0)
        # Banda principal
        self.c.setFillColor(color)
        self.c.rect(0, y0, self.W, self.H_HEADER, fill=1, stroke=0)
        # Línea decorativa inferior (blanca semitransparente → uso blanco)
        self.c.setFillColor(C_WHITE)
        self.c.rect(0, y0, self.W, 1 * mm, fill=1, stroke=0)
        # Título
        self.c.setFillColor(C_WHITE)
        if subtitulo:
            self.c.setFont('Helvetica-Bold', 13)
            self.c.drawString(self.MX, y0 + 13 * mm, titulo)
            self.c.setFont('Helvetica', 8)
            self.c.setFillColor(colors.HexColor('#c8d8f0'))
            self.c.drawString(self.MX, y0 + 6 * mm, subtitulo)
        else:
            self.c.setFont('Helvetica-Bold', 14)
            self.c.drawCentredString(self.W / 2, y0 + 8 * mm, titulo)
        return y0 - 2 * mm   # top of content area (just below shadow)

    # ----------------------------------------------------------
    # Primitivos visuales
    # ----------------------------------------------------------

    def _shadow_card(self, x: float, y: float, w: float, h: float,
                     fill: colors.Color, radius: float = 3 * mm):
        """Ficha redondeada con sombra (efecto 3D profundidad)."""
        # Sombra desplazada
        self.c.setFillColor(C_SHADOW)
        self.c.roundRect(x + 2 * mm, y - 2 * mm, w, h, radius, fill=1, stroke=0)
        # Tarjeta principal
        self.c.setFillColor(fill)
        self.c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

    def _kpi_card(self, x: float, y: float, w: float, h: float,
                  value: str, label: str, color: colors.Color):
        """Tarjeta KPI con acento de color y valor grande."""
        bg = _light_color(color, 0.85)
        self._shadow_card(x, y, w, h, bg, radius=3 * mm)
        # Barra izquierda de acento
        self.c.setFillColor(color)
        self.c.roundRect(x, y, 2.5 * mm, h, 2 * mm, fill=1, stroke=0)
        # Valor
        self.c.setFont('Helvetica-Bold', 18)
        self.c.setFillColor(color)
        self.c.drawCentredString(x + w / 2, y + h * 0.52, value)
        # Etiqueta
        self.c.setFont('Helvetica', 7)
        self.c.setFillColor(C_GRAY)
        self.c.drawCentredString(x + w / 2, y + h * 0.18, label)

    def _progress_bar(self, x: float, y: float, w: float, h: float,
                      pct: float, color: colors.Color = None):
        """Barra de progreso redondeada con texto central."""
        if color is None:
            color = color_semaforo(pct)
        r = h / 2
        # Fondo
        self.c.setFillColor(C_RING_BG)
        self.c.roundRect(x, y, w, h, r, fill=1, stroke=0)
        # Progreso
        fill_w = max(r * 2, w * min(float(pct), 100) / 100)
        self.c.setFillColor(color)
        self.c.roundRect(x, y, fill_w, h, r, fill=1, stroke=0)
        # Texto
        self.c.setFont('Helvetica-Bold', 6.5)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(x + w / 2, y + h / 2 - 2.2, f'{pct:.1f}%')

    def _ring_drawing(self, pct: float, size: float = 4 * cm) -> Drawing:
        """Crea un gráfico donut con color semáforo."""
        d = Drawing(size, size)
        pc = Pie()
        pc.x = size * 0.05
        pc.y = size * 0.05
        pc.width  = size * 0.9
        pc.height = size * 0.9
        completado = min(float(pct), 100)
        restante   = max(100 - completado, 0.001)
        pc.data = [completado, restante]
        pc.slices[0].fillColor = color_semaforo(pct)
        pc.slices[1].fillColor = C_RING_BG
        for i in range(2):
            pc.slices[i].strokeWidth = 0
            pc.slices[i].strokeColor = None
        pc.innerRadiusFraction = 0.64
        pc.startAngle = 90
        pc.direction  = 'clockwise'
        d.add(pc)
        return d

    def _wrap_paragraph(self, texto: str, x: float, y_top: float,
                        max_w: float, max_h: float,
                        font: str = 'Helvetica', size: float = 8,
                        color: colors.Color = None, align=TA_LEFT) -> float:
        """
        Dibuja texto con wrapping usando Paragraph.
        Retorna el alto real ocupado.
        """
        if color is None:
            color = C_DARK
        style = ParagraphStyle(
            'tmp',
            fontSize=size,
            fontName=font,
            leading=size * 1.35,
            textColor=color,
            alignment=align,
        )
        safe_txt = limpiar(texto).replace('\n', '<br/>')
        p = Paragraph(safe_txt, style)
        actual_w, actual_h = p.wrap(max_w, max_h)
        p.drawOn(self.c, x, y_top - actual_h)
        return actual_h

    # ----------------------------------------------------------
    # Páginas
    # ----------------------------------------------------------

    def portada(self, portada_path: Optional[str] = None):
        """Página 1: Portada."""
        self._page = 1
        if portada_path and os.path.exists(portada_path):
            self.c.drawImage(
                portada_path, 0, 0, self.W, self.H, preserveAspectRatio=False
            )
        else:
            # Fondo degradado navy (bandas horizontales de oscuro a menos oscuro)
            steps = 80
            for i in range(steps):
                t = i / steps
                r = int(10  + t * 15)
                g = int(34  + t * 25)
                b = int(64  + t * 35)
                self.c.setFillColorRGB(r / 255, g / 255, b / 255)
                band_h = self.H / steps + 1
                self.c.rect(0, self.H * i / steps, self.W, band_h, fill=1, stroke=0)
            # Acento dorado
            self.c.setFillColor(colors.HexColor('#FBAF17'))
            self.c.rect(0, self.H * 0.36, self.W, 3.5 * mm, fill=1, stroke=0)
            # Textos
            self.c.setFillColor(C_WHITE)
            self.c.setFont('Helvetica-Bold', 30)
            self.c.drawCentredString(self.W / 2, self.H * 0.56, 'INFORME ESTRATÉGICO')
            self.c.setFont('Helvetica-Bold', 22)
            self.c.drawCentredString(self.W / 2, self.H * 0.49, 'PLAN DE DESARROLLO')
            self.c.drawCentredString(self.W / 2, self.H * 0.43, f'INSTITUCIONAL {self.año}')
            self.c.setFont('Helvetica', 13)
            self.c.setFillColor(colors.HexColor('#FBAF17'))
            self.c.drawCentredString(self.W / 2, self.H * 0.33, 'Gerencia de Planeación Estratégica')
            self.c.setFont('Helvetica', 9)
            self.c.setFillColor(colors.HexColor('#a0b4c8'))
            fecha_larga = datetime.now().strftime('%B de %Y').title()
            self.c.drawCentredString(self.W / 2, self.H * 0.27, fecha_larga)
        self._new_page()

    def resumen_ejecutivo(self, metricas: Dict, analisis_texto: str = ""):
        """Página: Resumen Ejecutivo con KPIs y análisis IA general."""
        cont_top = self._header_band(
            C_NAVY, 'RESUMEN EJECUTIVO',
            f'Plan de Desarrollo Institucional {self.año}'
        )
        self._footer()

        cumpl  = float(metricas.get('cumplimiento_promedio', 0))
        total  = int(metricas.get('total_indicadores', 0))
        cumpl_n = int(metricas.get('indicadores_cumplidos', 0))
        en_prog = int(metricas.get('en_progreso', 0))
        atenc   = int(metricas.get('no_cumplidos', 0))
        c_sem   = color_semaforo(cumpl)

        # --- Anillo principal ---
        ring_sz = 6.8 * cm
        rx = self.MX
        ry = cont_top - ring_sz - 6 * mm
        renderPDF.draw(self._ring_drawing(cumpl, ring_sz), self.c, rx, ry)
        # Texto en el centro del anillo
        cx = rx + ring_sz / 2
        cy = ry + ring_sz / 2
        self.c.setFont('Helvetica-Bold', 16)
        self.c.setFillColor(c_sem)
        self.c.drawCentredString(cx, cy + 4, f'{cumpl:.1f}%')
        self.c.setFont('Helvetica', 6.5)
        self.c.setFillColor(C_GRAY)
        self.c.drawCentredString(cx, cy - 9, 'Cumplimiento')
        self.c.drawCentredString(cx, cy - 17, 'Global PDI')
        # Badge de estado debajo
        bw, bh = 30 * mm, 7 * mm
        bx = cx - bw / 2
        by = ry - 11 * mm
        self._shadow_card(bx, by, bw, bh, c_sem, radius=2.5 * mm)
        self.c.setFont('Helvetica-Bold', 7)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(cx, by + bh / 2 - 2, texto_estado(cumpl))

        # --- Fichas KPI ---
        kpi_x     = rx + ring_sz + 8 * mm
        kpi_w     = (self.W - kpi_x - self.MX) / 2 - 2 * mm
        kpi_h     = 20 * mm
        kpi_gap   = 4 * mm
        kpi_start = cont_top - 8 * mm

        kpis = [
            (str(total),   'Total Indicadores',  C_ACCENT),
            (str(cumpl_n), 'Cumplidos ≥100%',     C_VERDE),
            (str(en_prog), 'En Progreso 80–99%',  C_NARANJA),
            (str(atenc),   'Requieren Atención',  C_ROJO),
        ]
        for i, (val, lbl, col) in enumerate(kpis):
            col_i = i % 2
            row_i = i // 2
            kx = kpi_x + col_i * (kpi_w + kpi_gap)
            ky = kpi_start - row_i * (kpi_h + kpi_gap) - kpi_h
            self._kpi_card(kx, ky, kpi_w, kpi_h, val, lbl, col)

        # --- Tarjeta de análisis ejecutivo IA ---
        ai_top = min(ry - 14 * mm, cont_top - ring_sz - 20 * mm)
        ai_bottom = self.H_FOOTER + 4 * mm
        ai_h = ai_top - ai_bottom
        if analisis_texto and ai_h > 20 * mm:
            card_x = self.MX
            card_w = self.W - 2 * self.MX
            self._shadow_card(card_x, ai_bottom, card_w, ai_h,
                              colors.HexColor('#E8F5E9'), radius=3.5 * mm)
            self.c.setFillColor(C_VERDE)
            self.c.roundRect(card_x, ai_bottom, 3 * mm, ai_h, 2 * mm, fill=1, stroke=0)
            label_y = ai_bottom + ai_h - 5.5 * mm
            self.c.setFont('Helvetica-Bold', 8)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(card_x + 6 * mm, label_y, 'ANÁLISIS EJECUTIVO IA')
            self.c.setFont('Helvetica-Oblique', 6.5)
            self.c.setFillColor(C_GRAY)
            self.c.drawRightString(card_x + card_w - 3 * mm, label_y,
                                   'Generado con Inteligencia Artificial')
            self._wrap_paragraph(
                analisis_texto,
                x=card_x + 6 * mm,
                y_top=label_y - 3 * mm,
                max_w=card_w - 9 * mm,
                max_h=ai_h - 10 * mm,
                size=7.5,
                color=C_DARK,
            )
        elif not analisis_texto and ai_h > 10 * mm:
            # Sin análisis: pequeño mensaje informativo
            self.c.setFont('Helvetica-Oblique', 7.5)
            self.c.setFillColor(C_GRAY)
            self.c.drawCentredString(
                self.W / 2, ai_bottom + ai_h / 2,
                'Active el análisis IA para ver el resumen ejecutivo inteligente.'
            )

        self._new_page()

    def pagina_cumplimiento_lineas(self, df_lineas: pd.DataFrame):
        """
        Página de resumen circular: fondo navy, grid 3×2 (o 3×N) con anillos
        por línea estratégica (estilo visual del dashboard).
        """
        if df_lineas is None or df_lineas.empty:
            return

        # Fondo navy completo
        self.c.setFillColor(C_NAVY)
        self.c.rect(0, 0, self.W, self.H, fill=1, stroke=0)

        # Pie de página (sobre fondo navy)
        self.c.setFont('Helvetica', 6.5)
        self.c.setFillColor(colors.HexColor('#6a8aac'))
        fecha = datetime.now().strftime('%d/%m/%Y')
        self.c.drawString(self.MX, self.H_FOOTER - 4 * mm,
                          f'PDI {self.año} | Cumplimiento por Línea Estratégica')
        self.c.drawRightString(self.W - self.MX, self.H_FOOTER - 4 * mm,
                               f'Página {self._page} | Gerencia de Planeación | {fecha}')

        # Título
        self.c.setFillColor(C_WHITE)
        self.c.setFont('Helvetica-Bold', 15)
        self.c.drawCentredString(self.W / 2, self.H - 14 * mm,
                                 'CUMPLIMIENTO POR LÍNEA ESTRATÉGICA')
        self.c.setFont('Helvetica', 8.5)
        self.c.setFillColor(colors.HexColor('#8aacc8'))
        self.c.drawCentredString(self.W / 2, self.H - 20 * mm,
                                 f'Plan de Desarrollo Institucional {self.año}')

        # --- Grid de tarjetas ---
        lineas = [(str(r.get('Linea', r.get('Línea', ''))),
                   float(r.get('Cumplimiento', 0) or 0),
                   int(r.get('Total_Indicadores', 0) or 0))
                  for _, r in df_lineas.iterrows()]

        N_COLS   = 3
        N_ROWS   = (len(lineas) + N_COLS - 1) // N_COLS
        MX_GRID  = 12 * mm
        GAP      = 5 * mm
        avail_w  = self.W - 2 * MX_GRID
        avail_h  = self.H - 26 * mm - self.H_FOOTER
        card_w   = (avail_w - (N_COLS - 1) * GAP) / N_COLS
        card_h   = min((avail_h - (N_ROWS - 1) * GAP) / N_ROWS, 115 * mm)

        RING_SZ  = min(card_w * 0.62, 40 * mm)

        for idx, (nom, pct, n_ind) in enumerate(lineas):
            col_i   = idx % N_COLS
            row_i   = idx // N_COLS
            card_x  = MX_GRID + col_i * (card_w + GAP)
            card_y  = self.H - 26 * mm - (row_i + 1) * card_h - row_i * GAP

            col     = color_linea(nom)
            c_sem   = color_semaforo(pct)
            nom_d   = nombre_display(nom)

            # Sombra de tarjeta (tono navy oscuro)
            self.c.setFillColor(colors.HexColor('#061525'))
            self.c.roundRect(card_x + 2 * mm, card_y - 2 * mm,
                             card_w, card_h, 4 * mm, fill=1, stroke=0)
            # Tarjeta blanca
            self.c.setFillColor(C_WHITE)
            self.c.roundRect(card_x, card_y, card_w, card_h, 4 * mm, fill=1, stroke=0)
            # Banda de color superior
            self.c.setFillColor(col)
            self.c.roundRect(card_x, card_y + card_h - 11 * mm,
                             card_w, 11 * mm, 3 * mm, fill=1, stroke=0)
            # Relleno inferior de la banda (elimina esquinas redondeadas abajo)
            self.c.rect(card_x, card_y + card_h - 11 * mm,
                        card_w, 4 * mm, fill=1, stroke=0)

            # Nombre de línea en la banda
            self.c.setFillColor(C_WHITE)
            self.c.setFont('Helvetica-Bold', 7.5)
            # Dividir en 2 líneas si es largo
            palabras = nom_d.split()
            mid = len(palabras) // 2
            linea1 = ' '.join(palabras[:mid]) if mid > 0 else nom_d
            linea2 = ' '.join(palabras[mid:])
            if len(palabras) <= 2:
                linea1 = nom_d
                linea2 = ''
            self.c.drawCentredString(card_x + card_w / 2,
                                     card_y + card_h - 5.5 * mm, linea1)
            if linea2:
                self.c.setFont('Helvetica', 6.5)
                self.c.drawCentredString(card_x + card_w / 2,
                                         card_y + card_h - 9.5 * mm, linea2)

            # Anillo centrado
            ring_x = card_x + (card_w - RING_SZ) / 2
            ring_y = card_y + card_h - 11 * mm - RING_SZ - 4 * mm
            renderPDF.draw(self._ring_drawing(pct, RING_SZ), self.c, ring_x, ring_y)

            # Texto porcentaje en centro del anillo
            cx_c = ring_x + RING_SZ / 2
            cy_c = ring_y + RING_SZ / 2
            self.c.setFont('Helvetica-Bold', 12)
            self.c.setFillColor(c_sem)
            self.c.drawCentredString(cx_c, cy_c + 2, f'{pct:.0f}%')
            self.c.setFont('Helvetica', 5.5)
            self.c.setFillColor(C_GRAY)
            self.c.drawCentredString(cx_c, cy_c - 8, 'cumplimiento')

            # Indicadores
            ind_y = ring_y - 5 * mm
            self.c.setFont('Helvetica', 6.5)
            self.c.setFillColor(C_GRAY)
            self.c.drawCentredString(card_x + card_w / 2, ind_y,
                                     f'{n_ind} indicadores')

            # Badge estado
            bw_c, bh_c = card_w * 0.7, 6 * mm
            bx_c = card_x + (card_w - bw_c) / 2
            by_c = card_y + 3 * mm
            self.c.setFillColor(c_sem)
            self.c.roundRect(bx_c, by_c, bw_c, bh_c, 2 * mm, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 6)
            self.c.setFillColor(C_WHITE)
            self.c.drawCentredString(card_x + card_w / 2,
                                     by_c + bh_c / 2 - 2, texto_estado(pct))

        self._new_page()

    def pagina_linea(self, nombre: str, cumplimiento: float, total_ind: int,
                     objetivos: List[Dict], proyectos: List[Dict],
                     analisis: str):
        """
        Página detallada por línea estratégica.
        Layout:
          - Banda header (color de línea)
          - TOP: Anillo (derecha) + KPI mini-fichas (izquierda)
          - TABLA: Objetivo | Meta | Indicadores
          - SECCIÓN: Proyectos estratégicos
          - FINAL: Tarjeta de análisis IA (anclada al fondo)
        """
        col_linea = color_linea(nombre)
        nom_d     = nombre_display(nombre)
        cont_top  = self._header_band(
            col_linea,
            nom_d.upper(),
            f'Cumplimiento: {cumplimiento:.1f}%  |  {total_ind} indicadores'
        )
        self._footer(nom_d)
        c_sem = color_semaforo(cumplimiento)

        # ── Anillo (esquina superior derecha) ─────────────────────────
        RING_SZ  = 3.8 * cm
        ring_rx  = self.W - RING_SZ - self.MX
        ring_ry  = cont_top - RING_SZ - 5 * mm
        cx_r     = ring_rx + RING_SZ / 2
        cy_r     = ring_ry + RING_SZ / 2
        badge_by = ring_ry - 8 * mm

        renderPDF.draw(self._ring_drawing(cumplimiento, RING_SZ), self.c, ring_rx, ring_ry)
        self.c.setFont('Helvetica-Bold', 12)
        self.c.setFillColor(c_sem)
        self.c.drawCentredString(cx_r, cy_r + 3, f'{cumplimiento:.1f}%')
        self.c.setFont('Helvetica', 6)
        self.c.setFillColor(C_GRAY)
        self.c.drawCentredString(cx_r, cy_r - 9, texto_estado(cumplimiento))
        bw, bh = 30 * mm, 6.5 * mm
        self._shadow_card(cx_r - bw / 2, badge_by, bw, bh, c_sem, radius=2 * mm)
        self.c.setFont('Helvetica-Bold', 6.5)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(cx_r, badge_by + bh / 2 - 2, texto_estado(cumplimiento))

        # ── KPI mini-fichas (izquierda) — basadas en indicadores ─────
        left_w  = ring_rx - self.MX - 6 * mm
        kpi_w   = left_w / 3 - 2 * mm
        kpi_h   = 16 * mm
        kpi_y   = cont_top - 6 * mm - kpi_h
        # Recolectar todos los indicadores del nivel 4
        all_inds = [ind
                    for obj in objetivos
                    for meta in obj.get('metas', [])
                    for ind in meta.get('indicadores', [])]
        n_cumpl_ind = sum(1 for i in all_inds if float(i.get('cumplimiento', 0)) >= 100)
        n_aten_ind  = sum(1 for i in all_inds if float(i.get('cumplimiento', 0)) < 80)
        for i, (val, lbl, col) in enumerate([
            (str(total_ind),      'Total Indicadores', col_linea),
            (str(n_cumpl_ind),    'Cumplidos ≥100%',   C_VERDE),
            (str(n_aten_ind),     'Con Atención',      C_ROJO),
        ]):
            self._kpi_card(self.MX + i * (kpi_w + 2 * mm), kpi_y, kpi_w, kpi_h, val, lbl, col)

        # ── Inicio del contenido bajo anillo ──────────────────────────
        AI_H      = 52 * mm
        AI_BOTTOM = self.H_FOOTER + 3 * mm
        AI_TOP    = AI_BOTTOM + AI_H
        TABLE_BOTTOM = AI_TOP + 4 * mm
        y_cur = badge_by - 5 * mm

        # ── Cascada: N2 Objetivo → N3 Meta → N4 Indicadores ──────────
        # Alturas de fila por nivel
        OBJ_H  = 9 * mm   # Nivel 2: Objetivo estratégico
        META_H = 7 * mm   # Nivel 3: Meta estratégica
        HDR_H  = 6 * mm   # Encabezado de columnas (Nivel 4)
        ROW_H  = 6 * mm   # Fila de indicador (Nivel 4)

        # Columnas de Nivel 4: Indicador | Meta | Ejecución | Cumpl. | Estado
        IND_COL_W = [84 * mm, 20 * mm, 20 * mm, 25 * mm, 17 * mm]
        IND_TBL_W = sum(IND_COL_W)   # 166 mm

        if objetivos:
            self.c.setFont('Helvetica-Bold', 9)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(self.MX, y_cur, 'OBJETIVOS E INDICADORES')
            y_cur -= 5 * mm

            for obj in objetivos:
                # Necesitamos espacio mínimo para header + 1 meta + 1 fila
                if y_cur - (OBJ_H + META_H + HDR_H + ROW_H) < TABLE_BOTTOM:
                    break

                obj_pct = float(obj.get('cumplimiento', 0))
                obj_sem = color_semaforo(obj_pct)
                obj_txt = limpiar(str(obj.get('objetivo', '')))

                # ── Nivel 2: fila de Objetivo (fondo = color de línea) ─
                self.c.setFillColor(col_linea)
                self.c.rect(self.MX, y_cur - OBJ_H, IND_TBL_W, OBJ_H, fill=1, stroke=0)
                # Punto semáforo a la derecha
                self.c.setFillColor(obj_sem)
                self.c.circle(self.MX + IND_TBL_W - 5 * mm,
                              y_cur - OBJ_H / 2, 2.5 * mm, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 7)
                self.c.setFillColor(C_WHITE)
                obj_s = obj_txt[:90] + ('…' if len(obj_txt) > 90 else '')
                self.c.drawString(self.MX + 2.5 * mm,
                                  y_cur - OBJ_H + 3 * mm, obj_s)
                y_cur -= OBJ_H

                for meta in obj.get('metas', []):
                    if y_cur - (META_H + HDR_H + ROW_H) < TABLE_BOTTOM:
                        break

                    meta_txt = limpiar(str(meta.get('meta_pdi', '')))

                    # ── Nivel 3: fila de Meta (fondo más claro) ────────
                    meta_bg = _light_color(col_linea, 0.60)
                    self.c.setFillColor(meta_bg)
                    self.c.rect(self.MX, y_cur - META_H, IND_TBL_W, META_H,
                                fill=1, stroke=0)
                    self.c.setFont('Helvetica-Bold', 6.5)
                    self.c.setFillColor(C_WHITE)
                    if meta_txt:
                        meta_label = 'META: ' + meta_txt[:85] + ('…' if len(meta_txt) > 85 else '')
                    else:
                        meta_label = 'META ESTRATÉGICA'
                    self.c.drawString(self.MX + 3 * mm,
                                      y_cur - META_H + 2 * mm, meta_label)
                    y_cur -= META_H

                    inds = meta.get('indicadores', [])
                    if not inds:
                        continue

                    # ── Nivel 4: encabezado de columnas ────────────────
                    if y_cur - HDR_H < TABLE_BOTTOM:
                        break
                    self.c.setFillColor(C_DARK)
                    self.c.rect(self.MX, y_cur - HDR_H, IND_TBL_W, HDR_H,
                                fill=1, stroke=0)
                    self.c.setFont('Helvetica-Bold', 6)
                    self.c.setFillColor(C_WHITE)
                    hx = self.MX
                    for hdr, cw in zip(['Indicador', 'Meta', 'Ejecución',
                                        'Cumplimiento', 'Estado'], IND_COL_W):
                        self.c.drawCentredString(hx + cw / 2,
                                                 y_cur - HDR_H + 2 * mm, hdr)
                        hx += cw
                    y_cur -= HDR_H

                    # ── Nivel 4: filas de indicadores ──────────────────
                    for ridx, ind in enumerate(inds):
                        if y_cur - ROW_H < TABLE_BOTTOM:
                            break
                        ind_pct  = float(ind.get('cumplimiento', 0))
                        ind_scol = color_semaforo(ind_pct)
                        bg = C_BG if ridx % 2 == 0 else C_WHITE

                        self.c.setFillColor(bg)
                        self.c.rect(self.MX, y_cur - ROW_H, IND_TBL_W, ROW_H,
                                    fill=1, stroke=0)
                        self.c.setFillColor(ind_scol)
                        self.c.rect(self.MX, y_cur - ROW_H, 1.5 * mm, ROW_H,
                                    fill=1, stroke=0)
                        self.c.setStrokeColor(C_LIGHT)
                        self.c.setLineWidth(0.3)
                        self.c.rect(self.MX, y_cur - ROW_H, IND_TBL_W, ROW_H,
                                    fill=0, stroke=1)

                        ind_name = limpiar(str(ind.get('nombre', '')))
                        ind_name = ind_name[:57] + ('…' if len(ind_name) > 57 else '')
                        self.c.setFont('Helvetica', 6)
                        self.c.setFillColor(C_DARK)
                        self.c.drawString(self.MX + 2.5 * mm,
                                          y_cur - ROW_H + 1.8 * mm, ind_name)

                        meta_v = ind.get('meta_valor')
                        ejec_v = ind.get('ejecucion')
                        vals = [
                            f'{float(meta_v):.1f}' if (
                                meta_v is not None and
                                str(meta_v) not in ('nan', 'None', '')
                            ) else '-',
                            f'{float(ejec_v):.1f}' if (
                                ejec_v is not None and
                                str(ejec_v) not in ('nan', 'None', '')
                            ) else '-',
                            f'{ind_pct:.0f}%',
                            '✓' if ind_pct >= 100 else ('⚠' if ind_pct >= 80 else '✗'),
                        ]
                        hx = self.MX + IND_COL_W[0]
                        for j, (val, cw) in enumerate(zip(vals, IND_COL_W[1:])):
                            fnt = 'Helvetica-Bold' if j >= 2 else 'Helvetica'
                            clr = ind_scol if j >= 2 else C_DARK
                            self.c.setFont(fnt, 6.5)
                            self.c.setFillColor(clr)
                            self.c.drawCentredString(hx + cw / 2,
                                                     y_cur - ROW_H + 1.8 * mm, val)
                            hx += cw
                        y_cur -= ROW_H

        # ── Sección de Proyectos ───────────────────────────────────────
        if proyectos and y_cur - 8 * mm > TABLE_BOTTOM:
            y_cur -= 4 * mm
            self.c.setFont('Helvetica-Bold', 9)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(self.MX, y_cur, 'PROYECTOS ESTRATÉGICOS')
            y_cur -= 5 * mm

            PROW_H  = 6.5 * mm
            PCOL_W  = [108 * mm, 25 * mm, 25 * mm]
            PTBL_W  = sum(PCOL_W)

            # Encabezado proyectos
            self._shadow_card(self.MX, y_cur - PROW_H, PTBL_W, PROW_H,
                              C_ACCENT, radius=2 * mm)
            self.c.setFont('Helvetica-Bold', 7)
            self.c.setFillColor(C_WHITE)
            phx = self.MX
            for phdr, pcw in zip(['Proyecto', 'Cumplimiento', 'Estado'], PCOL_W):
                self.c.drawCentredString(phx + pcw / 2, y_cur - PROW_H + 2.5 * mm, phdr)
                phx += pcw
            y_cur -= PROW_H

            for pidx, proy in enumerate(proyectos[:6]):
                if y_cur - PROW_H < TABLE_BOTTOM:
                    break
                p_pct = float(proy.get('cumplimiento', 0))
                p_col = color_semaforo(p_pct)
                p_bg  = C_BG if pidx % 2 == 0 else C_WHITE

                self.c.setFillColor(p_bg)
                self.c.rect(self.MX, y_cur - PROW_H, PTBL_W, PROW_H, fill=1, stroke=0)
                self.c.setFillColor(p_col)
                self.c.rect(self.MX, y_cur - PROW_H, 1.5 * mm, PROW_H, fill=1, stroke=0)
                self.c.setStrokeColor(C_LIGHT)
                self.c.setLineWidth(0.3)
                self.c.rect(self.MX, y_cur - PROW_H, PTBL_W, PROW_H, fill=0, stroke=1)

                p_nom = limpiar(str(proy.get('nombre', '')))
                p_nom = p_nom[:65] + ('…' if len(p_nom) > 65 else '')
                self.c.setFont('Helvetica', 6)
                self.c.setFillColor(C_DARK)
                self.c.drawString(self.MX + 3 * mm, y_cur - PROW_H + 2 * mm, p_nom)

                self.c.setFont('Helvetica-Bold', 6.5)
                self.c.setFillColor(p_col)
                self.c.drawCentredString(
                    self.MX + PCOL_W[0] + PCOL_W[1] / 2,
                    y_cur - PROW_H + 2 * mm, f'{p_pct:.0f}%'
                )
                est = '✓' if p_pct >= 100 else ('⚠' if p_pct >= 80 else '✗')
                self.c.setFont('Helvetica-Bold', 8)
                self.c.drawCentredString(
                    self.MX + PCOL_W[0] + PCOL_W[1] + PCOL_W[2] / 2,
                    y_cur - PROW_H + 2 * mm, est
                )
                y_cur -= PROW_H

        # ── Tarjeta de análisis IA (anclada al fondo) ──────────────────
        if analisis:
            card_x = self.MX
            card_w = self.W - 2 * self.MX
            self._shadow_card(card_x, AI_BOTTOM, card_w, AI_H,
                              colors.HexColor('#E3F2FD'), radius=3.5 * mm)
            self.c.setFillColor(col_linea)
            self.c.roundRect(card_x, AI_BOTTOM, 3 * mm, AI_H, 2 * mm, fill=1, stroke=0)
            label_y = AI_BOTTOM + AI_H - 5.5 * mm
            self.c.setFont('Helvetica-Bold', 8)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(card_x + 6 * mm, label_y, 'ANÁLISIS ESTRATÉGICO IA')
            self.c.setFont('Helvetica-Oblique', 6.5)
            self.c.setFillColor(C_GRAY)
            self.c.drawRightString(card_x + card_w - 3 * mm, label_y,
                                   'Generado con Inteligencia Artificial')
            self._wrap_paragraph(
                analisis,
                x=card_x + 6 * mm,
                y_top=label_y - 3 * mm,
                max_w=card_w - 9 * mm,
                max_h=AI_H - 10 * mm,
                size=7.5,
                color=C_DARK,
            )

        self._new_page()

    def tabla_indicadores(self, df_indicadores: pd.DataFrame):
        """Tabla completa de indicadores, paginada, agrupada por línea."""
        if df_indicadores is None or df_indicadores.empty:
            return

        # Detectar columnas
        def _col(df, *names):
            for n in names:
                if n in df.columns:
                    return n
            return None

        c_ind   = _col(df_indicadores, 'Indicador', 'indicador', 'INDICADOR')
        c_linea = _col(df_indicadores, 'Linea', 'Línea', 'linea')
        c_meta  = _col(df_indicadores, 'Meta', 'meta', 'META')
        c_ejec  = _col(df_indicadores, 'Ejecucion', 'Ejecución', 'ejecucion', 'EJECUCION')
        c_cumpl = _col(df_indicadores, 'Cumplimiento', 'cumplimiento', 'CUMPLIMIENTO')

        # Ordenar por línea si existe
        if c_linea:
            df_sorted = df_indicadores.sort_values(c_linea)
        else:
            df_sorted = df_indicadores

        # Constantes de tabla
        COL_W  = [87 * mm, 17 * mm, 17 * mm, 16 * mm, 14 * mm]
        ROW_H  = 6 * mm
        HDR_H  = 8 * mm
        BOTTOM = self.H_FOOTER + 6 * mm

        def _draw_page_header():
            cont = self._header_band(
                C_NAVY, 'DETALLE DE INDICADORES',
                f'Total: {len(df_indicadores)} indicadores'
            )
            self._footer('Detalle de Indicadores')
            return cont

        def _draw_table_header(y):
            self._shadow_card(self.MX, y - HDR_H, sum(COL_W), HDR_H, C_NAVY, radius=2 * mm)
            self.c.setFont('Helvetica-Bold', 7.5)
            self.c.setFillColor(C_WHITE)
            hx = self.MX
            for hdr, cw in zip(['Indicador', 'Meta', 'Ejecución', '%', 'Estado'], COL_W):
                self.c.drawCentredString(hx + cw / 2, y - HDR_H + 3 * mm, hdr)
                hx += cw
            return y - HDR_H

        y = _draw_page_header()
        y = _draw_table_header(y)

        current_linea = None

        for idx, (_, row) in enumerate(df_sorted.iterrows()):
            # Subencabezado por línea
            if c_linea:
                linea_nom = limpiar(str(row.get(c_linea, '')))
                if linea_nom != current_linea:
                    current_linea = linea_nom
                    sub_h = 6.5 * mm
                    if y - sub_h < BOTTOM:
                        self._new_page()
                        y = _draw_page_header()
                        y = _draw_table_header(y)
                    sub_col = color_linea(linea_nom)
                    self.c.setFillColor(sub_col)
                    self.c.rect(self.MX, y - sub_h, sum(COL_W), sub_h, fill=1, stroke=0)
                    self.c.setFont('Helvetica-Bold', 7.5)
                    self.c.setFillColor(C_WHITE)
                    self.c.drawString(self.MX + 3 * mm, y - sub_h + 2 * mm, linea_nom)
                    y -= sub_h

            # Salto de página
            if y - ROW_H < BOTTOM:
                self._new_page()
                y = _draw_page_header()
                y = _draw_table_header(y)

            pct    = float(row.get(c_cumpl, 0) or 0) if c_cumpl else 0
            c_row  = C_BG if idx % 2 == 0 else C_WHITE
            c_s    = color_semaforo(pct)

            self.c.setFillColor(c_row)
            self.c.rect(self.MX, y - ROW_H, sum(COL_W), ROW_H, fill=1, stroke=0)
            self.c.setFillColor(c_s)
            self.c.rect(self.MX, y - ROW_H, 1.2 * mm, ROW_H, fill=1, stroke=0)
            self.c.setStrokeColor(C_LIGHT)
            self.c.setLineWidth(0.3)
            self.c.rect(self.MX, y - ROW_H, sum(COL_W), ROW_H, fill=0, stroke=1)

            # Nombre del indicador
            ind_txt = limpiar(str(row.get(c_ind, '') if c_ind else ''))[:56]
            if c_ind and len(limpiar(str(row.get(c_ind, '')))) > 56:
                ind_txt += '…'
            self.c.setFont('Helvetica', 6)
            self.c.setFillColor(C_DARK)
            self.c.drawString(self.MX + 2.5 * mm, y - ROW_H + 1.8 * mm, ind_txt)

            # Columnas numéricas
            meta = row.get(c_meta, None) if c_meta else None
            ejec = row.get(c_ejec, None) if c_ejec else None
            vals = [
                f'{float(meta):.1f}' if meta is not None else '-',
                f'{float(ejec):.1f}' if ejec is not None else '-',
                f'{pct:.1f}%',
                '✓' if pct >= 100 else ('⚠' if pct >= 80 else '✗'),
            ]
            hx = self.MX + COL_W[0]
            for j, (val, cw) in enumerate(zip(vals, COL_W[1:])):
                fnt = 'Helvetica-Bold' if j == 3 else 'Helvetica'
                clr = c_s if j == 3 else C_DARK
                self.c.setFont(fnt, 6.5)
                self.c.setFillColor(clr)
                self.c.drawCentredString(hx + cw / 2, y - ROW_H + 1.8 * mm, val)
                hx += cw

            y -= ROW_H

        self._new_page()

    def conclusiones(self, metricas: Dict, df_lineas: pd.DataFrame = None):
        """Página: Conclusiones, recomendaciones y glosario."""
        cont_top = self._header_band(C_NAVY, 'CONCLUSIONES Y RECOMENDACIONES', '')
        self._footer('Conclusiones')

        cumpl  = float(metricas.get('cumplimiento_promedio', 0))
        total  = int(metricas.get('total_indicadores', 0))
        cumpl_n = int(metricas.get('indicadores_cumplidos', 0))
        c_sem  = color_semaforo(cumpl)

        y = cont_top - 6 * mm

        # --- Badge de cumplimiento global ---
        bw, bh = 42 * mm, 19 * mm
        self._shadow_card(self.MX, y - bh, bw, bh, c_sem, radius=4 * mm)
        self.c.setFont('Helvetica-Bold', 22)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(self.MX + bw / 2, y - bh + 9 * mm, f'{cumpl:.1f}%')
        self.c.setFont('Helvetica', 6.5)
        self.c.drawCentredString(self.MX + bw / 2, y - bh + 4 * mm, 'Cumplimiento Global PDI')

        # Texto conclusiones
        lines = [
            ('Helvetica-Bold', 11, C_NAVY,
             f'Resultados del Plan de Desarrollo Institucional {self.año}'),
            ('Helvetica', 8.5, C_DARK, ''),
            ('Helvetica', 8.5, C_DARK,
             f'El PDI 2022-{self.año} alcanzó un cumplimiento global del {cumpl:.1f}%, '
             f'evidenciando el compromiso'),
            ('Helvetica', 8.5, C_DARK,
             f'institucional con los objetivos estratégicos definidos. '
             f'{cumpl_n} de {total} indicadores'),
            ('Helvetica', 8.5, C_DARK, 'alcanzaron o superaron sus metas establecidas.'),
        ]
        tx = self.MX + bw + 8 * mm
        ty = y - 4 * mm
        for fnt, sz, clr, txt in lines:
            self.c.setFont(fnt, sz)
            self.c.setFillColor(clr)
            self.c.drawString(tx, ty, txt)
            ty -= sz * 1.55

        y -= bh + 8 * mm

        # --- Recomendaciones ---
        self.c.setFont('Helvetica-Bold', 9.5)
        self.c.setFillColor(C_NAVY)
        self.c.drawString(self.MX, y, 'RECOMENDACIONES ESTRATÉGICAS')
        y -= 6 * mm

        recomendaciones = [
            ('Fortalecer seguimiento',
             'Implementar revisiones trimestrales de indicadores en progreso.'),
            ('Planes de acción',
             'Desarrollar acciones correctivas para indicadores que requieren atención.'),
            ('Mejores prácticas',
             'Documentar y replicar estrategias de las líneas con mejor desempeño.'),
            ('Alineación presupuestal',
             'Garantizar los recursos necesarios para el cumplimiento de metas pendientes.'),
        ]
        CARD_H = 12 * mm
        CARD_GAP = 3 * mm
        for titulo, desc in recomendaciones:
            if y - CARD_H < self.H_FOOTER + 50 * mm:
                break
            self._shadow_card(self.MX, y - CARD_H,
                              self.W - 2 * self.MX, CARD_H, C_BG, radius=2 * mm)
            self.c.setFillColor(C_ACCENT)
            self.c.roundRect(self.MX, y - CARD_H, 2 * mm, CARD_H, 1 * mm, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 8)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(self.MX + 4 * mm, y - 5 * mm, f'{titulo}:')
            self.c.setFont('Helvetica', 7.5)
            self.c.setFillColor(C_DARK)
            self.c.drawString(self.MX + 4 * mm, y - 10 * mm, desc)
            y -= CARD_H + CARD_GAP

        y -= 8 * mm

        # --- Glosario ---
        if y > self.H_FOOTER + 40 * mm:
            self.c.setFont('Helvetica-Bold', 9.5)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(self.MX, y, 'GLOSARIO DE SIGLAS')
            y -= 5 * mm

            items   = list(GLOSARIO.items())
            cols    = 2
            col_w   = (self.W - 2 * self.MX) / cols
            row_h_g = 8.5 * mm

            for i, (sigla, desc) in enumerate(items):
                gx = self.MX + (i % cols) * col_w
                gy = y - (i // cols) * row_h_g
                if gy < self.H_FOOTER + 2 * mm:
                    break
                self.c.setFont('Helvetica-Bold', 8)
                self.c.setFillColor(C_ACCENT)
                self.c.drawString(gx, gy, f'{sigla}:')
                self.c.setFont('Helvetica', 7)
                self.c.setFillColor(C_DARK)
                desc_s = desc[:48] + ('…' if len(desc) > 48 else '')
                self.c.drawString(gx + 14 * mm, gy, desc_s)

        self._new_page()

    def generar(self) -> bytes:
        """Finaliza y retorna los bytes del PDF."""
        self.c.save()
        return self.buffer.getvalue()


# ============================================================
# FUNCIÓN PRINCIPAL DE EXPORTACIÓN
# ============================================================

def exportar_informe_pdf_reportlab(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    año: int = 2025,
    df_cascada: Optional[pd.DataFrame] = None,
    analisis_lineas: Optional[Dict[str, str]] = None,
    df_unificado: Optional[pd.DataFrame] = None,
) -> bytes:
    """
    Genera el informe PDF ejecutivo completo con ReportLab.

    Args:
        metricas: Diccionario con métricas generales del PDI.
        df_lineas: DataFrame con líneas estratégicas y su cumplimiento.
        df_indicadores: DataFrame con todos los indicadores del año.
        analisis_texto: Texto de análisis ejecutivo general (IA).
        año: Año del informe.
        df_cascada: DataFrame cascada con jerarquía (Nivel, Linea, Objetivo, Meta_PDI, ...).
        analisis_lineas: Dict {nombre_linea: texto_analisis_IA}.
        df_unificado: DataFrame completo del PDI (para extraer proyectos por línea).

    Returns:
        bytes del PDF generado.
    """
    pdf = PDFReportePOLI(año)

    # 1. Portada
    portada_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Portada.png'
    )
    pdf.portada(portada_path if os.path.exists(portada_path) else None)

    # 2. Resumen ejecutivo (sin barras por línea; ahora solo KPIs + análisis IA)
    pdf.resumen_ejecutivo(metricas, analisis_texto=analisis_texto)

    # 3. Resumen circular por línea (página navy con grid de anillos)
    pdf.pagina_cumplimiento_lineas(df_lineas)

    # 4. Página detallada por línea estratégica
    if df_lineas is not None and not df_lineas.empty:
        nc = 'Nivel' if (df_cascada is not None and 'Nivel' in df_cascada.columns) else None
        lc = 'Linea' if (df_cascada is not None and 'Linea' in df_cascada.columns) else None

        for _, lr in df_lineas.iterrows():
            nom   = str(lr.get('Linea', lr.get('Línea', '')))
            cumpl = float(lr.get('Cumplimiento', 0) or 0)
            n_ind = int(lr.get('Total_Indicadores', 0) or 0)

            # ── Jerarquía: N2 Objetivo → N3 Meta_PDI → N4 Indicadores ──
            # Estructura: [{objetivo, cumplimiento, metas: [{meta_pdi, cumplimiento, indicadores[]}]}]
            objs = []
            _built_from_raw = False
            if df_unificado is not None and not df_unificado.empty and \
                    'Objetivo' in df_unificado.columns and 'Linea' in df_unificado.columns:
                # Filtrar por línea, año e indicadores (no proyectos)
                omask = df_unificado['Linea'] == nom
                if 'Año' in df_unificado.columns:
                    omask &= df_unificado['Año'] == año
                if 'Proyectos' in df_unificado.columns:
                    omask &= df_unificado['Proyectos'] == 0
                if 'Fuente' in df_unificado.columns:
                    omask &= df_unificado['Fuente'] == 'Avance'
                df_src = df_unificado[omask]

                _meta_col  = next((c for c in ['Meta', 'meta'] if c in df_src.columns), None)
                _ejec_col  = next((c for c in ['Ejecución', 'Ejecucion', 'ejecucion']
                                   if c in df_src.columns), None)
                _ind_col   = next((c for c in ['Indicador', 'indicador']
                                   if c in df_src.columns), None)
                _cumpl_col = 'Cumplimiento' if 'Cumplimiento' in df_src.columns else None
                _mpdi_col  = 'Meta_PDI' if 'Meta_PDI' in df_src.columns else None

                def _safe_val(v):
                    return None if (v is None or str(v) in ('nan', 'None', '')) else v

                if not df_src.empty and _ind_col:
                    for obj_name, df_obj in df_src.groupby('Objetivo', sort=True):
                        cumpl_obj = float(df_obj[_cumpl_col].mean()) if _cumpl_col else 0.0
                        metas_list = []

                        # Agrupar indicadores por Meta_PDI (Nivel 3)
                        if _mpdi_col and df_obj[_mpdi_col].notna().any():
                            for meta_val, df_meta in df_obj.groupby(_mpdi_col, sort=True):
                                cumpl_meta = float(df_meta[_cumpl_col].mean()) if _cumpl_col else 0.0
                                inds = []
                                for _, ir in df_meta.drop_duplicates(_ind_col).iterrows():
                                    inds.append({
                                        'nombre':       str(ir.get(_ind_col, '')),
                                        'meta_valor':   _safe_val(ir.get(_meta_col) if _meta_col else None),
                                        'ejecucion':    _safe_val(ir.get(_ejec_col) if _ejec_col else None),
                                        'cumplimiento': float(ir.get(_cumpl_col, 0) or 0) if _cumpl_col else 0.0,
                                    })
                                metas_list.append({
                                    'meta_pdi':     str(meta_val),
                                    'cumplimiento': cumpl_meta,
                                    'indicadores':  inds,
                                })
                        else:
                            # Sin Meta_PDI: todos los indicadores en un solo bloque
                            inds = []
                            for _, ir in df_obj.drop_duplicates(_ind_col).iterrows():
                                inds.append({
                                    'nombre':       str(ir.get(_ind_col, '')),
                                    'meta_valor':   _safe_val(ir.get(_meta_col) if _meta_col else None),
                                    'ejecucion':    _safe_val(ir.get(_ejec_col) if _ejec_col else None),
                                    'cumplimiento': float(ir.get(_cumpl_col, 0) or 0) if _cumpl_col else 0.0,
                                })
                            metas_list.append({
                                'meta_pdi':     '',
                                'cumplimiento': cumpl_obj,
                                'indicadores':  inds,
                            })

                        objs.append({
                            'objetivo':     str(obj_name),
                            'cumplimiento': cumpl_obj,
                            'metas':        metas_list,
                        })
                    _built_from_raw = True

            # Fallback: cascada cuando no hay df_unificado
            if not _built_from_raw and df_cascada is not None and \
                    not df_cascada.empty and nc and lc:
                mask2 = (df_cascada[nc] == 2) & (df_cascada[lc] == nom)
                for _, or_ in df_cascada[mask2].iterrows():
                    obj_name  = str(or_.get('Objetivo', nom))
                    cumpl_obj = float(or_.get('Cumplimiento', 0) or 0)
                    metas_fb  = []
                    if 'Meta_PDI' in df_cascada.columns:
                        mask3 = ((df_cascada[nc] == 3) & (df_cascada[lc] == nom) &
                                 (df_cascada['Objetivo'] == obj_name))
                        for _, mr in df_cascada[mask3].iterrows():
                            metas_fb.append({
                                'meta_pdi':     str(mr.get('Meta_PDI', '')),
                                'cumplimiento': float(mr.get('Cumplimiento', 0) or 0),
                                'indicadores':  [],
                            })
                    if not metas_fb:
                        metas_fb = [{'meta_pdi': '', 'cumplimiento': cumpl_obj, 'indicadores': []}]
                    objs.append({
                        'objetivo':     obj_name,
                        'cumplimiento': cumpl_obj,
                        'metas':        metas_fb,
                    })

            # ── Proyectos de esta línea (Proyectos=1 en df_unificado) ─
            proyectos = []
            if df_unificado is not None and not df_unificado.empty:
                has_proy = 'Proyectos' in df_unificado.columns
                has_lin  = 'Linea' in df_unificado.columns
                if has_proy and has_lin:
                    pmask = (df_unificado['Proyectos'] == 1) & (df_unificado['Linea'] == nom)
                    if 'Año' in df_unificado.columns:
                        pmask &= (df_unificado['Año'] == año)
                    id_col = 'Indicador' if 'Indicador' in df_unificado.columns else None
                    df_p = df_unificado[pmask]
                    if id_col:
                        df_p = df_p.drop_duplicates(id_col)
                    for _, pr in df_p.iterrows():
                        proyectos.append({
                            'nombre':       str(pr.get(id_col, '') if id_col else ''),
                            'cumplimiento': float(pr.get('Cumplimiento', 0) or 0),
                        })

            # ── Análisis IA por línea ─────────────────────────────────
            analisis_txt = ''
            if analisis_lineas:
                analisis_txt = analisis_lineas.get(nom, '')
                if not analisis_txt:
                    nom_n = _norm(nom)
                    for k, v in analisis_lineas.items():
                        if _norm(k) == nom_n:
                            analisis_txt = v
                            break

            pdf.pagina_linea(
                nombre=nom,
                cumplimiento=cumpl,
                total_ind=n_ind,
                objetivos=objs,
                proyectos=proyectos,
                analisis=analisis_txt,
            )

    # 5. Tabla de indicadores
    if df_indicadores is not None and not df_indicadores.empty:
        pdf.tabla_indicadores(df_indicadores)

    # 6. Conclusiones y glosario
    pdf.conclusiones(metricas, df_lineas)

    return pdf.generar()
