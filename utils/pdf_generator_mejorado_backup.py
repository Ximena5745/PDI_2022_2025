"""
Generador Mejorado de Informes PDF - Dashboard Estratégico POLI
===============================================================
Versión mejorada con visualizaciones profesionales, barras de progreso,
tarjetas redondeadas, heatmaps y análisis IA por línea.

Características:
- Mantiene portada original (Portada.png)
- Resumen ejecutivo visual con tarjetas y heatmap
- Páginas dedicadas por línea estratégica con colores distintivos
- Tablas de indicadores agrupadas y mejoradas
- Glosario de siglas y página de conclusiones
- Corrección de tildes y lenguaje profesional
"""

import os
import io
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from fpdf import FPDF


# ============================================================================
# CONSTANTES DE COLORES - Paleta Institucional POLI
# ============================================================================

COLORES_INSTITUCIONALES = {
    # Colores primarios institucionales
    'primary': '#0a2240',       # Azul marino POLI
    'accent': '#1e88e5',        # Azul claro

    # Colores de estado (semáforo)
    'cumple': '#2e7d32',        # Verde
    'en_progreso': '#f57f17',   # Ámbar
    'atencion': '#c62828',      # Rojo

    # Colores auxiliares
    'fondo_tarjetas': '#f5f7fa',
    'white': '#ffffff',
    'dark': '#212529',
    'gray': '#6c757d',
    'light_gray': '#e0e0e0',
}

# Colores específicos por Línea Estratégica (manteniendo los originales)
COLORES_LINEAS = {
    "Expansión": "#FBAF17",
    "Transformación Organizacional": "#42F2F2",
    "Calidad": "#EC0677",
    "Experiencia": "#1FB2DE",
    "Sostenibilidad": "#A6CE38",
    "Educación para toda la vida": "#0F385A",
}

# Glosario de siglas del PDI
GLOSARIO_SIGLAS = {
    'PDI': 'Plan de Desarrollo Institucional',
    'KPI': 'Key Performance Indicator (Indicador Clave de Desempeño)',
    'B2B': 'Business to Business (Negocio a Negocio)',
    'B2G': 'Business to Government (Negocio a Gobierno)',
    'SSI': 'Sistema de Soporte Institucional',
    'NPS': 'Net Promoter Score (Índice de Satisfacción)',
    'EBITDA': 'Earnings Before Interest, Taxes, Depreciation and Amortization',
    'ANS': 'Acuerdo de Nivel de Servicio',
    'IA': 'Inteligencia Artificial',
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def hex_to_rgb(hex_color: str) -> tuple:
    """Convierte color hexadecimal #RRGGBB a tupla RGB (R, G, B)."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def limpiar_texto_pdf(texto: str) -> str:
    """
    Limpia texto para evitar problemas con caracteres especiales en PDF.
    Mantiene tildes y eñes (NO las elimina).
    """
    if texto is None:
        return ""

    texto = str(texto)

    # Mapeo solo para emojis y símbolos especiales (NO tildes)
    reemplazos = {
        '⚠️': '⚠', '✅': '✓', '❌': '✗',
        '📊': '', '📈': '', '📉': '', '🎯': '',
        '●': '•', '→': '→', '≥': '>=', '≤': '<=',
        '"': '"', '"': '"', ''': "'", ''': "'",
        '…': '...',
    }

    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    return texto


def obtener_color_linea(nombre_linea: str) -> tuple:
    """Retorna el color RGB de una línea estratégica."""
    # Normalizar nombre
    nombre = nombre_linea.strip().title()

    # Mapeos alternativos
    mapeos = {
        'Transformacion Organizacional': 'Transformación Organizacional',
        'Educacion Para Toda La Vida': 'Educación para toda la vida',
    }

    nombre = mapeos.get(nombre, nombre)

    if nombre in COLORES_LINEAS:
        return hex_to_rgb(COLORES_LINEAS[nombre])

    # Color por defecto si no se encuentra
    return hex_to_rgb(COLORES_INSTITUCIONALES['primary'])


def obtener_color_estado(cumplimiento: float) -> tuple:
    """Retorna el color RGB según el nivel de cumplimiento."""
    if pd.isna(cumplimiento):
        return hex_to_rgb(COLORES_INSTITUCIONALES['gray'])
    elif cumplimiento >= 100:
        return hex_to_rgb(COLORES_INSTITUCIONALES['cumple'])
    elif cumplimiento >= 80:
        return hex_to_rgb(COLORES_INSTITUCIONALES['en_progreso'])
    else:
        return hex_to_rgb(COLORES_INSTITUCIONALES['atencion'])


def obtener_icono_estado(cumplimiento: float) -> str:
    """Retorna el ícono Unicode según el nivel de cumplimiento."""
    if pd.isna(cumplimiento):
        return '○'  # Círculo vacío
    elif cumplimiento >= 100:
        return '✓'  # Check verde
    elif cumplimiento >= 80:
        return '⚠'  # Advertencia ámbar
    else:
        return '✗'  # X roja


# ============================================================================
# CLASE PDF PERSONALIZADA
# ============================================================================

class PDFInformePOLI(FPDF):
    """Clase personalizada para generar PDF del informe estratégico POLI."""

    def __init__(self, año: int = 2025):
        super().__init__()
        self.año = año
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        """Encabezado de páginas (excepto portada)."""
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(108, 117, 125)  # Gray
            self.cell(0, 10, 'Informe Estratégico POLI - Plan de Desarrollo Institucional', 0, 0, 'C')
            self.ln(8)

    def footer(self):
        """Pie de página con número de página."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(108, 117, 125)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def rounded_rect(self, x, y, w, h, r, style=''):
        """
        Dibuja un rectángulo con esquinas redondeadas.
        Compatible con fpdf2 (polyfill para versiones antiguas).
        """
        try:
            # fpdf2 2.7+
            super().rounded_rect(x, y, w, h, r, style=style or 'D')
        except (AttributeError, TypeError):
            # Fallback: rectángulo normal si no soporta rounded_rect
            self.rect(x, y, w, h, style if style else 'D')

    def dibujar_barra_progreso(self, x, y, w, h, porcentaje, mostrar_texto=True):
        """
        Dibuja una barra de progreso horizontal.

        Args:
            x, y: Posición
            w, h: Ancho y alto de la barra
            porcentaje: Valor de 0 a 100+
            mostrar_texto: Si debe mostrar el porcentaje en el centro
        """
        # Fondo de la barra (gris claro)
        self.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['light_gray']))
        self.rounded_rect(x, y, w, h, h/1.5, 'F')

        # Calcular ancho de la barra de progreso
        progreso_w = min((porcentaje / 100) * w, w)

        # Color según el cumplimiento
        color = obtener_color_estado(porcentaje)
        self.set_fill_color(*color)

        if progreso_w > 0:
            self.rounded_rect(x, y, progreso_w, h, h/1.5, 'F')

        # Mostrar porcentaje en el centro (opcional)
        if mostrar_texto and porcentaje > 0:
            self.set_xy(x, y)
            self.set_font('Helvetica', 'B', 7)
            self.set_text_color(255, 255, 255)
            self.cell(w, h, f'{porcentaje:.1f}%', 0, 0, 'C')


