"""
Generador de Informes PDF - Dashboard Estrategico POLI
Estructura corporativa profesional con enfasis en azul institucional
Utiliza HTML/CSS + weasyprint para conversion a PDF
"""

import io
import os
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd


def limpiar_texto_pdf(texto):
    """
    Limpia el texto para evitar caracteres no soportados por Helvetica en PDF.
    Reemplaza emojis y caracteres Unicode especiales por texto ASCII equivalente.
    """
    if texto is None:
        return ""

    texto = str(texto)

    # Mapeo de emojis/caracteres especiales a texto ASCII
    reemplazos = {
        '⚠️': '[!]',
        '⚠': '[!]',
        '✅': '[OK]',
        '❌': '[X]',
        '📊': '',
        '📈': '',
        '📉': '',
        '🎯': '',
        '📋': '',
        '🔍': '',
        '📥': '',
        '🤖': '',
        '🚦': '',
        '🌊': '',
        '📌': '',
        '🎖️': '',
        '📄': '',
        '❓': '[?]',
        '●': '*',
        '○': '-',
        '•': '-',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '≥': '>=',
        '≤': '<=',
        '≠': '!=',
        '±': '+/-',
        '°': ' grados',
        '×': 'x',
        '÷': '/',
        '—': '-',
        '–': '-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        'á': 'a',
        'é': 'e',
        'í': 'i',
        'ó': 'o',
        'ú': 'u',
        'Á': 'A',
        'É': 'E',
        'Í': 'I',
        'Ó': 'O',
        'Ú': 'U',
        'ñ': 'n',
        'Ñ': 'N',
        'ü': 'u',
        'Ü': 'U',
    }

    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    # Eliminar cualquier otro caracter no ASCII
    texto = texto.encode('ascii', 'ignore').decode('ascii')

    return texto

# Colores corporativos POLI - Énfasis en Azul
COLORES_PDF = {
    'primary': '#003d82',      # Azul institucional oscuro
    'secondary': '#0056b3',    # Azul medio
    'accent': '#1976D2',       # Azul claro
    'light_blue': '#E3F2FD',   # Azul muy claro (fondos)
    'success': '#28a745',      # Verde
    'warning': '#ffc107',      # Amarillo
    'danger': '#dc3545',       # Rojo
    'gray': '#6c757d',         # Gris
    'light': '#f8f9fa',        # Gris claro
    'white': '#ffffff',
    'dark': '#212529'
}


def obtener_css_corporativo() -> str:
    """
    Retorna el CSS corporativo para el informe PDF.
    Estructura profesional con énfasis en azul institucional.
    Compatible con xhtml2pdf (CSS 2.1 principalmente).
    """
    return f"""
    @page {{
        size: A4;
        margin: 2cm 1.5cm 2cm 1.5cm;
    }}

    body {{
        font-family: Helvetica, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.4;
        color: {COLORES_PDF['dark']};
        background: {COLORES_PDF['white']};
    }}

    /* ============================================
       PORTADA MEJORADA
    ============================================ */
    .portada {{
        text-align: center;
        padding: 60px 40px;
        /* Gradiente de azul oscuro a azul claro */
        background: linear-gradient(180deg, {COLORES_PDF['primary']} 0%, {COLORES_PDF['secondary']} 50%, {COLORES_PDF['accent']} 100%);
        color: white;
        margin: -2cm -1.5cm 0 -1.5cm;
        padding-top: 100px;
        padding-bottom: 100px;
        position: relative;
        min-height: 27cm;
    }}

    .portada-logo {{
        font-size: 72pt;
        font-weight: bold;
        margin-bottom: 10px;
        letter-spacing: 8px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}

    .portada-titulo {{
        font-size: 32pt;
        font-weight: bold;
        margin-bottom: 15px;
        margin-top: 50px;
        text-transform: uppercase;
        letter-spacing: 4px;
        line-height: 1.2;
    }}

    .portada-subtitulo {{
        font-size: 16pt;
        margin-bottom: 35px;
        font-weight: 300;
        opacity: 0.95;
    }}

    .portada-linea {{
        width: 120px;
        height: 4px;
        background-color: white;
        margin: 25px auto;
        opacity: 0.7;
    }}

    .portada-fecha {{
        font-size: 12pt;
        margin-top: 35px;
        font-weight: 300;
    }}

    .portada-periodo {{
        background-color: rgba(255, 255, 255, 0.15);
        border: 2px solid white;
        padding: 15px 40px;
        font-size: 14pt;
        font-weight: bold;
        margin-top: 20px;
        display: inline-block;
        letter-spacing: 2px;
    }}

    /* ============================================
       ENCABEZADOS
    ============================================ */
    h1 {{
        color: {COLORES_PDF['primary']};
        font-size: 16pt;
        font-weight: bold;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 3px solid {COLORES_PDF['primary']};
        margin-top: 25px;
    }}

    h2 {{
        color: {COLORES_PDF['primary']};
        font-size: 13pt;
        font-weight: bold;
        margin-bottom: 10px;
        margin-top: 20px;
    }}

    h3 {{
        color: {COLORES_PDF['secondary']};
        font-size: 11pt;
        font-weight: bold;
        margin-bottom: 8px;
    }}

    /* ============================================
       SECCIONES
    ============================================ */
    .seccion {{
        margin-bottom: 20px;
    }}

    .seccion-header {{
        background-color: {COLORES_PDF['primary']};
        color: white;
        padding: 10px 15px;
        margin-bottom: 0;
    }}

    .seccion-header h2 {{
        font-size: 12pt;
        font-weight: bold;
        margin: 0;
        color: white;
    }}

    .seccion-contenido {{
        background-color: {COLORES_PDF['white']};
        border: 1px solid {COLORES_PDF['light_blue']};
        border-top: none;
        padding: 15px;
    }}

    /* ============================================
       KPIs - Usando tablas para compatibilidad
    ============================================ */
    .kpis-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 10px;
        margin-bottom: 20px;
    }}

    .kpis-table td {{
        text-align: center;
        padding: 15px 10px;
        border: 2px solid {COLORES_PDF['light_blue']};
        background-color: {COLORES_PDF['white']};
        width: 20%;
    }}

    .kpi-valor {{
        font-size: 22pt;
        font-weight: bold;
        color: {COLORES_PDF['primary']};
    }}

    .kpi-valor-success {{
        font-size: 22pt;
        font-weight: bold;
        color: {COLORES_PDF['success']};
    }}

    .kpi-valor-warning {{
        font-size: 22pt;
        font-weight: bold;
        color: {COLORES_PDF['warning']};
    }}

    .kpi-valor-danger {{
        font-size: 22pt;
        font-weight: bold;
        color: {COLORES_PDF['danger']};
    }}

    .kpi-label {{
        font-size: 8pt;
        color: {COLORES_PDF['gray']};
        text-transform: uppercase;
        margin-top: 5px;
    }}

    /* ============================================
       TABLAS
    ============================================ */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 9pt;
    }}

    table thead tr {{
        background-color: {COLORES_PDF['primary']};
        color: white;
    }}

    table th {{
        padding: 10px 8px;
        text-align: left;
        font-weight: bold;
        font-size: 8pt;
        color: white;
        border: 1px solid {COLORES_PDF['primary']};
    }}

    table td {{
        padding: 8px;
        border: 1px solid {COLORES_PDF['light_blue']};
    }}

    table tr.even {{
        background-color: {COLORES_PDF['light']};
    }}

    /* ============================================
       BADGES DE ESTADO
    ============================================ */
    .badge {{
        padding: 3px 10px;
        font-size: 8pt;
        font-weight: bold;
    }}

    .badge-success {{
        background-color: {COLORES_PDF['success']};
        color: white;
    }}

    .badge-warning {{
        background-color: {COLORES_PDF['warning']};
        color: {COLORES_PDF['dark']};
    }}

    .badge-danger {{
        background-color: {COLORES_PDF['danger']};
        color: white;
    }}

    .badge-info {{
        background-color: {COLORES_PDF['accent']};
        color: white;
    }}

    /* ============================================
       ANÁLISIS
    ============================================ */
    .analisis-box {{
        background-color: {COLORES_PDF['light_blue']};
        border-left: 4px solid {COLORES_PDF['primary']};
        padding: 15px;
        margin: 15px 0;
    }}

    .analisis-box h4 {{
        color: {COLORES_PDF['primary']};
        font-size: 11pt;
        margin-bottom: 10px;
        margin-top: 0;
    }}

    .analisis-box p {{
        font-size: 10pt;
        line-height: 1.5;
        color: {COLORES_PDF['dark']};
        margin: 0;
    }}

    /* ============================================
       SEMÁFORO
    ============================================ */
    .semaforo-table {{
        width: 100%;
        margin: 15px 0;
        background-color: {COLORES_PDF['light']};
    }}

    .semaforo-table td {{
        text-align: center;
        padding: 10px;
        font-size: 9pt;
    }}

    .dot-verde {{
        color: {COLORES_PDF['success']};
        font-size: 14pt;
    }}

    .dot-amarillo {{
        color: {COLORES_PDF['warning']};
        font-size: 14pt;
    }}

    .dot-rojo {{
        color: {COLORES_PDF['danger']};
        font-size: 14pt;
    }}

    /* ============================================
       PIE DE PÁGINA
    ============================================ */
    .footer {{
        margin-top: 30px;
        padding-top: 15px;
        border-top: 2px solid {COLORES_PDF['primary']};
        text-align: center;
        font-size: 8pt;
        color: {COLORES_PDF['gray']};
    }}

    .footer-logo {{
        color: {COLORES_PDF['primary']};
        font-weight: bold;
        font-size: 10pt;
    }}

    /* ============================================
       UTILIDADES
    ============================================ */
    .page-break {{
        page-break-after: always;
    }}

    .text-center {{
        text-align: center;
    }}

    .text-right {{
        text-align: right;
    }}

    .mt-20 {{
        margin-top: 20px;
    }}

    .mb-20 {{
        margin-bottom: 20px;
    }}
    /* ============================================
       HOJA CUMPLIMIENTO POR LINEA - TARJETAS
    ============================================ */
    .lineas-grid {{
        width: 100%;
        display: table;
        table-layout: fixed;
        margin-top: 6px;
    }}

    .lineas-row {{ display: table-row; }}
    .lineas-cell {{
        display: table-cell;
        padding: 8px;
        vertical-align: top;
        width: 33%;
    }}

    .linea-card {{
        background: white;
        border: 1px solid #e6eef9;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 1px 0 rgba(0,0,0,0.03);
    }}

    .linea-top {{ display:flex; justify-content:space-between; align-items:center; }}

    .linea-title {{
        font-weight:700;
        color: {COLORES_PDF['primary']};
        font-size: 10pt;
    }}

    .linea-meta {{ font-size: 9pt; color: {COLORES_PDF['gray']}; }}

    .circle {{
        width: 56px; height: 56px; border-radius: 50%;
        display:inline-flex; align-items:center; justify-content:center;
        font-weight:700; color: white; font-size: 12pt;
    }}

    .card-body {{ margin-top: 10px; display:flex; justify-content:space-between; align-items:center; }}

    .small-badge {{ padding:4px 8px; border-radius:12px; font-size:8pt; font-weight:700; }}

    .summary-box {{ float: right; text-align:center; background: {COLORES_PDF['primary']}; color: white; padding:8px 12px; border-radius:6px; }}

    """


