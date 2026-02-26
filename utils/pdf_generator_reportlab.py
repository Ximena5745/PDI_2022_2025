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
from typing import Dict, List, Optional, Any, Tuple

import pandas as pd

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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
from reportlab.lib.utils import ImageReader


# ============================================================
# PALETA DE COLORES
# ============================================================

# ── Semáforo (valores actualizados al sistema de diseño) ──────
C_VERDE   = colors.HexColor('#10B981')   # GREEN_SOLID
C_NARANJA = colors.HexColor('#F59E0B')   # AMBER_SOLID
C_ROJO    = colors.HexColor('#EF4444')   # RED_SOLID

# ── Institucionales ───────────────────────────────────────────
C_NAVY    = colors.HexColor('#0a2240')
C_ACCENT  = colors.HexColor('#1e88e5')
C_WHITE   = colors.white
C_BG      = colors.HexColor('#F8FAFC')
C_DARK    = colors.HexColor('#1E293B')   # TEXT_PRIMARY
C_GRAY    = colors.HexColor('#64748B')   # TEXT_SECONDARY
C_LIGHT   = colors.HexColor('#E2EAF4')   # TABLE_BORDER
C_SHADOW  = colors.HexColor('#cbd5e1')
C_RING_BG     = colors.HexColor('#e8ecef')
C_TABLE_ROW_ALT = colors.HexColor('#F0F5FB')
C_HDR_GRAD_END  = colors.HexColor('#1a3a5c')

# ── Paleta global del sistema de diseño ───────────────────────
NAVY_DARK      = colors.HexColor('#0a2240')
NAVY_MID       = colors.HexColor('#1a3a5c')
TEAL_ACCENT    = colors.HexColor('#00c9b1')
BG_PAGE        = colors.HexColor('#F8FAFC')
GREEN_SOLID    = colors.HexColor('#10B981')
GREEN_BG       = colors.HexColor('#DCFCE7')
GREEN_TEXT     = colors.HexColor('#166534')
AMBER_SOLID    = colors.HexColor('#F59E0B')
AMBER_BG       = colors.HexColor('#FEF3C7')
AMBER_TEXT     = colors.HexColor('#92400E')
RED_SOLID      = colors.HexColor('#EF4444')
RED_BG         = colors.HexColor('#FEE2E2')
RED_TEXT       = colors.HexColor('#991B1B')
GRAY_ND        = colors.HexColor('#94A3B8')
TABLE_BORDER   = colors.HexColor('#E2EAF4')
TEXT_PRIMARY   = colors.HexColor('#1E293B')
TEXT_SECONDARY = colors.HexColor('#64748B')
TEXT_MUTED     = colors.HexColor('#94A3B8')
AI_BORDER_COL  = colors.HexColor('#0891B2')
AI_BADGE_END   = colors.HexColor('#7C3AED')
AI_BG_COL      = colors.HexColor('#F0F9FF')
AI_TEXT_COL    = colors.HexColor('#334155')

# ── Orden obligatorio de líneas en todo el documento ──────────
ORDEN_LINEAS: List[str] = [
    'Calidad',
    'Expansión',
    'Educación para toda la vida',
    'Experiencia',
    'Transformación Organizacional',
    'Sostenibilidad',
]