# ============================================================================
# PÁGINA 1: PORTADA (Mantener original)
# ============================================================================

def generar_portada(pdf: PDFInformePOLI, año: int):
    """
    Genera la portada del informe usando la imagen Portada.png existente.
    Si no existe la imagen, genera una portada de respaldo.
    """
    portada_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Portada.png'
    )

    if os.path.exists(portada_path):
        # Usar imagen de portada existente
        pdf.image(portada_path, x=0, y=0, w=210, h=297)
    else:
        # Fallback: portada azul corporativa
        pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
        pdf.rect(0, 0, 210, 297, 'F')

        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 28)
        pdf.set_y(120)
        pdf.cell(0, 15, 'INFORME ESTRATÉGICO', 0, 1, 'C')

        pdf.set_font('Helvetica', '', 16)
        pdf.cell(0, 10, 'Plan de Desarrollo Institucional', 0, 1, 'C')

        pdf.set_font('Helvetica', 'B', 14)
        pdf.ln(10)
        pdf.cell(0, 10, f'Período 2021-{año}', 0, 1, 'C')


# ============================================================================
# PÁGINA 2: RESUMEN EJECUTIVO VISUAL MEJORADO
# ============================================================================

def generar_resumen_ejecutivo(pdf: PDFInformePOLI, metricas: Dict[str, Any],
                               df_lineas: pd.DataFrame, analisis_texto: str = ""):
    """
    Genera el resumen ejecutivo con tarjetas, barra de progreso global y heatmap.
    """
    pdf.add_page()

    # Extraer métricas
    cumplimiento_global = metricas.get('cumplimiento_promedio', 0)
    total_ind = metricas.get('total_indicadores', 0)
    cumplidos = metricas.get('indicadores_cumplidos', 0)
    en_progreso = metricas.get('en_progreso', 0)
    no_cumplidos = metricas.get('no_cumplidos', 0)

    # ─── TÍTULO ──────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
    pdf.cell(0, 10, 'Resumen Ejecutivo', 0, 1, 'L')
    pdf.ln(2)

    # ─── TARJETAS DE KPIs ────────────────────────────
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['accent']))
    pdf.cell(0, 6, 'INDICADORES CLAVE DE DESEMPEÑO', 0, 1, 'L')
    pdf.ln(3)

    # Tarjeta grande: Cumplimiento Global
    card_y = pdf.get_y()
    card_w = 60
    card_h = 50

    # Sombra
    pdf.set_fill_color(180, 180, 180)
    pdf.rounded_rect(13, card_y + 3, card_w, card_h, 8, 'F')

    # Tarjeta principal
    color_card = obtener_color_estado(cumplimiento_global)
    pdf.set_fill_color(*color_card)
    pdf.rounded_rect(10, card_y, card_w, card_h, 8, 'F')

    # Texto en tarjeta
    pdf.set_xy(10, card_y + 8)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(card_w, 5, 'CUMPLIMIENTO GLOBAL', 0, 0, 'C')

    pdf.set_xy(10, card_y + 18)
    pdf.set_font('Helvetica', 'B', 32)
    pdf.cell(card_w, 12, f'{cumplimiento_global:.1f}%', 0, 0, 'C')

    pdf.set_xy(10, card_y + 35)
    pdf.set_font('Helvetica', '', 7)
    icono = obtener_icono_estado(cumplimiento_global)
    estado = 'META CUMPLIDA' if cumplimiento_global >= 100 else 'EN PROGRESO' if cumplimiento_global >= 80 else 'REQUIERE ATENCIÓN'
    pdf.cell(card_w, 5, f'{icono} {estado}', 0, 0, 'C')

    # Tarjetas pequeñas (3 columnas)
    tarjetas_pequeñas = [
        ('CUMPLIDOS', cumplidos, 'cumple', '✓'),
        ('EN PROGRESO', en_progreso, 'en_progreso', '⚠'),
        ('NO CUMPLIDOS', no_cumplidos, 'atencion', '✗'),
    ]

    card_small_w = 38
    card_small_h = 24
    start_x = 75

    for i, (titulo, valor, tipo_color, icono) in enumerate(tarjetas_pequeñas):
        cx = start_x + (i * (card_small_w + 4))
        cy = card_y + (i // 3) * (card_small_h + 3)

        # Sombra
        pdf.set_fill_color(190, 190, 190)
        pdf.rounded_rect(cx + 2, cy + 2, card_small_w, card_small_h, 6, 'F')

        # Tarjeta
        pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['fondo_tarjetas']))
        pdf.rounded_rect(cx, cy, card_small_w, card_small_h, 6, 'F')

        # Borde de color
        color_borde = hex_to_rgb(COLORES_INSTITUCIONALES[tipo_color])
        pdf.set_draw_color(*color_borde)
        pdf.set_line_width(0.8)
        pdf.rounded_rect(cx, cy, card_small_w, card_small_h, 6, 'D')
        pdf.set_line_width(0.2)

        # Valor
        pdf.set_xy(cx, cy + 5)
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(*color_borde)
        pdf.cell(card_small_w, 8, str(valor), 0, 0, 'C')

        # Etiqueta
        pdf.set_xy(cx, cy + 15)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))
        pdf.cell(card_small_w, 4, titulo, 0, 0, 'C')

    # Tarjeta "Total"
    cx = start_x + (3 % 3) * (card_small_w + 4)
    cy = card_y + card_small_h + 3

    pdf.set_fill_color(190, 190, 190)
    pdf.rounded_rect(cx + 2, cy + 2, card_small_w, card_small_h, 6, 'F')

    pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['fondo_tarjetas']))
    pdf.rounded_rect(cx, cy, card_small_w, card_small_h, 6, 'F')

    pdf.set_xy(cx, cy + 5)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
    pdf.cell(card_small_w, 8, str(total_ind), 0, 0, 'C')

    pdf.set_xy(cx, cy + 15)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))
    pdf.cell(card_small_w, 4, 'TOTAL', 0, 0, 'C')

    pdf.ln(card_h + 8)

    # ─── BARRA DE PROGRESO GLOBAL ────────────────────
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['accent']))
    pdf.cell(0, 6, 'PROGRESO GLOBAL DEL PDI', 0, 1, 'L')
    pdf.ln(2)

    bar_y = pdf.get_y()
    pdf.dibujar_barra_progreso(10, bar_y, 190, 10, cumplimiento_global, mostrar_texto=True)

    pdf.ln(15)

    # ─── HEATMAP: TABLA DE CALOR POR LÍNEAS ──────────
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['accent']))
    pdf.cell(0, 6, 'CUMPLIMIENTO POR LÍNEA ESTRATÉGICA', 0, 1, 'L')
    pdf.ln(3)

    if df_lineas is not None and not df_lineas.empty:
        # Encabezado de tabla
        pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 8)

        pdf.cell(90, 8, 'Línea Estratégica', 1, 0, 'L', True)
        pdf.cell(35, 8, 'Cumplimiento', 1, 0, 'C', True)
        pdf.cell(65, 8, 'Progreso Visual', 1, 1, 'C', True)

        # Filas de datos
        pdf.set_font('Helvetica', '', 8)
        for idx, row in df_lineas.iterrows():
            linea = row.get('Linea', 'N/D')
            cumpl = row.get('Cumplimiento', 0)

            # Color de fondo alternado
            if idx % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(245, 247, 250)

            # Nombre de la línea con color
            color_linea = obtener_color_linea(linea)
            pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))

            # Círculo de color de línea
            cell_y = pdf.get_y()
            pdf.set_fill_color(*color_linea)
            pdf.circle(13, cell_y + 4, 1.5, 'F')

            pdf.set_x(16)
            pdf.cell(87, 8, limpiar_texto_pdf(linea[:50]), 1, 0, 'L', True)

            # Cumplimiento con ícono
            color_estado = obtener_color_estado(cumpl)
            pdf.set_text_color(*color_estado)
            pdf.set_font('Helvetica', 'B', 8)
            icono = obtener_icono_estado(cumpl)
            pdf.cell(35, 8, f'{icono} {cumpl:.1f}%', 1, 0, 'C', True)

            # Barra de progreso mini
            bar_x = pdf.get_x() + 2
            bar_y = pdf.get_y() + 2
            pdf.cell(65, 8, '', 1, 1, 'C', True)  # Celda vacía

            # Dibujar barra dentro de la celda
            pdf.dibujar_barra_progreso(bar_x, bar_y, 61, 4, cumpl, mostrar_texto=False)

    pdf.ln(5)

    # ─── ANÁLISIS EJECUTIVO IA ───────────────────────
    if analisis_texto:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['accent']))
        pdf.cell(0, 6, 'ANÁLISIS EJECUTIVO', 0, 1, 'L')
        pdf.ln(2)

        # Caja de análisis
        analisis_y = pdf.get_y()
        analisis_h = 40

        pdf.set_fill_color(*hex_to_rgb('#e3f2fd'))  # Azul muy claro
        pdf.rounded_rect(10, analisis_y, 190, analisis_h, 8, 'F')

        # Barra lateral azul
        pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['accent']))
        pdf.rect(10, analisis_y, 3, analisis_h, 'F')

        # Texto del análisis
        pdf.set_xy(16, analisis_y + 5)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))

        texto_limpio = limpiar_texto_pdf(analisis_texto.replace('**', '').replace('*', ''))
        pdf.multi_cell(181, 4, texto_limpio[:600], 0, 'J')

    # ─── LEYENDA DEL SEMÁFORO ─────────────────────────
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['gray']))

    leyenda_y = pdf.get_y()

    # Verde
    pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['cumple']))
    pdf.circle(12, leyenda_y + 2, 1.5, 'F')
    pdf.set_xy(15, leyenda_y)
    pdf.cell(40, 5, '✓ >= 100% Meta Cumplida', 0, 0, 'L')

    # Ámbar
    pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['en_progreso']))
    pdf.circle(57, leyenda_y + 2, 1.5, 'F')
    pdf.set_xy(60, leyenda_y)
    pdf.cell(40, 5, '⚠ 80-99% En Progreso', 0, 0, 'L')

    # Rojo
    pdf.set_fill_color(*hex_to_rgb(COLORES_INSTITUCIONALES['atencion']))
    pdf.circle(102, leyenda_y + 2, 1.5, 'F')
    pdf.set_xy(105, leyenda_y)
    pdf.cell(40, 5, '✗ < 80% Requiere Atención', 0, 0, 'L')


