# -*- coding: utf-8 -*-
"""
pdf_primitives.py — Helper functions y primitivos de dibujo para PDFs PDI.
"""
from __future__ import annotations

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

from utils.pdf_colors import *  # noqa: F401, F403


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
# MODULE-LEVEL PRIMITIVE DRAWING FUNCTIONS
# ============================================================

_C_BG_PAGE = colors.HexColor('#F7F9FC')


def _dot_bg(c, W: float, H: float, spacing: float = 14 * mm):
    """Draw a subtle dot-texture background."""
    c.setFillColor(colors.HexColor('#D1DCE8'))
    dot_r = 0.6
    x = spacing / 2
    while x < W:
        y = spacing / 2
        while y < H:
            c.circle(x, y, dot_r, fill=1, stroke=0)
            y += spacing
        x += spacing


def _page_bg(c, W: float, H: float, accent_col: colors.Color):
    """Page background: light fill + dot texture + decorative circle."""
    c.setFillColor(_C_BG_PAGE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    _dot_bg(c, W, H)
    # Large decorative circle top-right (faint)
    c.setFillColor(colors.Color(
        accent_col.red, accent_col.green, accent_col.blue, alpha=0.06
    ) if hasattr(accent_col, 'red') else colors.HexColor('#e3edf7'))
    try:
        c.setFillColor(colors.Color(accent_col.red, accent_col.green, accent_col.blue, 0.06))
    except Exception:
        c.setFillColor(colors.HexColor('#e3edf7'))
    c.circle(W + 10 * mm, H + 10 * mm, 55 * mm, fill=1, stroke=0)


def _std_header(c, W: float, H: float, HEADER_H: float, MX: float,
                titulo: str, subtitulo: str, accent_col: colors.Color):
    """Standard navy header band with diagonal accent stripe."""
    y0 = H - HEADER_H
    # Navy base
    c.setFillColor(NAVY_DARK)
    c.rect(0, y0, W, HEADER_H, fill=1, stroke=0)
    # Diagonal accent stripe (right third)
    stripe_w = W * 0.38
    pts = [W - stripe_w, y0,
           W, y0,
           W, y0 + HEADER_H,
           W - stripe_w * 0.7, y0 + HEADER_H]
    c.setFillColor(accent_col)
    c.setStrokeColor(accent_col)
    p = c.beginPath()
    p.moveTo(pts[0], pts[1])
    p.lineTo(pts[2], pts[3])
    p.lineTo(pts[4], pts[5])
    p.lineTo(pts[6], pts[7])
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # Bottom accent line
    c.setFillColor(accent_col)
    c.rect(0, y0, W, 2, fill=1, stroke=0)
    # Title text
    c.setFillColor(colors.white)
    if subtitulo:
        t_fsize = 13 if len(titulo) <= 24 else (11 if len(titulo) <= 34 else 9.5)
        c.setFont('Helvetica-Bold', t_fsize)
        t_y = y0 + HEADER_H * 0.58
        c.drawString(MX, t_y, titulo)
        c.setFont('Helvetica', 7.5)
        c.setFillColor(colors.HexColor('#c8d8f0'))
        c.drawString(MX, y0 + HEADER_H * 0.22, subtitulo)
    else:
        t_fsize = 14 if len(titulo) <= 28 else (11 if len(titulo) <= 38 else 9)
        c.setFont('Helvetica-Bold', t_fsize)
        c.drawCentredString(W / 2, y0 + HEADER_H * 0.38, titulo)
    return y0 - 2 * mm


def _header_linea(c, W: float, H: float, MX: float,
                  nombre: str, cumplimiento: float, total_ind: int,
                  col_linea: colors.Color, n_cumpl: int, año: int):
    """
    Header A for line pages: navy base + right trapezoid zone with 4 stats.
    Returns y_bottom of header (start of content area).
    """
    HEADER_H = 28 * mm
    y0 = H - HEADER_H
    # Navy base
    c.setFillColor(NAVY_DARK)
    c.rect(0, y0, W, HEADER_H, fill=1, stroke=0)
    # Right trapezoid in line color
    trap_w = W * 0.45
    p = c.beginPath()
    p.moveTo(W - trap_w * 1.1, y0)
    p.lineTo(W, y0)
    p.lineTo(W, y0 + HEADER_H)
    p.lineTo(W - trap_w * 0.85, y0 + HEADER_H)
    p.close()
    c.setFillColor(col_linea)
    c.drawPath(p, fill=1, stroke=0)
    # Bottom accent line
    c.setFillColor(col_linea)
    c.rect(0, y0, W, 2, fill=1, stroke=0)
    # Line name (left)
    nom_d = nombre_display(nombre)
    c.setFillColor(colors.white)
    t_fsize = 13 if len(nom_d) <= 24 else (11 if len(nom_d) <= 34 else 9.5)
    c.setFont('Helvetica-Bold', t_fsize)
    c.drawString(MX, y0 + HEADER_H * 0.58, nom_d.upper())
    c.setFont('Helvetica', 7.5)
    c.setFillColor(colors.HexColor('#c8d8f0'))
    c.drawString(MX, y0 + HEADER_H * 0.22, f'Plan de Desarrollo Institucional {año}')
    # 4 stats in right trapezoid zone
    txt_col = darken(col_linea, 0.55) if is_light_color(col_linea) else colors.white
    stats = [
        (f'{cumplimiento:.1f}%', 'Cumplimiento'),
        (str(total_ind),         'Indicadores'),
        (str(n_cumpl),           'Cumplidos'),
        (texto_estado(cumplimiento), 'Estado'),
    ]
    stat_zone_x = W - trap_w * 0.85
    stat_zone_w = W - stat_zone_x - MX * 0.5
    sw = stat_zone_w / 4
    for i, (val, lbl) in enumerate(stats):
        sx = stat_zone_x + i * sw + sw / 2
        c.setFont('Helvetica-Bold', 9 if len(val) <= 6 else 7)
        c.setFillColor(txt_col)
        c.drawCentredString(sx, y0 + HEADER_H * 0.58, val)
        c.setFont('Helvetica', 5.5)
        c.setFillColor(darken(col_linea, 0.3) if is_light_color(col_linea) else colors.HexColor('#c8d8f0'))
        c.drawCentredString(sx, y0 + HEADER_H * 0.28, lbl)
    return y0 - 2 * mm


def _footer_std(c, W: float, FOOTER_H: float, MX: float,
                año: int, page_num: int, subtitulo: str,
                accent_col: colors.Color):
    """Footer with accent color top line."""
    y = FOOTER_H - 4 * mm
    # Accent line
    c.setStrokeColor(accent_col)
    c.setLineWidth(1.2)
    c.line(MX, y + 3 * mm, W - MX, y + 3 * mm)
    c.setLineWidth(0.4)
    c.setFont('Helvetica', 6.5)
    c.setFillColor(TEXT_SECONDARY)
    fecha = datetime.now().strftime('%d/%m/%Y')
    c.drawString(MX, y, f'PDI {año} | {limpiar(subtitulo)}')
    c.drawRightString(W - MX, y,
                      f'Página {page_num} | Gerencia de Planeación | {fecha}')


def _ai_block(c, x: float, y: float, w: float, h: float,
              texto: str, gradient_fn=None):
    """Module-level AI analysis card."""
    # Background
    c.setFillColor(AI_BG_COL)
    c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=0)
    # Subtle border
    c.setStrokeColor(colors.HexColor('#BAE6FD'))
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 3 * mm, fill=0, stroke=1)
    # Left accent bar
    c.setFillColor(AI_BORDER_COL)
    c.roundRect(x, y, 3, h, 1.5 * mm, fill=1, stroke=0)
    # Badge gradient (manual steps)
    badge_w, badge_h = 34 * mm, 6.5 * mm
    badge_x = x + 6 * mm
    badge_y = y + h - badge_h - 3.5 * mm
    steps = 24
    c1, c2 = AI_BORDER_COL, AI_BADGE_END
    for i in range(steps):
        t = i / steps
        r = c1.red   + (c2.red   - c1.red)   * t
        g = c1.green + (c2.green - c1.green) * t
        b = c1.blue  + (c2.blue  - c1.blue)  * t
        bw = badge_w / steps + 0.5
        c.setFillColorRGB(r, g, b)
        c.rect(badge_x + badge_w * i / steps, badge_y, bw, badge_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 6.5)
    c.drawString(badge_x + 2.5 * mm, badge_y + badge_h / 2 - 2.5,
                 '\u2736 IA  Análisis Estratégico')
    c.setFont('Helvetica-Oblique', 5.5)
    c.setFillColor(TEXT_MUTED)
    c.drawRightString(x + w - 3 * mm, badge_y + badge_h / 2 - 2,
                      'Generado con Inteligencia Artificial')
    # Text
    if texto:
        style = ParagraphStyle(
            'ai_ml',
            fontSize=8,
            fontName='Helvetica-Oblique',
            leading=10.8,
            textColor=AI_TEXT_COL,
        )
        safe_txt = limpiar(texto).replace('\n', '<br/>')
        p = Paragraph(safe_txt, style)
        txt_y_top = badge_y - 2.5 * mm
        avail_h = txt_y_top - y - 2 * mm
        avail_w = w - 10 * mm
        _, actual_h = p.wrap(avail_w, avail_h)
        p.drawOn(c, x + 6 * mm, txt_y_top - actual_h)
