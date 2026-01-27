"""
Generador de Informes PDF - Dashboard Estratégico POLI
Estructura corporativa profesional con énfasis en azul institucional
Utiliza HTML/CSS + weasyprint para conversión a PDF
"""

import io
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

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
       PORTADA
    ============================================ */
    .portada {{
        text-align: center;
        padding: 60px 40px;
        background-color: {COLORES_PDF['primary']};
        color: white;
        margin: -2cm -1.5cm 0 -1.5cm;
        padding-top: 120px;
        padding-bottom: 120px;
    }}

    .portada-logo {{
        font-size: 60pt;
        margin-bottom: 30px;
    }}

    .portada-titulo {{
        font-size: 26pt;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    .portada-subtitulo {{
        font-size: 14pt;
        margin-bottom: 30px;
    }}

    .portada-linea {{
        width: 100px;
        height: 3px;
        background-color: white;
        margin: 20px auto;
    }}

    .portada-fecha {{
        font-size: 11pt;
        margin-top: 30px;
    }}

    .portada-periodo {{
        background-color: {COLORES_PDF['secondary']};
        padding: 12px 30px;
        font-size: 12pt;
        margin-top: 15px;
        display: inline-block;
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
    """Genera el HTML de la portada del informe."""
    return f"""
    <div class="portada">
        <div class="portada-logo">POLI</div>
        <div class="portada-titulo">{titulo}</div>
        <div class="portada-subtitulo">{subtitulo}</div>
        <div class="portada-linea">&nbsp;</div>
        <div class="portada-periodo">{periodo}</div>
        <div class="portada-fecha">Generado el {fecha}</div>
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
            badge = '<span class="badge badge-success">OK</span>'
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


def generar_pdf(html_content: str) -> bytes:
    """
    Convierte HTML a PDF usando xhtml2pdf (compatible con Windows).

    Args:
        html_content: Contenido HTML del informe

    Returns:
        Bytes del archivo PDF
    """
    # Usar xhtml2pdf como opción principal (puro Python, sin dependencias del sistema)
    try:
        from xhtml2pdf import pisa

        pdf_buffer = io.BytesIO()
        # Convertir HTML a PDF
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
        # Fallback: intentar con weasyprint (requiere librerías del sistema)
        try:
            from weasyprint import HTML

            pdf_buffer = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            return pdf_buffer.getvalue()

        except ImportError:
            raise ImportError(
                "Se requiere instalar xhtml2pdf para generar PDFs.\n"
                "Ejecute: pip install xhtml2pdf"
            )
        except Exception as e:
            raise ImportError(
                f"weasyprint requiere librerías del sistema no disponibles.\n"
                f"Instale xhtml2pdf en su lugar: pip install xhtml2pdf\n"
                f"Error: {str(e)}"
            )


def exportar_informe_pdf(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    figuras: List[tuple] = None,
    año: int = 2025
) -> bytes:
    """
    Función principal para exportar el informe completo a PDF.

    Args:
        metricas: Diccionario con métricas generales
        df_lineas: DataFrame con cumplimiento por línea
        df_indicadores: DataFrame con detalle de indicadores
        analisis_texto: Texto del análisis IA (opcional)
        figuras: Lista de tuplas (titulo, figura_plotly, descripcion) (opcional)
        año: Año del informe

    Returns:
        Bytes del archivo PDF
    """
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