# ============================================================================
# PÁGINA 3+: DETALLE POR LÍNEA ESTRATÉGICA
# ============================================================================

def generar_paginas_lineas(pdf: PDFInformePOLI, df_cascada: pd.DataFrame,
                            analisis_lineas: Dict[str, str] = None):
    """
    Genera una página dedicada por cada línea estratégica con:
    - Color distintivo de la línea
    - Barra de progreso grande de la línea
    - Lista de indicadores con mini barras de progreso
    - Bloque de análisis IA por línea
    """
    if df_cascada is None or df_cascada.empty:
        return

    # Agrupar por línea
    lineas = df_cascada[df_cascada['Nivel'] == 1]['Linea'].unique()

    for linea_nombre in lineas:
        pdf.add_page()

        # Obtener datos de la línea
        linea_data = df_cascada[df_cascada['Linea'] == linea_nombre]
        cumpl_linea = linea_data[linea_data['Nivel'] == 1]['Cumplimiento'].iloc[0]

        color_linea = obtener_color_linea(linea_nombre)
        color_linea_hex = COLORES_LINEAS.get(linea_nombre, COLORES_INSTITUCIONALES['primary'])

        # ─── ENCABEZADO DE LÍNEA ──────────────────────
        pdf.set_fill_color(*color_linea)
        pdf.rect(0, pdf.get_y(), 210, 25, 'F')

        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.ln(5)
        pdf.cell(0, 8, limpiar_texto_pdf(linea_nombre), 0, 1, 'C')

        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, f'Cumplimiento: {cumpl_linea:.1f}%', 0, 1, 'C')

        pdf.ln(3)

        # ─── BARRA DE PROGRESO GRANDE ─────────────────
        bar_y = pdf.get_y()
        pdf.dibujar_barra_progreso(20, bar_y, 170, 12, cumpl_linea, mostrar_texto=True)

        pdf.ln(18)

        # ─── INDICADORES DE LA LÍNEA ──────────────────
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*color_linea)
        pdf.cell(0, 8, 'Indicadores', 0, 1, 'L')
        pdf.ln(2)

        # Filtrar indicadores (nivel 4)
        indicadores = linea_data[linea_data['Nivel'] == 4]

        if not indicadores.empty:
            # Encabezado de tabla
            pdf.set_fill_color(*color_linea)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 8)

            pdf.cell(110, 7, 'Indicador', 1, 0, 'L', True)
            pdf.cell(30, 7, 'Cumplimiento', 1, 0, 'C', True)
            pdf.cell(50, 7, 'Progreso', 1, 1, 'C', True)

            # Filas
            pdf.set_font('Helvetica', '', 7)
            for idx, (_, row) in enumerate(indicadores.iterrows()):
                indicador_nombre = row.get('Indicador', 'N/D')
                cumpl_ind = row.get('Cumplimiento', 0)

                # Fondo alternado
                if idx % 2 == 0:
                    pdf.set_fill_color(255, 255, 255)
                else:
                    pdf.set_fill_color(245, 247, 250)

                # Nombre
                pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))
                pdf.cell(110, 6, limpiar_texto_pdf(indicador_nombre[:65]), 1, 0, 'L', True)

                # Cumplimiento con ícono
                color_estado = obtener_color_estado(cumpl_ind)
                pdf.set_text_color(*color_estado)
                pdf.set_font('Helvetica', 'B', 7)
                icono = obtener_icono_estado(cumpl_ind)
                pdf.cell(30, 6, f'{icono} {cumpl_ind:.1f}%', 1, 0, 'C', True)

                # Barra de progreso
                bar_x = pdf.get_x() + 2
                bar_y = pdf.get_y() + 1.5
                pdf.cell(50, 6, '', 1, 1, 'C', True)

                pdf.dibujar_barra_progreso(bar_x, bar_y, 46, 3, cumpl_ind, mostrar_texto=False)

                pdf.set_font('Helvetica', '', 7)

        pdf.ln(8)

        # ─── ANÁLISIS IA POR LÍNEA ────────────────────
        if analisis_lineas and linea_nombre in analisis_lineas:
            analisis_txt = analisis_lineas[linea_nombre]

            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(*color_linea)
            pdf.cell(0, 8, 'Análisis Estratégico', 0, 1, 'L')
            pdf.ln(2)

            # Caja de análisis
            analisis_y = pdf.get_y()
            analisis_h = 45

            # Fondo claro
            pdf.set_fill_color(245, 247, 250)
            pdf.rounded_rect(10, analisis_y, 190, analisis_h, 8, 'F')

            # Barra lateral con color de línea
            pdf.set_fill_color(*color_linea)
            pdf.rect(10, analisis_y, 4, analisis_h, 'F')

            # Texto
            pdf.set_xy(18, analisis_y + 5)
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))

            texto_limpio = limpiar_texto_pdf(analisis_txt.replace('**', '').replace('*', ''))
            pdf.multi_cell(179, 4, texto_limpio[:700], 0, 'J')


