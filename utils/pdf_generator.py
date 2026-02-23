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


def generar_seccion_jerarquica_fpdf(pdf, df_cascada: pd.DataFrame) -> None:
    """
    Genera sección jerárquica en PDF con estructura en bucle:
    Línea -> Objetivo 1 -> Meta 1 -> Indicadores -> Meta 2 -> Indicadores
         -> Objetivo 2 -> Meta 3 -> Indicadores -> etc.

    Incluye barras visuales de cumplimiento para cada nivel.

    Args:
        pdf: Instancia de PDFInforme
        df_cascada: DataFrame con estructura jerárquica de cumplimiento
    """
    if df_cascada is None or df_cascada.empty:
        return

    pdf.add_page()
    pdf.set_text_color(0, 61, 130)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Estructura Jerarquica del PDI', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    linea_actual = None
    objetivo_actual = None

    def dibujar_barra_progreso(x, y, ancho, cumplimiento):
        """Dibuja una barra de progreso visual"""
        # Borde de la barra
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(x, y, ancho, 3, 'D')

        # Relleno según cumplimiento
        if cumplimiento > 0:
            ancho_relleno = (cumplimiento / 100) * ancho
            ancho_relleno = min(ancho_relleno, ancho)  # No exceder el ancho total

            if cumplimiento >= 100:
                pdf.set_fill_color(40, 167, 69)  # Verde
            elif cumplimiento >= 80:
                pdf.set_fill_color(255, 193, 7)  # Amarillo
            else:
                pdf.set_fill_color(220, 53, 69)  # Rojo

            pdf.rect(x, y, ancho_relleno, 3, 'F')

    for _, row in df_cascada.iterrows():
        nivel = int(row['Nivel'])
        cumpl = row.get('Cumplimiento', 0)

        # Determinar color según cumplimiento
        if cumpl >= 100:
            color = (40, 167, 69)  # Verde
        elif cumpl >= 80:
            color = (255, 193, 7)  # Amarillo
        else:
            color = (220, 53, 69)  # Rojo

        # Nivel 1: Línea Estratégica
        if nivel == 1:
            linea_actual = limpiar_texto_pdf(str(row['Linea']))

            # Nueva página para cada línea (excepto la primera)
            if pdf.get_y() > 50 and linea_actual:
                pdf.add_page()

            # Título de la línea con fondo
            pdf.set_fill_color(0, 61, 130)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 13)
            pdf.cell(0, 10, f' {linea_actual[:75]}', 0, 1, 'L', True)

            # Barra de progreso de la línea
            y_pos = pdf.get_y() + 1
            dibujar_barra_progreso(10, y_pos, 150, cumpl)

            pdf.set_text_color(*color)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_xy(165, y_pos - 1)
            pdf.cell(35, 5, f'{cumpl:.1f}%', 0, 1, 'R')
            pdf.ln(5)

        # Nivel 2: Objetivo
        elif nivel == 2:
            objetivo_actual = limpiar_texto_pdf(str(row['Objetivo']))

            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(0, 86, 179)
            pdf.set_x(15)
            pdf.cell(5, 6, 'O', 0, 0, 'L')
            pdf.cell(135, 6, objetivo_actual[:70], 0, 0, 'L')

            # Barra de progreso del objetivo
            y_pos = pdf.get_y() + 1
            pdf.ln(6)
            dibujar_barra_progreso(20, y_pos + 5, 130, cumpl)

            pdf.set_text_color(*color)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_xy(155, y_pos)
            pdf.cell(35, 6, f'{cumpl:.1f}%', 0, 1, 'R')
            pdf.ln(2)

        # Nivel 3: Meta PDI
        elif nivel == 3:
            meta_actual = limpiar_texto_pdf(str(row['Meta_PDI']))
            if meta_actual and meta_actual != 'N/D':
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(80, 80, 80)
                pdf.set_x(25)
                pdf.cell(3, 5, '-', 0, 0, 'L')
                pdf.cell(125, 5, f'Meta PDI: {meta_actual[:65]}', 0, 0, 'L')

                pdf.set_text_color(*color)
                pdf.set_font('Helvetica', 'B', 8)
                pdf.cell(30, 5, f'{cumpl:.1f}%', 0, 1, 'R')
                pdf.ln(1)

        # Nivel 4: Indicador
        elif nivel == 4:
            indicador = limpiar_texto_pdf(str(row['Indicador']))

            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(35)
            pdf.cell(3, 4, '>', 0, 0, 'L')
            pdf.cell(110, 4, indicador[:62], 0, 0, 'L')

            # Mini barra de progreso para indicador
            y_pos = pdf.get_y()
            dibujar_barra_progreso(150, y_pos + 0.5, 30, cumpl)

            pdf.set_text_color(*color)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.set_xy(183, y_pos)
            pdf.cell(15, 4, f'{cumpl:.0f}%', 0, 1, 'R')

        # Verificar si necesita nueva página
        if pdf.get_y() > 275:
            pdf.add_page()
            # Re-imprimir encabezado de línea si estamos en medio de una
            if linea_actual:
                pdf.set_font('Helvetica', 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f'(continuacion: {linea_actual[:70]})', 0, 1, 'L')
                pdf.ln(3)


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

    # ===== RESUMEN EJECUTIVO - DISEÑO LIGHT =====
    pdf.add_page()

    # Paleta light
    C_BG       = (255, 255, 255)
    C_CARD     = (243, 246, 252)
    C_PRIMARY  = (0, 61, 130)
    C_ACCENT   = (0, 86, 179)
    C_DARK     = (33, 37, 41)
    C_GRAY     = (108, 117, 125)
    C_LINE     = (220, 225, 235)
    C_PROG_BG  = (220, 225, 235)
    C_GREEN    = (40, 167, 69)
    C_ORANGE   = (255, 152, 0)
    C_RED      = (220, 53, 69)

    # Fondo blanco de página (cubre el header automático)
    pdf.set_fill_color(*C_BG)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_line_width(0.2)

    # ---- HEADER ----
    pdf.set_xy(10, 12)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(100, 10, 'Resumen Ejecutivo', 0, 0)

    pdf.set_xy(110, 12)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(*C_GRAY)
    pdf.cell(90, 5, 'PLAN DE DESARROLLO INSTITUCIONAL', 0, 1, 'R')

    pdf.set_xy(110, 18)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(90, 5, f'Periodo de Evaluacion {año}', 0, 1, 'R')

    pdf.set_xy(10, 24)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*C_ACCENT)
    pdf.cell(100, 5, 'INFORME ESTRATEGICO POLI', 0, 1)

    # Separador
    pdf.set_draw_color(*C_LINE)
    pdf.set_line_width(0.4)
    pdf.line(10, 32, 200, 32)
    pdf.set_line_width(0.2)

    # ---- SECCIÓN KPIs ----
    pdf.set_xy(10, 37)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(0, 5, 'INDICADORES CLAVE DE DESEMPENO', 0, 1)

    pdf.set_draw_color(*C_ACCENT)
    pdf.set_line_width(0.6)
    pdf.line(10, 43, 200, 43)
    pdf.set_line_width(0.2)

    cumplimiento   = metricas.get('cumplimiento_promedio', 0)
    total_ind      = metricas.get('total_indicadores', 0)
    cumplidos_ind  = metricas.get('indicadores_cumplidos', 0)
    en_progreso_ind = metricas.get('en_progreso', 0)
    no_cumplidos_ind = metricas.get('no_cumplidos', 0)

    kpis_data = [
        ('Cumplimiento',  f'{cumplimiento:.1f}%',    C_ACCENT,  'C'),
        ('Cumplidos',     str(cumplidos_ind),          C_GREEN,   'OK'),
        ('En Progreso',   str(en_progreso_ind),        C_ORANGE,  '~'),
        ('No Cumplidos',  str(no_cumplidos_ind),       C_RED,     'X'),
        ('Total',         str(total_ind),              C_PRIMARY, '='),
    ]

    y_cards  = 47
    card_w   = 36
    card_h   = 40
    card_gap = 2
    x0       = 10

    for i, (label, valor, color, icon) in enumerate(kpis_data):
        x = x0 + i * (card_w + card_gap)

        # Fondo de tarjeta
        pdf.set_fill_color(*C_CARD)
        pdf.rect(x, y_cards, card_w, card_h, 'F')

        # Borde superior de color
        pdf.set_fill_color(*color)
        pdf.rect(x, y_cards, card_w, 2, 'F')

        # Icono pequeño
        pdf.set_xy(x, y_cards + 4)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*C_GRAY)
        pdf.cell(card_w, 4, icon, 0, 0, 'C')

        # Valor principal
        font_size = 17 if len(valor) <= 5 else 13
        pdf.set_xy(x, y_cards + 11)
        pdf.set_font('Helvetica', 'B', font_size)
        pdf.set_text_color(*color)
        pdf.cell(card_w, 10, valor, 0, 0, 'C')

        # Etiqueta
        pdf.set_xy(x, y_cards + 26)
        pdf.set_font('Helvetica', 'B', 5.5)
        pdf.set_text_color(*C_GRAY)
        pdf.cell(card_w, 4, label.upper(), 0, 0, 'C')

    # ---- PROGRESO GLOBAL ----
    y_prog = y_cards + card_h + 8

    pdf.set_xy(10, y_prog)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(0, 5, 'PROGRESO GLOBAL DEL PLAN', 0, 1)

    pdf.set_draw_color(*C_ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(10, y_prog + 6, 200, y_prog + 6)
    pdf.set_line_width(0.2)

    y_bar  = y_prog + 12
    bar_x  = 10
    bar_w  = 155
    bar_h  = 7

    # Fondo barra
    pdf.set_fill_color(*C_PROG_BG)
    pdf.rect(bar_x, y_bar, bar_w, bar_h, 'F')

    # Segmentos
    if total_ind > 0:
        w_cum  = (cumplidos_ind / total_ind) * bar_w
        w_prog = (en_progreso_ind / total_ind) * bar_w
        if w_cum > 0:
            pdf.set_fill_color(*C_GREEN)
            pdf.rect(bar_x, y_bar, w_cum, bar_h, 'F')
        if w_prog > 0:
            pdf.set_fill_color(*C_ORANGE)
            pdf.rect(bar_x + w_cum, y_bar, w_prog, bar_h, 'F')

    # Porcentaje a la derecha
    pct_comp = (cumplidos_ind / total_ind * 100) if total_ind > 0 else 0
    pdf.set_xy(bar_x + bar_w + 3, y_bar - 3)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(32, 7, f'{pct_comp:.1f}%', 0, 1, 'R')

    pdf.set_xy(bar_x + bar_w + 3, y_bar + 5)
    pdf.set_font('Helvetica', '', 6)
    pdf.set_text_color(*C_GRAY)
    pdf.cell(32, 4, 'Indicadores completados', 0, 0, 'R')

    # Leyenda de la barra
    y_leg = y_bar + bar_h + 5

    pdf.set_fill_color(*C_GREEN)
    pdf.rect(10, y_leg + 1.5, 3, 3, 'F')
    pdf.set_xy(15, y_leg)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(*C_GRAY)
    pdf.cell(45, 5, f'Cumplidos  {cumplidos_ind}', 0, 0)

    pdf.set_fill_color(*C_ORANGE)
    pdf.rect(65, y_leg + 1.5, 3, 3, 'F')
    pdf.set_xy(70, y_leg)
    pdf.cell(45, 5, f'En Progreso  {en_progreso_ind}', 0, 0)

    pdf.set_fill_color(*C_RED)
    pdf.rect(120, y_leg + 1.5, 3, 3, 'F')
    pdf.set_xy(125, y_leg)
    pdf.cell(50, 5, f'No Cumplidos  {no_cumplidos_ind}', 0, 0)

    # ---- ANÁLISIS EJECUTIVO ----
    if analisis_texto:
        y_ana = y_leg + 12
        pdf.set_fill_color(227, 242, 253)
        pdf.rect(10, y_ana, 190, 50, 'F')
        pdf.set_fill_color(*C_ACCENT)
        pdf.rect(10, y_ana, 2.5, 50, 'F')

        pdf.set_xy(15, y_ana + 5)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*C_PRIMARY)
        pdf.cell(0, 5, 'Analisis Ejecutivo', 0, 1)

        pdf.set_x(15)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*C_DARK)
        texto_limpio = limpiar_texto_pdf(analisis_texto.replace('**', '').replace('*', ''))[:350]
        pdf.multi_cell(182, 5, texto_limpio)

    # ---- LEYENDA SEMÁFORO (pie de página) ----
    y_sem = 272
    pdf.set_fill_color(*C_CARD)
    pdf.rect(10, y_sem, 190, 12, 'F')

    pdf.set_fill_color(*C_GREEN)
    pdf.rect(13, y_sem + 4.5, 3, 3, 'F')
    pdf.set_xy(18, y_sem + 3)
    pdf.set_font('Helvetica', '', 6.5)
    pdf.set_text_color(*C_GRAY)
    pdf.cell(55, 6, '>= 100% Meta Cumplida', 0, 0)

    pdf.set_fill_color(*C_ORANGE)
    pdf.rect(78, y_sem + 4.5, 3, 3, 'F')
    pdf.set_xy(83, y_sem + 3)
    pdf.cell(55, 6, '80-99% En Progreso', 0, 0)

    pdf.set_fill_color(*C_RED)
    pdf.rect(143, y_sem + 4.5, 3, 3, 'F')
    pdf.set_xy(148, y_sem + 3)
    pdf.cell(52, 6, '< 80% Requiere Atencion', 0, 0)

    # ===== LINEAS ESTRATEGICAS =====
    pdf.add_page()
    pdf.set_text_color(0, 61, 130)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Cumplimiento por Linea Estrategica', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    if df_lineas is not None and not df_lineas.empty:
        # Header tabla
        pdf.set_fill_color(0, 61, 130)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(100, 8, 'Linea Estrategica', 1, 0, 'L', True)
        pdf.cell(30, 8, 'Indicadores', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Cumplimiento', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Estado', 1, 1, 'C', True)

        pdf.set_font('Helvetica', '', 8)
        for idx, (_, row) in enumerate(df_lineas.iterrows()):
            if idx % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(248, 249, 250)

            linea = limpiar_texto_pdf(str(row.get('Linea', 'N/D')))[:50]
            cumpl = row.get('Cumplimiento', 0)
            total_ind = row.get('Total_Indicadores', 0)

            if cumpl >= 100:
                estado = 'Cumplido'
                pdf.set_text_color(40, 167, 69)
            elif cumpl >= 80:
                estado = 'En Progreso'
                pdf.set_text_color(255, 193, 7)
            else:
                estado = 'Atencion'
                pdf.set_text_color(220, 53, 69)

            pdf.set_text_color(33, 37, 41)
            pdf.cell(100, 7, linea, 1, 0, 'L', True)
            pdf.cell(30, 7, str(total_ind), 1, 0, 'C', True)
            pdf.cell(30, 7, f"{cumpl:.1f}%", 1, 0, 'C', True)

            if cumpl >= 100:
                pdf.set_text_color(40, 167, 69)
            elif cumpl >= 80:
                pdf.set_text_color(255, 193, 7)
            else:
                pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, estado, 1, 1, 'C', True)

    # ===== ESTRUCTURA JERARQUICA =====
    # Generar sección con jerarquía Línea > Objetivo > Meta > Indicadores
    if df_cascada is not None and not df_cascada.empty:
        generar_seccion_jerarquica_fpdf(pdf, df_cascada)

    # ===== INDICADORES =====
    pdf.add_page()
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
    # Intentar con fpdf2 primero (más ligero y compatible)
    try:
        return generar_pdf_fpdf(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_indicadores,
            analisis_texto=analisis_texto,
            año=año,
            df_cascada=df_cascada
        )
    except ImportError:
        # Fallback a xhtml2pdf
        html = generar_informe_html(
            metricas=metricas,
            df_lineas=df_lineas,
            df_indicadores=df_indicadores,
            analisis_texto=analisis_texto,
            figuras=figuras,
            año=año
        )
        return generar_pdf(html)


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
