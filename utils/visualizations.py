"""
Módulo de visualizaciones para el Dashboard Estratégico POLI.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from .data_loader import COLORS, calcular_cumplimiento, obtener_color_semaforo


def crear_grafico_historico(df_indicador, nombre_indicador):
    """
    Crea un gráfico de barras agrupadas con Meta vs Ejecución y línea de cumplimiento.

    Args:
        df_indicador: DataFrame con columnas año, Meta, Ejecución
        nombre_indicador: Nombre del indicador para el título

    Returns:
        Figura de Plotly
    """
    if df_indicador.empty:
        return go.Figure()

    # Asegurar orden por año
    df = df_indicador.sort_values('Año')
    años = df['Año'].tolist()

    # Crear etiquetas para el eje X (marcar 2021 como línea base)
    etiquetas_años = []
    for a in años:
        if a == 2021:
            etiquetas_años.append(f"{a}<br>(Línea Base)")
        else:
            etiquetas_años.append(str(a))

    fig = go.Figure()

    # Barras de Meta
    fig.add_trace(go.Bar(
        name='Meta',
        x=etiquetas_años,
        y=df['Meta'].tolist(),
        marker_color=COLORS['accent'],
        text=df['Meta'].round(2).tolist(),
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>Meta %{x}</b><br>Valor: %{y:.2f}<extra></extra>'
    ))

    # Barras de Ejecución
    fig.add_trace(go.Bar(
        name='Ejecución',
        x=etiquetas_años,
        y=df['Ejecución'].tolist(),
        marker_color=COLORS['primary'],
        text=df['Ejecución'].round(2).tolist(),
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>Ejecución %{x}</b><br>Valor: %{y:.2f}<extra></extra>'
    ))

    # Calcular cumplimientos
    cumplimientos = []
    for _, row in df.iterrows():
        c = calcular_cumplimiento(row['Meta'], row['Ejecución'])
        cumplimientos.append(c if c is not None else 0)

    # Línea de Cumplimiento en eje secundario
    fig.add_trace(go.Scatter(
        name='% Cumplimiento',
        x=etiquetas_años,
        y=cumplimientos,
        mode='lines+markers+text',
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=12, symbol='circle', color=COLORS['secondary']),
        text=[f"{c:.1f}%" for c in cumplimientos],
        textposition='top center',
        textfont=dict(size=11, color=COLORS['primary']),
        yaxis='y2',
        hovertemplate='<b>Cumplimiento %{x}</b><br>%{y:.1f}%<extra></extra>'
    ))

    # Configurar layout
    max_valor = max(df['Meta'].max(), df['Ejecución'].max()) if not df.empty else 100

    fig.update_layout(
        title=dict(
            text=f"<b>Evolución Histórica: {nombre_indicador}</b>",
            font=dict(size=16, color=COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Año",
            titlefont=dict(size=12, color=COLORS['gray']),
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title="Valor (Meta / Ejecución)",
            titlefont=dict(size=12, color=COLORS['gray']),
            tickfont=dict(size=11),
            range=[0, max_valor * 1.3]
        ),
        yaxis2=dict(
            title="% Cumplimiento",
            titlefont=dict(size=12, color=COLORS['secondary']),
            tickfont=dict(size=11, color=COLORS['secondary']),
            overlaying='y',
            side='right',
            range=[0, 130],
            showgrid=False
        ),
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        hovermode='x unified',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        margin=dict(t=100, b=50, l=60, r=60)
    )

    # Agregar líneas de referencia para semáforo
    fig.add_hline(y=90, line_dash="dash", line_color=COLORS['success'],
                  annotation_text="Meta (90%)", annotation_position="right",
                  yref='y2', opacity=0.5)
    fig.add_hline(y=70, line_dash="dash", line_color=COLORS['warning'],
                  annotation_text="Progreso (70%)", annotation_position="right",
                  yref='y2', opacity=0.5)

    return fig


def crear_grafico_lineas(df_resumen, titulo="Cumplimiento por Línea Estratégica"):
    """
    Crea un gráfico de barras horizontales para el cumplimiento por línea.

    Args:
        df_resumen: DataFrame con columnas Linea, Cumplimiento
        titulo: Título del gráfico

    Returns:
        Figura de Plotly
    """
    if df_resumen is None or df_resumen.empty:
        return go.Figure()

    # Validar que existan las columnas necesarias
    if 'Linea' not in df_resumen.columns or 'Cumplimiento' not in df_resumen.columns:
        return go.Figure()

    # Crear copia y limpiar datos
    df = df_resumen.copy()
    df = df.dropna(subset=['Linea', 'Cumplimiento'])
    df['Cumplimiento'] = pd.to_numeric(df['Cumplimiento'], errors='coerce').fillna(0)
    df['Linea'] = df['Linea'].astype(str)

    if df.empty:
        return go.Figure()

    # Ordenar por cumplimiento
    df = df.sort_values('Cumplimiento', ascending=True)

    # Asignar colores según semáforo
    colores = [obtener_color_semaforo(c) for c in df['Cumplimiento']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['Linea'],
        x=df['Cumplimiento'],
        orientation='h',
        marker_color=colores,
        text=[f"{c:.1f}%" for c in df['Cumplimiento']],
        textposition='outside',
        textfont=dict(size=12, color=COLORS['primary']),
        hovertemplate='<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=16, color=COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="% Cumplimiento",
            titlefont=dict(size=12, color=COLORS['gray']),
            range=[0, 120],
            ticksuffix='%'
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11)
        ),
        height=max(300, len(df) * 50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=200, r=80, t=60, b=40),
        showlegend=False
    )

    # Líneas de referencia
    fig.add_vline(x=90, line_dash="dash", line_color=COLORS['success'], opacity=0.5)
    fig.add_vline(x=70, line_dash="dash", line_color=COLORS['warning'], opacity=0.5)

    return fig


def crear_grafico_semaforo(metas_cumplidas, en_progreso, requieren_atencion):
    """
    Crea un gráfico de dona mostrando la distribución por semáforo.

    Args:
        metas_cumplidas: Cantidad de indicadores con cumplimiento >= 90%
        en_progreso: Cantidad de indicadores con cumplimiento 70-89%
        requieren_atencion: Cantidad de indicadores con cumplimiento < 70%

    Returns:
        Figura de Plotly
    """
    labels = ['Meta Cumplida (≥90%)', 'En Progreso (70-89%)', 'Requiere Atención (<70%)']
    values = [metas_cumplidas, en_progreso, requieren_atencion]
    colors = [COLORS['success'], COLORS['warning'], COLORS['danger']]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='label+percent+value',
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{label}</b><br>Indicadores: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )])

    total = sum(values)
    fig.update_layout(
        title=dict(
            text="<b>Distribución de Indicadores por Estado</b>",
            font=dict(size=14, color=COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        annotations=[dict(
            text=f'<b>{total}</b><br>Total',
            x=0.5, y=0.5,
            font_size=16,
            font_color=COLORS['primary'],
            showarrow=False
        )],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(t=60, b=80, l=20, r=20)
    )

    return fig


def crear_grafico_tendencia(df_indicador, nombre_indicador):
    """
    Crea un gráfico de línea mostrando la tendencia del cumplimiento.

    Args:
        df_indicador: DataFrame con datos del indicador
        nombre_indicador: Nombre del indicador

    Returns:
        Figura de Plotly
    """
    if df_indicador.empty:
        return go.Figure()

    df = df_indicador.sort_values('Año')

    # Calcular cumplimientos
    df['Cumplimiento_Calc'] = df.apply(
        lambda x: calcular_cumplimiento(x['Meta'], x['Ejecución']),
        axis=1
    )

    fig = go.Figure()

    # Áreas de colores de fondo para semáforo
    fig.add_hrect(y0=90, y1=130, fillcolor=COLORS['success'], opacity=0.1,
                  line_width=0, annotation_text="Meta cumplida",
                  annotation_position="right")
    fig.add_hrect(y0=70, y1=90, fillcolor=COLORS['warning'], opacity=0.1,
                  line_width=0, annotation_text="En progreso",
                  annotation_position="right")
    fig.add_hrect(y0=0, y1=70, fillcolor=COLORS['danger'], opacity=0.1,
                  line_width=0, annotation_text="Requiere atención",
                  annotation_position="right")

    # Línea de tendencia
    fig.add_trace(go.Scatter(
        x=df['Año'],
        y=df['Cumplimiento_Calc'],
        mode='lines+markers+text',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=12, color=COLORS['primary']),
        text=[f"{c:.1f}%" if pd.notna(c) else "N/D" for c in df['Cumplimiento_Calc']],
        textposition='top center',
        textfont=dict(size=11),
        name='Cumplimiento',
        hovertemplate='<b>Año %{x}</b><br>Cumplimiento: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>Tendencia de Cumplimiento: {nombre_indicador}</b>",
            font=dict(size=14, color=COLORS['primary']),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Año",
            tickmode='linear',
            dtick=1
        ),
        yaxis=dict(
            title="% Cumplimiento",
            range=[0, 130],
            ticksuffix='%'
        ),
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        margin=dict(t=60, b=40, l=60, r=100)
    )

    return fig


def crear_tarjeta_kpi(valor, etiqueta, icono="📊", delta=None, color_fondo=None):
    """
    Genera el HTML para una tarjeta de KPI estilizada.

    Args:
        valor: Valor a mostrar
        etiqueta: Texto descriptivo
        icono: Emoji o icono
        delta: Cambio vs periodo anterior (opcional)
        color_fondo: Color de fondo personalizado

    Returns:
        str: HTML de la tarjeta
    """
    if color_fondo is None:
        color_fondo = f"linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%)"

    delta_html = ""
    if delta is not None:
        delta_color = COLORS['success'] if delta >= 0 else COLORS['danger']
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f'<div style="font-size: 14px; color: {delta_color};">{delta_icon} {abs(delta):.1f}% vs año anterior</div>'

    return f"""
    <div style="
        background: {color_fondo};
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        text-align: center;
    ">
        <div style="font-size: 24px; margin-bottom: 5px;">{icono}</div>
        <div style="font-size: 14px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">{etiqueta}</div>
        <div style="font-size: 42px; font-weight: bold; margin: 10px 0;">{valor}</div>
        {delta_html}
    </div>
    """


def crear_indicador_semaforo_html(cumplimiento, texto=None):
    """
    Genera HTML para un indicador visual de semáforo.

    Args:
        cumplimiento: Porcentaje de cumplimiento
        texto: Texto opcional para mostrar

    Returns:
        str: HTML del indicador
    """
    color = obtener_color_semaforo(cumplimiento)

    if texto is None:
        if cumplimiento >= 90:
            texto = "✅ Meta cumplida"
        elif cumplimiento >= 70:
            texto = "⚠️ En progreso"
        else:
            texto = "❌ Requiere atención"

    return f"""
    <div style="
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        background-color: {color};
        color: {'#333' if color == COLORS['warning'] else 'white'};
        font-size: 13px;
        font-weight: 600;
    ">
        {texto}
    </div>
    """


def crear_objetivo_card_html(objetivo, indicadores, cumplimiento):
    """
    Genera HTML para una tarjeta de objetivo.
    """
    color = obtener_color_semaforo(cumplimiento)

    return f"""
    <div style="
        padding: 15px 20px;
        margin: 10px 0;
        background: white;
        border-left: 5px solid {color};
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: {COLORS['primary']};">{objetivo}</strong><br>
                <small style="color: {COLORS['gray']};">{indicadores} indicadores</small>
            </div>
            <div style="
                font-size: 24px;
                font-weight: bold;
                color: {color};
            ">
                {cumplimiento:.1f}%
            </div>
        </div>
    </div>
    """