def generar_portada(titulo: str, subtitulo: str, periodo: str, fecha: str) -> str:
    """Genera el HTML de la portada del informe con diseño mejorado."""
    return f"""
    <div class="portada">
        <!-- Logo Poli (Nota: Reemplazar con <img> real si se tiene el archivo) -->
        <div class="portada-logo">POLI</div>
        <div style="font-size: 10pt; margin-bottom: 5px;">POLITECNICO GRANCOLOMBIANO</div>
        <div style="font-size: 8pt; margin-bottom: 40px; opacity: 0.9;">INSTITUCION UNIVERSITARIA</div>

        <div class="portada-titulo">{titulo}</div>
        <div class="portada-subtitulo">{subtitulo}</div>
        <div class="portada-linea">&nbsp;</div>
        <div class="portada-periodo">{periodo}</div>
        <div class="portada-fecha">Generado el {fecha}</div>
        <div style="position: absolute; bottom: 30px; left: 0; right: 0; text-align: center; font-size: 9pt; opacity: 0.8;">
            Dashboard Estrategico - Sistema de Monitoreo PDI
        </div>
    </div>
    <div class="page-break"></div>
    """


def generar_seccion_kpis(metricas: Dict[str, Any]) -> str:
    """Genera el HTML de la sección de KPIs principales usando tablas (compatible xhtml2pdf)."""
    cumplimiento = metricas.get('cumplimiento_promedio', 0)

    # Determinar clase del KPI principal según cumplimiento
    if cumplimiento >= 100:
        clase_cumpl = 'kpi-valor-success'
    elif cumplimiento >= 80:
        clase_cumpl = 'kpi-valor-warning'
    else:
        clase_cumpl = 'kpi-valor-danger'

    return f"""
    <div class="seccion">
        <div class="seccion-header">
            <h2>Indicadores Clave de Desempeno</h2>
        </div>
        <div class="seccion-contenido">
            <table class="kpis-table">
                <tr>
                    <td style="border-top: 4px solid {COLORES_PDF['primary'] if cumplimiento >= 100 else COLORES_PDF['warning'] if cumplimiento >= 80 else COLORES_PDF['danger']};">
                        <div class="{clase_cumpl}">{cumplimiento:.1f}%</div>
                        <div class="kpi-label">Cumplimiento General</div>
                    </td>
                    <td style="border-top: 4px solid {COLORES_PDF['success']};">
                        <div class="kpi-valor-success">{metricas.get('indicadores_cumplidos', 0)}</div>
                        <div class="kpi-label">Cumplidos</div>
                    </td>
                    <td style="border-top: 4px solid {COLORES_PDF['warning']};">
                        <div class="kpi-valor-warning">{metricas.get('en_progreso', 0)}</div>
                        <div class="kpi-label">En Progreso</div>
                    </td>
                    <td style="border-top: 4px solid {COLORES_PDF['danger']};">
                        <div class="kpi-valor-danger">{metricas.get('no_cumplidos', 0)}</div>
                        <div class="kpi-label">No Cumplidos</div>
                    </td>
                    <td style="border-top: 4px solid {COLORES_PDF['primary']};">
                        <div class="kpi-valor">{metricas.get('total_indicadores', 0)}</div>
                        <div class="kpi-label">Total</div>
                    </td>
                </tr>
            </table>

            <table class="semaforo-table">
                <tr>
                    <td>
                        <span class="dot-verde">&#9679;</span> &ge;100% Meta Cumplida
                    </td>
                    <td>
                        <span class="dot-amarillo">&#9679;</span> 80-99% En Progreso
                    </td>
                    <td>
                        <span class="dot-rojo">&#9679;</span> &lt;80% Requiere Atencion
                    </td>
                </tr>
            </table>
        </div>
    </div>
    """


def generar_tabla_lineas(df_lineas: pd.DataFrame) -> str:
    """Genera la tabla HTML de cumplimiento por línea estratégica."""
    if df_lineas is None or df_lineas.empty:
        return "<p>No hay datos disponibles.</p>"

    filas_html = ""
    for idx, (_, row) in enumerate(df_lineas.iterrows()):
        cumpl = row.get('Cumplimiento', 0)
        if cumpl >= 100:
            badge = f'<span class="badge badge-success">Cumplido</span>'
        elif cumpl >= 80:
            badge = f'<span class="badge badge-warning">En Progreso</span>'
        else:
            badge = f'<span class="badge badge-danger">Atencion</span>'

        clase_fila = 'even' if idx % 2 == 1 else ''

        filas_html += f"""
        <tr class="{clase_fila}">
            <td>{row.get('Linea', 'N/D')}</td>
            <td style="text-align: center;">{row.get('Total_Indicadores', 0)}</td>
            <td style="text-align: right;"><strong>{cumpl:.1f}%</strong></td>
            <td style="text-align: center;">{badge}</td>
        </tr>
        """

    return f"""
    <div class="seccion">
        <div class="seccion-header">
            <h2>Cumplimiento por Linea Estrategica</h2>
        </div>
        <div class="seccion-contenido">
            <table>
                <thead>
                    <tr>
                        <th>Linea Estrategica</th>
                        <th style="text-align: center;">Indicadores</th>
                        <th style="text-align: right;">Cumplimiento</th>
                        <th style="text-align: center;">Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
    </div>
    """