# ============================================================================
# TABLA DE DETALLE DE INDICADORES MEJORADA
# ============================================================================

def generar_tabla_indicadores_mejorada(pdf: PDFInformePOLI, df_indicadores: pd.DataFrame):
    """
    Genera tabla de indicadores mejorada con:
    - Agrupación por línea estratégica
    - Separación de KPIs cuantitativos vs hitos (100%/0%)
    - Sección para N/D
    - Ordenamiento por estado
    - Mini barras de progreso
    """
    if df_indicadores is None or df_indicadores.empty:
        return

    pdf.add_page()

    # Título
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
    pdf.cell(0, 10, 'Detalle de Indicadores', 0, 1, 'L')
    pdf.ln(5)

    # Agrupar por línea
    if 'Linea' not in df_indicadores.columns:
        df_indicadores['Linea'] = 'Sin clasificar'

    lineas = df_indicadores['Linea'].dropna().unique()

    for linea in sorted(lineas):
        df_linea = df_indicadores[df_indicadores['Linea'] == linea].copy()

        if df_linea.empty:
            continue

        # Encabezado de línea
        color_linea = obtener_color_linea(linea)

        pdf.set_fill_color(*color_linea)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 8, limpiar_texto_pdf(linea), 0, 1, 'L', True)
        pdf.ln(2)

        # Clasificar indicadores
        df_linea['Es_Hito'] = df_linea['Cumplimiento'].apply(
            lambda x: x in [0, 100] if pd.notna(x) else False
        )

        df_kpis = df_linea[~df_linea['Es_Hito'] & df_linea['Cumplimiento'].notna()]
        df_hitos = df_linea[df_linea['Es_Hito']]
        df_nd = df_linea[df_linea['Cumplimiento'].isna()]

        # Ordenar por estado (primero atención, luego progreso, luego cumplidos)
        def orden_estado(cumpl):
            if pd.isna(cumpl):
                return 3
            elif cumpl < 80:
                return 0  # Atención primero
            elif cumpl < 100:
                return 1  # En progreso
            else:
                return 2  # Cumplidos al final

        df_kpis['Orden'] = df_kpis['Cumplimiento'].apply(orden_estado)
        df_kpis = df_kpis.sort_values('Orden')

        # KPIs Cuantitativos
        if not df_kpis.empty:
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))
            pdf.cell(0, 6, 'KPIs Cuantitativos', 0, 1, 'L')

            _dibujar_tabla_indicadores(pdf, df_kpis, color_linea)
            pdf.ln(3)

        # Hitos de Proyecto
        if not df_hitos.empty:
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))
            pdf.cell(0, 6, 'Hitos de Proyecto (100% / 0%)', 0, 1, 'L')

            _dibujar_tabla_indicadores(pdf, df_hitos, color_linea)
            pdf.ln(3)

        # Sin Meta Definida (N/D)
        if not df_nd.empty:
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['gray']))
            pdf.cell(0, 6, 'Sin Meta Definida (N/D)', 0, 1, 'L')

            _dibujar_tabla_indicadores(pdf, df_nd, color_linea, mostrar_nd=True)
            pdf.ln(3)

        pdf.ln(5)