# Por línea estratégica (con y sin tilde)
COLOR_LINEAS: Dict[str, colors.Color] = {
    'Expansión':                         colors.HexColor('#FBAF17'),
    'Expansion':                         colors.HexColor('#FBAF17'),
    'Transformación Organizacional':     colors.HexColor('#42F2F2'),
    'Transformacion Organizacional':     colors.HexColor('#42F2F2'),
    'Calidad':                           colors.HexColor('#EC0677'),
    'Experiencia':                       colors.HexColor('#1FB2DE'),
    'Sostenibilidad':                    colors.HexColor('#A6CE38'),
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


def is_light_color(c: colors.Color) -> bool:
    """True when luminance > 0.65 → color needs dark text (never use as direct text)."""
    return 0.299 * c.red + 0.587 * c.green + 0.114 * c.blue > 0.65


def contrasting_text(col: colors.Color) -> colors.Color:
    """Return legible text color for given background (dark on light, white on dark)."""
    return darken(col, 0.5) if is_light_color(col) else colors.white


def color_semaforo(pct: float) -> colors.Color:
    if pct >= 100:
        return GREEN_SOLID
    if pct >= 80:
        return AMBER_SOLID
    return RED_SOLID


def color_semaforo_bg(pct: float) -> colors.Color:
    if pct >= 100:
        return GREEN_BG
    if pct >= 80:
        return AMBER_BG
    return RED_BG


def color_semaforo_text(pct: float) -> colors.Color:
    if pct >= 100:
        return GREEN_TEXT
    if pct >= 80:
        return AMBER_TEXT
    return RED_TEXT


def texto_estado(pct: float) -> str:
    if pct >= 100:
        return 'CUMPLIDO'
    if pct >= 80:
        return 'EN PROGRESO'
    return 'ATENCIÓN'


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


def darken(c: colors.Color, factor: float = 0.3) -> colors.Color:
    """Mix color with black to get a darker shade."""
    r = max(0.0, c.red   * (1 - factor))
    g = max(0.0, c.green * (1 - factor))
    b = max(0.0, c.blue  * (1 - factor))
    return colors.Color(r, g, b)


def hex_to_rgb(hex_str: str):
    """Convert #RRGGBB hex string to (r, g, b) floats 0–1."""
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def fig_to_image(fig, w_pt: float = None, h_pt: float = None):
    """Render a matplotlib figure to a ReportLab ImageReader (PNG in memory)."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                transparent=True)
    buf.seek(0)
    return ImageReader(buf)


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
        # Título — tamaño adaptativo según longitud del texto
        self.c.setFillColor(C_WHITE)
        if subtitulo:
            # Escala font según largo del título (máx 13pt, mín 10pt)
            t_fsize = 13 if len(titulo) <= 24 else (11 if len(titulo) <= 34 else 9.5)
            self.c.setFont('Helvetica-Bold', t_fsize)
            # Alineación vertical: si font pequeño, ajustar posición
            t_y = y0 + 13 * mm if t_fsize >= 12 else y0 + 14 * mm
            self.c.drawString(self.MX, t_y, titulo)
            self.c.setFont('Helvetica', 7.5)
            self.c.setFillColor(colors.HexColor('#c8d8f0'))
            self.c.drawString(self.MX, y0 + 5.5 * mm, subtitulo)
        else:
            t_fsize = 14 if len(titulo) <= 28 else (11 if len(titulo) <= 38 else 9)
            self.c.setFont('Helvetica-Bold', t_fsize)
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
    # Primitivos visuales avanzados
    # ----------------------------------------------------------

    def _gradient_band(self, x: float, y: float, w: float, h: float,
                       c1: colors.Color, c2: colors.Color, steps: int = 32):
        """Fill rectangle with horizontal gradient from c1 (left) to c2 (right)."""
        for i in range(steps):
            t = i / steps
            r = c1.red   + (c2.red   - c1.red)   * t
            g = c1.green + (c2.green - c1.green) * t
            b = c1.blue  + (c2.blue  - c1.blue)  * t
            band_w = w / steps + 0.5
            self.c.setFillColorRGB(r, g, b)
            self.c.rect(x + w * i / steps, y, band_w, h, fill=1, stroke=0)

    def _status_circle(self, cx: float, cy: float, r: float, pct: float):
        """Draw a filled semaphore circle with ✓ / ⚠ / ✗ symbol."""
        col = color_semaforo(pct)
        bg  = _light_color(col, 0.75)
        self.c.setFillColor(bg)
        self.c.circle(cx, cy, r, fill=1, stroke=0)
        self.c.setFillColor(col)
        self.c.setFont('Helvetica-Bold', r * 1.15)
        sym = '\u2713' if pct >= 100 else ('\u26a0' if pct >= 80 else '\u2717')
        self.c.drawCentredString(cx, cy - r * 0.38, sym)

    def _ai_block(self, x: float, y: float, w: float, h: float,
                  texto: str, col_linea: colors.Color = None):
        """Draw AI analysis card: #F0F9FF bg, #0891B2 border, gradient badge."""
        # Background
        self.c.setFillColor(AI_BG_COL)
        self.c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=0)
        # Subtle full border
        self.c.setStrokeColor(colors.HexColor('#BAE6FD'))
        self.c.setLineWidth(0.5)
        self.c.roundRect(x, y, w, h, 3 * mm, fill=0, stroke=1)
        # Left accent bar 3px solid #0891B2
        self.c.setFillColor(AI_BORDER_COL)
        self.c.roundRect(x, y, 3, h, 1.5 * mm, fill=1, stroke=0)
        # Badge: gradient #0891B2 → #7C3AED
        badge_w, badge_h = 34 * mm, 6.5 * mm
        badge_x = x + 6 * mm
        badge_y = y + h - badge_h - 3.5 * mm
        self._gradient_band(badge_x, badge_y, badge_w, badge_h,
                            AI_BORDER_COL, AI_BADGE_END)
        self.c.setFillColor(C_WHITE)
        self.c.setFont('Helvetica-Bold', 6.5)
        self.c.drawString(badge_x + 2.5 * mm, badge_y + badge_h / 2 - 2.5,
                          '\u2736 IA  Análisis Estratégico')
        # Generation note (right-aligned, muted)
        self.c.setFont('Helvetica-Oblique', 5.5)
        self.c.setFillColor(TEXT_MUTED)
        self.c.drawRightString(x + w - 3 * mm, badge_y + badge_h / 2 - 2,
                               'Generado con Inteligencia Artificial')
        # Text content: italic 8.5pt #334155
        if texto:
            txt_y_top = badge_y - 2.5 * mm
            self._wrap_paragraph(
                texto,
                x=x + 6 * mm,
                y_top=txt_y_top,
                max_w=w - 10 * mm,
                max_h=txt_y_top - y - 2 * mm,
                font='Helvetica-Oblique',
                size=8,
                color=AI_TEXT_COL,
            )

    def _donut_chart_buf(self, cumpl_n: int, en_prog: int, atenc: int, total: int):
        """Return ImageReader of a 3-segment donut chart using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        try:
            nd = max(0, total - cumpl_n - en_prog - atenc)
            raw = [(cumpl_n, '#2e7d32', 'Cumplidos'),
                   (en_prog, '#F9A825', 'En Progreso'),
                   (atenc,   '#b71c1c', 'Atención'),
                   (nd,      '#dee2e6', 'Sin dato')]
            segs = [(s, c, l) for s, c, l in raw if s > 0]
            if not segs:
                return None
            sizes, cols, labels = zip(*segs)
            fig, ax = plt.subplots(figsize=(3.2, 3.2),
                                   subplot_kw=dict(aspect='equal'))
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
            wedge_props = dict(width=0.48, edgecolor='white', linewidth=2)
            ax.pie(sizes, colors=cols, wedgeprops=wedge_props, startangle=90)
            pct_global = (cumpl_n / total * 100) if total > 0 else 0
            ax.text(0, 0.08, f'{pct_global:.0f}%', ha='center', va='center',
                    fontsize=13, fontweight='bold', color='#0a2240',
                    fontfamily='DejaVu Sans')
            ax.text(0, -0.22, f'{cumpl_n}/{total}', ha='center', va='center',
                    fontsize=8, color='#6c757d',
                    fontfamily='DejaVu Sans')
            patches = [mpatches.Patch(color=c, label=l)
                       for c, l in zip(cols, labels)]
            ax.legend(handles=patches, loc='lower center', ncol=2, fontsize=6.5,
                      bbox_to_anchor=(0.5, -0.18), frameon=False)
            fig.tight_layout(pad=0.2)
            img = fig_to_image(fig)
            plt.close(fig)
            return img
        except Exception:
            return None

    def _donut_mini_rl(self, cumpl_n: int, en_prog: int, atenc: int, total: int,
                       size: float = 3 * cm) -> Drawing:
        """Small 3-segment ReportLab donut (cumplidos/en-progreso/atención/ND)."""
        d = Drawing(size, size)
        pc = Pie()
        pc.x = size * 0.05
        pc.y = size * 0.05
        pc.width  = size * 0.9
        pc.height = size * 0.9
        nd = max(0, total - cumpl_n - en_prog - atenc)
        segs = [(cumpl_n, GREEN_SOLID), (en_prog, AMBER_SOLID),
                (atenc, RED_SOLID),   (nd, GRAY_ND)]
        # Filter empty segments (Pie needs at least 1)
        segs = [(v, c) for v, c in segs if v > 0] or [(1, GRAY_ND)]
        pc.data   = [v for v, _ in segs]
        for i, (_, col) in enumerate(segs):
            pc.slices[i].fillColor   = col
            pc.slices[i].strokeWidth  = 0
            pc.slices[i].strokeColor  = None
        pc.innerRadiusFraction = 0.60
        pc.startAngle = 90
        pc.direction  = 'clockwise'
        d.add(pc)
        return d

    def _draw_leyenda_header(self, x: float, y: float, w: float,
                              col_linea: colors.Color) -> float:
        """
        Draw the cascade level legend (Niveles/Objetivo/Meta/Indicadores + dots).
        Returns the Y coordinate immediately below the legend.
        """
        PILL_H  = 6 * mm
        PILL_R  = PILL_H / 2
        GAP     = 2.5 * mm

        # Level pills
        pills = [
            ('NIVELES',    C_NAVY),
            ('OBJETIVO',   col_linea),
            ('META PDI',   _light_color(col_linea, 0.55)),
            ('INDICADORES',C_DARK),
        ]
        px = x
        for label, bg in pills:
            pill_w = len(label) * 4 * mm + 5 * mm
            pill_bg = bg
            self.c.setFillColor(pill_bg)
            self.c.roundRect(px, y - PILL_H, pill_w, PILL_H, PILL_R, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 5.5)
            self.c.setFillColor(contrasting_text(pill_bg))
            self.c.drawCentredString(px + pill_w / 2, y - PILL_H + 2, label)
            px += pill_w + GAP

        # Semaphore dots (right side)
        dots = [
            ('\u25cf Cumple',   GREEN_SOLID),
            ('\u25cf Progreso', AMBER_SOLID),
            ('\u25cf Atención', RED_SOLID),
        ]
        dx = x + w
        for label, col in reversed(dots):
            self.c.setFont('Helvetica', 6)
            lw = len(label) * 3.5 * mm + 2 * mm
            dx -= lw
            self.c.setFillColor(col)
            self.c.drawString(dx, y - PILL_H + 2, label)

        # Separator line
        self.c.setStrokeColor(TABLE_BORDER)
        self.c.setLineWidth(0.5)
        self.c.line(x, y - PILL_H - 1.5 * mm, x + w, y - PILL_H - 1.5 * mm)

        return y - PILL_H - 4 * mm

    def _bar_chart_lineas_buf(self, df_lineas: 'pd.DataFrame',
                              w_pt: float, h_pt: float):
        """Return ImageReader of horizontal bar chart per strategic line."""
        if not MATPLOTLIB_AVAILABLE or df_lineas is None or df_lineas.empty:
            return None
        try:
            nom_col = next((c for c in ['Linea', 'Línea'] if c in df_lineas.columns),
                           df_lineas.columns[0])
            cum_col = next((c for c in ['Cumplimiento'] if c in df_lineas.columns),
                           df_lineas.columns[1])

            # Sort rows by ORDEN_LINEAS; barh plots bottom-to-top so reverse for top-down order
            def _bc_sort(row):
                n = _norm(str(row.get(nom_col, '')))
                for i, ol in enumerate(ORDEN_LINEAS):
                    if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                        return i
                return 99
            rows_sorted = sorted(df_lineas.to_dict('records'), key=_bc_sort, reverse=True)

            # Replace underscores, truncate display names
            noms  = [nombre_display(str(r.get(nom_col, '')))[:28] for r in rows_sorted]
            cumps = [float(r.get(cum_col, 0) or 0) for r in rows_sorted]
            bar_cols = []
            for r in rows_sorted:
                col = color_linea(str(r.get(nom_col, '')))
                bar_cols.append(f'#{int(col.red*255):02x}'
                                f'{int(col.green*255):02x}'
                                f'{int(col.blue*255):02x}')
            fig, ax = plt.subplots(figsize=(w_pt / 72, h_pt / 72))
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
            y_pos = range(len(noms))
            bars = ax.barh(y_pos, cumps, color=bar_cols, height=0.55, zorder=2)
            ax.axvline(100, color='#b71c1c', linestyle='--', linewidth=1,
                       alpha=0.8, zorder=3)
            # Value labels
            for bar, val in zip(bars, cumps):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                        f'{val:.0f}%', va='center', fontsize=6.5,
                        color='#212529', fontfamily='DejaVu Sans')
            ax.set_yticks(list(y_pos))
            ax.set_yticklabels(noms, fontsize=7)
            ax.set_xlim(0, max(125, max(cumps, default=0) + 15))
            ax.set_xlabel('Cumplimiento (%)', fontsize=7)
            ax.grid(axis='x', alpha=0.25, zorder=1)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            fig.tight_layout(pad=0.3)
            img = fig_to_image(fig)
            plt.close(fig)
            return img
        except Exception:
            return None

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

    def resumen_ejecutivo(self, metricas: Dict, analisis_texto: str = "",
                          df_lineas: 'Optional[pd.DataFrame]' = None):
        """Página: Resumen Ejecutivo — KPI grande + 3 fichas + donut/barras + IA."""
        cont_top = self._header_band(
            NAVY_DARK, 'RESUMEN EJECUTIVO',
            f'Plan de Desarrollo Institucional {self.año}'
        )
        self._footer()

        cumpl   = float(metricas.get('cumplimiento_promedio', 0))
        total   = int(metricas.get('total_indicadores', 0))
        cumpl_n = int(metricas.get('indicadores_cumplidos', 0))
        en_prog = int(metricas.get('en_progreso', 0))
        atenc   = int(metricas.get('no_cumplidos', 0))
        c_sem   = color_semaforo(cumpl)

        MX       = self.MX
        card_w   = self.W - 2 * MX
        GAP      = 4 * mm

        # ── MAIN KPI CARD (full width, gradient navy) ─────────────────
        MAIN_H = 28 * mm
        y_main = cont_top - 6 * mm - MAIN_H

        # Gradient background
        self._gradient_band(MX, y_main, card_w, MAIN_H, NAVY_DARK, NAVY_MID)

        # Big number
        self.c.setFont('Helvetica-Bold', 40)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(self.W / 2, y_main + MAIN_H * 0.5 + 2, f'{cumpl:.1f}%')

        # Label
        self.c.setFont('Helvetica', 9)
        self.c.setFillColor(TEXT_MUTED)
        self.c.drawCentredString(self.W / 2, y_main + 5 * mm, 'Cumplimiento Global PDI')

        # Teal progress bar inside card
        bar_y = y_main + 1.5 * mm
        bar_h = 3 * mm
        bar_bw = card_w - 8 * mm
        self.c.setFillColor(NAVY_MID)
        self.c.roundRect(MX + 4 * mm, bar_y, bar_bw, bar_h, bar_h / 2, fill=1, stroke=0)
        fill_frac = min(cumpl / 100.0, 1.2)
        self.c.setFillColor(TEAL_ACCENT)
        self.c.roundRect(MX + 4 * mm, bar_y, bar_bw * fill_frac, bar_h, bar_h / 2, fill=1, stroke=0)

        # Badge (top-right corner of main card)
        badge_txt = '\u2713 META SUPERADA' if cumpl >= 100 else texto_estado(cumpl)
        badge_col = GREEN_SOLID if cumpl >= 100 else c_sem
        bw, bh = 38 * mm, 6 * mm
        bx = MX + card_w - bw - 3 * mm
        bby = y_main + MAIN_H - bh - 3 * mm
        self.c.setFillColor(badge_col)
        self.c.roundRect(bx, bby, bw, bh, 2 * mm, fill=1, stroke=0)
        self.c.setFont('Helvetica-Bold', 6.5)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(bx + bw / 2, bby + bh / 2 - 2.2, badge_txt)

        # ── 3 KPI CARDS with visual hierarchy ─────────────────────────
        # Total (primary/biggest) | Cumplidos (medium) | En Progreso (small)
        KPI_SPECS = [
            # (val, label, bg_hex, accent_hex, txt_hex, font_size, card_h)
            (str(total),   'Total Indicadores', '#EFF6FF', '#1FB2DE', '#0a2240',  36, 24 * mm),
            (str(cumpl_n), 'Cumplidos ≥100%',   '#F0FDF4', '#10B981', '#166534',  26, 19 * mm),
            (str(en_prog), 'En Progreso 80–99%','#FFFBEB', '#F59E0B', '#92400E',  20, 16 * mm),
        ]
        KPI_MAX_H = KPI_SPECS[0][6]          # tallest card height
        KPI_Y_BOT = y_main - GAP - KPI_MAX_H # bottom-align all cards here
        KPI_W = (card_w - 2 * GAP) / 3

        for i, (val, lbl, bg_h, top_h, txt_h, fsize, kpi_h) in enumerate(KPI_SPECS):
            kx = MX + i * (KPI_W + GAP)
            ky = KPI_Y_BOT + (KPI_MAX_H - kpi_h)  # bottom-aligned
            # Shadow
            self.c.setFillColor(C_SHADOW)
            self.c.roundRect(kx + 2, ky - 2, KPI_W, kpi_h, 3 * mm, fill=1, stroke=0)
            # Card bg
            self.c.setFillColor(colors.HexColor(bg_h))
            self.c.roundRect(kx, ky, KPI_W, kpi_h, 3 * mm, fill=1, stroke=0)
            # Top border 3–4px
            top_c = colors.HexColor(top_h)
            border_h = 4 if i == 0 else 3
            self.c.setFillColor(top_c)
            self.c.roundRect(kx, ky + kpi_h - border_h, KPI_W, border_h,
                             1.5 * mm, fill=1, stroke=0)
            self.c.rect(kx, ky + kpi_h - border_h - 2, KPI_W, 2, fill=1, stroke=0)
            # Value (big number)
            self.c.setFont('Helvetica-Bold', fsize)
            self.c.setFillColor(colors.HexColor(txt_h))
            self.c.drawCentredString(kx + KPI_W / 2, ky + kpi_h * 0.45, val)
            # Label
            self.c.setFont('Helvetica', 7 if i == 0 else 6.5)
            self.c.setFillColor(TEXT_SECONDARY)
            self.c.drawCentredString(kx + KPI_W / 2, ky + 3 * mm, lbl)
            # Sub-badge percentage (below label, never overlapping number)
            if i > 0 and total:
                badge = f'{int(val) / total * 100:.0f}%'
                # Small pill badge at very bottom of card
                bpw, bph = 14 * mm, 4 * mm
                bpx = kx + (KPI_W - bpw) / 2
                bpy = ky + 0.5 * mm
                self.c.setFillColor(_light_color(colors.HexColor(top_h), 0.65))
                self.c.roundRect(bpx, bpy, bpw, bph, 2 * mm, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 6)
                self.c.setFillColor(colors.HexColor(top_h))
                self.c.drawCentredString(kx + KPI_W / 2, bpy + 1 * mm, badge)

        KPI_Y = KPI_Y_BOT  # reference for chart row below

        # ── CHART ROW: Donut (40%) + Bars (60%) ───────────────────────
        CHART_H = 64 * mm
        CHART_Y = KPI_Y - GAP - CHART_H
        donut_w = card_w * 0.40
        bars_w  = card_w * 0.57
        bars_x  = MX + donut_w + card_w * 0.03

        # Donut
        donut_img = self._donut_chart_buf(cumpl_n, en_prog, atenc, total)
        if donut_img is not None:
            self.c.drawImage(donut_img, MX, CHART_Y, donut_w, CHART_H,
                             preserveAspectRatio=True, mask='auto')
        else:
            rz = min(donut_w, CHART_H) * 0.95
            rx = MX + (donut_w - rz) / 2
            renderPDF.draw(self._ring_drawing(cumpl, rz), self.c, rx, CHART_Y)

        # Horizontal bar chart
        if df_lineas is not None and not df_lineas.empty:
            bar_img = self._bar_chart_lineas_buf(df_lineas, bars_w, CHART_H)
            if bar_img is not None:
                self.c.drawImage(bar_img, bars_x, CHART_Y, bars_w, CHART_H,
                                 preserveAspectRatio=True, mask='auto')

        # ── AI ANALYSIS BLOCK (amplified — no redundant table) ────────
        # Use all space from chart bottom to footer for the IA block
        AI_BOTTOM = self.H_FOOTER + 4 * mm
        ai_h      = max(CHART_Y - AI_BOTTOM - 6 * mm, 40 * mm)
        if analisis_texto and ai_h > 15 * mm:
            self._ai_block(MX, AI_BOTTOM, card_w, ai_h, analisis_texto)
        elif not analisis_texto and ai_h > 10 * mm:
            self.c.setFont('Helvetica-Oblique', 7.5)
            self.c.setFillColor(C_GRAY)
            self.c.drawCentredString(
                self.W / 2, AI_BOTTOM + ai_h / 2,
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
        # Extract per-line data (with optional indicator breakdown)
        lineas = []
        for _, r in df_lineas.iterrows():
            nom   = str(r.get('Linea', r.get('Línea', '')))
            pct   = float(r.get('Cumplimiento', 0) or 0)
            n_ind = int(r.get('Total_Indicadores', 0) or 0)
            cn    = int(r.get('Cumplidos', r.get('indicadores_cumplidos', 0)) or 0)
            ep    = int(r.get('En_Progreso', r.get('en_progreso', 0)) or 0)
            ac    = int(r.get('No_Cumplidos', r.get('Atencion', 0)) or 0)
            # Fallback: estimate from pct when no breakdown
            if cn == 0 and ep == 0 and ac == 0 and n_ind > 0:
                cn = round(n_ind * min(pct / 100, 1.0))
                ep = round((n_ind - cn) * (0.6 if pct >= 80 else 0.3))
                ac = n_ind - cn - ep
            lineas.append((nom, pct, n_ind, cn, ep, ac))

        # Sort by ORDEN_LINEAS
        def _linea_order(t):
            n = _norm(t[0])
            for i, ol in enumerate(ORDEN_LINEAS):
                if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                    return i
            return 99
        lineas.sort(key=_linea_order)

        N_COLS   = 3
        N_ROWS   = (len(lineas) + N_COLS - 1) // N_COLS
        MX_GRID  = 12 * mm
        GAP      = 5 * mm
        avail_w  = self.W - 2 * MX_GRID
        avail_h  = self.H - 26 * mm - self.H_FOOTER
        card_w   = (avail_w - (N_COLS - 1) * GAP) / N_COLS
        card_h   = min((avail_h - (N_ROWS - 1) * GAP) / N_ROWS, 90 * mm)
        # Distribuir filas con espacio uniforme para llenar la hoja visualmente
        row_gap  = (avail_h - N_ROWS * card_h) / (N_ROWS + 1) if N_ROWS > 0 else GAP

        for idx, (nom, pct, n_ind, cn, ep, ac) in enumerate(lineas):
            col_i  = idx % N_COLS
            row_i  = idx // N_COLS
            card_x = MX_GRID + col_i * (card_w + GAP)
            # Posición Y: distribuida uniformemente entre margen superior y footer
            card_top = self.H - 26 * mm - row_gap * (row_i + 1) - card_h * row_i
            card_y   = card_top - card_h

            col   = color_linea(nom)
            c_sem = color_semaforo(pct)
            nom_d = nombre_display(nom)

            # ── Shadow (3D offset) ────────────────────────────────────
            self.c.setFillColor(C_SHADOW)
            self.c.roundRect(card_x + 3, card_y - 3, card_w, card_h,
                             6 * mm, fill=1, stroke=0)
            # ── Card bg: lighten(col, 0.70) — stronger tint ───────────
            card_bg = _light_color(col, 0.70)
            self.c.setFillColor(card_bg)
            self.c.roundRect(card_x, card_y, card_w, card_h, 6 * mm, fill=1, stroke=0)
            # ── 4px left accent (clipped to card by drawing inside rounded rect) ─
            self.c.setFillColor(col)
            # Use rounded rect on left side to respect card corners
            self.c.roundRect(card_x, card_y + 6 * mm, 5, card_h - 12 * mm, 0,
                             fill=1, stroke=0)

            # ── Header stripe 22pt (name rendered inside) ────────────
            STRIPE_H = 22
            stripe_y = card_y + card_h - STRIPE_H
            # Rounded top corners: overdraw rounded rect + flat bottom cover
            self.c.setFillColor(col)
            self.c.roundRect(card_x, stripe_y, card_w, STRIPE_H + int(4 * mm),
                             4 * mm, fill=1, stroke=0)
            self.c.rect(card_x, stripe_y, card_w, STRIPE_H // 2, fill=1, stroke=0)

            # Name: white on dark line, darken(col,0.55) on light line
            name_col = darken(col, 0.55) if is_light_color(col) else C_WHITE
            # Wrap long names to 2 balanced lines (split near char midpoint)
            words = nom_d.split()
            if len(words) > 2:
                total_chars = len(nom_d)
                mid_target = total_chars // 2
                best_split, best_dist = 1, total_chars
                acc = 0
                for wi, w in enumerate(words[:-1]):
                    acc += len(w) + 1  # +1 for space
                    dist = abs(acc - mid_target)
                    if dist < best_dist:
                        best_dist = dist
                        best_split = wi + 1
                ln1 = ' '.join(words[:best_split])
                ln2 = ' '.join(words[best_split:])
            else:
                ln1 = nom_d
                ln2 = ''
            self.c.setFillColor(name_col)
            if ln2:
                self.c.setFont('Helvetica-Bold', 8.5)
                self.c.drawCentredString(card_x + card_w / 2,
                                         stripe_y + STRIPE_H - 9, ln1)
                self.c.setFont('Helvetica', 7)
                self.c.setFillColor(name_col)
                self.c.drawCentredString(card_x + card_w / 2,
                                         stripe_y + STRIPE_H - 18, ln2)
            else:
                self.c.setFont('Helvetica-Bold', 9)
                self.c.drawCentredString(card_x + card_w / 2,
                                         stripe_y + STRIPE_H / 2 - 4, ln1)

            name_bottom = stripe_y - 2

            # ── Status badge ──────────────────────────────────────────
            badge_txt = texto_estado(pct)
            bw_s, bh_s = min(card_w - 8 * mm, 35 * mm), 6 * mm
            bx_s = card_x + (card_w - bw_s) / 2
            by_s = name_bottom - bh_s - 3
            self.c.setFillColor(color_semaforo_bg(pct))
            self.c.roundRect(bx_s, by_s, bw_s, bh_s, 2 * mm, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 5.5)
            self.c.setFillColor(color_semaforo_text(pct))
            self.c.drawCentredString(card_x + card_w / 2,
                                     by_s + bh_s / 2 - 2, badge_txt)

            # ── Big percentage ─────────────────────────────────────────
            pct_y = by_s - 4
            self.c.setFont('Helvetica-Bold', 30)
            self.c.setFillColor(c_sem)
            self.c.drawCentredString(card_x + card_w / 2, pct_y - 28, f'{pct:.0f}%')

            # ── Progress bar (4pt) ────────────────────────────────────
            bar_h_s = 4
            bar_w_s = card_w - 8 * mm
            bar_x_s = card_x + 4 * mm
            bar_y_s = pct_y - 37
            self.c.setFillColor(TABLE_BORDER)
            self.c.roundRect(bar_x_s, bar_y_s, bar_w_s, bar_h_s,
                             2, fill=1, stroke=0)
            self.c.setFillColor(c_sem)
            self.c.roundRect(bar_x_s, bar_y_s,
                             bar_w_s * min(pct / 100, 1.0), bar_h_s,
                             2, fill=1, stroke=0)

            # ── N indicadores ─────────────────────────────────────────
            self.c.setFont('Helvetica', 6.5)
            self.c.setFillColor(TEXT_MUTED)
            self.c.drawCentredString(card_x + card_w / 2, bar_y_s - 9,
                                     f'{n_ind} indicadores')

            # ── Mini 3-segment donut (bottom of card) ─────────────────
            donut_avail = bar_y_s - 12 - card_y - 4 * mm
            if donut_avail >= 20 * mm:
                dsz = min(donut_avail, card_w * 0.75)
                dx  = card_x + (card_w - dsz) / 2
                dy  = card_y + (donut_avail - dsz) / 2 + 4 * mm
                renderPDF.draw(
                    self._donut_mini_rl(cn, ep, ac, n_ind, dsz),
                    self.c, dx, dy
                )
                # Centre label: pct only (n_ind already shown in "X indicadores" above)
                dcx = dx + dsz / 2
                dcy = dy + dsz / 2
                self.c.setFont('Helvetica-Bold', 8)
                self.c.setFillColor(c_sem)
                self.c.drawCentredString(dcx, dcy - 3, f'{pct:.0f}%')

        self._new_page()

    def pagina_linea(self, nombre: str, cumplimiento: float, total_ind: int,
                     objetivos: List[Dict], proyectos: List[Dict],
                     analisis: str, sin_meta: List[Dict] = None):
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
        # Altura dinámica: estimamos líneas de texto (6 chars/pt ≈ aprox)
        AI_BOTTOM = self.H_FOOTER + 3 * mm
        _ai_line_w = self.W - 2 * self.MX - 16 * mm  # ancho útil texto IA (pts)
        _chars_per_line = max(1, int(_ai_line_w / 3.8))  # ~3.8pt/char Helvetica 6.5
        _ai_lines = max(1, len(analisis or '') // _chars_per_line + 1) if analisis else 0
        AI_H      = max(38 * mm, min(_ai_lines * 8 + int(16 * mm), 70 * mm))
        AI_TOP    = AI_BOTTOM + AI_H
        TABLE_BOTTOM = AI_TOP + 4 * mm
        y_cur = badge_by - 5 * mm

        # ── Cascada: N2 Objetivo → N3 Meta → N4 Indicadores ──────────
        # Estilo: sin bordes rectos, pill-badges para %, fondos diferenciados
        OBJ_H  = 9 * mm   # Nivel 2: Objetivo estratégico
        META_H = 7.5 * mm # Nivel 3: Meta estratégica
        HDR_H  = 6 * mm   # Encabezado global de columnas (UNA VEZ)
        ROW_H  = 6.5 * mm # Fila de indicador (ligeramente más alta para pill)

        # Columnas: Indicador | Meta | Ejecución | % | Estado
        IND_COL_W = [84 * mm, 20 * mm, 20 * mm, 25 * mm, 17 * mm]
        IND_TBL_W = sum(IND_COL_W)   # 166 mm

        # Zona derecha para barra obj/meta
        RIGHT_W = 50 * mm
        BAR_W   = 24 * mm
        BAR_X   = self.MX + IND_TBL_W - RIGHT_W
        PCT_CX  = BAR_X + BAR_W + 11 * mm
        CIRC_X  = self.MX + IND_TBL_W - 5 * mm

        # Pill-badge helper (dibuja badge redondeado + texto centrado)
        def _pill(cx, cy, txt, bg_col, txt_col, pw=12*mm, ph=4*mm):
            px = cx - pw / 2
            py = cy - ph / 2
            self.c.setFillColor(bg_col)
            self.c.roundRect(px, py, pw, ph, ph / 2, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 6)
            self.c.setFillColor(txt_col)
            self.c.drawCentredString(cx, py + ph / 2 - 2, txt)

        if objetivos:
            self.c.setFont('Helvetica-Bold', 9)
            self.c.setFillColor(NAVY_DARK)
            self.c.drawString(self.MX, y_cur, 'OBJETIVOS E INDICADORES')
            y_cur -= 5 * mm

            # Leyenda
            y_cur = self._draw_leyenda_header(self.MX, y_cur, IND_TBL_W, col_linea)

            # ── Encabezado columnas: gradiente suave + SIN borde exterior ──
            if y_cur - HDR_H >= TABLE_BOTTOM:
                self._gradient_band(self.MX, y_cur - HDR_H, IND_TBL_W, HDR_H,
                                    darken(col_linea, 0.30), darken(col_linea, 0.55))
                # Línea inferior de acento (más visible, sin borde superior)
                self.c.setFillColor(_light_color(col_linea, 0.50))
                self.c.rect(self.MX, y_cur - HDR_H, IND_TBL_W, 1.5, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 6)
                self.c.setFillColor(C_WHITE)
                hx = self.MX
                for hdr, cw in zip(['Indicador', 'Meta', 'Ejecución',
                                    'Cumplimiento', 'Estado'], IND_COL_W):
                    self.c.drawCentredString(hx + cw / 2, y_cur - HDR_H + 2 * mm, hdr)
                    hx += cw
                y_cur -= HDR_H

            for obj in objetivos:
                if y_cur - (OBJ_H + META_H + ROW_H) < TABLE_BOTTOM:
                    break

                obj_pct = float(obj.get('cumplimiento', 0))
                obj_sem = color_semaforo(obj_pct)
                obj_txt = limpiar(str(obj.get('objetivo', '')))
                obj_text_col = contrasting_text(col_linea)

                # ── Nivel 2: Objetivo — banda con bordes redondeados ───
                if y_cur - OBJ_H < TABLE_BOTTOM:
                    break
                # Fondo redondeado para el objetivo (sin borde exterior)
                self.c.setFillColor(col_linea)
                self.c.roundRect(self.MX, y_cur - OBJ_H, IND_TBL_W, OBJ_H,
                                 2 * mm, fill=1, stroke=0)

                obj_max_chars = 72
                obj_s = obj_txt[:obj_max_chars] + ('…' if len(obj_txt) > obj_max_chars else '')
                cy_obj = y_cur - OBJ_H / 2
                self.c.setFont('Helvetica-Bold', 7)
                self.c.setFillColor(obj_text_col)
                self.c.drawString(self.MX + 4 * mm, cy_obj - 3, '\u25b6 ' + obj_s)

                # Barra de progreso compacta
                bar_by_o = cy_obj - 2
                track_o = (_light_color(col_linea, 0.35) if not is_light_color(col_linea)
                           else darken(col_linea, 0.25))
                self.c.setFillColor(track_o)
                self.c.roundRect(BAR_X, bar_by_o, BAR_W, 3.5, 1.5, fill=1, stroke=0)
                self.c.setFillColor(obj_sem)
                self.c.roundRect(BAR_X, bar_by_o, BAR_W * min(obj_pct / 100, 1.0), 3.5,
                                 1.5, fill=1, stroke=0)
                # % como texto limpio (sin pill en objetivo para no solapar barra)
                self.c.setFont('Helvetica-Bold', 8)
                self.c.setFillColor(obj_text_col)
                self.c.drawCentredString(PCT_CX, cy_obj - 3, f'{obj_pct:.0f}%')
                self._status_circle(CIRC_X, cy_obj, 2.5 * mm, obj_pct)

                y_cur -= OBJ_H
                y_cur -= 1  # micro-separación

                for meta in obj.get('metas', []):
                    if y_cur - (META_H + ROW_H) < TABLE_BOTTOM:
                        break

                    meta_txt = limpiar(str(meta.get('meta_pdi', '')))
                    meta_pct = float(meta.get('cumplimiento', 0))
                    meta_sem = color_semaforo(meta_pct)

                    # ── Nivel 3: Meta — fondo tinte, sin borde ─────────
                    if y_cur - META_H < TABLE_BOTTOM:
                        break
                    meta_bg = _light_color(col_linea, 0.78)
                    self.c.setFillColor(meta_bg)
                    # Fondo sin borde — solo relleno
                    self.c.rect(self.MX, y_cur - META_H, IND_TBL_W, META_H,
                                fill=1, stroke=0)
                    # Acento izquierdo redondeado (3px)
                    self.c.setFillColor(col_linea)
                    self.c.roundRect(self.MX, y_cur - META_H, 3, META_H,
                                     1, fill=1, stroke=0)

                    meta_txt_col = contrasting_text(meta_bg)
                    meta_label = (meta_txt[:92] + ('…' if len(meta_txt) > 92 else '')) \
                                 if meta_txt else 'META ESTRATÉGICA'
                    cy_meta = y_cur - META_H / 2

                    self.c.setFont('Helvetica', 6.5)
                    self.c.setFillColor(meta_txt_col)
                    self.c.drawString(self.MX + 6 * mm, cy_meta - 3,
                                      '\u25c6 ' + meta_label)

                    # Pill-badge % para meta (pequeño, derecha)
                    _pill(PCT_CX, cy_meta,
                          f'{meta_pct:.0f}%',
                          color_semaforo_bg(meta_pct),
                          meta_sem,
                          pw=11 * mm, ph=3.5 * mm)

                    y_cur -= META_H

                    inds = meta.get('indicadores', [])
                    if not inds:
                        continue

                    # ── Nivel 4: Indicadores — filas limpias, sin bordes ──
                    for ridx, ind in enumerate(inds):
                        if y_cur - ROW_H < TABLE_BOTTOM:
                            break
                        ind_pct  = float(ind.get('cumplimiento', 0))
                        ind_scol = color_semaforo(ind_pct)
                        # Fondo alternado muy sutil (sin borde)
                        bg = C_TABLE_ROW_ALT if ridx % 2 == 0 else C_WHITE
                        self.c.setFillColor(bg)
                        self.c.rect(self.MX, y_cur - ROW_H, IND_TBL_W, ROW_H,
                                    fill=1, stroke=0)
                        # Punto semáforo izquierdo (2px)
                        self.c.setFillColor(ind_scol)
                        self.c.roundRect(self.MX + 1, y_cur - ROW_H + 1.5 * mm,
                                         2, ROW_H - 3 * mm, 1, fill=1, stroke=0)
                        # Línea separadora inferior muy tenue
                        self.c.setStrokeColor(TABLE_BORDER)
                        self.c.setLineWidth(0.2)
                        self.c.line(self.MX + 3 * mm, y_cur - ROW_H,
                                    self.MX + IND_TBL_W - 3 * mm, y_cur - ROW_H)

                        ind_name = limpiar(str(ind.get('nombre', '')))
                        ind_name = ind_name[:60] + ('…' if len(ind_name) > 60 else '')
                        self.c.setFont('Helvetica', 6)
                        self.c.setFillColor(C_DARK)
                        self.c.drawString(self.MX + 4 * mm,
                                          y_cur - ROW_H + 2 * mm, ind_name)

                        meta_v = ind.get('meta_valor')
                        ejec_v = ind.get('ejecucion')
                        meta_str = (f'{float(meta_v):.1f}' if (meta_v is not None and
                                    str(meta_v) not in ('nan','None','')) else '-')
                        ejec_str = (f'{float(ejec_v):.1f}' if (ejec_v is not None and
                                    str(ejec_v) not in ('nan','None','')) else '-')

                        hx = self.MX + IND_COL_W[0]
                        # Meta (col 1)
                        self.c.setFont('Helvetica', 6.5)
                        self.c.setFillColor(TEXT_MUTED)
                        self.c.drawCentredString(hx + IND_COL_W[1] / 2,
                                                 y_cur - ROW_H + 2 * mm, meta_str)
                        hx += IND_COL_W[1]
                        # Ejecución (col 2)
                        self.c.setFont('Helvetica', 6.5)
                        self.c.setFillColor(C_DARK)
                        self.c.drawCentredString(hx + IND_COL_W[2] / 2,
                                                 y_cur - ROW_H + 2 * mm, ejec_str)
                        hx += IND_COL_W[2]
                        # % como pill-badge (col 3)
                        _pill(hx + IND_COL_W[3] / 2,
                              y_cur - ROW_H / 2,
                              f'{ind_pct:.0f}%',
                              color_semaforo_bg(ind_pct),
                              ind_scol,
                              pw=13 * mm, ph=4 * mm)
                        hx += IND_COL_W[3]
                        # Estado (col 4)
                        self._status_circle(hx + IND_COL_W[4] / 2,
                                            y_cur - ROW_H / 2, 2.5 * mm, ind_pct)
                        y_cur -= ROW_H

        # ── Proyectos + Stand By — dos columnas lado a lado ──────────
        PROW_H   = 6 * mm
        PHDR_H   = 7 * mm
        TWO_GAP  = 4 * mm
        has_sin_meta = sin_meta and len(sin_meta) > 0
        has_proyectos = proyectos and len(proyectos) > 0

        if (has_proyectos or has_sin_meta) and y_cur - (PHDR_H + 16 * mm) > TABLE_BOTTOM:
            y_cur -= 5 * mm

            # Column widths: Stand By (left, 42%) | Projects (right, 55%)
            COL1_W = IND_TBL_W * 0.42   # Stand By
            COL2_W = IND_TBL_W * 0.55   # Projects
            COL1_X = self.MX
            COL2_X = self.MX + COL1_W + TWO_GAP

            y_start   = y_cur
            y_col1    = y_start
            y_col2    = y_start

            # ── COLUMNA 1: Stand By / Sin Resultados ─────────────────
            if has_sin_meta:
                self.c.setFont('Helvetica-Bold', 7.5)
                self.c.setFillColor(NAVY_DARK)
                self.c.drawString(COL1_X, y_col1, '\u23f8 Stand By / Sin Resultados')
                y_col1 -= 4 * mm
                # Header (color institucional: amber oscuro → navy)
                self._gradient_band(COL1_X, y_col1 - PHDR_H, COL1_W, PHDR_H,
                                    NAVY_DARK, NAVY_MID)
                self.c.setFont('Helvetica-Bold', 5.5)
                self.c.setFillColor(C_WHITE)
                self.c.drawString(COL1_X + 2 * mm, y_col1 - PHDR_H + 2 * mm, 'Indicador sin resultado')
                y_col1 -= PHDR_H

                for sidx, si in enumerate(sin_meta[:14]):
                    if y_col1 - PROW_H < TABLE_BOTTOM:
                        break
                    si_bg = AMBER_BG if sidx % 2 == 0 else C_WHITE
                    self.c.setFillColor(si_bg)
                    self.c.rect(COL1_X, y_col1 - PROW_H, COL1_W, PROW_H, fill=1, stroke=0)
                    self.c.setFillColor(AMBER_SOLID)
                    self.c.rect(COL1_X, y_col1 - PROW_H, 2, PROW_H, fill=1, stroke=0)
                    self.c.setStrokeColor(TABLE_BORDER)
                    self.c.setLineWidth(0.3)
                    self.c.rect(COL1_X, y_col1 - PROW_H, COL1_W, PROW_H, fill=0, stroke=1)
                    si_nm = limpiar(str(si.get('nombre', '')))
                    # Truncate to fit column
                    max_chars = int(COL1_W / (3.5))
                    si_nm = si_nm[:max_chars] + ('…' if len(si_nm) > max_chars else '')
                    self.c.setFont('Helvetica', 5.5)
                    self.c.setFillColor(C_DARK)
                    self.c.drawString(COL1_X + 3, y_col1 - PROW_H + 1.8 * mm, si_nm)
                    y_col1 -= PROW_H

            # ── COLUMNA 2: Proyectos Estratégicos ────────────────────
            if has_proyectos:
                self.c.setFont('Helvetica-Bold', 7.5)
                self.c.setFillColor(NAVY_DARK)
                self.c.drawString(COL2_X, y_col2, '\u25c6 Proyectos Estratégicos')
                y_col2 -= 4 * mm
                # Header
                self._gradient_band(COL2_X, y_col2 - PHDR_H, COL2_W, PHDR_H,
                                    NAVY_DARK, NAVY_MID)
                self.c.setFillColor(col_linea)
                self.c.rect(COL2_X, y_col2 - PHDR_H, COL2_W, 2, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 5.5)
                self.c.setFillColor(C_WHITE)
                _p2cols = [('Proyecto', 0.62), ('%', 0.16), ('Prog.', 0.14), ('Est', 0.08)]
                phx2 = COL2_X
                for phdr2, pfrac2 in _p2cols:
                    phw2 = COL2_W * pfrac2
                    self.c.drawCentredString(phx2 + phw2 / 2, y_col2 - PHDR_H + 2 * mm, phdr2)
                    phx2 += phw2
                y_col2 -= PHDR_H

                pw1 = COL2_W * 0.62
                pw2 = COL2_W * 0.16
                pw3 = COL2_W * 0.14
                pw4 = COL2_W * 0.08

                for pidx, proy in enumerate(proyectos[:14]):
                    if y_col2 - PROW_H < TABLE_BOTTOM:
                        break
                    p_pct = float(proy.get('cumplimiento', 0))
                    p_col = color_semaforo(p_pct)
                    p_bg  = C_TABLE_ROW_ALT if pidx % 2 == 0 else C_WHITE
                    self.c.setFillColor(p_bg)
                    self.c.rect(COL2_X, y_col2 - PROW_H, COL2_W, PROW_H, fill=1, stroke=0)
                    self.c.setFillColor(p_col)
                    self.c.rect(COL2_X, y_col2 - PROW_H, 2, PROW_H, fill=1, stroke=0)
                    self.c.setStrokeColor(TABLE_BORDER)
                    self.c.setLineWidth(0.3)
                    self.c.rect(COL2_X, y_col2 - PROW_H, COL2_W, PROW_H, fill=0, stroke=1)
                    p_nm = limpiar(str(proy.get('nombre', '')))
                    max_pc = int(pw1 / 3.5)
                    p_nm = p_nm[:max_pc] + ('…' if len(p_nm) > max_pc else '')
                    self.c.setFont('Helvetica', 5.5)
                    self.c.setFillColor(C_DARK)
                    self.c.drawString(COL2_X + 3, y_col2 - PROW_H + 1.8 * mm, p_nm)
                    self.c.setFont('Helvetica-Bold', 6)
                    self.c.setFillColor(p_col)
                    self.c.drawCentredString(COL2_X + pw1 + pw2 / 2,
                                             y_col2 - PROW_H + 1.8 * mm, f'{p_pct:.0f}%')
                    # Mini progress bar
                    mbx = COL2_X + pw1 + pw2 + 2
                    mbw = pw3 - 4
                    mbh = 3
                    mby = y_col2 - PROW_H + (PROW_H - mbh) / 2
                    self.c.setFillColor(TABLE_BORDER)
                    self.c.roundRect(mbx, mby, mbw, mbh, 1, fill=1, stroke=0)
                    self.c.setFillColor(p_col)
                    self.c.roundRect(mbx, mby, mbw * min(p_pct / 100, 1.0), mbh, 1,
                                     fill=1, stroke=0)
                    sym = '\u2713' if p_pct >= 100 else ('\u26a0' if p_pct >= 80 else '\u2717')
                    self.c.setFont('Helvetica-Bold', 8)
                    self.c.setFillColor(p_col)
                    self.c.drawCentredString(COL2_X + pw1 + pw2 + pw3 + pw4 / 2,
                                             y_col2 - PROW_H + 1.8 * mm, sym)
                    y_col2 -= PROW_H

            # Advance y_cur by whichever column consumed more space
            y_cur = min(y_col1, y_col2)

        # ── Tarjeta de análisis IA (anclada al fondo) ──────────────────
        if analisis:
            self._ai_block(
                self.MX, AI_BOTTOM,
                self.W - 2 * self.MX, AI_H,
                analisis, col_linea
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

        # Ordenar por ORDEN_LINEAS (canonical order) luego por indicador
        if c_linea:
            def _linea_sort_key(nom):
                n = _norm(str(nom))
                for i, ol in enumerate(ORDEN_LINEAS):
                    if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                        return i
                return 99
            df_sorted = df_indicadores.copy()
            df_sorted['_ord'] = df_sorted[c_linea].map(_linea_sort_key)
            df_sorted = df_sorted.sort_values(['_ord', c_linea]).drop(columns=['_ord'])
        else:
            df_sorted = df_indicadores

        # Constantes de tabla
        COL_W  = [87 * mm, 17 * mm, 17 * mm, 16 * mm, 14 * mm]
        ROW_H  = 6 * mm
        HDR_H  = 8 * mm
        BOTTOM = self.H_FOOTER + 3 * mm

        def _draw_page_header():
            cont = self._header_band(
                C_NAVY, 'DETALLE DE INDICADORES',
                f'Total: {len(df_indicadores)} indicadores'
            )
            self._footer('Detalle de Indicadores')
            return cont

        def _draw_table_header(y, accent_col=None):
            tbl_w = sum(COL_W)
            # Gradient fill: #0a2240 → #1a3a5c
            self._gradient_band(self.MX, y - HDR_H, tbl_w, HDR_H, C_NAVY, C_HDR_GRAD_END)
            # 2px accent line at bottom
            self.c.setFillColor(accent_col or C_ACCENT)
            self.c.rect(self.MX, y - HDR_H, tbl_w, 2, fill=1, stroke=0)
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
                    sub_txt = nombre_display(linea_nom)   # elimina guiones bajos
                    sub_txt_col = contrasting_text(sub_col)
                    self.c.setFillColor(sub_col)
                    self.c.rect(self.MX, y - sub_h, sum(COL_W), sub_h, fill=1, stroke=0)
                    self.c.setFont('Helvetica-Bold', 7.5)
                    self.c.setFillColor(sub_txt_col)
                    self.c.drawString(self.MX + 3 * mm, y - sub_h + 2 * mm, sub_txt)
                    y -= sub_h

            # Salto de página
            if y - ROW_H < BOTTOM:
                self._new_page()
                y = _draw_page_header()
                y = _draw_table_header(y)

            pct    = float(row.get(c_cumpl, 0) or 0) if c_cumpl else 0
            c_row  = C_TABLE_ROW_ALT if idx % 2 == 0 else C_WHITE
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

            # Columnas numéricas (Meta, Ejecución, %)
            meta = row.get(c_meta, None) if c_meta else None
            ejec = row.get(c_ejec, None) if c_ejec else None
            num_vals = [
                f'{float(meta):.1f}' if meta is not None else '-',
                f'{float(ejec):.1f}' if ejec is not None else '-',
                f'{pct:.1f}%',
            ]
            hx = self.MX + COL_W[0]
            for j, (val, cw) in enumerate(zip(num_vals, COL_W[1:4])):
                fnt = 'Helvetica-Bold' if j == 2 else 'Helvetica'
                clr = c_s if j == 2 else C_DARK
                self.c.setFont(fnt, 6.5)
                self.c.setFillColor(clr)
                self.c.drawCentredString(hx + cw / 2, y - ROW_H + 1.8 * mm, val)
                hx += cw
            # Estado: status circle
            circ_cx = hx + COL_W[4] / 2
            circ_cy = y - ROW_H / 2
            self._status_circle(circ_cx, circ_cy, 2.5 * mm, pct)

            y -= ROW_H

        self._new_page()

    def conclusiones(self, metricas: Dict, df_lineas: pd.DataFrame = None,
                     df_indicadores: pd.DataFrame = None):
        """
        Página: Conclusiones con 5 secciones.
          1. Resumen global
          2. 🔴 Indicadores que Requieren Atención (<80% o sin meta)
          3. ⚠ Indicadores En Progreso (80-99%)
          4. Recomendaciones
          5. Glosario
        """
        cont_top = self._header_band(C_NAVY, 'CONCLUSIONES Y RECOMENDACIONES', '')
        self._footer('Conclusiones')

        cumpl   = float(metricas.get('cumplimiento_promedio', 0))
        total   = int(metricas.get('total_indicadores', 0))
        cumpl_n = int(metricas.get('indicadores_cumplidos', 0))
        atenc_n = int(metricas.get('no_cumplidos', 0))
        prog_n  = int(metricas.get('en_progreso', 0))
        c_sem   = color_semaforo(cumpl)
        BW      = self.W - 2 * self.MX
        FLOOR   = self.H_FOOTER + 4 * mm

        y = cont_top - 6 * mm

        # ── SECCIÓN 1: Resumen global ─────────────────────────────────
        bw, bh = 42 * mm, 20 * mm
        self._shadow_card(self.MX, y - bh, bw, bh, c_sem, radius=4 * mm)
        self.c.setFont('Helvetica-Bold', 22)
        self.c.setFillColor(C_WHITE)
        self.c.drawCentredString(self.MX + bw / 2, y - bh + 10 * mm, f'{cumpl:.1f}%')
        self.c.setFont('Helvetica', 6.5)
        self.c.drawCentredString(self.MX + bw / 2, y - bh + 4 * mm, 'Cumplimiento Global PDI')

        # Summary KPI pills (right of badge)
        pill_items = [
            (str(total),   'Total',      C_NAVY),
            (str(cumpl_n), 'Cumplidos',  GREEN_SOLID),
            (str(prog_n),  'Progreso',   AMBER_SOLID),
            (str(atenc_n), 'Atención',   RED_SOLID),
        ]
        px = self.MX + bw + 5 * mm
        pw = (BW - bw - 5 * mm - 2 * mm * 3) / 4
        for val, lbl, col in pill_items:
            pill_bg = _light_color(col, 0.88)
            self.c.setFillColor(pill_bg)
            self.c.roundRect(px, y - bh, pw, bh, 3 * mm, fill=1, stroke=0)
            self.c.setFillColor(col)
            self.c.roundRect(px, y - bh + bh - 3, pw, 3, 2 * mm, fill=1, stroke=0)
            self.c.rect(px, y - bh + bh - 5, pw, 2, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 18)
            self.c.setFillColor(darken(col, 0.35))
            self.c.drawCentredString(px + pw / 2, y - bh + bh * 0.45, val)
            self.c.setFont('Helvetica', 6)
            self.c.setFillColor(TEXT_SECONDARY)
            self.c.drawCentredString(px + pw / 2, y - bh + 3 * mm, lbl)
            px += pw + 2 * mm

        y -= bh + 5 * mm

        # Texto descriptivo global
        en_prog_pct = prog_n / total * 100 if total else 0
        desc_txt = (
            f'El PDI 2022-{self.año} registra un cumplimiento global del {cumpl:.1f}%. '
            f'De {total} indicadores, {cumpl_n} alcanzaron o superaron su meta, '
            f'{prog_n} están en progreso ({en_prog_pct:.0f}%) y '
            f'{atenc_n} requieren atención inmediata.'
        )
        self._wrap_paragraph(desc_txt, self.MX, y, BW, 20 * mm,
                             font='Helvetica', size=8, color=C_DARK)
        y -= 14 * mm

        # ── Helper: draw semáforo block ───────────────────────────────
        def _draw_sem_block(rows, section_title, intro_text,
                            bg_col, border_col, txt_col, max_rows=20):
            nonlocal y
            if not rows or y - 14 * mm < FLOOR:
                return
            BROW_H  = 6.5 * mm
            INTRO_H = 8 * mm
            HDR_H   = 9 * mm
            n_show  = min(len(rows), max_rows)
            block_h = HDR_H + INTRO_H + n_show * BROW_H + 3 * mm
            if y - block_h < FLOOR:
                avail = y - FLOOR
                n_show = max(0, int((avail - HDR_H - INTRO_H - 3 * mm) / BROW_H))
                block_h = HDR_H + INTRO_H + n_show * BROW_H + 3 * mm
            if n_show == 0:
                return

            # Block bg + border
            self.c.setFillColor(bg_col)
            self.c.roundRect(self.MX, y - block_h, BW, block_h, 3 * mm, fill=1, stroke=0)
            self.c.setStrokeColor(border_col)
            self.c.setLineWidth(1.2)
            self.c.roundRect(self.MX, y - block_h, BW, block_h, 3 * mm, fill=0, stroke=1)
            # Left accent 4px
            self.c.setFillColor(border_col)
            self.c.roundRect(self.MX, y - block_h, 4, block_h, 2 * mm, fill=1, stroke=0)

            # Section title header
            self.c.setFont('Helvetica-Bold', 9)
            self.c.setFillColor(txt_col)
            self.c.drawString(self.MX + 7 * mm, y - HDR_H + 3 * mm, section_title)
            # Count: "N de M" when truncated, else "N indicadores"
            cnt_lbl = (f'{n_show} de {len(rows)} indicadores'
                       if n_show < len(rows)
                       else f'{len(rows)} indicador{"es" if len(rows) != 1 else ""}')
            self.c.setFont('Helvetica', 6.5)
            self.c.drawRightString(self.MX + BW - 4 * mm, y - HDR_H + 3 * mm, cnt_lbl)
            # Separator
            self.c.setStrokeColor(border_col)
            self.c.setLineWidth(0.5)
            self.c.line(self.MX + 7 * mm, y - HDR_H,
                        self.MX + BW - 4 * mm, y - HDR_H)

            # Intro text
            self.c.setFont('Helvetica-Oblique', 6.5)
            self.c.setFillColor(txt_col)
            self.c.drawString(self.MX + 7 * mm, y - HDR_H - 5 * mm, intro_text)

            row_y = y - HDR_H - INTRO_H
            for irow in rows[:n_show]:
                if row_y - BROW_H < y - block_h + 1 * mm:
                    break
                # Line pill badge
                self.c.setFillColor(irow['col_l'])
                pill_w, pill_h = 16 * mm, 4.5 * mm
                pill_x = self.MX + 7 * mm
                pill_y = row_y - BROW_H + (BROW_H - pill_h) / 2
                self.c.roundRect(pill_x, pill_y, pill_w, pill_h, 2 * mm, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 5)
                self.c.setFillColor(contrasting_text(irow['col_l']))
                linea_s = irow['linea'][:12]
                self.c.drawCentredString(pill_x + pill_w / 2, pill_y + pill_h / 2 - 1.8, linea_s)

                # Indicator name
                ind_nm = irow['nombre'][:65] + ('…' if len(irow['nombre']) > 65 else '')
                self.c.setFont('Helvetica', 6)
                self.c.setFillColor(C_DARK)
                self.c.drawString(pill_x + pill_w + 2 * mm,
                                  row_y - BROW_H + 1.8 * mm, ind_nm)

                # Meta → Ejec → % (right-aligned)
                mt  = irow['meta']
                ej  = irow['ejec']
                mt_s = f'{float(mt):.1f}' if mt is not None and str(mt) not in ('nan','None','') else 'S/M'
                ej_s = f'{float(ej):.1f}' if ej is not None and str(ej) not in ('nan','None','') else 'S/D'
                pct_s = f'{irow["pct"]:.0f}%'
                info = f'Meta {mt_s}  \u2192  Ejec {ej_s}  \u2192  {pct_s}'
                self.c.setFont('Helvetica-Bold', 6)
                self.c.setFillColor(border_col)
                self.c.drawRightString(self.MX + BW - 5 * mm,
                                       row_y - BROW_H + 1.8 * mm, info)

                # Separator line between rows
                self.c.setStrokeColor(border_col)
                self.c.setLineWidth(0.2)
                self.c.line(self.MX + 7 * mm, row_y - BROW_H,
                            self.MX + BW - 5 * mm, row_y - BROW_H)
                row_y -= BROW_H

            y -= block_h + 5 * mm

        # ── Preparar listas de indicadores ───────────────────────────
        rojo_rows  = []
        ambar_rows = []
        if df_indicadores is not None and not df_indicadores.empty:
            _ci   = next((c for c in ['Indicador','indicador']  if c in df_indicadores.columns), None)
            _cl   = next((c for c in ['Linea','Línea','linea']  if c in df_indicadores.columns), None)
            _ccmp = next((c for c in ['Cumplimiento','cumplimiento'] if c in df_indicadores.columns), None)
            _cm   = next((c for c in ['Meta','meta']            if c in df_indicadores.columns), None)
            _ce   = next((c for c in ['Ejecucion','Ejecución','ejecucion'] if c in df_indicadores.columns), None)

            if _ci and _ccmp:
                def _mk_row(r):
                    pct_v = float(r.get(_ccmp, 0) or 0)
                    ln    = str(r.get(_cl, '')) if _cl else ''
                    return {
                        'nombre': limpiar(str(r.get(_ci, ''))),
                        'linea':  ln[:16] + ('…' if len(ln) > 16 else ''),
                        'meta':   r.get(_cm) if _cm else None,
                        'ejec':   r.get(_ce) if _ce else None,
                        'pct':    pct_v,
                        'col_l':  color_linea(ln) if _cl else C_GRAY,
                    }
                rojo_rows  = sorted(
                    [_mk_row(r) for _, r in df_indicadores.iterrows()
                     if float(r.get(_ccmp, 0) or 0) < 80],
                    key=lambda x: x['pct']
                )
                ambar_rows = sorted(
                    [_mk_row(r) for _, r in df_indicadores.iterrows()
                     if 80 <= float(r.get(_ccmp, 0) or 0) < 100],
                    key=lambda x: x['pct']
                )

        # ── SECCIÓN 2: Indicadores que Requieren Atención ─────────────
        _draw_sem_block(
            rojo_rows,
            section_title='\u25cf Indicadores que Requieren Atención Inmediata  (<80%)',
            intro_text='Los siguientes indicadores no alcanzaron la meta establecida o se encuentran pendientes de definición:',
            bg_col=RED_BG, border_col=RED_SOLID, txt_col=RED_TEXT,
        )

        # ── SECCIÓN 3: Indicadores En Progreso ────────────────────────
        _draw_sem_block(
            ambar_rows,
            section_title='\u25cf Indicadores En Progreso  (80–99%)',
            intro_text='Los siguientes indicadores están cerca de la meta pero aún no la han alcanzado:',
            bg_col=AMBER_BG, border_col=AMBER_SOLID, txt_col=AMBER_TEXT,
        )

        # ── SECCIÓN 4: Recomendaciones (basadas en datos) ─────────────
        if y - 14 * mm > FLOOR:
            self.c.setFont('Helvetica-Bold', 9.5)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(self.MX, y, 'RECOMENDACIONES ESTRATÉGICAS')
            y -= 6 * mm

            # Build executive recommendations from rojo_rows / ambar_rows
            recomendaciones = []

            # R1: Indicadores críticos (<80%) — intervención inmediata
            if rojo_rows:
                worst = rojo_rows[:3]
                bullets = [f'• {r["nombre"][:70]} ({r["pct"]:.0f}%)' for r in worst]
                recomendaciones.append((
                    'Atención prioritaria',
                    C_ROJO,
                    (f'{len(rojo_rows)} indicador{"es" if len(rojo_rows)!=1 else ""} no '
                     f'alcanzaron la meta establecida. Se requiere intervención inmediata '
                     f'con plan de choque antes del cierre de {self.año}:\n'
                     + '\n'.join(bullets))
                ))

            # R2: Líneas en riesgo vs. sostenimiento
            lineas_riesgo = []
            lineas_ok = []
            if df_lineas is not None and not df_lineas.empty:
                nc_l = next((c for c in ['Linea','Línea'] if c in df_lineas.columns), None)
                cc_l = next((c for c in ['Cumplimiento'] if c in df_lineas.columns), None)
                if nc_l and cc_l:
                    for _, lr in df_lineas.iterrows():
                        pct_l = float(lr.get(cc_l, 100) or 100)
                        nom_l = nombre_display(str(lr.get(nc_l, '')))
                        if pct_l < 80:
                            lineas_riesgo.append(f'{nom_l} ({pct_l:.0f}%)')
                        elif pct_l >= 100:
                            lineas_ok.append(nom_l)
            if lineas_riesgo:
                recomendaciones.append((
                    'Líneas estratégicas en riesgo',
                    C_NARANJA,
                    ('Las siguientes líneas presentan cumplimiento por debajo del umbral mínimo '
                     'del 80% y requieren revisión de su plan de acción:\n• '
                     + '\n• '.join(lineas_riesgo[:4]))
                ))
            else:
                n_ok = len(lineas_ok)
                recomendaciones.append((
                    'Sostenimiento de logros institucionales',
                    C_VERDE,
                    (f'El {100*n_ok//max(1,len(lineas_ok)+len(lineas_riesgo))}% de las líneas '
                     f'estratégicas superaron su meta anual. Se recomienda documentar las '
                     f'mejores prácticas y replicar metodologías exitosas en las líneas con '
                     f'menor dinamismo para el siguiente ciclo de planeación.')
                    if n_ok else
                    'Todas las líneas superan el 80% de cumplimiento. Mantener el ritmo '
                    'de ejecución y evitar retrocesos en los indicadores de alto impacto.'
                ))

            # R3: Indicadores próximos a meta — esfuerzo final
            if ambar_rows:
                close = sorted(ambar_rows, key=lambda x: -x['pct'])[:3]
                bullets_c = [f'• {r["nombre"][:65]} ({r["pct"]:.0f}%)' for r in close]
                gap_promedio = sum(100 - r['pct'] for r in close) / len(close)
                recomendaciones.append((
                    'Indicadores próximos al cierre',
                    C_ACCENT,
                    (f'{len(ambar_rows)} indicadores están en progreso con una brecha promedio '
                     f'de {gap_promedio:.1f}% respecto a la meta. Con acciones focalizadas es '
                     f'posible alcanzar el 100%:\n' + '\n'.join(bullets_c))
                ))

            # R4: Transferencia de conocimiento
            if lineas_ok:
                recomendaciones.append((
                    'Transferencia de buenas prácticas',
                    C_NAVY,
                    (f'Las líneas {", ".join(lineas_ok[:3])} demuestran un desempeño '
                     f'sobresaliente. Se recomienda sistematizar sus modelos de gestión y '
                     f'transferir aprendizajes al resto de la organización para el siguiente '
                     f'ciclo del PDI.')
                ))

            CARD_GAP = 3 * mm
            for titulo, accent_col, desc in recomendaciones:
                # Calcular altura necesaria según líneas de texto
                desc_lines = desc.count('\n') + max(1, len(desc) // 90)
                CARD_H = max(14 * mm, min(8 + desc_lines * 8, int(40 * mm)))
                if y - CARD_H < FLOOR:
                    break
                self._shadow_card(self.MX, y - CARD_H, BW, CARD_H, C_BG, radius=2 * mm)
                self.c.setFillColor(accent_col)
                self.c.roundRect(self.MX, y - CARD_H, 2.5 * mm, CARD_H, 1 * mm, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 8.5)
                self.c.setFillColor(C_NAVY)
                self.c.drawString(self.MX + 5 * mm, y - 5.5 * mm, titulo)
                # Texto de descripción con wrap
                self._wrap_paragraph(desc.replace('\n• ', ' • ').replace('\n', ' '),
                                     self.MX + 5 * mm, y - 7.5 * mm,
                                     BW - 7 * mm, CARD_H - 9 * mm,
                                     font='Helvetica', size=7, color=C_DARK)
                y -= CARD_H + CARD_GAP

        y -= 5 * mm

        # ── SECCIÓN 5: Glosario ───────────────────────────────────────
        if y > FLOOR + 30 * mm:
            self.c.setFont('Helvetica-Bold', 9.5)
            self.c.setFillColor(C_NAVY)
            self.c.drawString(self.MX, y, 'GLOSARIO DE SIGLAS')
            y -= 5 * mm

            items   = list(GLOSARIO.items())
            cols    = 2
            col_w   = BW / cols
            row_h_g = 8.5 * mm

            for i, (sigla, desc) in enumerate(items):
                gx = self.MX + (i % cols) * col_w
                gy = y - (i // cols) * row_h_g
                if gy < FLOOR:
                    break
                self.c.setFont('Helvetica-Bold', 8)
                self.c.setFillColor(C_ACCENT)
                self.c.drawString(gx, gy, f'{sigla}:')
                self.c.setFont('Helvetica', 7)
                self.c.setFillColor(C_DARK)
                # Use full description (no truncation) — col_w is ~87mm, ~80 chars at 7pt
                max_g = int((col_w - 16 * mm) / (3.8))
                desc_s = desc[:max_g] + ('…' if len(desc) > max_g else '')
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

    # 2. Resumen ejecutivo con gráficas
    pdf.resumen_ejecutivo(metricas, analisis_texto=analisis_texto,
                          df_lineas=df_lineas)

    # 3. Resumen circular por línea (tarjetas con mini donut)
    pdf.pagina_cumplimiento_lineas(df_lineas)

    # 4. Página detallada por línea estratégica — en ORDEN_LINEAS
    if df_lineas is not None and not df_lineas.empty:
        nc = 'Nivel' if (df_cascada is not None and 'Nivel' in df_cascada.columns) else None
        lc = 'Linea' if (df_cascada is not None and 'Linea' in df_cascada.columns) else None

        # Sort df_lineas by ORDEN_LINEAS
        def _sort_key(row):
            n = _norm(str(row.get('Linea', row.get('Línea', ''))))
            for i, ol in enumerate(ORDEN_LINEAS):
                if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                    return i
            return 99

        df_lineas_sorted = df_lineas.copy()
        df_lineas_sorted['_sort'] = [
            _sort_key(r) for _, r in df_lineas_sorted.iterrows()
        ]
        df_lineas_sorted = df_lineas_sorted.sort_values('_sort').drop(columns=['_sort'])

        for _, lr in df_lineas_sorted.iterrows():
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

            # ── Indicadores Sin Meta (Meta=NaN/0) ─────────────────────
            sin_meta = []
            if df_unificado is not None and not df_unificado.empty:
                has_lin_u  = 'Linea' in df_unificado.columns
                has_meta_u = 'Meta' in df_unificado.columns
                has_ind_u  = 'Indicador' in df_unificado.columns
                if has_lin_u and has_meta_u and has_ind_u:
                    smask = df_unificado['Linea'] == nom
                    if 'Año' in df_unificado.columns:
                        smask &= df_unificado['Año'] == año
                    if 'Proyectos' in df_unificado.columns:
                        smask &= df_unificado['Proyectos'] == 0
                    df_sm = df_unificado[smask]
                    # Filter where Meta is NaN or zero
                    meta_null = df_sm['Meta'].isna() | (df_sm['Meta'] == 0)
                    df_sm_null = df_sm[meta_null].drop_duplicates('Indicador')
                    for _, sr in df_sm_null.iterrows():
                        sin_meta.append({
                            'nombre': str(sr.get('Indicador', '')),
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
                sin_meta=sin_meta if sin_meta else None,
            )

    # 5. Tabla de indicadores
    if df_indicadores is not None and not df_indicadores.empty:
        pdf.tabla_indicadores(df_indicadores)

    # 6. Conclusiones y glosario
    pdf.conclusiones(metricas, df_lineas, df_indicadores=df_indicadores)

    return pdf.generar()