def generar_hoja_cumplimiento_por_linea_html(df_lineas: pd.DataFrame, metricas: Dict[str, Any]) -> str:
    """Genera una hoja visual (tarjetas) de cumplimiento por línea estratégica.

    Diseñado para la conversión HTML->PDF (xhtml2pdf compatible, CSS 2.1 limitado).
    """
    if df_lineas is None or df_lineas.empty:
        return "<p>No hay datos disponibles.</p>"

    # Resumen superior
    total = int(metricas.get('total_indicadores', df_lineas.get('Total_Indicadores', 0).sum()))
    cumplidos = int(metricas.get('indicadores_cumplidos', 0))
    en_progreso = int(metricas.get('en_progreso', 0))
    no_cumplidos = int(metricas.get('no_cumplidos', 0))

    resumen_html = f"""
    <div style="overflow: auto; margin-bottom: 8px;">
        <div style="float:left;">
            <h2 style="margin:0;">Cumplimiento por Línea Estratégica</h2>
            <div style="font-size:9pt; color: #6c757d;">Resumen general del periodo</div>
        </div>
        <div class="summary-box">
            <div style="font-size:12pt; font-weight:700">{total}</div>
            <div style="font-size:8pt; opacity:0.9">INDICADORES</div>
        </div>
    </div>
    """

    # Construir grid de 3 columnas
    filas = []
    cards = []
    for _, row in df_lineas.iterrows():
        linea = limpiar_texto_pdf(str(row.get('Linea', 'N/D')))
        total_ind = int(row.get('Total_Indicadores', 0) or 0)
        cumpl = float(row.get('Cumplimiento', 0) or 0)

        if cumpl >= 100:
            color = COLORES_PDF['success']
            estado_txt = 'CUMPLIDO'
            badge_class = 'small-badge'
            badge_style = f'background:{COLORES_PDF["success"]}; color: white;'
        elif cumpl >= 80:
            color = COLORES_PDF['warning']
            estado_txt = 'EN PROGRESO'
            badge_style = f'background:{COLORES_PDF["warning"]}; color: {COLORES_PDF["dark"]};'
        else:
            color = COLORES_PDF['danger']
            estado_txt = 'EN ATENCIÓN'
            badge_style = f'background:{COLORES_PDF["danger"]}; color: white;'

        circle_html = f'<div class="circle" style="background:{color};">{cumpl:.0f}%</div>'

        card = f"""
        <div class="linea-card">
            <div class="linea-top">
                <div>
                    <div class="linea-title">{linea}</div>
                    <div class="linea-meta">{total_ind} indicadores</div>
                </div>
                <div>{circle_html}</div>
            </div>
            <div class="card-body">
                <div style="font-size:9pt; color: {COLORES_PDF['gray']};">&nbsp;</div>
                <div class="small-badge" style="{badge_style}">{estado_txt}</div>
            </div>
        </div>
        """

        cards.append(card)

    # Agrupar en filas de 3
    rows_html = ""
    for i in range(0, len(cards), 3):
        row_cards = cards[i:i+3]
        cells_html = ""
        for c in row_cards:
            cells_html += f'<div class="lineas-cell">{c}</div>'
        # completar celdas vacías si hay menos de 3
        missing = 3 - len(row_cards)
        for _ in range(missing):
            cells_html += '<div class="lineas-cell">&nbsp;</div>'
        rows_html += f'<div class="lineas-row">{cells_html}</div>'

    grid_html = f"""
    {resumen_html}
    <div class="lineas-grid">
        {rows_html}
    </div>
    """

    return f"<div class=\"seccion\">\n<div class=\"seccion-header\"><h2></h2></div>\n<div class=\"seccion-contenido\">{grid_html}</div>\n</div>"


def generar_tabla_indicadores(df_indicadores: pd.DataFrame, titulo: str = "Detalle de Indicadores") -> str:
    """Genera la tabla HTML de indicadores detallados."""
    if df_indicadores is None or df_indicadores.empty:
        return "<p>No hay datos disponibles.</p>"

    filas_html = ""
    for idx, (_, row) in enumerate(df_indicadores.iterrows()):
        cumpl = row.get('Cumplimiento', 0)
        if pd.isna(cumpl):
            badge = '<span class="badge badge-info">N/D</span>'
            cumpl_str = "N/D"
        elif cumpl >= 100:
            badge = '<span class="badge badge-success">Cumple</span>'
            cumpl_str = f"{cumpl:.1f}%"
        elif cumpl >= 80:
            badge = '<span class="badge badge-warning">!</span>'
            cumpl_str = f"{cumpl:.1f}%"
        else:
            badge = '<span class="badge badge-danger">X</span>'
            cumpl_str = f"{cumpl:.1f}%"

        indicador = row.get('Indicador', 'N/D')
        # Truncar si es muy largo
        if len(str(indicador)) > 55:
            indicador = str(indicador)[:52] + "..."

        # Formatear meta y ejecución
        meta = row.get('Meta', 'N/D')
        if pd.notna(meta) and isinstance(meta, (int, float)):
            meta = f"{meta:.2f}"

        ejecucion = row.get('Ejecución', row.get('Ejecucion', 'N/D'))
        if pd.notna(ejecucion) and isinstance(ejecucion, (int, float)):
            ejecucion = f"{ejecucion:.2f}"

        clase_fila = 'even' if idx % 2 == 1 else ''

        filas_html += f"""
        <tr class="{clase_fila}">
            <td>{indicador}</td>
            <td style="text-align: right;">{meta}</td>
            <td style="text-align: right;">{ejecucion}</td>
            <td style="text-align: right;"><strong>{cumpl_str}</strong></td>
            <td style="text-align: center;">{badge}</td>
        </tr>
        """

    return f"""
    <div class="seccion">
        <div class="seccion-header">
            <h2>{titulo}</h2>
        </div>
        <div class="seccion-contenido">
            <table>
                <thead>
                    <tr>
                        <th style="width: 45%;">Indicador</th>
                        <th style="width: 12%; text-align: right;">Meta</th>
                        <th style="width: 12%; text-align: right;">Ejecucion</th>
                        <th style="width: 15%; text-align: right;">Cumplimiento</th>
                        <th style="width: 10%; text-align: center;">Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
    </div>
    """


def generar_seccion_analisis(titulo: str, contenido: str) -> str:
    """Genera una sección de análisis con formato de caja."""
    # Limpiar contenido de caracteres especiales que pueden causar problemas
    contenido_limpio = contenido.replace('**', '').replace('*', '')
    contenido_limpio = contenido_limpio.replace('\n', '<br/>')

    return f"""
    <div class="analisis-box">
        <h4>Analisis: {titulo}</h4>
        <p>{contenido_limpio}</p>
    </div>
    """


def figura_a_base64(fig) -> str:
    """Convierte una figura de Plotly a imagen base64 para incrustar en HTML."""
    try:
        img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error al convertir figura: {e}")
        return ""


def generar_seccion_grafico(titulo: str, fig, descripcion: str = "") -> str:
    """Genera una sección con un gráfico incrustado."""
    img_src = figura_a_base64(fig)
    if not img_src:
        return f"<p>No se pudo generar el gráfico: {titulo}</p>"

    desc_html = f'<p style="font-size: 9pt; color: {COLORES_PDF["gray"]}; margin-top: 10px;">{descripcion}</p>' if descripcion else ""

    return f"""
    <div class="seccion no-break">
        <div class="seccion-header">
            <h2>📊 {titulo}</h2>
        </div>
        <div class="seccion-contenido">
            <div class="grafico-container">
                <img src="{img_src}" alt="{titulo}">
                {desc_html}
            </div>
        </div>
    </div>
    """