def _dibujar_tabla_indicadores(pdf: PDFInformePOLI, df: pd.DataFrame, color_linea: tuple,
                                 mostrar_nd: bool = False):
    """Función auxiliar para dibujar una tabla de indicadores."""
    # Encabezado
    pdf.set_fill_color(*color_linea)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 7)

    pdf.cell(75, 6, 'Indicador', 1, 0, 'L', True)
    pdf.cell(20, 6, 'Meta', 1, 0, 'C', True)
    pdf.cell(20, 6, 'Ejecución', 1, 0, 'C', True)
    pdf.cell(25, 6, 'Cumplimiento', 1, 0, 'C', True)
    pdf.cell(50, 6, 'Progreso', 1, 1, 'C', True)

    # Filas
    pdf.set_font('Helvetica', '', 7)
    for idx, (_, row) in enumerate(df.head(50).iterrows()):
        indicador = limpiar_texto_pdf(str(row.get('Indicador', 'N/D'))[:50])
        meta = row.get('Meta', 'N/D')
        ejec = row.get('Ejecución', row.get('Ejecucion', 'N/D'))
        cumpl = row.get('Cumplimiento', None)

        # Formatear valores
        meta_str = f"{meta:.1f}" if isinstance(meta, (int, float)) and pd.notna(meta) else 'N/D'
        ejec_str = f"{ejec:.1f}" if isinstance(ejec, (int, float)) and pd.notna(ejec) else 'N/D'

        # Fondo alternado
        if idx % 2 == 0:
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_fill_color(248, 250, 252)

        # Nombre
        pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))
        pdf.cell(75, 5, indicador, 1, 0, 'L', True)

        # Meta y Ejecución
        pdf.cell(20, 5, meta_str, 1, 0, 'C', True)
        pdf.cell(20, 5, ejec_str, 1, 0, 'C', True)

        # Cumplimiento
        if pd.notna(cumpl):
            color_estado = obtener_color_estado(cumpl)
            pdf.set_text_color(*color_estado)
            pdf.set_font('Helvetica', 'B', 7)
            icono = obtener_icono_estado(cumpl)
            cumpl_str = f'{icono} {cumpl:.1f}%'
        else:
            pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['gray']))
            cumpl_str = 'N/D'
            cumpl = 0

        pdf.cell(25, 5, cumpl_str, 1, 0, 'C', True)

        # Barra de progreso
        bar_x = pdf.get_x() + 2
        bar_y = pdf.get_y() + 1
        pdf.cell(50, 5, '', 1, 1, 'C', True)

        if not mostrar_nd and pd.notna(cumpl):
            pdf.dibujar_barra_progreso(bar_x, bar_y, 46, 3, cumpl, mostrar_texto=False)

        pdf.set_font('Helvetica', '', 7)


