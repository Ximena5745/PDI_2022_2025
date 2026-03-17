# -*- coding: utf-8 -*-
"""
pdf_pages.py — Clase PDFReportePOLI con todos los métodos de generación de páginas.
"""
from __future__ import annotations

import os
import io
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
from utils.pdf_primitives import *  # noqa: F401, F403


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
            import matplotlib.colors as mcolors

            fig, ax = plt.subplots(figsize=(w_pt / 72, h_pt / 72))
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
            y_pos = list(range(len(noms)))

            # Background extent: max of 107% or max compliance + 5, rounded up
            bg_extent = max(107, (max(cumps, default=0) + 5))

            BAR_H = 0.52

            for i, (nom, val, col_hex) in enumerate(zip(noms, cumps, bar_cols)):
                # Light background bar
                light = mcolors.to_rgba(col_hex, alpha=0.18)
                ax.barh(i, bg_extent, color=light, height=BAR_H, zorder=1,
                        edgecolor='none')
                # Actual filled bar
                ax.barh(i, val, color=col_hex, height=BAR_H, zorder=2,
                        edgecolor='none')
                # Percentage label to the right of background bar
                ax.text(bg_extent + 1.5, i,
                        f'{val:.0f}%', va='center', ha='left', fontsize=7,
                        color='#333333', fontfamily='DejaVu Sans',
                        fontweight='bold')

            # Dashed reference line at 100%
            ax.axvline(100, color='#555555', linestyle='--', linewidth=0.9,
                       alpha=0.7, zorder=3)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(noms, fontsize=7.5, color='#333333')
            ax.set_xlim(0, bg_extent + 14)
            ax.set_xlabel('')
            ax.tick_params(axis='x', bottom=False, labelbottom=False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.tick_params(axis='y', length=0)
            fig.tight_layout(pad=0.4)
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
        ACC = colors.HexColor('#1e88e5')
        _page_bg(self.c, self.W, self.H, ACC)
        cont_top = _std_header(
            self.c, self.W, self.H, self.H_HEADER, self.MX,
            'RESUMEN EJECUTIVO',
            f'Plan de Desarrollo Institucional {self.año}',
            ACC
        )
        _footer_std(self.c, self.W, self.H_FOOTER, self.MX,
                    self.año, self._page, 'Resumen Ejecutivo', ACC)

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
            top_c = colors.HexColor(top_h)
            # Shadow
            self.c.setFillColor(C_SHADOW)
            self.c.roundRect(kx + 2, ky - 2, KPI_W, kpi_h, 3 * mm, fill=1, stroke=0)
            # Card bg
            self.c.setFillColor(colors.HexColor(bg_h))
            self.c.roundRect(kx, ky, KPI_W, kpi_h, 3 * mm, fill=1, stroke=0)
            # Left accent bar (4px, rounded)
            self.c.setFillColor(top_c)
            self.c.roundRect(kx, ky + 3 * mm, 4, kpi_h - 6 * mm, 2, fill=1, stroke=0)
            # Value (big number) — centrado verticalmente en la mitad superior
            num_y = ky + kpi_h * 0.50
            self.c.setFont('Helvetica-Bold', fsize)
            self.c.setFillColor(colors.HexColor(txt_h))
            self.c.drawCentredString(kx + KPI_W / 2, num_y, val)
            # Label — debajo del numero con separación clara
            lbl_y = ky + 2.5 * mm
            self.c.setFont('Helvetica', 6 if i > 0 else 7)
            self.c.setFillColor(TEXT_SECONDARY)
            self.c.drawCentredString(kx + KPI_W / 2, lbl_y, lbl)
            # Porcentaje — solo para cards 2 y 3, entre numero y label (sin solapar)
            if i > 0 and total:
                pct_badge = f'{int(val) / total * 100:.0f}%'
                mid_y = ky + kpi_h * 0.25  # zona entre numero y label
                self.c.setFont('Helvetica-Bold', 7)
                self.c.setFillColor(top_c)
                self.c.drawCentredString(kx + KPI_W / 2, mid_y, pct_badge)

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
            _ai_block(self.c, MX, AI_BOTTOM, card_w, ai_h, analisis_texto)
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
        Página de resumen: fondo claro, header estándar, grid 3×2 con
        medidores semicirculares (gauges) por línea estratégica.
        """
        if df_lineas is None or df_lineas.empty:
            return

        ACC = colors.HexColor('#1e88e5')
        _page_bg(self.c, self.W, self.H, ACC)
        _std_header(self.c, self.W, self.H, self.H_HEADER, self.MX,
                    'CUMPLIMIENTO POR LÍNEA ESTRATÉGICA',
                    f'Plan de Desarrollo Institucional {self.año}',
                    ACC)
        _footer_std(self.c, self.W, self.H_FOOTER, self.MX,
                    self.año, self._page,
                    'Cumplimiento por Línea Estratégica', ACC)

        # Extract per-line data
        lineas = []
        for _, r in df_lineas.iterrows():
            nom   = str(r.get('Linea', r.get('Línea', '')))
            pct   = float(r.get('Cumplimiento', 0) or 0)
            n_ind = int(r.get('Total_Indicadores', 0) or 0)
            cn    = int(r.get('Cumplidos', r.get('indicadores_cumplidos', 0)) or 0)
            ep    = int(r.get('En_Progreso', r.get('en_progreso', 0)) or 0)
            ac    = int(r.get('No_Cumplidos', r.get('Atencion', 0)) or 0)
            if cn == 0 and ep == 0 and ac == 0 and n_ind > 0:
                cn = round(n_ind * min(pct / 100, 1.0))
                ep = round((n_ind - cn) * (0.6 if pct >= 80 else 0.3))
                ac = n_ind - cn - ep
            lineas.append((nom, pct, n_ind, cn, ep, ac))

        def _linea_order(t):
            n = _norm(t[0])
            for i, ol in enumerate(ORDEN_LINEAS):
                if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                    return i
            return 99
        lineas.sort(key=_linea_order)

        # ── Matplotlib figure with 3×2 semicircular gauges ─────────
        if MATPLOTLIB_AVAILABLE and lineas:
            try:
                import math as _math
                import numpy as _np
                from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

                N = len(lineas)
                n_cols = 3
                n_rows = (N + n_cols - 1) // n_cols

                # Figure fills the exact PDF content area → no wasted space
                img_x  = self.MX
                img_y  = self.H_FOOTER + 3 * mm
                img_w  = self.W - 2 * self.MX          # pts
                img_h  = self.H - self.H_HEADER - self.H_FOOTER - 6 * mm
                fig_w  = img_w / 72                     # pts → inches
                fig_h  = img_h / 72

                fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h))
                fig.patch.set_facecolor('#F7F9FC')

                # Normalise axes array to always be 2-D list
                if n_rows == 1 and n_cols == 1:
                    axes = [[axes]]
                elif n_rows == 1:
                    axes = [list(axes)]
                elif n_cols == 1:
                    axes = [[ax] for ax in axes]

                # Tight margins – gauges fill every cell
                fig.subplots_adjust(left=0.01, right=0.99,
                                    top=0.99, bottom=0.01,
                                    hspace=0.06, wspace=0.06)

                # ── Coordinate space per cell ────────────────────────────
                # xlim: -1.25 … 1.25  (2.5 units, symmetric)
                # ylim: -1.10 … 1.40  (2.5 units → square data area)
                # set_aspect is NOT set → matplotlib fills the full cell
                # The arc is drawn via fill-polygon using cos/sin but scaled
                # to stay circular regardless of cell proportions.

                for idx, (nom, pct, n_ind, cn, ep, ac) in enumerate(lineas):
                    ri = idx // n_cols
                    ci = idx % n_cols
                    ax = axes[ri][ci]

                    col_rl  = color_linea(nom)
                    col_hex = f'#{int(col_rl.red*255):02x}' \
                              f'{int(col_rl.green*255):02x}' \
                              f'{int(col_rl.blue*255):02x}'
                    sem_rl  = color_semaforo(pct)
                    sem_hex = f'#{int(sem_rl.red*255):02x}' \
                              f'{int(sem_rl.green*255):02x}' \
                              f'{int(sem_rl.blue*255):02x}'
                    is_lt   = is_light_color(col_rl)
                    txt_col = '#1E293B' if is_lt else 'white'

                    # ── Axes limits and background ───────────────────────
                    XL, XR = -1.25, 1.25     # x range  (2.5 units)
                    YB, YT =  -1.10, 1.40    # y range  (2.5 units)
                    ax.set_xlim(XL, XR)
                    ax.set_ylim(YB, YT)
                    ax.axis('off')
                    ax.set_facecolor('#F7F9FC')

                    # Subtle card background
                    card_bg = FancyBboxPatch(
                        (XL, YB), XR - XL, YT - YB,
                        boxstyle='round,pad=0.03,rounding_size=0.12',
                        facecolor='white', edgecolor='#E2EAF4',
                        linewidth=1.2, zorder=0)
                    ax.add_patch(card_bg)

                    # ── Header strip ─────────────────────────────────────
                    HDR_Y = 0.92          # top-of-strip y
                    HDR_H = 0.38          # strip height
                    hdr = FancyBboxPatch(
                        (XL + 0.05, HDR_Y), (XR - XL - 0.10), HDR_H,
                        boxstyle='round,pad=0.02,rounding_size=0.08',
                        facecolor=col_hex, edgecolor='none', zorder=3)
                    ax.add_patch(hdr)

                    nom_d  = nombre_display(nom)
                    words  = nom_d.split()
                    if len(words) > 2:
                        mid = len(words) // 2
                        ln1 = ' '.join(words[:mid])
                        ln2 = ' '.join(words[mid:])
                    else:
                        ln1, ln2 = nom_d, ''
                    if ln2:
                        ax.text(0, HDR_Y + HDR_H * 0.70, ln1,
                                ha='center', va='center',
                                fontsize=7, fontweight='bold', color=txt_col,
                                fontfamily='DejaVu Sans', zorder=4)
                        ax.text(0, HDR_Y + HDR_H * 0.28, ln2,
                                ha='center', va='center',
                                fontsize=6.5, color=txt_col,
                                fontfamily='DejaVu Sans', zorder=4)
                    else:
                        ax.text(0, HDR_Y + HDR_H * 0.50, ln1,
                                ha='center', va='center',
                                fontsize=7.5, fontweight='bold', color=txt_col,
                                fontfamily='DejaVu Sans', zorder=4)

                    # ── Semicircular gauge ────────────────────────────────
                    # Arc polygon: outer radius=0.82, inner=0.54, center=(0,0)
                    R_OUT, R_IN = 0.82, 0.54
                    theta_full = _np.linspace(_math.pi, 0, 300)
                    xs_out = R_OUT * _np.cos(theta_full)
                    ys_out = R_OUT * _np.sin(theta_full)
                    xs_in  = R_IN  * _np.cos(theta_full[::-1])
                    ys_in  = R_IN  * _np.sin(theta_full[::-1])
                    ax.fill(list(xs_out) + list(xs_in),
                            list(ys_out) + list(ys_in),
                            color='#DDE3EA', zorder=2)

                    # Value arc (up to 125% max = full sweep)
                    val_frac = min(pct / 125.0, 1.0)
                    theta_v  = _np.linspace(_math.pi,
                                            _math.pi - _math.pi * val_frac, 300)
                    xs_ov = R_OUT * _np.cos(theta_v)
                    ys_ov = R_OUT * _np.sin(theta_v)
                    xs_iv = R_IN  * _np.cos(theta_v[::-1])
                    ys_iv = R_IN  * _np.sin(theta_v[::-1])
                    ax.fill(list(xs_ov) + list(xs_iv),
                            list(ys_ov) + list(ys_iv),
                            color=sem_hex, zorder=3)

                    # 100% reference tick
                    frac_100 = 100 / 125.0
                    ang_100  = _math.pi - _math.pi * frac_100
                    tx0 = R_IN  * _math.cos(ang_100)
                    ty0 = R_IN  * _math.sin(ang_100)
                    tx1 = (R_OUT + 0.08) * _math.cos(ang_100)
                    ty1 = (R_OUT + 0.08) * _math.sin(ang_100)
                    ax.plot([tx0, tx1], [ty0, ty1],
                            color='#EF4444', linewidth=1.2,
                            alpha=0.75, zorder=4)
                    ax.text(tx1 + 0.04, ty1 + 0.03, '100%',
                            ha='left', va='bottom',
                            fontsize=4.5, color='#EF4444',
                            alpha=0.80, fontfamily='DejaVu Sans')

                    # Scale labels 0% / 125%
                    ax.text(-R_OUT - 0.08, -0.04, '0%',
                            ha='center', va='top',
                            fontsize=5, color='#94A3B8',
                            fontfamily='DejaVu Sans')
                    ax.text( R_OUT + 0.08, -0.04, '125%',
                            ha='center', va='top',
                            fontsize=5, color='#94A3B8',
                            fontfamily='DejaVu Sans')

                    # Needle
                    needle_ang = _math.pi - _math.pi * val_frac
                    nx = (R_IN + 0.18) * _math.cos(needle_ang)
                    ny = (R_IN + 0.18) * _math.sin(needle_ang)
                    ax.annotate('',
                        xy=(nx, ny), xytext=(0, 0),
                        arrowprops=dict(arrowstyle='->', color='#0a2240',
                                        lw=1.8, mutation_scale=10),
                        zorder=6)
                    ax.scatter([0], [0], s=30, color='#0a2240',
                               zorder=7, clip_on=False)

                    # ── Central text ─────────────────────────────────────
                    ax.text(0, 0.24, f'{pct:.0f}%',
                            ha='center', va='center',
                            fontsize=16, fontweight='bold',
                            color=sem_hex, fontfamily='DejaVu Sans', zorder=7)

                    # Status badge (pill)
                    estado = texto_estado(pct)
                    sbg = {'CUMPLIDO': '#DCFCE7',
                           'EN PROGRESO': '#FEF3C7',
                           'ATENCIÓN': '#FEE2E2'}.get(estado, '#F1F5F9')
                    sfg = {'CUMPLIDO': '#166534',
                           'EN PROGRESO': '#92400E',
                           'ATENCIÓN': '#991B1B'}.get(estado, '#334155')
                    badge = FancyBboxPatch(
                        (-0.60, -0.20), 1.20, 0.25,
                        boxstyle='round,pad=0.02,rounding_size=0.06',
                        facecolor=sbg, edgecolor='none', zorder=5)
                    ax.add_patch(badge)
                    ax.text(0, -0.075, estado,
                            ha='center', va='center',
                            fontsize=6, fontweight='bold', color=sfg,
                            fontfamily='DejaVu Sans', zorder=6)

                    # ── Bottom info (indicator count + mini bar) ─────────
                    ax.text(0, -0.40,
                            f'{n_ind} indicadores',
                            ha='center', va='center',
                            fontsize=6, color='#64748B',
                            fontfamily='DejaVu Sans')

                    # Mini progress bar
                    bar_y  = -0.62
                    bar_h  = 0.12
                    bar_xL = -0.80
                    bar_w  = 1.60
                    bar_bg = FancyBboxPatch(
                        (bar_xL, bar_y), bar_w, bar_h,
                        boxstyle='round,pad=0,rounding_size=0.05',
                        facecolor='#E2EAF4', edgecolor='none', zorder=4)
                    ax.add_patch(bar_bg)
                    fill_frac = min(pct / 100.0, 1.0)
                    bar_fill = FancyBboxPatch(
                        (bar_xL, bar_y), bar_w * fill_frac, bar_h,
                        boxstyle='round,pad=0,rounding_size=0.05',
                        facecolor=sem_hex, edgecolor='none', zorder=5)
                    ax.add_patch(bar_fill)

                    # Cumplidos / total pill below bar
                    ax.text(0, -0.88,
                            f'{cn} cumplidos  ·  {ep} en progreso  ·  {ac} atención',
                            ha='center', va='center',
                            fontsize=5, color='#94A3B8',
                            fontfamily='DejaVu Sans')

                # ── Hide extra cells ─────────────────────────────────────
                for idx in range(N, n_rows * n_cols):
                    ri = idx // n_cols
                    ci = idx % n_cols
                    axes[ri][ci].axis('off')
                    axes[ri][ci].set_facecolor('#F7F9FC')

                gauge_img = fig_to_image(fig)
                plt.close(fig)

                if gauge_img is not None:
                    # preserveAspectRatio=False: figure already matches PDF area
                    self.c.drawImage(gauge_img, img_x, img_y, img_w, img_h,
                                     preserveAspectRatio=False, mask='auto')
            except Exception:
                pass  # fallback: no gauges drawn

        self._new_page()

    def pagina_linea(self, nombre: str, cumplimiento: float, total_ind: int,
                     objetivos: List[Dict], proyectos: List[Dict],
                     analisis: str, sin_meta: List[Dict] = None):
        """
        Página detallada por línea estratégica.
        Layout:
          - Background + Header A (stats in trapezoid)
          - TABLA: Objetivo | Meta | Indicadores
          - SECCIÓN: Proyectos estratégicos
          - FINAL: Tarjeta de análisis IA (anclada al fondo)
        """
        col_linea = color_linea(nombre)
        nom_d     = nombre_display(nombre)

        # Collect all level-4 indicators for stats
        all_inds = [ind
                    for obj in objetivos
                    for meta in obj.get('metas', [])
                    for ind in meta.get('indicadores', [])]
        n_cumpl_ind = sum(1 for i in all_inds if float(i.get('cumplimiento', 0)) >= 100)

        _page_bg(self.c, self.W, self.H, col_linea)
        # Use extended header height for line pages
        LINE_HDR_H = 28 * mm
        cont_top = _header_linea(
            self.c, self.W, self.H, self.MX,
            nombre, cumplimiento, total_ind,
            col_linea, n_cumpl_ind, self.año
        )
        _footer_std(self.c, self.W, self.H_FOOTER, self.MX,
                    self.año, self._page, nom_d, col_linea)

        # ── Inicio del contenido ──────────────────────────────────────
        AI_BOTTOM = self.H_FOOTER + 3 * mm
        _ai_line_w = self.W - 2 * self.MX - 16 * mm
        _chars_per_line = max(1, int(_ai_line_w / 3.8))
        _ai_lines = max(1, len(analisis or '') // _chars_per_line + 1) if analisis else 0
        AI_H      = max(38 * mm, min(_ai_lines * 8 + int(16 * mm), 70 * mm))
        AI_TOP    = AI_BOTTOM + AI_H
        TABLE_BOTTOM = AI_TOP + 4 * mm
        y_cur = cont_top - 4 * mm

        # ── Cascada: N2 Objetivo → N3 Meta → N4 Indicadores ──────────
        # Estilo: sin bordes rectos, pill-badges para %, fondos diferenciados
        OBJ_H  = 9 * mm   # Nivel 2: Objetivo estratégico
        META_H = 7.5 * mm # Nivel 3: Meta estratégica
        HDR_H  = 6 * mm   # Encabezado global de columnas (UNA VEZ)
        ROW_H  = 6.5 * mm # Fila de indicador (ligeramente más alta para pill)

        # Columnas: Indicador(0) | Meta(1) | Ejecución(2) | Cumplimiento(3) | Estado(4)
        IND_COL_W = [84 * mm, 20 * mm, 20 * mm, 25 * mm, 17 * mm]
        IND_TBL_W = sum(IND_COL_W)   # 166 mm

        # Posiciones X fijas para columnas numéricas (siempre visibles)
        COL1_X = self.MX + IND_COL_W[0]                          # Meta
        COL2_X = COL1_X + IND_COL_W[1]                           # Ejecución
        COL3_X = COL2_X + IND_COL_W[2]                           # Cumplimiento
        COL4_X = COL3_X + IND_COL_W[3]                           # Estado

        # Barra de progreso para objetivo/meta (span col1+col2 = 40mm)
        PROG_X  = COL1_X
        PROG_W  = IND_COL_W[1] + IND_COL_W[2]   # 40 mm
        PROG_H  = 3 * mm                          # altura barra
        CIRC_X  = COL4_X + IND_COL_W[4] / 2      # centro col Estado

        # Pill-badge helper — badge redondeado + texto centrado
        def _pill(cx, cy, txt, bg_col, txt_col, pw=12*mm, ph=4*mm):
            px = cx - pw / 2
            py = cy - ph / 2
            self.c.setFillColor(bg_col)
            self.c.roundRect(px, py, pw, ph, ph / 2, fill=1, stroke=0)
            self.c.setFont('Helvetica-Bold', 6)
            self.c.setFillColor(txt_col)
            self.c.drawCentredString(cx, py + ph / 2 - 2, txt)

        # Barra de progreso helper — track gris + fill color
        def _prog_bar(bx, cy, bw, bh, pct, col):
            by = cy - bh / 2
            self.c.setFillColor(colors.HexColor('#E8ECF0'))
            self.c.roundRect(bx, by, bw, bh, bh / 2, fill=1, stroke=0)
            fill_w = bw * min(pct / 100.0, 1.0)
            if fill_w > 0:
                self.c.setFillColor(col)
                self.c.roundRect(bx, by, fill_w, bh, bh / 2, fill=1, stroke=0)

        if objetivos:
            self.c.setFont('Helvetica-Bold', 9)
            self.c.setFillColor(NAVY_DARK)
            self.c.drawString(self.MX, y_cur, 'OBJETIVOS E INDICADORES')
            y_cur -= 5 * mm

            # ── Encabezado de columnas: fondo claro + texto oscuro ──────────
            if y_cur - HDR_H >= TABLE_BOTTOM:
                hdr_bg      = _light_color(col_linea, 0.88)
                hdr_txt_col = darken(col_linea, 0.45)
                self.c.setFillColor(hdr_bg)
                self.c.roundRect(self.MX, y_cur - HDR_H, IND_TBL_W, HDR_H,
                                 1.5 * mm, fill=1, stroke=0)
                # Línea inferior en color de línea (2px)
                self.c.setFillColor(col_linea)
                self.c.rect(self.MX, y_cur - HDR_H, IND_TBL_W, 2, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 6.5)
                self.c.setFillColor(hdr_txt_col)
                hx = self.MX
                for hdr_lbl, cw in zip(['Indicador / Objetivo / Meta',
                                        'Meta', 'Ejecución',
                                        'Cumplimiento', 'Estado'], IND_COL_W):
                    self.c.drawCentredString(hx + cw / 2, y_cur - HDR_H + 2.2 * mm, hdr_lbl)
                    hx += cw
                y_cur -= HDR_H

            for obj in objetivos:
                if y_cur - (OBJ_H + META_H + ROW_H) < TABLE_BOTTOM:
                    break

                obj_pct = float(obj.get('cumplimiento', 0))
                obj_sem = color_semaforo(obj_pct)
                obj_txt = limpiar(str(obj.get('objetivo', '')))

                # ── Nivel 2: Objetivo (navy background) ──────────────────────
                if y_cur - OBJ_H < TABLE_BOTTOM:
                    break
                cy_obj = y_cur - OBJ_H / 2

                # Navy background for N2 objectives
                self.c.setFillColor(NAVY_DARK)
                self.c.rect(self.MX, y_cur - OBJ_H, IND_TBL_W, OBJ_H, fill=1, stroke=0)
                self.c.setFillColor(col_linea)
                self.c.rect(self.MX, y_cur - 1, IND_TBL_W, 1, fill=1, stroke=0)
                # Acento izquierdo (6px) en color de línea
                self.c.rect(self.MX, y_cur - OBJ_H, 6, OBJ_H, fill=1, stroke=0)

                # Nombre objetivo (col 0, desde 9mm para no solapar acento)
                obj_s = obj_txt[:72] + ('…' if len(obj_txt) > 72 else '')
                self.c.setFont('Helvetica-Bold', 7)
                self.c.setFillColor(colors.white)
                self.c.drawString(self.MX + 9 * mm, cy_obj - 2.5, obj_s)

                # Col 1+2 → barra de progreso centrada verticalmente
                _prog_bar(PROG_X + 2 * mm, cy_obj, PROG_W - 4 * mm, PROG_H, obj_pct, obj_sem)

                # Col 3 → pill badge %
                _pill(COL3_X + IND_COL_W[3] / 2, cy_obj,
                      f'{obj_pct:.0f}%',
                      color_semaforo_bg(obj_pct), obj_sem,
                      pw=14 * mm, ph=5 * mm)

                # Col 4 → círculo estado
                self._status_circle(CIRC_X, cy_obj, 2.5 * mm, obj_pct)

                y_cur -= OBJ_H
                y_cur -= 1  # micro-gap

                for meta in obj.get('metas', []):
                    if y_cur - (META_H + ROW_H) < TABLE_BOTTOM:
                        break

                    meta_txt = limpiar(str(meta.get('meta_pdi', '')))
                    meta_pct = float(meta.get('cumplimiento', 0))
                    meta_sem = color_semaforo(meta_pct)

                    # ── Nivel 3: Meta ─────────────────────────────────────────
                    if y_cur - META_H < TABLE_BOTTOM:
                        break
                    cy_meta = y_cur - META_H / 2

                    # Fondo blanco + separador gris suave
                    self.c.setFillColor(C_WHITE)
                    self.c.rect(self.MX, y_cur - META_H, IND_TBL_W, META_H,
                                fill=1, stroke=0)
                    self.c.setStrokeColor(colors.HexColor('#E0E4EA'))
                    self.c.setLineWidth(0.4)
                    self.c.line(self.MX, y_cur, self.MX + IND_TBL_W, y_cur)
                    # Acento izquierdo delgado (3px, indentado 8px)
                    self.c.setFillColor(col_linea)
                    self.c.rect(self.MX + 8, y_cur - META_H, 3, META_H, fill=1, stroke=0)

                    # Nombre meta (col 0, indentado 16mm)
                    meta_label = (meta_txt[:88] + ('…' if len(meta_txt) > 88 else '')) \
                                 if meta_txt else 'Meta estratégica'
                    self.c.setFont('Helvetica', 6.5)
                    self.c.setFillColor(TEXT_SECONDARY)
                    self.c.drawString(self.MX + 16 * mm, cy_meta - 2.5,
                                      '\u25c6  ' + meta_label)

                    # Col 1+2 → barra de progreso (más pequeña que objetivo)
                    _prog_bar(PROG_X + 2 * mm, cy_meta, PROG_W - 4 * mm,
                              PROG_H - 0.5 * mm, meta_pct, meta_sem)

                    # Col 3 → pill badge %
                    _pill(COL3_X + IND_COL_W[3] / 2, cy_meta,
                          f'{meta_pct:.0f}%',
                          color_semaforo_bg(meta_pct), meta_sem,
                          pw=12 * mm, ph=4 * mm)

                    # Col 4 → círculo estado
                    self._status_circle(CIRC_X, cy_meta, 2 * mm, meta_pct)

                    y_cur -= META_H

                    inds = meta.get('indicadores', [])
                    if not inds:
                        continue

                    # ── Nivel 4: Indicadores ──────────────────────────────────
                    for ridx, ind in enumerate(inds):
                        if y_cur - ROW_H < TABLE_BOTTOM:
                            break
                        ind_pct  = float(ind.get('cumplimiento', 0))
                        ind_scol = color_semaforo(ind_pct)

                        # Fondo alternado muy sutil — sin bordes
                        bg = colors.HexColor('#F5F7FA') if ridx % 2 == 0 else C_WHITE
                        self.c.setFillColor(bg)
                        self.c.rect(self.MX, y_cur - ROW_H, IND_TBL_W, ROW_H,
                                    fill=1, stroke=0)
                        # Separador inferior tenue
                        self.c.setStrokeColor(colors.HexColor('#EAECEF'))
                        self.c.setLineWidth(0.2)
                        self.c.line(self.MX + 3 * mm, y_cur - ROW_H,
                                    self.MX + IND_TBL_W - 3 * mm, y_cur - ROW_H)

                        cy_ind = y_cur - ROW_H / 2

                        # Dot semáforo izquierdo
                        self.c.setFillColor(ind_scol)
                        self.c.circle(self.MX + 5 * mm, cy_ind, 1.5, fill=1, stroke=0)

                        # Nombre indicador (col 0, desde 9mm)
                        ind_name = limpiar(str(ind.get('nombre', '')))
                        ind_name = ind_name[:62] + ('…' if len(ind_name) > 62 else '')
                        self.c.setFont('Helvetica', 6)
                        self.c.setFillColor(C_DARK)
                        self.c.drawString(self.MX + 9 * mm,
                                          cy_ind - 2.5, ind_name)

                        # ── Valores numéricos siempre visibles ──────────────
                        meta_v = ind.get('meta_valor')
                        ejec_v = ind.get('ejecucion')
                        meta_str = (f'{float(meta_v):.1f}'
                                    if (meta_v is not None and
                                        str(meta_v) not in ('nan', 'None', ''))
                                    else '-')
                        ejec_str = (f'{float(ejec_v):.1f}'
                                    if (ejec_v is not None and
                                        str(ejec_v) not in ('nan', 'None', ''))
                                    else '-')

                        # Col 1 → Meta
                        self.c.setFont('Helvetica', 6.5)
                        self.c.setFillColor(TEXT_MUTED)
                        self.c.drawCentredString(COL1_X + IND_COL_W[1] / 2,
                                                 cy_ind - 2.5, meta_str)
                        # Col 2 → Ejecución
                        self.c.setFillColor(C_DARK)
                        self.c.drawCentredString(COL2_X + IND_COL_W[2] / 2,
                                                 cy_ind - 2.5, ejec_str)
                        # Col 3 → barra de progreso redondeada con % centrado
                        bar_x3 = COL3_X + 2 * mm
                        bar_w3 = IND_COL_W[3] - 4 * mm
                        bar_h3 = 3.5 * mm
                        bar_y3 = cy_ind - bar_h3 / 2
                        self.c.setFillColor(colors.HexColor('#E8ECF0'))
                        self.c.roundRect(bar_x3, bar_y3, bar_w3, bar_h3,
                                         bar_h3 / 2, fill=1, stroke=0)
                        fill_w3 = bar_w3 * min(ind_pct / 100.0, 1.0)
                        if fill_w3 > 0:
                            self.c.setFillColor(ind_scol)
                            self.c.roundRect(bar_x3, bar_y3, fill_w3, bar_h3,
                                             bar_h3 / 2, fill=1, stroke=0)
                        self.c.setFont('Helvetica-Bold', 5.5)
                        self.c.setFillColor(C_WHITE)
                        self.c.drawCentredString(bar_x3 + bar_w3 / 2,
                                                 cy_ind - 2, f'{ind_pct:.0f}%')
                        # Col 4 → símbolo estado simple
                        sym = '\u2713' if ind_pct >= 100 else ('\u26a0' if ind_pct >= 80 else '\u2717')
                        self.c.setFont('Helvetica-Bold', 8)
                        self.c.setFillColor(ind_scol)
                        self.c.drawCentredString(CIRC_X, cy_ind - 3, sym)

                        y_cur -= ROW_H

        # ── Proyectos + Stand By ──────────────────────────────────────
        PROW_H   = 6 * mm
        PHDR_H   = 7 * mm
        has_sin_meta  = bool(sin_meta)
        has_proyectos = bool(proyectos)

        if (has_proyectos or has_sin_meta) and y_cur - (PHDR_H + PROW_H + 10 * mm) > TABLE_BOTTOM:
            y_cur -= 5 * mm

            # ── Stand By: lista completa, ancho total ─────────────────
            if has_sin_meta:
                self.c.setFont('Helvetica-Bold', 7.5)
                self.c.setFillColor(NAVY_DARK)
                self.c.drawString(self.MX, y_cur, '\u23f8 Stand By / Sin Resultados')
                y_cur -= 4 * mm
                # Header
                self.c.setFillColor(colors.HexColor('#F0F2F5'))
                self.c.roundRect(self.MX, y_cur - PHDR_H, IND_TBL_W, PHDR_H,
                                 1.5 * mm, fill=1, stroke=0)
                self.c.setFillColor(AMBER_SOLID)
                self.c.rect(self.MX, y_cur - PHDR_H, IND_TBL_W, 2, fill=1, stroke=0)
                self.c.setFont('Helvetica-Bold', 5.5)
                self.c.setFillColor(NAVY_DARK)
                self.c.drawString(self.MX + 2 * mm, y_cur - PHDR_H + 2 * mm,
                                  'Indicador sin resultado')
                y_cur -= PHDR_H
                for sidx, si in enumerate(sin_meta[:10]):
                    if y_cur - PROW_H < TABLE_BOTTOM:
                        break
                    si_bg = AMBER_BG if sidx % 2 == 0 else C_WHITE
                    self.c.setFillColor(si_bg)
                    self.c.rect(self.MX, y_cur - PROW_H, IND_TBL_W, PROW_H,
                                fill=1, stroke=0)
                    self.c.setFillColor(AMBER_SOLID)
                    self.c.rect(self.MX, y_cur - PROW_H, 2, PROW_H, fill=1, stroke=0)
                    si_nm = limpiar(str(si.get('nombre', '')))[:int(IND_TBL_W / 3.5)]
                    self.c.setFont('Helvetica', 5.5)
                    self.c.setFillColor(C_DARK)
                    self.c.drawString(self.MX + 3, y_cur - PROW_H + 1.8 * mm, si_nm)
                    y_cur -= PROW_H
                y_cur -= 3 * mm

            # ── Proyectos: grid 2 por fila, ancho total ───────────────
            if has_proyectos and y_cur - (PHDR_H + PROW_H) > TABLE_BOTTOM:
                self.c.setFont('Helvetica-Bold', 7.5)
                self.c.setFillColor(NAVY_DARK)
                self.c.drawString(self.MX, y_cur, '\u25c6 Proyectos Estratégicos')
                y_cur -= 4 * mm

                PCELL_GAP = 3 * mm
                PCELL_W   = (IND_TBL_W - PCELL_GAP) / 2   # 2 proyectos por fila
                PCT_W     = 14 * mm   # ancho zona % (derecha de cada celda)
                BAR_H     = 3 * mm

                for pidx, proy in enumerate(proyectos[:12]):
                    col_in_row = pidx % 2
                    if col_in_row == 0:
                        # Nueva fila: verificar espacio
                        if y_cur - PROW_H < TABLE_BOTTOM:
                            break
                    p_pct = float(proy.get('cumplimiento', 0))
                    p_col = color_semaforo(p_pct)
                    cell_x = self.MX + col_in_row * (PCELL_W + PCELL_GAP)
                    cell_y = y_cur - PROW_H

                    # Fondo celda alternado
                    cell_bg = C_TABLE_ROW_ALT if (pidx // 2) % 2 == 0 else C_WHITE
                    self.c.setFillColor(cell_bg)
                    self.c.rect(cell_x, cell_y, PCELL_W, PROW_H, fill=1, stroke=0)
                    # Acento izquierdo color semáforo
                    self.c.setFillColor(p_col)
                    self.c.rect(cell_x, cell_y, 3, PROW_H, fill=1, stroke=0)
                    # Borde celda
                    self.c.setStrokeColor(TABLE_BORDER)
                    self.c.setLineWidth(0.3)
                    self.c.rect(cell_x, cell_y, PCELL_W, PROW_H, fill=0, stroke=1)

                    # Nombre proyecto
                    p_nm = limpiar(str(proy.get('nombre', '')))
                    max_pc = int((PCELL_W - PCT_W - 6) / 3.5)
                    p_nm = p_nm[:max_pc] + ('…' if len(p_nm) > max_pc else '')
                    self.c.setFont('Helvetica', 5.5)
                    self.c.setFillColor(C_DARK)
                    self.c.drawString(cell_x + 4, cell_y + 1.8 * mm, p_nm)

                    # Mini barra de progreso
                    mbx = cell_x + PCELL_W - PCT_W - 2 * mm
                    mbw = PCT_W - 12 * mm
                    mby = cell_y + (PROW_H - BAR_H) / 2
                    self.c.setFillColor(TABLE_BORDER)
                    self.c.roundRect(mbx, mby, mbw, BAR_H, 1, fill=1, stroke=0)
                    self.c.setFillColor(p_col)
                    self.c.roundRect(mbx, mby, mbw * min(p_pct / 100, 1.0),
                                     BAR_H, 1, fill=1, stroke=0)

                    # % valor (bold, color semáforo)
                    self.c.setFont('Helvetica-Bold', 6)
                    self.c.setFillColor(p_col)
                    self.c.drawRightString(cell_x + PCELL_W - 2 * mm,
                                           cell_y + 1.8 * mm, f'{p_pct:.0f}%')

                    # Avanzar fila al completar par
                    if col_in_row == 1:
                        y_cur -= PROW_H

        # ── Tarjeta de análisis IA (anclada al fondo) ──────────────────
        if analisis:
            _ai_block(
                self.c, self.MX, AI_BOTTOM,
                self.W - 2 * self.MX, AI_H,
                analisis
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

        ACC = colors.HexColor('#1e88e5')

        def _draw_page_header():
            _page_bg(self.c, self.W, self.H, ACC)
            cont = _std_header(
                self.c, self.W, self.H, self.H_HEADER, self.MX,
                'DETALLE DE INDICADORES',
                f'Total: {len(df_indicadores)} indicadores',
                ACC
            )
            _footer_std(self.c, self.W, self.H_FOOTER, self.MX,
                        self.año, self._page, 'Detalle de Indicadores', ACC)
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
        ACC = colors.HexColor('#1e88e5')
        _page_bg(self.c, self.W, self.H, ACC)
        cont_top = _std_header(
            self.c, self.W, self.H, self.H_HEADER, self.MX,
            'CONCLUSIONES Y RECOMENDACIONES', '', ACC
        )
        _footer_std(self.c, self.W, self.H_FOOTER, self.MX,
                    self.año, self._page, 'Conclusiones', ACC)

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