def generar_informe_html(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    figuras: List[tuple] = None,
    año: int = 2025
) -> str:
    """
    Genera el HTML completo del informe PDF.

    Args:
        metricas: Diccionario con métricas generales
        df_lineas: DataFrame con cumplimiento por línea
        df_indicadores: DataFrame con detalle de indicadores
        analisis_texto: Texto del análisis IA
        figuras: Lista de tuplas (titulo, figura_plotly, descripcion)
        año: Año del informe

    Returns:
        HTML completo del informe
    """
    fecha_generacion = datetime.now().strftime("%d de %B de %Y a las %H:%M")

    # Secciones del informe
    portada = generar_portada(
        titulo="Informe Estratégico",
        subtitulo="Plan de Desarrollo Institucional",
        periodo=f"Periodo 2021-{año}",
        fecha=fecha_generacion
    )

    kpis = generar_seccion_kpis(metricas)
    # Generar hoja visual de cumplimiento por línea (tarjetas). Si falla, caer a tabla simple.
    try:
        tabla_lineas = generar_hoja_cumplimiento_por_linea_html(df_lineas, metricas)
    except Exception:
        tabla_lineas = generar_tabla_lineas(df_lineas)

    # Gráficos
    graficos_html = ""
    if figuras:
        for titulo, fig, descripcion in figuras:
            graficos_html += generar_seccion_grafico(titulo, fig, descripcion)
            graficos_html += '<div class="page-break"></div>'

    # Análisis IA
    analisis_html = ""
    if analisis_texto:
        analisis_html = generar_seccion_analisis("Análisis Ejecutivo", analisis_texto)

    # Tabla de indicadores
    tabla_indicadores = generar_tabla_indicadores(df_indicadores)

    # Footer
    footer = f"""
    <div class="footer">
        <div class="footer-logo">POLITECNICO GRANCOLOMBIANO</div>
        <p>Dashboard Estrategico POLI - Plan de Desarrollo Institucional 2021-{año}</p>
        <p>Documento generado automaticamente el {fecha_generacion}</p>
    </div>
    """

    # HTML completo - Sin emojis para compatibilidad con xhtml2pdf
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Informe Estrategico POLI {año}</title>
        <style>
            {obtener_css_corporativo()}
        </style>
    </head>
    <body>
        {portada}

        <h1>Resumen Ejecutivo</h1>
        {kpis}
        {analisis_html}

        <div class="page-break"></div>

        <h1>Analisis por Linea Estrategica</h1>
        {tabla_lineas}

        {graficos_html}

        <div class="page-break"></div>

        <h1>Detalle de Indicadores</h1>
        {tabla_indicadores}

        {footer}
    </body>
    </html>
    """

    return html


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convierte '#RRGGBB' a (R, G, B)."""
    h = hex_color.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _generar_paginas_lineas(pdf, df_cascada: pd.DataFrame, año: int) -> None:
    """
    Genera una página visual por línea estratégica, replicando el diseño dashboard:
    leyenda superior → header navy con color de línea → filas objetivo/meta/indicador → footer.
    """
    import unicodedata

    if df_cascada is None or df_cascada.empty:
        return

    _COLORES_HEX = {
        "expansion":                     "#FBAF17",
        "transformacion organizacional":  "#42F2F2",
        "calidad":                       "#EC0677",
        "experiencia":                   "#1FB2DE",
        "sostenibilidad":                "#A6CE38",
        "educacion para toda la vida":   "#0F385A",
    }

    def _norm(s):
        return ''.join(
            c for c in unicodedata.normalize('NFD', s.lower().strip())
            if unicodedata.category(c) != 'Mn'
        )

    def _color_linea(nombre):
        n = _norm(nombre)
        for k, hx in _COLORES_HEX.items():
            if k in n or n in k:
                return _hex_to_rgb(hx)
        return (0, 61, 130)

    C_NAVY   = (  0,  38,  97)
    C_WHITE  = (255, 255, 255)
    C_BG     = (246, 248, 252)
    C_DARK   = ( 33,  37,  41)
    C_GRAY   = (118, 128, 143)
    C_OBJBG  = (228, 232, 242)
    C_GREEN  = ( 34, 154,  82)
    C_ORANGE = (245, 130,   0)
    C_RED    = (210,  40,  55)
    LG_H  = 10   # leyenda
    BND_H = 42   # header band
    FTR_Y = 278  # footer y
    CTN_Y = LG_H + BND_H + 4  # contenido empieza en y=56

    # ── Agrupar df por línea ────────────────────────────────────────────────
    lineas_order = []
    lineas_rows  = {}
    linea_cumpl  = {}
    cur_linea    = None

    for _, row in df_cascada.iterrows():
        nivel = int(row['Nivel'])
        if nivel == 1:
            cur_linea = limpiar_texto_pdf(str(row['Linea']))
            if cur_linea not in lineas_rows:
                lineas_order.append(cur_linea)
                lineas_rows[cur_linea] = []
                linea_cumpl[cur_linea] = float(row.get('Cumplimiento', 0) or 0)
        elif cur_linea:
            lineas_rows[cur_linea].append(row)

    pdf.set_auto_page_break(auto=False)

    # ── Renderizar cada línea ───────────────────────────────────────────────
    for linea_nom in lineas_order:
        rows    = lineas_rows[linea_nom]
        if not rows:
            continue
        CL      = _color_linea(linea_nom)
        cl_lum  = 0.299*CL[0] + 0.587*CL[1] + 0.114*CL[2]
        CL_TXT  = C_DARK if cl_lum > 155 else C_WHITE
        cum_lin = linea_cumpl[linea_nom]

        # ── Helpers locales (capturan CL, cum_lin, linea_nom del scope actual) ──

        def _mini_bar(x, y, w, h, c):
            pdf.set_fill_color(208, 218, 235)
            pdf.rounded_rect(x, y, w, h, h/2, 'F')
            if c > 0:
                fw = min((c / 100) * w, w)
                if c >= 100:   pdf.set_fill_color(*C_GREEN)
                elif c >= 80:  pdf.set_fill_color(*C_ORANGE)
                else:          pdf.set_fill_color(*C_RED)
                pdf.rounded_rect(x, y, fw, h, h/2, 'F')

        def _draw_leyenda():
            pdf.set_fill_color(*C_WHITE)
            pdf.rect(0, 0, 210, LG_H, 'F')
            pdf.set_draw_color(210, 220, 235)
            pdf.set_line_width(0.3)
            pdf.line(0, LG_H, 210, LG_H)
            pdf.set_line_width(0.2)
            x = 5
            pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', 'B', 5.5)
            pdf.set_text_color(*C_DARK); pdf.cell(15, 5, 'NIVELES', 0, 0); x += 16
            pdf.set_fill_color(185, 198, 218)
            pdf.rounded_rect(x, 2.8, 16, 4.4, 1, 'F')
            pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', 'B', 4.8); pdf.set_text_color(*C_DARK)
            pdf.cell(16, 5, 'OBJETIVO', 0, 0, 'C'); x += 17
            pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', '', 5.3); pdf.set_text_color(*C_GRAY)
            pdf.cell(32, 5, 'Porcentaje promedio neutral', 0, 0); x += 33
            pdf.set_fill_color(*CL)
            pdf.rounded_rect(x, 2.8, 15, 4.4, 1, 'F')
            pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', 'B', 4.5); pdf.set_text_color(*CL_TXT)
            pdf.cell(15, 5, 'META PDI', 0, 0, 'C'); x += 16
            pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', '', 5.3); pdf.set_text_color(*C_GRAY)
            pdf.cell(33, 5, 'Porcentaje referencial neutral', 0, 0); x += 34
            pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', 'B', 5.5); pdf.set_text_color(*C_DARK)
            pdf.cell(20, 5, 'INDICADORES', 0, 0); x += 21
            for dc, dt in [(C_GREEN, 'Cumple'), (C_ORANGE, 'Progreso'), (C_RED, 'Atencion')]:
                pdf.set_fill_color(*dc)
                pdf.ellipse(x, 4, 3, 3, 'F'); x += 4
                pdf.set_xy(x, 2.5); pdf.set_font('Helvetica', '', 5.3)
                pdf.set_text_color(*C_GRAY); pdf.cell(15, 5, dt, 0, 0); x += 14

        def _draw_header():
            pdf.set_fill_color(*C_NAVY)
            pdf.rect(0, LG_H, 210, BND_H, 'F')
            pdf.set_fill_color(*CL)
            pdf.rect(0, LG_H + BND_H - 3, 210, 3, 'F')
            pdf.set_xy(10, LG_H + 7)
            pdf.set_font('Helvetica', '', 6); pdf.set_text_color(155, 192, 235)
            pdf.cell(120, 4, 'LINEA ESTRATEGICA  -  PDI', 0, 0)
            pdf.set_xy(10, LG_H + 13)
            pdf.set_font('Helvetica', 'B', 16); pdf.set_text_color(*C_WHITE)
            pdf.multi_cell(112, 9, linea_nom, 0, 'L')
            # Badge estado
            if cum_lin >= 100:   bt = 'v  META SUPERADA';    bc = C_GREEN
            elif cum_lin >= 80:  bt = 'EN PROGRESO';          bc = C_ORANGE
            else:                bt = 'REQUIERE ATENCION';    bc = C_RED
            pdf.set_fill_color(*bc)
            pdf.rounded_rect(123, LG_H + 13, 30, 7, 2, 'F')
            pdf.set_xy(123, LG_H + 13); pdf.set_font('Helvetica', 'B', 5.5)
            pdf.set_text_color(*C_WHITE); pdf.cell(30, 7, bt, 0, 0, 'C')
            # Porcentaje
            cum_s = f'{cum_lin:.1f}%'
            pdf.set_xy(153, LG_H + 9)
            pdf.set_font('Helvetica', 'B', 26 if len(cum_s) <= 6 else 20)
            pdf.set_text_color(*C_WHITE); pdf.cell(52, 18, cum_s, 0, 0, 'R')
            pdf.set_xy(153, LG_H + 29)
            pdf.set_font('Helvetica', '', 5.5); pdf.set_text_color(155, 192, 235)
            pdf.cell(52, 4, 'CUMPLIMIENTO GLOBAL', 0, 0, 'R')

        def _draw_footer():
            pdf.set_fill_color(241, 244, 250)
            pdf.rect(0, FTR_Y, 210, 19, 'F')
            pdf.set_draw_color(208, 218, 235); pdf.set_line_width(0.3)
            pdf.line(0, FTR_Y, 210, FTR_Y); pdf.set_line_width(0.2)
            pdf.set_xy(10, FTR_Y + 3); pdf.set_font('Helvetica', 'B', 5.5)
            pdf.set_text_color(*C_DARK); pdf.cell(20, 5, 'INDICADORES', 0, 0)
            cx = 32
            for dc, dt in [(C_GREEN, '>= 100%  Cumple'), (C_ORANGE, '80-99%  En Progreso'), (C_RED, '< 80%  Atencion')]:
                pdf.set_fill_color(*dc); pdf.ellipse(cx, FTR_Y + 5, 3, 3, 'F'); cx += 4
                pdf.set_xy(cx, FTR_Y + 3); pdf.set_font('Helvetica', '', 5.5)
                pdf.set_text_color(*C_GRAY); pdf.cell(38, 5, dt, 0, 0); cx += 37
            pdf.set_xy(150, FTR_Y + 3); pdf.set_font('Helvetica', 'B', 6)
            pdf.set_text_color(*C_GRAY); pdf.cell(55, 5, f'PDI  .  {año}', 0, 0, 'R')

        def _cont_header():
            """Mini header de continuación para páginas adicionales de la misma línea."""
            _draw_footer()
            pdf.add_page()
            pdf.set_fill_color(*C_BG); pdf.rect(0, 0, 210, 297, 'F')
            pdf.set_fill_color(*C_NAVY); pdf.rect(0, 0, 210, 14, 'F')
            pdf.set_fill_color(*CL);    pdf.rect(0, 11, 210, 3, 'F')
            pdf.set_xy(10, 3); pdf.set_font('Helvetica', 'B', 7)
            pdf.set_text_color(*C_WHITE); pdf.cell(130, 6, linea_nom, 0, 0)
            pdf.set_font('Helvetica', '', 7); pdf.set_text_color(155, 192, 235)
            pdf.cell(0, 6, f'Continuacion  /  {cum_lin:.1f}%', 0, 0, 'R')
            pdf.set_y(17)

        # ── Primera página de la línea ──────────────────────────────────────
        pdf.add_page()
        pdf.set_fill_color(*C_BG); pdf.rect(0, 0, 210, 297, 'F')
        _draw_leyenda()
        _draw_header()
        pdf.set_y(CTN_Y)

        # ── Filas de contenido ──────────────────────────────────────────────
        for row in rows:
            nivel = int(row['Nivel'])
            cumpl = float(row.get('Cumplimiento', 0) or 0)
            if cumpl >= 100:  c_st = C_GREEN
            elif cumpl >= 80: c_st = C_ORANGE
            else:             c_st = C_RED

            if nivel == 2:  # OBJETIVO
                objetivo = limpiar_texto_pdf(str(row.get('Objetivo', '')))
                if pdf.get_y() + 12 > FTR_Y:
                    _cont_header()
                y0 = pdf.get_y()
                pdf.set_fill_color(*C_OBJBG)
                pdf.rect(10, y0, 190, 10, 'F')
                pdf.set_fill_color(148, 165, 192)
                pdf.rounded_rect(11, y0+2, 17, 6, 1, 'F')
                pdf.set_xy(11, y0+2); pdf.set_font('Helvetica', 'B', 4.8)
                pdf.set_text_color(*C_WHITE); pdf.cell(17, 6, 'OBJETIVO', 0, 0, 'C')
                pdf.set_xy(30, y0+2.5); pdf.set_font('Helvetica', 'B', 7.5)
                pdf.set_text_color(*C_DARK); pdf.cell(118, 5, objetivo[:72], 0, 0, 'L')
                _mini_bar(152, y0+3.5, 26, 3, cumpl)
                pdf.set_xy(179, y0+1.5); pdf.set_font('Helvetica', 'B', 7.5)
                pdf.set_text_color(*c_st); pdf.cell(20, 7, f'{cumpl:.1f}%', 0, 0, 'R')
                pdf.set_y(y0 + 11)

            elif nivel == 3:  # META PDI
                meta = limpiar_texto_pdf(str(row.get('Meta_PDI', '')))
                if not meta or meta == 'N/D':
                    continue
                if pdf.get_y() + 9 > FTR_Y:
                    _cont_header()
                y0 = pdf.get_y()
                pdf.set_fill_color(*CL); pdf.rect(10, y0, 2.5, 8, 'F')
                pdf.set_fill_color(*CL)
                pdf.rounded_rect(14, y0+1, 16, 6, 1, 'F')
                pdf.set_xy(14, y0+1); pdf.set_font('Helvetica', 'B', 4.5)
                pdf.set_text_color(*CL_TXT); pdf.cell(16, 6, 'META PDI', 0, 0, 'C')
                pdf.set_xy(32, y0+2); pdf.set_font('Helvetica', '', 7)
                pdf.set_text_color(*C_DARK); pdf.cell(118, 5, meta[:72], 0, 0, 'L')
                pdf.set_xy(152, y0+1.5); pdf.set_font('Helvetica', 'B', 7)
                pdf.set_text_color(*c_st); pdf.cell(20, 5, f'{cumpl:.1f}%', 0, 0, 'R')
                _mini_bar(173, y0+2.5, 24, 3, cumpl)
                pdf.set_y(y0 + 9)

            elif nivel == 4:  # INDICADOR
                indicador = limpiar_texto_pdf(str(row.get('Indicador', '')))
                if pdf.get_y() + 8 > FTR_Y:
                    _cont_header()
                y0 = pdf.get_y()
                pdf.set_fill_color(250, 252, 255)
                pdf.rect(10, y0, 190, 7, 'F')
                pdf.set_xy(13, y0+1); pdf.set_font('Helvetica', '', 7)
                pdf.set_text_color(*C_GRAY); pdf.cell(5, 5, '>', 0, 0, 'C')
                pdf.set_xy(19, y0+1); pdf.set_font('Helvetica', '', 7)
                pdf.set_text_color(*C_DARK); pdf.cell(110, 5, indicador[:66], 0, 0, 'L')
                if cumpl >= 100:  sb=(218,245,228); st='CUMPLE';      sc=C_GREEN
                elif cumpl >= 80: sb=(255,240,215); st='EN PROGRESO';  sc=C_ORANGE
                else:             sb=(255,224,224); st='ATENCION';     sc=C_RED
                pdf.set_fill_color(*sb)
                pdf.rounded_rect(131, y0+1, 21, 5, 1.5, 'F')
                pdf.set_xy(131, y0+1); pdf.set_font('Helvetica', 'B', 4.5)
                pdf.set_text_color(*sc); pdf.cell(21, 5, st, 0, 0, 'C')
                pdf.set_xy(154, y0+1); pdf.set_font('Helvetica', 'B', 7)
                pdf.set_text_color(*c_st); pdf.cell(18, 5, f'{cumpl:.0f}%', 0, 0, 'R')
                _mini_bar(173, y0+2, 24, 3, cumpl)
                pdf.set_y(y0 + 7)

        _draw_footer()

    pdf.set_auto_page_break(auto=True, margin=20)