# ============================================================================
# PÁGINA FINAL: CONCLUSIONES Y GLOSARIO
# ============================================================================

def generar_conclusiones(pdf: PDFInformePOLI, metricas: Dict[str, Any],
                          df_lineas: pd.DataFrame):
    """
    Genera página de conclusiones ejecutivas con:
    - 3 mejores logros
    - 2 aspectos críticos
    - Glosario de siglas
    """
    pdf.add_page()

    # ─── CONCLUSIONES EJECUTIVAS ──────────────────────
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
    pdf.cell(0, 10, 'Conclusiones Ejecutivas', 0, 1, 'L')
    pdf.ln(5)

    # ─── MEJORES LOGROS ───────────────────────────────
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['cumple']))
    pdf.cell(0, 8, '✓ Mejores Logros del Período', 0, 1, 'L')
    pdf.ln(2)

    # Identificar top 3 líneas
    if df_lineas is not None and not df_lineas.empty:
        top_lineas = df_lineas.nlargest(3, 'Cumplimiento')

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))

        for i, (_, row) in enumerate(top_lineas.iterrows(), 1):
            linea = row.get('Linea', 'N/D')
            cumpl = row.get('Cumplimiento', 0)

            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(10, 6, f'{i}.', 0, 0, 'L')
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(180, 6,
                f'{limpiar_texto_pdf(linea)}: {cumpl:.1f}% de cumplimiento, '
                f'superando la meta establecida para el período.', 0, 'L')
            pdf.ln(1)

    pdf.ln(3)

    # ─── ASPECTOS CRÍTICOS ────────────────────────────
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['atencion']))
    pdf.cell(0, 8, '⚠ Aspectos Críticos para el Próximo Ciclo', 0, 1, 'L')
    pdf.ln(2)

    # Identificar 2 líneas con menor cumplimiento
    if df_lineas is not None and not df_lineas.empty:
        bottom_lineas = df_lineas.nsmallest(2, 'Cumplimiento')

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))

        for i, (_, row) in enumerate(bottom_lineas.iterrows(), 1):
            linea = row.get('Linea', 'N/D')
            cumpl = row.get('Cumplimiento', 0)

            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(10, 6, f'{i}.', 0, 0, 'L')
            pdf.set_font('Helvetica', '', 9)

            if cumpl < 100:
                pdf.multi_cell(180, 6,
                    f'{limpiar_texto_pdf(linea)}: {cumpl:.1f}% de cumplimiento, '
                    f'requiere atención prioritaria y plan de acción correctivo.', 0, 'L')
            else:
                pdf.multi_cell(180, 6,
                    f'{limpiar_texto_pdf(linea)}: {cumpl:.1f}% de cumplimiento, '
                    f'mantener el monitoreo para asegurar sostenibilidad.', 0, 'L')
            pdf.ln(1)

    pdf.ln(8)

    # ─── GLOSARIO DE SIGLAS ───────────────────────────
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['primary']))
    pdf.cell(0, 8, 'Glosario de Siglas', 0, 1, 'L')
    pdf.ln(3)

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['dark']))

    # Dividir en dos columnas
    mitad = len(GLOSARIO_SIGLAS) // 2
    siglas_lista = list(GLOSARIO_SIGLAS.items())

    col1 = siglas_lista[:mitad]
    col2 = siglas_lista[mitad:]

    y_inicial = pdf.get_y()

    # Columna 1
    for sigla, definicion in col1:
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(10, 5, f'{sigla}:', 0, 0, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.multi_cell(85, 5, limpiar_texto_pdf(definicion), 0, 'L')

    # Columna 2
    pdf.set_xy(105, y_inicial)
    for sigla, definicion in col2:
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(10, 5, f'{sigla}:', 0, 0, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.multi_cell(85, 5, limpiar_texto_pdf(definicion), 0, 'L')

    # Pie de página final
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(*hex_to_rgb(COLORES_INSTITUCIONALES['gray']))
    pdf.cell(0, 5, '─' * 80, 0, 1, 'C')
    pdf.cell(0, 5, 'Generado automáticamente por el Sistema de Monitoreo PDI', 0, 1, 'C')
    pdf.cell(0, 5, 'Politécnico Grancolombiano - Institución Universitaria', 0, 1, 'C')


# ============================================================================
# FUNCIÓN PRINCIPAL DE EXPORTACIÓN
# ============================================================================

def exportar_informe_pdf_mejorado(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    año: int = 2025,
    df_cascada: pd.DataFrame = None,
    analisis_lineas: Dict[str, str] = None
) -> bytes:
    """
    Función principal para generar el PDF mejorado del informe estratégico.

    Args:
        metricas: Diccionario con métricas generales (cumplimiento, totales, etc.)
        df_lineas: DataFrame con cumplimiento por línea estratégica
        df_indicadores: DataFrame con detalle de todos los indicadores
        analisis_texto: Texto de análisis ejecutivo general (IA)
        año: Año del informe (default: 2025)
        df_cascada: DataFrame con estructura jerárquica (línea > objetivo > meta > indicador)
        analisis_lineas: Diccionario {nombre_linea: texto_analisis_ia}

    Returns:
        bytes: Contenido del PDF generado

    Ejemplo de uso:
        >>> metricas = {
        ...     'cumplimiento_promedio': 104.0,
        ...     'total_indicadores': 34,
        ...     'indicadores_cumplidos': 27,
        ...     'en_progreso': 7,
        ...     'no_cumplidos': 0
        ... }
        >>> pdf_bytes = exportar_informe_pdf_mejorado(metricas, df_lineas, df_indicadores)
        >>> with open('Informe_Estrategico_POLI_2025.pdf', 'wb') as f:
        ...     f.write(pdf_bytes)
    """
    # Crear instancia del PDF
    pdf = PDFInformePOLI(año=año)

    # 1. PORTADA (mantener original)
    generar_portada(pdf, año)

    # 2. RESUMEN EJECUTIVO VISUAL
    generar_resumen_ejecutivo(pdf, metricas, df_lineas, analisis_texto)

    # 3. PÁGINAS POR LÍNEA ESTRATÉGICA
    if df_cascada is not None and not df_cascada.empty:
        generar_paginas_lineas(pdf, df_cascada, analisis_lineas)

    # 4. TABLA DE INDICADORES MEJORADA
    if df_indicadores is not None and not df_indicadores.empty:
        generar_tabla_indicadores_mejorada(pdf, df_indicadores)

    # 5. CONCLUSIONES Y GLOSARIO
    generar_conclusiones(pdf, metricas, df_lineas)

    # Retornar PDF como bytes
    return bytes(pdf.output())


# ============================================================================
# DATOS DE EJEMPLO PARA TESTING
# ============================================================================

def generar_datos_ejemplo():
    """
    Genera datos de ejemplo para probar el generador de PDF.
    Simula la estructura real del PDI del Politécnico Grancolombiano.
    """
    # Métricas globales
    metricas = {
        'cumplimiento_promedio': 104.0,
        'total_indicadores': 34,
        'indicadores_cumplidos': 27,
        'en_progreso': 7,
        'no_cumplidos': 0,
        'año_actual': 2025
    }

    # Cumplimiento por línea
    df_lineas = pd.DataFrame({
        'Linea': [
            'Transformación Organizacional',
            'Expansión',
            'Educación para toda la vida',
            'Experiencia',
            'Calidad',
            'Sostenibilidad'
        ],
        'Cumplimiento': [109.4, 106.7, 105.6, 103.4, 103.3, 95.9],
        'Total_Indicadores': [5, 10, 4, 4, 4, 7]
    })

    # Detalle de indicadores (ejemplo simplificado)
    df_indicadores = pd.DataFrame({
        'Linea': ['Expansión'] * 5 + ['Calidad'] * 3 + ['Sostenibilidad'] * 4,
        'Indicador': [
            'Número de estudiantes matriculados B2B',
            'Número de estudiantes matriculados B2G',
            'Tasa de cobertura educación superior',
            'Número de programas académicos activos',
            'Índice de presencia regional',
            'Tasa de graduación oportuna',
            'Acreditación institucional vigente',
            'Índice de calidad docente',
            'EBITDA institucional',
            'Índice de sostenibilidad ambiental',
            'Ratio de eficiencia energética',
            'Porcentaje de residuos reciclados'
        ],
        'Meta': [15000, 8000, 35, 120, 85, 70, 100, 4.2, 25000, 80, 0.75, 60],
        'Ejecución': [16200, 8500, 38, 128, 88, 68, 100, 4.3, 24500, 77, 0.72, 58],
        'Cumplimiento': [108, 106.3, 108.6, 106.7, 103.5, 97.1, 100, 102.4, 98, 96.3, 96, 96.7]
    })

    # Estructura cascada (ejemplo simplificado)
    df_cascada = pd.DataFrame({
        'Nivel': [1, 2, 4, 4, 1, 2, 4, 4],
        'Linea': ['Expansión'] * 4 + ['Calidad'] * 4,
        'Objetivo': [''] + ['Ampliar cobertura nacional'] * 3 + [''] + ['Fortalecer calidad académica'] * 3,
        'Meta_PDI': [''] * 2 + ['Meta 1.1', 'Meta 1.2'] + [''] * 2 + ['Meta 2.1', 'Meta 2.2'],
        'Indicador': [''] * 2 + ['Estudiantes B2B', 'Programas activos'] + [''] * 2 + ['Tasa graduación', 'Calidad docente'],
        'Cumplimiento': [106.7, 107, 108, 106.7, 103.3, 99.8, 97.1, 102.4],
        'Total_Indicadores': [10, 4, 1, 1, 4, 2, 1, 1]
    })

    # Análisis general
    analisis_texto = """
    El Plan de Desarrollo Institucional 2021-2025 presenta un cumplimiento global del 104%,
    evidenciando el compromiso institucional con la excelencia académica y la transformación
    organizacional. Destacan especialmente las líneas de Transformación Organizacional (109.4%)
    y Expansión (106.7%), que superaron significativamente sus metas.

    La línea de Sostenibilidad (95.9%) requiere atención prioritaria para el próximo período,
    con énfasis en la implementación de iniciativas ambientales y de eficiencia energética.
    """

    # Análisis por línea
    analisis_lineas = {
        'Expansión': 'La línea de Expansión alcanzó un 106.7% de cumplimiento, impulsada por el '
                     'crecimiento en matrículas B2B y B2G, superando las proyecciones iniciales en '
                     'un 8%. La presencia regional se fortaleció con 3 nuevos centros de atención.',

        'Calidad': 'Con un 103.3% de cumplimiento, la línea de Calidad mantiene la acreditación '
                   'institucional vigente y mejora continua en el índice de calidad docente. '
                   'La tasa de graduación oportuna (97.1%) requiere planes de acción específicos.',

        'Sostenibilidad': 'La línea de Sostenibilidad presenta un 95.9% de cumplimiento. Si bien '
                          'el EBITDA se encuentra próximo a la meta (98%), se identifican oportunidades '
                          'de mejora en eficiencia energética y gestión de residuos.'
    }

    return metricas, df_lineas, df_indicadores, analisis_texto, df_cascada, analisis_lineas


# ============================================================================
# SCRIPT DE EJEMPLO / TESTING
# ============================================================================

if __name__ == '__main__':
    """
    Script de ejemplo para generar el PDF con datos de prueba.
    Ejecutar este archivo directamente generará un PDF de ejemplo.
    """
    print("Generando Informe Estratégico POLI - Versión Mejorada...")

    # Generar datos de ejemplo
    metricas, df_lineas, df_indicadores, analisis, df_cascada, analisis_lineas = generar_datos_ejemplo()

    # Generar PDF
    pdf_bytes = exportar_informe_pdf_mejorado(
        metricas=metricas,
        df_lineas=df_lineas,
        df_indicadores=df_indicadores,
        analisis_texto=analisis,
        año=2025,
        df_cascada=df_cascada,
        analisis_lineas=analisis_lineas
    )

    # Guardar archivo
    fecha_actual = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f'Informe_Estrategico_POLI_{fecha_actual}.pdf'

    with open(nombre_archivo, 'wb') as f:
        f.write(pdf_bytes)

    print(f"✓ PDF generado exitosamente: {nombre_archivo}")
    print(f"  - Tamaño: {len(pdf_bytes) / 1024:.1f} KB")
    print(f"  - Páginas: Portada + Resumen + {len(df_cascada['Linea'].unique())} líneas + Indicadores + Conclusiones")
