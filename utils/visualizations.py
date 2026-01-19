"""
Módulo de visualizaciones para el Dashboard Estratégico POLI.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from .data_loader import COLORS, COLORES_LINEAS, calcular_cumplimiento, obtener_color_semaforo


def crear_grafico_historico(df_indicador, nombre_indicador, sentido='Creciente', unidad='', periodicidad='Anual', linea_estrategica=None):
    """
    Crea un gráfico de barras agrupadas con Meta vs Ejecución y línea de cumplimiento.
    Soporta datos anuales y semestrales.

    Args:
        df_indicador: DataFrame con columnas Periodo (o Año), Meta, Ejecución
        nombre_indicador: Nombre del indicador para el título
        sentido: 'Creciente' o 'Decreciente'
        unidad: Unidad de medida (%, $, ENT, etc.)
        periodicidad: 'Anual' o 'Semestral'
        linea_estrategica: Nombre de la línea estratégica (opcional)

    Returns:
        Figura de Plotly
    """
    if df_indicador is None or df_indicador.empty:
        return go.Figure()

    try:
        # Crear copia y limpiar datos
        df = df_indicador.copy()

        # Verificar columnas necesarias
        if 'Meta' not in df.columns or 'Ejecución' not in df.columns:
            return go.Figure()

        # Determinar columna de periodo
        if 'Periodo' in df.columns:
            periodo_col = 'Periodo'
            orden_col = 'Periodo_orden' if 'Periodo_orden' in df.columns else 'Periodo'
        elif 'Año' in df.columns:
            periodo_col = 'Año'
            orden_col = 'Año'
            df['Periodo'] = df['Año'].apply(lambda x: str(int(x)) if pd.notna(x) else '')
        else:
            return go.Figure()

        # Limpiar valores NaN
        df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce').fillna(0)
        df['Ejecución'] = pd.to_numeric(df['Ejecución'], errors='coerce').fillna(0)

        # Filtrar filas con periodo válido
        df = df[df['Periodo'].astype(str).str.strip() != '']

        if df.empty:
            return go.Figure()

        # Ordenar
        if orden_col in df.columns:
            df = df.sort_values(orden_col)

        # Convertir a listas
        periodos = df['Periodo'].astype(str).tolist()
        metas = [float(m) for m in df['Meta'].tolist()]
        ejecuciones = [float(e) for e in df['Ejecución'].tolist()]

        # Crear etiquetas para el eje X
        etiquetas = []
        for p in periodos:
            if p == '2021' or p == '2021-S1':
                etiquetas.append(f"{p}<br>(Linea Base)")
            else:
                etiquetas.append(str(p))

        fig = go.Figure()

        # Formatear valores según unidad
        def formatear_valor(v):
            if unidad == '%':
                return f"{v:.1f}%"
            elif unidad == '$':
                return f"${v:,.0f}"
            elif unidad == 'ENT':
                return f"{v:,.0f}"
            else:
                return f"{v:.2f}"

        # Determinar colores para Meta y Ejecución
        # Meta usa el color de la línea estratégica (si está disponible)
        # Ejecución usa un tono más oscuro de la misma paleta
        if linea_estrategica and linea_estrategica in COLORES_LINEAS:
            color_meta = COLORES_LINEAS[linea_estrategica]
            # Crear un color más oscuro para Ejecución
            color_ejecucion = COLORS['primary']  # Color oscuro de la paleta
        else:
            # Colores por defecto si no se especifica línea
            color_meta = COLORS['accent']
            color_ejecucion = COLORS['primary']

        # Barras de Meta
        fig.add_trace(go.Bar(
            name='Meta',
            x=etiquetas,
            y=metas,
            marker_color=color_meta,
            text=[formatear_valor(m) for m in metas],
            textposition='outside',
            textfont=dict(size=9),
            hovertemplate='<b>Meta %{x}</b><br>Valor: %{y:.2f}<extra></extra>'
        ))

        # Barras de Ejecución
        fig.add_trace(go.Bar(
            name='Ejecucion',
            x=etiquetas,
            y=ejecuciones,
            marker_color=color_ejecucion,
            text=[formatear_valor(e) for e in ejecuciones],
            textposition='outside',
            textfont=dict(size=9),
            hovertemplate='<b>Ejecucion %{x}</b><br>Valor: %{y:.2f}<extra></extra>'
        ))

        # Calcular cumplimientos considerando el sentido
        cumplimientos = []
        for m, e in zip(metas, ejecuciones):
            c = calcular_cumplimiento(m, e, sentido)
            cumplimientos.append(float(c) if c is not None else 0.0)

        # Línea de Cumplimiento en eje secundario
        # Usar un color distintivo para el cumplimiento (magenta/fucsia)
        color_cumplimiento = '#E91E63'  # Color distintivo para cumplimiento

        fig.add_trace(go.Scatter(
            name='% Cumplimiento',
            x=etiquetas,
            y=cumplimientos,
            mode='lines+markers+text',
            line=dict(color=color_cumplimiento, width=3),
            marker=dict(size=10, symbol='circle', color=color_cumplimiento),
            text=[f"{c:.1f}%" for c in cumplimientos],
            textposition='top center',
            textfont=dict(size=9, color=color_cumplimiento),
            yaxis='y2',
            hovertemplate='<b>Cumplimiento %{x}</b><br>%{y:.1f}%<extra></extra>'
        ))

        # Configurar layout
        max_meta = max(metas) if metas else 100
        max_ejec = max(ejecuciones) if ejecuciones else 100
        max_valor = max(max_meta, max_ejec, 1)

        # Título con info de sentido
        sentido_texto = "(Mayor es mejor)" if sentido == 'Creciente' else "(Menor es mejor)"
        titulo_completo = f"<b>Evolucion Historica</b><br><span style='font-size:12px'>{sentido_texto}</span>"

        fig.update_layout(
            title=dict(
                text=titulo_completo,
                font=dict(size=14, color=COLORS['primary']),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(
                    text="Periodo" if periodicidad == 'Semestral' else "Ano",
                    font=dict(size=12, color=COLORS['gray'])
                ),
                tickfont=dict(size=10),
                tickangle=-45 if len(etiquetas) > 5 else 0
            ),
            yaxis=dict(
                title=dict(
                    text=f"Valor ({unidad})" if unidad else "Valor",
                    font=dict(size=12, color=COLORS['gray'])
                ),
                tickfont=dict(size=11),
                range=[0, max_valor * 1.4]
            ),
            yaxis2=dict(
                title=dict(
                    text="% Cumplimiento",
                    font=dict(size=12, color='#E91E63')
                ),
                tickfont=dict(size=11, color='#E91E63'),
                overlaying='y',
                side='right',
                range=[0, 150],
                showgrid=False
            ),
            barmode='group',
            bargap=0.15,
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
            margin=dict(t=100, b=80, l=60, r=60)
        )

        # Agregar líneas de referencia para semáforo
        fig.add_hline(y=90, line_dash="dash", line_color=COLORS['success'],
                      annotation_text="Meta (90%)", annotation_position="right",
                      yref='y2', opacity=0.5)
        fig.add_hline(y=70, line_dash="dash", line_color=COLORS['warning'],
                      annotation_text="Progreso (70%)", annotation_position="right",
                      yref='y2', opacity=0.5)

        return fig
    except Exception as e:
        st.error(f"Error al crear grafico historico: {str(e)}")
        return go.Figure()


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

    try:
        # Asignar colores según la línea estratégica
        colores = [COLORES_LINEAS.get(linea, COLORS['primary']) for linea in df['Linea']]

        fig = go.Figure()

        # Convertir a listas para evitar problemas con tipos de datos
        lineas_list = df['Linea'].tolist()
        cumpl_list = [float(c) for c in df['Cumplimiento'].tolist()]

        # Color distintivo para los labels de cumplimiento
        color_label_cumplimiento = '#E91E63'  # Color distintivo para destacar

        fig.add_trace(go.Bar(
            y=lineas_list,
            x=cumpl_list,
            orientation='h',
            marker_color=colores,
            text=[f"{c:.1f}%" for c in cumpl_list],
            textposition='outside',
            textfont=dict(size=12, color=color_label_cumplimiento, weight='bold'),
            hovertemplate='<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<extra></extra>'
        ))

        altura = max(300, len(df) * 50)

        fig.update_layout(
            title=dict(
                text=f"<b>{titulo}</b>",
                font=dict(size=16, color=COLORS['primary']),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(
                    text="% Cumplimiento",
                    font=dict(size=12, color=COLORS['gray'])
                ),
                range=[0, 120],
                ticksuffix='%'
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=11)
            ),
            height=altura,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=200, r=80, t=60, b=40),
            showlegend=False
        )

        # Líneas de referencia
        fig.add_vline(x=90, line_dash="dash", line_color=COLORS['success'], opacity=0.5)
        fig.add_vline(x=70, line_dash="dash", line_color=COLORS['warning'], opacity=0.5)

        return fig
    except Exception as e:
        st.error(f"Error al crear grafico de lineas: {str(e)}")
        return go.Figure()


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