def _generar_hoja_lineas_fpdf(pdf, df_lineas: pd.DataFrame, metricas: Dict[str, Any], año: int) -> None:
    """Dibuja una hoja resumen tipo 'tarjetas' con cumplimiento por línea usando fpdf2."""
    if df_lineas is None or df_lineas.empty:
        return

    pdf.add_page()
    pdf.set_fill_color(246, 248, 252)
    pdf.rect(0, 0, 210, 297, 'F')

    # Título
    pdf.set_xy(10, 10)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(0, 61, 130)
    pdf.cell(0, 10, 'Cumplimiento por Línea Estratégica', 0, 1)

    # Layout 3 columnas
    left = 10
    top = 28
    gap = 4
    card_w = (190 - 2*gap) / 3  # 190 usable width
    card_h = 48

    # Color conversion helper
    def _hexrgb(hx):
        try:
            return _hex_to_rgb(hx)
        except Exception:
            return (0, 61, 130)

    # Iterar y dibujar tarjetas
    x = left
    y = top
    col = 0
    for idx, (_, row) in enumerate(df_lineas.iterrows()):
        linea = limpiar_texto_pdf(str(row.get('Linea', 'N/D')))
        total_ind = int(row.get('Total_Indicadores', 0) or 0)
        cumpl = float(row.get('Cumplimiento', 0) or 0)

        # Estado color
        if cumpl >= 100:
            st_color = _hexrgb(COLORES_PDF['success'])
            badge_txt = 'CUMPLIDO'
            badge_bg = _hexrgb(COLORES_PDF['success'])
            badge_tc = (255,255,255)
        elif cumpl >= 80:
            st_color = _hexrgb(COLORES_PDF['warning'])
            badge_txt = 'EN PROGRESO'
            badge_bg = _hexrgb(COLORES_PDF['warning'])
            badge_tc = _hexrgb(COLORES_PDF['dark'])
        else:
            st_color = _hexrgb(COLORES_PDF['danger'])
            badge_txt = 'EN ATENCIÓN'
            badge_bg = _hexrgb(COLORES_PDF['danger'])
            badge_tc = (255,255,255)

        # Card background
        pdf.set_fill_color(255,255,255)
        pdf.set_draw_color(*_hexrgb(COLORES_PDF['light_blue']))
        pdf.rounded_rect(x, y, card_w, card_h, 3, 'DF')

        # Left text
        pdf.set_xy(x + 6, y + 6)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 61, 130)
        pdf.cell(card_w - 60, 6, linea[:30], 0, 2)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(100,100,100)
        pdf.cell(card_w - 60, 5, f'{total_ind} indicadores', 0, 2)

        # Circle percentage on right
        circ_x = x + card_w - 34
        circ_y = y + 6
        pdf.set_fill_color(*st_color)
        pdf.ellipse(circ_x, circ_y, 28, 28, 'F')
        pdf.set_xy(circ_x, circ_y + 6)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(255,255,255)
        pdf.cell(28, 10, f'{cumpl:.0f}%', 0, 0, 'C')

        # Badge bottom-right
        bw = 36; bh = 8
        bx = x + card_w - bw - 6; by = y + card_h - bh - 6
        pdf.set_fill_color(*badge_bg)
        pdf.rounded_rect(bx, by, bw, bh, 2, 'F')
        pdf.set_xy(bx, by + 1)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_text_color(*badge_tc)
        pdf.cell(bw, bh, badge_txt, 0, 0, 'C')

        # Avanzar columna/fila
        col += 1
        x += card_w + gap
        if col == 3:
            col = 0
            x = left
            y += card_h + 8
            # Si nos acercamos al footer, nueva página
            if y + card_h + 20 > 270:
                pdf.add_page()
                y = top



