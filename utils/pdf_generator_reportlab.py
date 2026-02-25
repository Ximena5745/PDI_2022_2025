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
            noms  = [str(n)[:24] for n in df_lineas[nom_col]]
            cumps = [float(c or 0) for c in df_lineas[cum_col]]
            bar_cols = []
            for n in df_lineas[nom_col]:
                col = color_linea(str(n))
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

        # ── 3 SMALLER KPI CARDS ───────────────────────────────────────
        KPI_H = 19 * mm
        KPI_Y = y_main - GAP - KPI_H
        KPI_W = (card_w - 2 * GAP) / 3

        small_kpis = [
            (str(total),   'Total Indicadores', '#F0F9FF', '#1FB2DE', '#0a2240', None),
            (str(cumpl_n), 'Cumplidos ≥100%',   '#F0FDF4', '#10B981', '#166534',
             f'{cumpl_n / total * 100:.1f}%' if total else ''),
            (str(en_prog), 'En Progreso 80–99%','#FFFBEB', '#F59E0B', '#92400E',
             f'{en_prog / total * 100:.1f}%' if total else ''),
        ]
        for i, (val, lbl, bg_h, top_h, txt_h, badge) in enumerate(small_kpis):
            kx = MX + i * (KPI_W + GAP)
            ky = KPI_Y
            # Shadow
            self.c.setFillColor(C_SHADOW)
            self.c.roundRect(kx + 2, ky - 2, KPI_W, KPI_H, 3 * mm, fill=1, stroke=0)
            # Card bg
            self.c.setFillColor(colors.HexColor(bg_h))
            self.c.roundRect(kx, ky, KPI_W, KPI_H, 3 * mm, fill=1, stroke=0)
            # Top border 3px
            top_c = colors.HexColor(top_h)
            self.c.setFillColor(top_c)
            self.c.roundRect(kx, ky + KPI_H - 3, KPI_W, 3, 1.5 * mm, fill=1, stroke=0)
            self.c.rect(kx, ky + KPI_H - 5, KPI_W, 2, fill=1, stroke=0)
            # Value
            self.c.setFont('Helvetica-Bold', 30)
            self.c.setFillColor(colors.HexColor(txt_h))
            self.c.drawCentredString(kx + KPI_W / 2, ky + KPI_H * 0.47, val)
            # Label
            self.c.setFont('Helvetica', 7.5)
            self.c.setFillColor(TEXT_SECONDARY)
            self.c.drawCentredString(kx + KPI_W / 2, ky + 3 * mm, lbl)
            # Sub-badge percentage
            if badge:
                sb_col = colors.HexColor(top_h)
                sb_bg  = colors.HexColor(bg_h)
                self.c.setFillColor(sb_bg)
                self.c.setFont('Helvetica-Bold', 6.5)
                self.c.setFillColor(sb_col)
                self.c.drawCentredString(kx + KPI_W / 2, ky + KPI_H * 0.72, badge)

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

        # ── AI ANALYSIS BLOCK ─────────────────────────────────────────
        AI_BOTTOM = self.H_FOOTER + 4 * mm
        ai_h = CHART_Y - GAP - AI_BOTTOM
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
                if _norm(ol) == n or _norm(ol) in n or n in _norm(ol):
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
        card_h   = min((avail_h - (N_ROWS - 1) * GAP) / N_ROWS, 115 * mm)

        for idx, (nom, pct, n_ind, cn, ep, ac) in enumerate(lineas):
            col_i  = idx % N_COLS
            row_i  = idx // N_COLS
            card_x = MX_GRID + col_i * (card_w + GAP)
            card_y = self.H - 26 * mm - (row_i + 1) * card_h - row_i * GAP

            col   = color_linea(nom)
            c_sem = color_semaforo(pct)
            nom_d = nombre_display(nom)

            # ── Shadow (3D offset) ────────────────────────────────────
            self.c.setFillColor(C_SHADOW)
            self.c.roundRect(card_x + 3, card_y - 3, card_w, card_h,
                             4 * mm, fill=1, stroke=0)
            # ── Card bg: lighten(col, 0.88) ───────────────────────────
            card_bg = _light_color(col, 0.88)
            self.c.setFillColor(card_bg)
            self.c.roundRect(card_x, card_y, card_w, card_h, 4 * mm, fill=1, stroke=0)
            # ── 4px left border ───────────────────────────────────────
            self.c.setFillColor(col)
            self.c.rect(card_x, card_y, 4, card_h, fill=1, stroke=0)
            # ── 5pt top stripe ────────────────────────────────────────
            self.c.roundRect(card_x, card_y + card_h - 5,
                             card_w, 5, 4 * mm, fill=1, stroke=0)
            self.c.rect(card_x, card_y + card_h - 7, card_w, 3, fill=1, stroke=0)

            # ── Name label (Bold 10pt, contrasting color) ─────────────
            # Always inside the card, 12pt below top stripe
            name_col = contrasting_text(card_bg)   # dark on light bg
            # For extra readability, always use darken(col, 0.50)
            name_col = darken(col, 0.50)
            self.c.setFont('Helvetica-Bold', 9)
            self.c.setFillColor(name_col)
            # Wrap long names to 2 lines
            words = nom_d.split()
            if len(words) > 2:
                mid = (len(words) + 1) // 2
                ln1 = ' '.join(words[:mid])
                ln2 = ' '.join(words[mid:])
            else:
                ln1 = nom_d
                ln2 = ''
            name_top = card_y + card_h - 8        # just below top stripe
            self.c.drawCentredString(card_x + card_w / 2, name_top - 10, ln1)
            if ln2:
                self.c.setFont('Helvetica', 7.5)
                self.c.drawCentredString(card_x + card_w / 2, name_top - 20, ln2)

            name_bottom = name_top - (22 if ln2 else 14)

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
                # Centre label: total indicadores
                dcx = dx + dsz / 2
                dcy = dy + dsz / 2
                self.c.setFont('Helvetica-Bold', 7)
                self.c.setFillColor(TEXT_PRIMARY)
                self.c.drawCentredString(dcx, dcy - 3, str(n_ind))

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
            self.c.setFillColor(NAVY_DARK)
            self.c.drawString(self.MX, y_cur, 'OBJETIVOS E INDICADORES')
            y_cur -= 5 * mm

            # Leyenda de cascada — dibujada UNA sola vez, antes del bucle
            tbl_w = sum(IND_COL_W)
            y_cur = self._draw_leyenda_header(self.MX, y_cur, tbl_w, col_linea)


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
                    self._gradient_band(self.MX, y_cur - HDR_H, IND_TBL_W, HDR_H,
                                        C_NAVY, C_HDR_GRAD_END)
                    # 2px accent line bottom of header
                    self.c.setFillColor(col_linea)
                    self.c.rect(self.MX, y_cur - HDR_H, IND_TBL_W, 2, fill=1, stroke=0)
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
                        bg = C_TABLE_ROW_ALT if ridx % 2 == 0 else C_WHITE

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
                        num_vals = [
                            f'{float(meta_v):.1f}' if (
                                meta_v is not None and
                                str(meta_v) not in ('nan', 'None', '')
                            ) else '-',
                            f'{float(ejec_v):.1f}' if (
                                ejec_v is not None and
                                str(ejec_v) not in ('nan', 'None', '')
                            ) else '-',
                            f'{ind_pct:.0f}%',
                        ]
                        hx = self.MX + IND_COL_W[0]
                        for j, (val, cw) in enumerate(zip(num_vals, IND_COL_W[1:4])):
                            fnt = 'Helvetica-Bold' if j == 2 else 'Helvetica'
                            clr = ind_scol if j == 2 else C_DARK
                            self.c.setFont(fnt, 6.5)
                            self.c.setFillColor(clr)
                            self.c.drawCentredString(hx + cw / 2,
                                                     y_cur - ROW_H + 1.8 * mm, val)
                            hx += cw
                        # Estado: status circle
                        self._status_circle(hx + IND_COL_W[4] / 2,
                                            y_cur - ROW_H / 2, 2.5 * mm, ind_pct)
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
                if _norm(ol) == n or _norm(ol) in n or n in _norm(ol):
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
