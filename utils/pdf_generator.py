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
    """
    return f"""
    @page {{
        size: A4;
        margin: 15mm 15mm 20mm 15mm;

        @top-center {{
            content: "Informe Estratégico POLI - Plan de Desarrollo Institucional";
            font-size: 9pt;
            color: {COLORES_PDF['gray']};
        }}

        @bottom-center {{
            content: "Página " counter(page) " de " counter(pages);
            font-size: 9pt;
            color: {COLORES_PDF['gray']};
        }}

        @bottom-right {{
            content: "Politécnico Grancolombiano";
            font-size: 8pt;
            color: {COLORES_PDF['primary']};
        }}
    }}

    @page :first {{
        margin-top: 0;
        @top-center {{ content: none; }}
    }}

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    body {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.5;
        color: {COLORES_PDF['dark']};
        background: {COLORES_PDF['white']};
    }}

    /* ============================================
       PORTADA
    ============================================ */
    .portada {{
        page-break-after: always;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: linear-gradient(180deg, {COLORES_PDF['primary']} 0%, {COLORES_PDF['secondary']} 100%);
        color: white;
        padding: 40px;
        margin: -15mm -15mm 0 -15mm;
    }}

    .portada-logo {{
        width: 120px;
        height: 120px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}

    .portada-logo span {{
        font-size: 48pt;
        color: {COLORES_PDF['primary']};
    }}

    .portada-titulo {{
        font-size: 28pt;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    .portada-subtitulo {{
        font-size: 16pt;
        opacity: 0.9;
        margin-bottom: 40px;
    }}

    .portada-linea {{
        width: 100px;
        height: 3px;
        background: white;
        margin: 30px auto;
    }}

    .portada-fecha {{
        font-size: 12pt;
        opacity: 0.8;
        margin-top: 40px;
    }}

    .portada-periodo {{
        background: rgba(255,255,255,0.2);
        padding: 15px 40px;
        border-radius: 30px;
        font-size: 14pt;
        margin-top: 20px;
    }}

    /* ============================================
       ENCABEZADOS DE SECCIÓN
    ============================================ */
    .seccion {{
        page-break-inside: avoid;
        margin-bottom: 25px;
    }}

    .seccion-header {{
        background: linear-gradient(90deg, {COLORES_PDF['primary']} 0%, {COLORES_PDF['secondary']} 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
    }}

    .seccion-header h2 {{
        font-size: 14pt;
        font-weight: 600;
        margin: 0;
    }}

    .seccion-contenido {{
        background: {COLORES_PDF['white']};
        border: 1px solid {COLORES_PDF['light_blue']};
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 20px;
    }}

    h1 {{
        color: {COLORES_PDF['primary']};
        font-size: 18pt;
        font-weight: bold;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid {COLORES_PDF['primary']};
    }}

    h2 {{
        color: {COLORES_PDF['primary']};
        font-size: 14pt;
        font-weight: 600;
        margin-bottom: 15px;
    }}

    h3 {{
        color: {COLORES_PDF['secondary']};
        font-size: 12pt;
        font-weight: 600;
        margin-bottom: 10px;
    }}

    /* ============================================
       KPIs / MÉTRICAS
    ============================================ */
    .kpis-container {{
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }}

    .kpi-card {{
        flex: 1;
        background: {COLORES_PDF['white']};
        border: 2px solid {COLORES_PDF['light_blue']};
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: {COLORES_PDF['primary']};
    }}

    .kpi-card.success::before {{ background: {COLORES_PDF['success']}; }}
    .kpi-card.warning::before {{ background: {COLORES_PDF['warning']}; }}
    .kpi-card.danger::before {{ background: {COLORES_PDF['danger']}; }}

    .kpi-valor {{
        font-size: 24pt;
        font-weight: bold;
        color: {COLORES_PDF['primary']};
        line-height: 1.2;
    }}

    .kpi-card.success .kpi-valor {{ color: {COLORES_PDF['success']}; }}
    .kpi-card.warning .kpi-valor {{ color: {COLORES_PDF['warning']}; }}
    .kpi-card.danger .kpi-valor {{ color: {COLORES_PDF['danger']}; }}

    .kpi-label {{
        font-size: 9pt;
        color: {COLORES_PDF['gray']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 5px;
    }}

    .kpi-delta {{
        font-size: 9pt;
        margin-top: 5px;
        padding: 2px 8px;
        border-radius: 10px;
        display: inline-block;
    }}

    .kpi-delta.positive {{
        background: {COLORES_PDF['success']};
        color: white;
    }}

    .kpi-delta.negative {{
        background: {COLORES_PDF['danger']};
        color: white;
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

    table thead {{
        background: {COLORES_PDF['primary']};
        color: white;
    }}

    table th {{
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 8pt;
        letter-spacing: 0.5px;
    }}

    table td {{
        padding: 10px 12px;
        border-bottom: 1px solid {COLORES_PDF['light_blue']};
    }}

    table tbody tr:nth-child(even) {{
        background: {COLORES_PDF['light']};
    }}

    table tbody tr:hover {{
        background: {COLORES_PDF['light_blue']};
    }}

    /* ============================================
       BADGES DE ESTADO
    ============================================ */
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 8pt;
        font-weight: 600;
        text-transform: uppercase;
    }}

    .badge-success {{
        background: {COLORES_PDF['success']};
        color: white;
    }}

    .badge-warning {{
        background: {COLORES_PDF['warning']};
        color: {COLORES_PDF['dark']};
    }}

    .badge-danger {{
        background: {COLORES_PDF['danger']};
        color: white;
    }}

    .badge-info {{
        background: {COLORES_PDF['accent']};
        color: white;
    }}

    /* ============================================
       GRÁFICOS
    ============================================ */
    .grafico-container {{
        text-align: center;
        margin: 20px 0;
        page-break-inside: avoid;
    }}

    .grafico-container img {{
        max-width: 100%;
        height: auto;
        border: 1px solid {COLORES_PDF['light_blue']};
        border-radius: 8px;
    }}

    .grafico-titulo {{
        font-size: 11pt;
        font-weight: 600;
        color: {COLORES_PDF['primary']};
        margin-bottom: 10px;
    }}

    /* ============================================
       ANÁLISIS / RESUMEN
    ============================================ */
    .analisis-box {{
        background: {COLORES_PDF['light_blue']};
        border-left: 4px solid {COLORES_PDF['primary']};
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }}

    .analisis-box h4 {{
        color: {COLORES_PDF['primary']};
        font-size: 11pt;
        margin-bottom: 10px;
    }}

    .analisis-box p {{
        font-size: 10pt;
        line-height: 1.6;
        color: {COLORES_PDF['dark']};
    }}

    /* ============================================
       LÍNEAS ESTRATÉGICAS
    ============================================ */
    .linea-card {{
        background: {COLORES_PDF['white']};
        border: 1px solid {COLORES_PDF['light_blue']};
        border-radius: 8px;
        margin-bottom: 15px;
        overflow: hidden;
        page-break-inside: avoid;
    }}

    .linea-header {{
        background: {COLORES_PDF['primary']};
        color: white;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .linea-nombre {{
        font-weight: 600;
        font-size: 11pt;
    }}

    .linea-cumplimiento {{
        font-size: 14pt;
        font-weight: bold;
    }}

    .linea-body {{
        padding: 15px;
    }}

    .linea-objetivos {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }}

    .objetivo-item {{
        background: {COLORES_PDF['light']};
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 9pt;
        flex: 1 1 45%;
    }}

    /* ============================================
       SEMÁFORO / LEYENDA
    ============================================ */
    .semaforo {{
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 20px 0;
        padding: 15px;
        background: {COLORES_PDF['light']};
        border-radius: 8px;
    }}

    .semaforo-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 9pt;
    }}

    .semaforo-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }}

    .semaforo-dot.verde {{ background: {COLORES_PDF['success']}; }}
    .semaforo-dot.amarillo {{ background: {COLORES_PDF['warning']}; }}
    .semaforo-dot.rojo {{ background: {COLORES_PDF['danger']}; }}

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

    .no-break {{
        page-break-inside: avoid;
    }}

    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; }}
    .mt-20 {{ margin-top: 20px; }}
    .mb-20 {{ margin-bottom: 20px; }}

    .row {{
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }}

    .col-6 {{ flex: 1; }}
    .col-4 {{ flex: 0 0 33.33%; }}
    .col-8 {{ flex: 0 0 66.66%; }}
    """


def generar_portada(titulo: str, subtitulo: str, periodo: str, fecha: str) -> str:
    """Genera el HTML de la portada del informe."""
    return f"""
    <div class="portada">
        <div class="portada-logo">
            <span>📊</span>
        </div>
        <div class="portada-titulo">{titulo}</div>
        <div class="portada-subtitulo">{subtitulo}</div>
        <div class="portada-linea"></div>
        <div class="portada-periodo">{periodo}</div>
        <div class="portada-fecha">Generado el {fecha}</div>
    </div>
    """


def generar_seccion_kpis(metricas: Dict[str, Any]) -> str:
    """Genera el HTML de la sección de KPIs principales."""
    cumplimiento = metricas.get('cumplimiento_promedio', 0)

    # Determinar clase del KPI principal según cumplimiento
    clase_cumpl = 'success' if cumplimiento >= 100 else 'warning' if cumplimiento >= 80 else 'danger'

    return f"""
    <div class="seccion">
        <div class="seccion-header">
            <h2>📊 Indicadores Clave de Desempeño</h2>
        </div>
        <div class="seccion-contenido">
            <div class="kpis-container">
                <div class="kpi-card {clase_cumpl}">
                    <div class="kpi-valor">{cumplimiento:.1f}%</div>
                    <div class="kpi-label">Cumplimiento General</div>
                </div>
                <div class="kpi-card success">
                    <div class="kpi-valor">{metricas.get('indicadores_cumplidos', 0)}</div>
                    <div class="kpi-label">Indicadores Cumplidos</div>
                </div>
                <div class="kpi-card warning">
                    <div class="kpi-valor">{metricas.get('en_progreso', 0)}</div>
                    <div class="kpi-label">En Progreso</div>
                </div>
                <div class="kpi-card danger">
                    <div class="kpi-valor">{metricas.get('no_cumplidos', 0)}</div>
                    <div class="kpi-label">No Cumplidos</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-valor">{metricas.get('total_indicadores', 0)}</div>
                    <div class="kpi-label">Total Indicadores</div>
                </div>
            </div>

            <div class="semaforo">
                <div class="semaforo-item">
                    <div class="semaforo-dot verde"></div>
                    <span>≥100% Meta Cumplida</span>
                </div>
                <div class="semaforo-item">
                    <div class="semaforo-dot amarillo"></div>
                    <span>80-99% En Progreso</span>
                </div>
                <div class="semaforo-item">
                    <div class="semaforo-dot rojo"></div>
                    <span>&lt;80% Requiere Atención</span>
                </div>
            </div>
        </div>
    </div>
    """


def generar_tabla_lineas(df_lineas: pd.DataFrame) -> str:
    """Genera la tabla HTML de cumplimiento por línea estratégica."""
    if df_lineas is None or df_lineas.empty:
        return "<p>No hay datos disponibles.</p>"

    filas_html = ""
    for _, row in df_lineas.iterrows():
        cumpl = row.get('Cumplimiento', 0)
        if cumpl >= 100:
            badge = '<span class="badge badge-success">Cumplido</span>'
        elif cumpl >= 80:
            badge = '<span class="badge badge-warning">En Progreso</span>'
        else:
            badge = '<span class="badge badge-danger">Atención</span>'

        filas_html += f"""
        <tr>
            <td>{row.get('Linea', 'N/D')}</td>
            <td class="text-center">{row.get('Total_Indicadores', 0)}</td>
            <td class="text-right"><strong>{cumpl:.1f}%</strong></td>
            <td class="text-center">{badge}</td>
        </tr>
        """

    return f"""
    <div class="seccion">
        <div class="seccion-header">
            <h2>📈 Cumplimiento por Línea Estratégica</h2>
        </div>
        <div class="seccion-contenido">
            <table>
                <thead>
                    <tr>
                        <th>Línea Estratégica</th>
                        <th class="text-center">Indicadores</th>
                        <th class="text-right">Cumplimiento</th>
                        <th class="text-center">Estado</th>
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
    for _, row in df_indicadores.iterrows():
        cumpl = row.get('Cumplimiento', 0)
        if pd.isna(cumpl):
            badge = '<span class="badge badge-info">N/D</span>'
            cumpl_str = "N/D"
        elif cumpl >= 100:
            badge = '<span class="badge badge-success">✓</span>'
            cumpl_str = f"{cumpl:.1f}%"
        elif cumpl >= 80:
            badge = '<span class="badge badge-warning">!</span>'
            cumpl_str = f"{cumpl:.1f}%"
        else:
            badge = '<span class="badge badge-danger">✗</span>'
            cumpl_str = f"{cumpl:.1f}%"

        indicador = row.get('Indicador', 'N/D')
        # Truncar si es muy largo
        if len(str(indicador)) > 60:
            indicador = str(indicador)[:57] + "..."

        filas_html += f"""
        <tr>
            <td>{indicador}</td>
            <td class="text-right">{row.get('Meta', 'N/D')}</td>
            <td class="text-right">{row.get('Ejecución', 'N/D')}</td>
            <td class="text-right"><strong>{cumpl_str}</strong></td>
            <td class="text-center">{badge}</td>
        </tr>
        """

    return f"""
    <div class="seccion no-break">
        <div class="seccion-header">
            <h2>📋 {titulo}</h2>
        </div>
        <div class="seccion-contenido">
            <table>
                <thead>
                    <tr>
                        <th style="width: 45%;">Indicador</th>
                        <th class="text-right" style="width: 12%;">Meta</th>
                        <th class="text-right" style="width: 12%;">Ejecución</th>
                        <th class="text-right" style="width: 15%;">Cumplimiento</th>
                        <th class="text-center" style="width: 10%;">Estado</th>
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
    return f"""
    <div class="analisis-box">
        <h4>🤖 {titulo}</h4>
        <p>{contenido}</p>
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
        <div class="footer-logo">POLITÉCNICO GRANCOLOMBIANO</div>
        <p>Dashboard Estratégico POLI - Plan de Desarrollo Institucional 2021-{año}</p>
        <p>Documento generado automáticamente el {fecha_generacion}</p>
    </div>
    """

    # HTML completo
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Informe Estratégico POLI {año}</title>
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

        <h1>Análisis por Línea Estratégica</h1>
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
    Convierte HTML a PDF usando weasyprint.

    Args:
        html_content: Contenido HTML del informe

    Returns:
        Bytes del archivo PDF
    """
    try:
        from weasyprint import HTML, CSS

        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        return pdf_buffer.getvalue()

    except ImportError:
        # Fallback: intentar con xhtml2pdf
        try:
            from xhtml2pdf import pisa

            pdf_buffer = io.BytesIO()
            pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buffer)
            return pdf_buffer.getvalue()

        except ImportError:
            raise ImportError(
                "Se requiere instalar weasyprint o xhtml2pdf para generar PDFs.\n"
                "Ejecute: pip install weasyprint\n"
                "O: pip install xhtml2pdf"
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