def _resumen_ejecutivo_fpdf2(pdf, metricas: Dict[str, Any], año: int, analisis_texto: str) -> None:
    """Resumen Ejecutivo profesional - layout con header navy, tarjetas 3D y footer."""
    # ── Paleta ─────────────────────────────────────────────────────────────
    C_NAVY    = (  0,  38,  97)
    C_PRIMARY = (  0,  61, 130)
    C_ACCENT  = (  0, 102, 204)
    C_GOLD    = (215, 160,  30)
    C_TEAL    = (  0, 140, 130)
    C_WHITE   = (255, 255, 255)
    C_BG      = (246, 248, 252)
    C_CARD    = (255, 255, 255)
    C_SHADOW  = (195, 208, 228)
    C_DARK    = ( 33,  37,  41)
    C_GRAY    = (118, 128, 143)
    C_GREEN   = ( 34, 154,  82)
    C_ORANGE  = (245, 130,   0)
    C_RED     = (210,  40,  55)

    # ── Métricas ───────────────────────────────────────────────────────────
    cumplimiento     = metricas.get('cumplimiento_promedio', 0)
    total_ind        = metricas.get('total_indicadores', 0)
    cumplidos_ind    = metricas.get('indicadores_cumplidos', 0)
    en_progreso_ind  = metricas.get('en_progreso', 0)
    no_cumplidos_ind = metricas.get('no_cumplidos', 0)
    pct_cum  = (cumplidos_ind  / total_ind * 100) if total_ind > 0 else 0
    pct_prog = (en_progreso_ind / total_ind * 100) if total_ind > 0 else 0
    pct_no   = (no_cumplidos_ind / total_ind * 100) if total_ind > 0 else 0

    # ── Fondo de página ────────────────────────────────────────────────────
    pdf.set_fill_color(*C_BG)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_line_width(0.2)

    # ── Header band navy ───────────────────────────────────────────────────
    BAND_H = 43
    pdf.set_fill_color(*C_NAVY)
    pdf.rect(0, 0, 210, BAND_H, 'F')

    pdf.set_xy(10, 8)
    pdf.set_font('Helvetica', '', 6.5)
    pdf.set_text_color(155, 192, 235)
    pdf.cell(190, 4, 'INFORME ESTRATEGICO  -  POLI', 0, 0)

    pdf.set_xy(10, 13)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(*C_WHITE)
    pdf.cell(150, 10, 'Resumen Ejecutivo', 0, 1)

    # Línea dorada bajo el título
    pdf.set_fill_color(*C_GOLD)
    pdf.rect(10, 25, 22, 1.3, 'F')

    pdf.set_xy(10, 28)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(135, 182, 235)
    pdf.cell(190, 5, 'Plan de Desarrollo Institucional  -  Evaluacion de Indicadores', 0, 0)

    # Barras proporcionales (verde/naranja/rojo) en parte inferior del header
    if total_ind > 0:
        wg = (cumplidos_ind  / total_ind) * 210
        wo = (en_progreso_ind / total_ind) * 210
        wr = (no_cumplidos_ind / total_ind) * 210
    else:
        wg = wo = wr = 0
    pdf.set_fill_color(*C_GREEN)
    pdf.rect(0, BAND_H - 4, wg, 4, 'F')
    pdf.set_fill_color(*C_ORANGE)
    pdf.rect(wg, BAND_H - 4, wo, 4, 'F')
    if wr > 0:
        pdf.set_fill_color(*C_RED)
        pdf.rect(wg + wo, BAND_H - 4, wr, 4, 'F')

    # ── Sección KPI ────────────────────────────────────────────────────────
    Y_SEC = BAND_H + 8
    pdf.set_xy(10, Y_SEC)
    pdf.set_font('Helvetica', 'B', 6.5)
    pdf.set_text_color(*C_ACCENT)
    pdf.cell(0, 4, 'INDICADORES CLAVE DE DESEMPENO', 0, 1)
    pdf.set_draw_color(205, 218, 235)
    pdf.set_line_width(0.3)
    pdf.line(10, Y_SEC + 5.5, 200, Y_SEC + 5.5)
    pdf.set_line_width(0.2)

    # ── Cards ──────────────────────────────────────────────────────────────
    Y_CARDS = Y_SEC + 9

    # ── Tarjeta izquierda grande (Cumplimiento) ────────────────────────────
    LW = 68; LH = 65; LX = 10; LY = Y_CARDS
    pdf.set_fill_color(*C_SHADOW)
    pdf.rounded_rect(LX+2, LY+2, LW, LH, 3, 'F')
    pdf.set_fill_color(*C_NAVY)
    pdf.rounded_rect(LX, LY, LW, LH, 3, 'F')

    pdf.set_xy(LX, LY + 8)
    pdf.set_font('Helvetica', 'B', 6)
    pdf.set_text_color(155, 192, 235)
    pdf.cell(LW, 4, 'TASA GLOBAL', 0, 0, 'C')

    cum_str = f'{cumplimiento:.0f}%' if cumplimiento >= 10 else f'{cumplimiento:.1f}%'
    pdf.set_xy(LX, LY + 14)
    pdf.set_font('Helvetica', 'B', 30 if len(cum_str) <= 4 else 24)
    pdf.set_text_color(*C_GOLD)
    pdf.cell(LW, 18, cum_str, 0, 0, 'C')

    pdf.set_xy(LX, LY + 34)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*C_WHITE)
    pdf.cell(LW, 5, 'Cumplimiento', 0, 0, 'C')

    # Badge de estado
    if cumplimiento >= 100:
        badge_txt = 'META SUPERADA';     badge_c = C_TEAL
    elif cumplimiento >= 80:
        badge_txt = 'EN PROGRESO';       badge_c = C_ORANGE
    else:
        badge_txt = 'REQUIERE ATENCION'; badge_c = C_RED
    bw = 44; bh = 7; bx_b = LX + (LW - bw) / 2; by_b = LY + 50
    pdf.set_draw_color(*badge_c)
    pdf.set_line_width(0.5)
    pdf.rounded_rect(bx_b, by_b, bw, bh, 2, 'D')
    pdf.set_line_width(0.2)
    pdf.set_xy(bx_b, by_b)
    pdf.set_font('Helvetica', 'B', 6)
    pdf.set_text_color(*badge_c)
    pdf.cell(bw, bh, badge_txt, 0, 0, 'C')

    # ── Cuatro tarjetas 2x2 a la derecha ──────────────────────────────────
    RX0 = LX + LW + 4
    RW  = (200 - RX0 - 3) / 2
    RH  = (LH - 3) / 2

    right_cards = [
        (C_GREEN,  str(cumplidos_ind),    'Cumplidos',            f'{pct_cum:.1f}%',  'check'),
        (C_ORANGE, str(en_progreso_ind),  'En Progreso',          f'{pct_prog:.1f}%', 'circle'),
        (C_RED,    str(no_cumplidos_ind), 'No Cumplidos',         f'{pct_no:.0f}%',   'x'),
        (C_DARK,   str(total_ind),        'Total de Indicadores', '100%',             'lines'),
    ]

    for i, (color, valor, label, badge_pct, icon_type) in enumerate(right_cards):
        col = i % 2; row = i // 2
        rx = RX0 + col * (RW + 3)
        ry = LY  + row * (RH + 3)
        # Sombra y tarjeta blanca
        pdf.set_fill_color(*C_SHADOW)
        pdf.rounded_rect(rx+2, ry+2, RW, RH, 3, 'F')
        pdf.set_fill_color(*C_CARD)
        pdf.rounded_rect(rx, ry, RW, RH, 3, 'F')

        # Icono (centrado verticalmente en la izquierda)
        ix = rx + 8; iy = ry + RH / 2; isz = 5.5
        if icon_type == 'check':
            pdf.set_fill_color(*color)
            pdf.rounded_rect(ix - isz/2, iy - isz/2, isz, isz, 1, 'F')
            pdf.set_draw_color(255, 255, 255)
            pdf.set_line_width(0.7)
            pdf.line(ix-1.8, iy+0.1, ix-0.4, iy+1.8)
            pdf.line(ix-0.4, iy+1.8, ix+2.2, iy-1.8)
            pdf.set_line_width(0.2)
        elif icon_type == 'circle':
            pdf.set_fill_color(*color)
            pdf.ellipse(ix-isz/2, iy-isz/2, isz, isz, 'F')
            pdf.set_fill_color(*C_CARD)
            pdf.rect(ix, iy-isz/2-0.5, isz/2+0.5, isz+1, 'F')
        elif icon_type == 'x':
            pdf.set_fill_color(*color)
            pdf.rounded_rect(ix-isz/2, iy-isz/2, isz, isz, 1, 'F')
            pdf.set_draw_color(255, 255, 255)
            pdf.set_line_width(0.8)
            pdf.line(ix-2, iy-2, ix+2, iy+2)
            pdf.line(ix-2, iy+2, ix+2, iy-2)
            pdf.set_line_width(0.2)
        else:  # lines
            pdf.set_fill_color(228, 234, 248)
            pdf.rounded_rect(ix-isz/2, iy-isz/2, isz, isz, 1, 'F')
            pdf.set_draw_color(80, 95, 120)
            pdf.set_line_width(0.55)
            for dy in [-1.5, 0, 1.5]:
                pdf.line(ix-2, iy+dy, ix+2, iy+dy)
            pdf.set_line_width(0.2)

        # Número grande
        nx = rx + 17; ny = ry + 4
        pdf.set_xy(nx, ny)
        fsz = 22 if len(valor) <= 3 else 17
        pdf.set_font('Helvetica', 'B', fsz)
        pdf.set_text_color(*color)
        pdf.cell(RW - 27, 14, valor, 0, 0, 'L')

        # Etiqueta
        pdf.set_xy(nx, ny + 15)
        pdf.set_font('Helvetica', '', 6.5)
        pdf.set_text_color(*C_GRAY)
        pdf.cell(RW - 27, 4, label, 0, 0, 'L')

        # Badge de porcentaje (esquina superior derecha)
        if color == C_GREEN:
            bg_b2 = (220, 245, 225); tc_b2 = C_GREEN
        elif color == C_ORANGE:
            bg_b2 = (255, 240, 215); tc_b2 = C_ORANGE
        elif color == C_RED:
            bg_b2 = (255, 225, 225); tc_b2 = C_RED
        else:
            bg_b2 = (218, 228, 250); tc_b2 = C_PRIMARY
        bw2 = 17; bh2 = 6; bx2 = rx + RW - bw2 - 2; by2 = ry + 3
        pdf.set_fill_color(*bg_b2)
        pdf.rounded_rect(bx2, by2, bw2, bh2, 1.5, 'F')
        pdf.set_xy(bx2, by2)
        pdf.set_font('Helvetica', 'B', 6.5)
        pdf.set_text_color(*tc_b2)
        pdf.cell(bw2, bh2, badge_pct, 0, 0, 'C')

    # ── Distribución de Indicadores ────────────────────────────────────────
    Y_DIST = Y_CARDS + LH + 9
    BOX_H  = 36
    pdf.set_fill_color(*C_SHADOW)
    pdf.rounded_rect(12, Y_DIST+2, 190, BOX_H, 3, 'F')
    pdf.set_fill_color(251, 252, 255)
    pdf.rounded_rect(10, Y_DIST, 190, BOX_H, 3, 'F')

    pdf.set_xy(14, Y_DIST + 5)
    pdf.set_font('Helvetica', 'B', 6.5)
    pdf.set_text_color(*C_ACCENT)
    pdf.cell(0, 4, 'DISTRIBUCION DE INDICADORES', 0, 1)

    y_bar = Y_DIST + 13
    bar_x = 14; bar_w = 182; bar_h = 6
    pdf.set_fill_color(208, 218, 235)
    pdf.rounded_rect(bar_x, y_bar, bar_w, bar_h, 1.5, 'F')
    if total_ind > 0:
        wg2 = (cumplidos_ind  / total_ind) * bar_w
        wo2 = (en_progreso_ind / total_ind) * bar_w
        wr2 = (no_cumplidos_ind / total_ind) * bar_w
        if wg2 > 0:
            pdf.set_fill_color(*C_GREEN)
            pdf.rect(bar_x, y_bar, wg2, bar_h, 'F')
        if wo2 > 0:
            pdf.set_fill_color(*C_ORANGE)
            pdf.rect(bar_x + wg2, y_bar, wo2, bar_h, 'F')
        if wr2 > 0:
            pdf.set_fill_color(*C_RED)
            pdf.rect(bar_x + wg2 + wo2, y_bar, wr2, bar_h, 'F')

    y_leg = y_bar + bar_h + 5
    for dot_x, dot_color, txt in [
        ( 14, C_GREEN,  f'Cumplidos  -  {cumplidos_ind}'),
        ( 70, C_ORANGE, f'En Progreso  -  {en_progreso_ind}'),
        (126, C_RED,    f'No Cumplidos  -  {no_cumplidos_ind}'),
    ]:
        pdf.set_fill_color(*dot_color)
        pdf.rect(dot_x, y_leg + 1.5, 3.5, 3, 'F')
        pdf.set_xy(dot_x + 5, y_leg)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*C_GRAY)
        pdf.cell(52, 5, txt, 0, 0)

    # ── Análisis Ejecutivo (opcional) ──────────────────────────────────────
    if analisis_texto:
        Y_ANA = Y_DIST + BOX_H + 8
        ana_h = min(68, 270 - Y_ANA)
        if ana_h > 20:
            pdf.set_fill_color(*C_SHADOW)
            pdf.rounded_rect(12, Y_ANA+2, 190, ana_h, 3, 'F')
            pdf.set_fill_color(228, 240, 255)
            pdf.rounded_rect(10, Y_ANA, 190, ana_h, 3, 'F')
            pdf.set_fill_color(*C_PRIMARY)
            pdf.rect(10, Y_ANA, 3, ana_h, 'F')
            pdf.set_xy(16, Y_ANA + 5)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(*C_PRIMARY)
            pdf.cell(0, 5, 'Analisis Ejecutivo', 0, 1)
            pdf.set_x(16)
            pdf.set_font('Helvetica', 'I', 7)
            pdf.set_text_color(*C_ACCENT)
            pdf.cell(0, 4, f'RESUMEN EJECUTIVO PDI 2021-2025 (Ano {año})', 0, 1)
            pdf.ln(1)
            pdf.set_x(16)
            pdf.set_font('Helvetica', '', 7.5)
            pdf.set_text_color(*C_DARK)
            max_c = max(150, int((ana_h - 22) * 33))
            texto = limpiar_texto_pdf(analisis_texto.replace('**', '').replace('*', ''))[:max_c]
            pdf.multi_cell(181, 4.5, texto, align='J')

    # ── Footer ─────────────────────────────────────────────────────────────
    Y_FOOT = 278
    pdf.set_fill_color(241, 244, 250)
    pdf.rect(0, Y_FOOT, 210, 19, 'F')
    pdf.set_draw_color(208, 218, 235)
    pdf.set_line_width(0.3)
    pdf.line(0, Y_FOOT, 210, Y_FOOT)
    pdf.set_line_width(0.2)

    for lx, lcolor, txt in [
        ( 14, C_GREEN,  '>= 100%  Meta Cumplida'),
        ( 76, C_ORANGE, '80-99%  En Progreso'),
        (138, C_RED,    '< 80%  Requiere Atencion'),
    ]:
        pdf.set_draw_color(*lcolor)
        pdf.set_line_width(1.3)
        pdf.line(lx, Y_FOOT + 10, lx + 9, Y_FOOT + 10)
        pdf.set_line_width(0.2)
        pdf.set_xy(lx + 11, Y_FOOT + 7)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*C_GRAY)
        pdf.cell(55, 5, txt, 0, 0)

    pdf.set_xy(150, Y_FOOT + 7)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*C_GRAY)
    pdf.cell(50, 5, f'PDI  .  {año}', 0, 0, 'R')


def generar_pdf_fpdf(metricas: Dict[str, Any], df_lineas: pd.DataFrame,
                     df_indicadores: pd.DataFrame, analisis_texto: str = "", año: int = 2025,
                     df_cascada: pd.DataFrame = None) -> bytes:
    """
    Genera PDF usando fpdf2 (ligero y compatible con Streamlit Cloud).

    Args:
        metricas: Métricas generales del PDI
        df_lineas: DataFrame con cumplimiento por línea
        df_indicadores: DataFrame con detalle de indicadores
        analisis_texto: Análisis IA (opcional)
        año: Año del informe
        df_cascada: DataFrame con estructura jerárquica (opcional)
    """
    from fpdf import FPDF

    class PDFInforme(FPDF):
        def __init__(self):
            super().__init__()
            self.set_auto_page_break(auto=True, margin=20)

        def header(self):
            if self.page_no() > 1:
                self.set_font('Helvetica', 'I', 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, 'Informe Estrategico POLI - Plan de Desarrollo Institucional', 0, 0, 'C')
                self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    pdf = PDFInforme()

    # ===== PORTADA CON IMAGEN =====
    pdf.add_page()

    portada_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Portada.png')
    if os.path.exists(portada_path):
        pdf.image(portada_path, x=0, y=0, w=210, h=297)
    else:
        # Fallback: fondo azul si no se encuentra la imagen
        pdf.set_fill_color(0, 61, 130)
        pdf.rect(0, 0, 210, 297, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 28)
        pdf.set_y(120)
        pdf.cell(0, 15, 'INFORME ESTRATEGICO', 0, 1, 'C')

    # ===== RESUMEN EJECUTIVO =====
    pdf.add_page()
    _resumen_ejecutivo_fpdf2(pdf, metricas, año, analisis_texto)

    # ===== LINEAS ESTRATEGICAS (una página visual por línea) =====
    # Generar hoja resumen tipo tarjetas si hay `df_lineas`
    try:
        if df_lineas is not None and not df_lineas.empty:
            _generar_hoja_lineas_fpdf(pdf, df_lineas, metricas, año)
    except Exception:
        pass

    if df_cascada is not None and not df_cascada.empty:
        _generar_paginas_lineas(pdf, df_cascada, año)

    # ===== INDICADORES =====
    if df_indicadores is not None and not df_indicadores.empty:
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.set_text_color(0, 61, 130)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, 'Detalle de Indicadores', 0, 1, 'L')
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
    if df_indicadores is not None and not df_indicadores.empty:
        # Header
        pdf.set_fill_color(0, 61, 130)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(80, 7, 'Indicador', 1, 0, 'L', True)
        pdf.cell(25, 7, 'Meta', 1, 0, 'C', True)
        pdf.cell(25, 7, 'Ejecucion', 1, 0, 'C', True)
        pdf.cell(25, 7, 'Cumplimiento', 1, 0, 'C', True)
        pdf.cell(25, 7, 'Estado', 1, 1, 'C', True)

        pdf.set_font('Helvetica', '', 7)
        for idx, (_, row) in enumerate(df_indicadores.head(50).iterrows()):
            if idx % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(248, 249, 250)

            indicador = limpiar_texto_pdf(str(row.get('Indicador', 'N/D')))[:45]
            meta = row.get('Meta', 'N/D')
            ejec = row.get('Ejecución', row.get('Ejecucion', 'N/D'))
            cumpl = row.get('Cumplimiento', 0)

            meta_str = f"{meta:.2f}" if isinstance(meta, (int, float)) and pd.notna(meta) else limpiar_texto_pdf(str(meta))
            ejec_str = f"{ejec:.2f}" if isinstance(ejec, (int, float)) and pd.notna(ejec) else limpiar_texto_pdf(str(ejec))

            if pd.isna(cumpl):
                cumpl_str = "N/D"
                estado = "N/D"
            else:
                cumpl_str = f"{cumpl:.1f}%"
                estado = "Cumple" if cumpl >= 100 else "!" if cumpl >= 80 else "X"

            pdf.set_text_color(33, 37, 41)
            pdf.cell(80, 6, indicador, 1, 0, 'L', True)
            pdf.cell(25, 6, meta_str[:10], 1, 0, 'C', True)
            pdf.cell(25, 6, ejec_str[:10], 1, 0, 'C', True)
            pdf.cell(25, 6, cumpl_str, 1, 0, 'C', True)

            if not pd.isna(cumpl):
                if cumpl >= 100:
                    pdf.set_text_color(40, 167, 69)
                elif cumpl >= 80:
                    pdf.set_text_color(255, 193, 7)
                else:
                    pdf.set_text_color(220, 53, 69)
            pdf.cell(25, 6, estado, 1, 1, 'C', True)

            if pdf.get_y() > 270:
                pdf.add_page()
                pdf.set_fill_color(0, 61, 130)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Helvetica', 'B', 7)
                pdf.cell(80, 7, 'Indicador', 1, 0, 'L', True)
                pdf.cell(25, 7, 'Meta', 1, 0, 'C', True)
                pdf.cell(25, 7, 'Ejecucion', 1, 0, 'C', True)
                pdf.cell(25, 7, 'Cumplimiento', 1, 0, 'C', True)
                pdf.cell(25, 7, 'Estado', 1, 1, 'C', True)
                pdf.set_font('Helvetica', '', 7)

    # Footer final
    pdf.ln(15)
    pdf.set_text_color(0, 61, 130)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 5, 'POLITECNICO GRANCOLOMBIANO', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f'Dashboard Estrategico POLI - PDI 2021-{año}', 0, 1, 'C')

    # pdf.output() devuelve bytearray, convertir a bytes para Streamlit
    return bytes(pdf.output())


def generar_pdf(html_content: str) -> bytes:
    """
    Convierte HTML a PDF. Intenta usar xhtml2pdf primero.

    Args:
        html_content: Contenido HTML del informe

    Returns:
        Bytes del archivo PDF
    """
    try:
        from xhtml2pdf import pisa

        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_content,
            dest=pdf_buffer,
            encoding='utf-8'
        )

        if pisa_status.err:
            raise Exception(f"Error en xhtml2pdf: {pisa_status.err}")

        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    except ImportError:
        raise ImportError(
            "Se requiere instalar xhtml2pdf o fpdf2 para generar PDFs.\n"
            "Ejecute: pip install fpdf2"
        )
    except Exception as e:
        raise Exception(f"Error generando PDF: {str(e)}")


def exportar_informe_pdf(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    figuras: List[tuple] = None,
    año: int = 2025,
    df_cascada: pd.DataFrame = None
) -> bytes:
    """
    Función principal para exportar el informe completo a PDF.
    Usa fpdf2 como opción principal (más compatible con Streamlit Cloud).

    Args:
        metricas: Diccionario con métricas generales
        df_lineas: DataFrame con cumplimiento por línea
        df_indicadores: DataFrame con detalle de indicadores
        analisis_texto: Texto del análisis IA (opcional)
        figuras: Lista de tuplas (titulo, figura_plotly, descripcion) (opcional)
        año: Año del informe
        df_cascada: DataFrame con estructura jerárquica del PDI (opcional)

    Returns:
        Bytes del archivo PDF
    """
    # Preferir la ruta HTML->PDF (xhtml2pdf) para consistencia visual en Streamlit Cloud.
    try:
        html = generar_informe_html(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_indicadores,
            analisis_texto=analisis_texto,
            figuras=figuras,
            año=año
        )
        return generar_pdf(html)
    except Exception:
        # Fallback a fpdf2 si xhtml2pdf no está disponible o falla
        return generar_pdf_fpdf(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_indicadores,
            analisis_texto=analisis_texto,
            año=año,
            df_cascada=df_cascada
        )


# Función auxiliar para previsualizar HTML (útil para debugging)
def previsualizar_html(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    año: int = 2025
) -> str:
    """
    Genera solo el HTML para previsualización sin convertir a PDF.
    """
    return generar_informe_html(
        metricas=metricas,
        df_lineas=df_lineas,
        df_indicadores=df_indicadores,
        analisis_texto=analisis_texto,
        figuras=None,
        año=año
    )
