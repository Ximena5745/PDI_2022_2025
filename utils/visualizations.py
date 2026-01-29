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
                tickangle=-45 if len(etiquetas) > 5 else 0,
                type='category',  # Forzar eje categórico para evitar decimales
                categoryorder='array',
                categoryarray=etiquetas  # Usar etiquetas en orden
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

        # Agregar líneas de referencia para semáforo (sin anotaciones superpuestas)
        fig.add_hline(y=100, line_dash="dash", line_color=COLORS['success'],
                      yref='y2', opacity=0.5)
        fig.add_hline(y=80, line_dash="dash", line_color=COLORS['warning'],
                      yref='y2', opacity=0.5)

        # Agregar anotaciones con posición fija a la izquierda para evitar superposición
        fig.add_annotation(
            x=0.02, y=100, xref='paper', yref='y2',
            text="Meta (100%)", showarrow=False,
            font=dict(size=10, color=COLORS['success']),
            bgcolor='rgba(255,255,255,0.8)', borderpad=2
        )
        fig.add_annotation(
            x=0.02, y=80, xref='paper', yref='y2',
            text="Alerta (80%)", showarrow=False,
            font=dict(size=10, color=COLORS['warning']),
            bgcolor='rgba(255,255,255,0.8)', borderpad=2
        )

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
        fig.add_vline(x=100, line_dash="dash", line_color=COLORS['success'], opacity=0.5)
        fig.add_vline(x=80, line_dash="dash", line_color=COLORS['warning'], opacity=0.5)

        return fig
    except Exception as e:
        st.error(f"Error al crear grafico de lineas: {str(e)}")
        return go.Figure()


def crear_grafico_semaforo(indicadores_cumplidos, en_progreso, no_cumplidos, stand_by=0):
    """
    Crea un gráfico de dona mostrando la distribución por semáforo.

    Args:
        indicadores_cumplidos: Cantidad de indicadores con cumplimiento >= 100%
        en_progreso: Cantidad de indicadores con cumplimiento 80-99.9%
        no_cumplidos: Cantidad de indicadores con cumplimiento < 80%
        stand_by: Cantidad de indicadores en estado Stand by

    Returns:
        Figura de Plotly
    """
    labels = ['Cumplido (>=100%)', 'En Progreso (80-99%)', 'No Cumplido (<80%)']
    values = [indicadores_cumplidos, en_progreso, no_cumplidos]
    colors = [COLORS['success'], COLORS['warning'], COLORS['danger']]

    # Agregar Stand by si hay indicadores en ese estado
    if stand_by > 0:
        labels.append('Stand by')
        values.append(stand_by)
        colors.append(COLORS['standby'])

    total = sum(values)

    # Crear texto personalizado para mostrar dentro y fuera
    custom_text = []
    for label, value in zip(labels, values):
        pct = (value / total * 100) if total > 0 else 0
        custom_text.append(f"{value}<br>{pct:.1f}%")

    # Configurar pull para separar segmentos
    pull_values = [0.02] * len(values)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='text',
        text=custom_text,
        textposition='outside',
        textfont=dict(size=10),
        insidetextorientation='horizontal',
        pull=pull_values,
        hovertemplate='<b>%{label}</b><br>Indicadores: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text="<b>Distribucion de Indicadores por Estado</b>",
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
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        height=450,
        margin=dict(t=60, b=100, l=60, r=60),
        uniformtext_minsize=9,
        uniformtext_mode='hide'
    )

    return fig


def crear_grafico_proyectos(finalizados, en_ejecucion, stand_by):
    """
    Crea un gráfico de dona mostrando la distribución de proyectos por estado.

    Args:
        finalizados: Cantidad de proyectos con Ejecución = 100%
        en_ejecucion: Cantidad de proyectos con Ejecución > 0% y < 100%
        stand_by: Cantidad de proyectos en Stand by

    Returns:
        Figura de Plotly
    """
    labels = ['Finalizado (100%)', 'En Ejecución (<100%)', 'Stand by']
    values = [finalizados, en_ejecucion, stand_by]
    colors = [COLORS['success'], COLORS['warning'], COLORS['standby']]

    total = sum(values)

    # Crear texto personalizado para mostrar dentro y fuera
    custom_text = []
    for label, value in zip(labels, values):
        pct = (value / total * 100) if total > 0 else 0
        custom_text.append(f"{value}<br>{pct:.1f}%")

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='text',
        text=custom_text,
        textposition='outside',
        textfont=dict(size=10),
        insidetextorientation='horizontal',
        pull=[0.02, 0.02, 0.02],  # Separar ligeramente los segmentos
        hovertemplate='<b>%{label}</b><br>Proyectos: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text="<b>Distribución de Proyectos por Estado</b>",
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
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        height=450,
        margin=dict(t=60, b=100, l=60, r=60),
        uniformtext_minsize=9,
        uniformtext_mode='hide'
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
    fig.add_hrect(y0=100, y1=150, fillcolor=COLORS['success'], opacity=0.1,
                  line_width=0, annotation_text="Meta cumplida",
                  annotation_position="right")
    fig.add_hrect(y0=80, y1=100, fillcolor=COLORS['warning'], opacity=0.1,
                  line_width=0, annotation_text="Alerta",
                  annotation_position="right")
    fig.add_hrect(y0=0, y1=80, fillcolor=COLORS['danger'], opacity=0.1,
                  line_width=0, annotation_text="Peligro",
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
        if cumplimiento >= 100:
            texto = "✅ Meta cumplida"
        elif cumplimiento >= 80:
            texto = "⚠️ Alerta"
        else:
            texto = "❌ Peligro"

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


def aclarar_color(color_hex, factor=0.5):
    """
    Genera un tono más claro del color base.

    Args:
        color_hex: Color en formato hexadecimal (#RRGGBB)
        factor: Factor de aclarado (0.0 = original, 1.0 = blanco)

    Returns:
        Color aclarado en formato hexadecimal
    """
    # Eliminar el # si existe
    color_hex = color_hex.lstrip('#')

    # Convertir hex a RGB
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)

    # Aclarar hacia blanco (255, 255, 255)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)

    # Convertir de vuelta a hex
    return f"#{r:02x}{g:02x}{b:02x}"


def obtener_color_texto(color_hex):
    """
    Determina un color de texto visualmente atractivo según la luminosidad del fondo.
    Usa colores más vibrantes y contrastantes.

    Args:
        color_hex: Color de fondo en formato hexadecimal (#RRGGBB)

    Returns:
        Color de texto en formato hexadecimal para mejor contraste
    """
    color_hex = color_hex.lstrip('#')
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)

    # Calcular luminosidad (fórmula estándar)
    luminosidad = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Retornar colores más visuales en lugar de solo blanco/negro
    if luminosidad < 0.4:
        return '#FFFFFF'  # Blanco para fondos muy oscuros
    elif luminosidad < 0.6:
        return '#FFFFFF'  # Blanco para fondos oscuros/medios
    else:
        return '#1a1a1a'  # Gris oscuro para fondos claros


def dividir_texto_largo(texto, max_caracteres=40):
    """
    Divide un texto largo en múltiples líneas según un máximo de caracteres.
    
    Args:
        texto: Texto a dividir
        max_caracteres: Máximo de caracteres por línea (default: 40)
    
    Returns:
        Texto con saltos de línea para ajustarse al ancho
    """
    texto = str(texto)
    if len(texto) <= max_caracteres:
        return texto
    
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    
    for palabra in palabras:
        if len(linea_actual) + len(palabra) + 1 <= max_caracteres:
            linea_actual += (" " if linea_actual else "") + palabra
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    
    if linea_actual:
        lineas.append(linea_actual)
    
    return "<br>".join(lineas)


def crear_grafico_cascada(df_cascada, titulo="Cumplimiento por Línea Estratégica y Objetivo"):
    """
    Crea un gráfico Sunburst para el Dashboard General.
    Muestra la jerarquía de cumplimiento con colores por línea estratégica.

    Args:
        df_cascada: DataFrame con estructura jerárquica
        titulo: Título del gráfico

    Returns:
        Figura de Plotly
    """
    if df_cascada is None or df_cascada.empty:
        st.warning("No hay datos disponibles para crear el gráfico de cascada.")
        return go.Figure()

    try:
        df_viz = df_cascada.copy()

        labels = []
        labels_completos = []  # Lista para nombres completos (hover)
        cumplimientos = []
        colores = []
        parents = []
        ids = []

        linea_color_map = {}
        contador_obj = {}
        contador_meta = {}

        for idx, row in df_viz.iterrows():
            nivel = int(row['Nivel'])
            cumpl = row['Cumplimiento']
            cumpl_display = min(cumpl, 200) if pd.notna(cumpl) else 0

            if nivel == 1:
                id_linea = f"L1-{idx}"
                nombre = row['Linea']
                # Nombre más corto para las líneas (reemplazar guiones bajos)
                nombre_display = nombre.replace('_', ' ')
                labels.append(dividir_texto_largo(nombre_display, max_caracteres=20))
                labels_completos.append(nombre_display)
                parents.append("")
                color_linea = COLORES_LINEAS.get(row['Linea'], COLORS['primary'])
                colores.append(color_linea)
                linea_color_map[row['Linea']] = (color_linea, id_linea)
                ids.append(id_linea)

            elif nivel == 2:
                linea_info = linea_color_map.get(row['Linea'])
                id_linea = linea_info[1] if linea_info else ""

                id_obj = f"L2-{idx}"
                nombre = row['Objetivo']
                # Nombre más corto para objetivos (máx 25 caracteres por línea)
                labels.append(dividir_texto_largo(nombre, max_caracteres=25))
                labels_completos.append(nombre)
                parents.append(id_linea)
                color_base = linea_info[0] if linea_info else COLORS['primary']
                colores.append(aclarar_color(color_base, factor=0.4))
                ids.append(id_obj)
                contador_obj[f"{row['Linea']}-{row['Objetivo']}"] = id_obj

            elif nivel == 3:
                key_obj = f"{row['Linea']}-{row['Objetivo']}"
                id_obj = contador_obj.get(key_obj, "")

                id_meta = f"L3-{idx}"
                nombre = str(row['Meta_PDI'])
                # Nombre dividido en múltiples líneas
                labels.append(dividir_texto_largo(f"Meta: {nombre}", max_caracteres=30))
                labels_completos.append(f"Meta: {nombre}")
                parents.append(id_obj)
                linea_info = linea_color_map.get(row['Linea'])
                color_base = linea_info[0] if linea_info else COLORS['primary']
                colores.append(aclarar_color(color_base, factor=0.6))
                ids.append(id_meta)
                contador_meta[f"{row['Linea']}-{row['Objetivo']}-{row['Meta_PDI']}"] = id_meta

            elif nivel == 4:
                if row['Meta_PDI'] == 'N/D' or pd.isna(row['Meta_PDI']):
                    key_obj = f"{row['Linea']}-{row['Objetivo']}"
                    id_parent = contador_obj.get(key_obj, "")
                else:
                    key_meta = f"{row['Linea']}-{row['Objetivo']}-{row['Meta_PDI']}"
                    id_parent = contador_meta.get(key_meta, "")

                id_ind = f"L4-{idx}"
                nombre = row['Indicador']
                # Nombre dividido en múltiples líneas
                labels.append(dividir_texto_largo(nombre, max_caracteres=35))
                labels_completos.append(nombre)
                parents.append(id_parent)
                linea_info = linea_color_map.get(row['Linea'])
                color_base = linea_info[0] if linea_info else COLORS['primary']
                colores.append(aclarar_color(color_base, factor=0.75))
                ids.append(id_ind)

            cumplimientos.append(cumpl_display)

        # Crear textos de porcentaje con colores dinámicos (mejorados visualmente)
        textos_porcentaje = []
        for i, c in enumerate(cumplimientos):
            color_fondo = colores[i]
            color_hex = color_fondo.lstrip('#')
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            luminosidad = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Usar colores más vibrantes según el fondo
            if luminosidad < 0.5:
                color_texto_porcentaje = '#FFFFFF'  # Blanco para fondos oscuros
            else:
                color_texto_porcentaje = '#0A3F6B'  # Azul oscuro para fondos claros
            
            textos_porcentaje.append(f"<b style='font-size: 11px; color: {color_texto_porcentaje}'>{c:.1f}%</b>")

        # Determinar colores de texto según luminosidad del fondo
        colores_texto = [obtener_color_texto(c) for c in colores]

        # Crear customdata con nombre completo y porcentaje para hover
        customdata = list(zip(labels_completos, textos_porcentaje))

        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            marker=dict(
                colors=colores,
                line=dict(color='white', width=2)
            ),
            text=textos_porcentaje,
            textinfo='text+label',
            textfont=dict(size=10, color='#1a1a1a', family='Arial'),
            insidetextfont=dict(color=colores_texto, size=9, family='Arial'),
            insidetextorientation='horizontal',  # Orientación horizontal para mejor legibilidad
            customdata=customdata,
            hovertemplate='<b>%{customdata[0]}</b><br><br>Cumplimiento: %{customdata[1]}<extra></extra>',
            hoverlabel=dict(
                bgcolor='white',
                font_size=12,
                font_color='black',
                namelength=-1,
                bordercolor='#333'
            ),
            branchvalues="remainder"
        ))

        fig.update_layout(
            title=dict(
                text=f"<b>{titulo}</b>",
                font=dict(size=14, color=COLORS['primary'], family='Arial'),
                x=0.5,
                xanchor='center',
                y=0.98,
                yanchor='top'
            ),
            height=600,  # Altura reducida para mejor proporción
            margin=dict(t=50, b=10, l=10, r=10),
            uniformtext=dict(minsize=6, mode='hide'),  # Ocultar texto si es muy pequeño
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=10, color='#1a1a1a')
        )

        return fig
    except Exception as e:
        st.error(f"Error al crear gráfico de cascada: {str(e)}")
        return go.Figure()


def crear_grafico_cascada_icicle(df_cascada, titulo="Cumplimiento en Cascada"):
    """
    Crea un gráfico Treemap para Análisis por Línea.
    Muestra nombre truncado + % de cumplimiento centrado.

    Args:
        df_cascada: DataFrame con estructura jerárquica
        titulo: Título del gráfico

    Returns:
        Figura de Plotly
    """
    if df_cascada is None or df_cascada.empty:
        st.warning("No hay datos disponibles para crear el gráfico.")
        return go.Figure()

    try:
        df_viz = df_cascada.copy()

        labels = []
        labels_hover = []
        cumplimientos = []
        colores = []
        parents = []
        ids = []
        valores = []

        linea_color_map = {}
        contador_obj = {}
        contador_meta = {}

        for idx, row in df_viz.iterrows():
            nivel = int(row['Nivel'])
            cumpl = row['Cumplimiento']
            cumpl_display = min(cumpl, 200) if pd.notna(cumpl) else 0
            total_ind = row.get('Total_Indicadores', 1)

            if nivel == 1:
                id_linea = f"L1-{idx}"
                nombre = row['Linea']
                # Nombre dividido en múltiples líneas
                labels.append(dividir_texto_largo(nombre, max_caracteres=30))
                labels_hover.append(nombre)
                parents.append("")
                color_linea = COLORES_LINEAS.get(row['Linea'], COLORS['primary'])
                colores.append(color_linea)
                linea_color_map[row['Linea']] = (color_linea, id_linea)
                ids.append(id_linea)
                valores.append(total_ind)

            elif nivel == 2:
                linea_info = linea_color_map.get(row['Linea'])
                id_linea = linea_info[1] if linea_info else ""

                id_obj = f"L2-{idx}"
                nombre = row['Objetivo']
                # Nombre dividido en múltiples líneas
                labels.append(dividir_texto_largo(nombre, max_caracteres=35))
                labels_hover.append(nombre)
                parents.append(id_linea)
                color_base = linea_info[0] if linea_info else COLORS['primary']
                colores.append(aclarar_color(color_base, factor=0.35))
                ids.append(id_obj)
                contador_obj[f"{row['Linea']}-{row['Objetivo']}"] = id_obj
                valores.append(total_ind)

            elif nivel == 3:
                key_obj = f"{row['Linea']}-{row['Objetivo']}"
                id_obj = contador_obj.get(key_obj, "")

                id_meta = f"L3-{idx}"
                nombre = str(row['Meta_PDI'])
                # Nombre dividido en múltiples líneas
                labels.append(dividir_texto_largo(f"Meta: {nombre}", max_caracteres=30))
                labels_hover.append(f"Meta: {nombre}")
                parents.append(id_obj)
                linea_info = linea_color_map.get(row['Linea'])
                color_base = linea_info[0] if linea_info else COLORS['primary']
                colores.append(aclarar_color(color_base, factor=0.55))
                ids.append(id_meta)
                contador_meta[f"{row['Linea']}-{row['Objetivo']}-{row['Meta_PDI']}"] = id_meta
                valores.append(total_ind)

            elif nivel == 4:
                if row['Meta_PDI'] == 'N/D' or pd.isna(row['Meta_PDI']):
                    key_obj = f"{row['Linea']}-{row['Objetivo']}"
                    id_parent = contador_obj.get(key_obj, "")
                else:
                    key_meta = f"{row['Linea']}-{row['Objetivo']}-{row['Meta_PDI']}"
                    id_parent = contador_meta.get(key_meta, "")

                id_ind = f"L4-{idx}"
                nombre = row['Indicador']
                # Nombre dividido en múltiples líneas
                labels.append(dividir_texto_largo(nombre, max_caracteres=35))
                labels_hover.append(nombre)
                parents.append(id_parent)
                linea_info = linea_color_map.get(row['Linea'])
                color_base = linea_info[0] if linea_info else COLORS['primary']
                colores.append(aclarar_color(color_base, factor=0.7))
                ids.append(id_ind)
                valores.append(1)

            cumplimientos.append(cumpl_display)

        # Crear gráfico Treemap con texto simplificado y colores dinámicos
        # Usar text para mostrar porcentaje y textinfo para controlar visibilidad
        textos_porcentaje = []
        for i, c in enumerate(cumplimientos):
            color_fondo = colores[i]
            color_hex = color_fondo.lstrip('#')
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            luminosidad = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Usar colores más vibrantes según el fondo
            if luminosidad < 0.5:
                color_texto_porcentaje = '#FFFFFF'  # Blanco para fondos oscuros
            else:
                color_texto_porcentaje = '#0A3F6B'  # Azul oscuro para fondos claros
            
            textos_porcentaje.append(f"<b style='font-size: 15px; color: {color_texto_porcentaje}'>{c:.1f}%</b>")

        # Determinar colores de texto según luminosidad del fondo
        colores_texto = [obtener_color_texto(c) for c in colores]

        fig = go.Figure(go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=valores,
            marker=dict(
                colors=colores,
                line=dict(color='white', width=3)  # Aumentar grosor de borde
            ),
            text=textos_porcentaje,
            textinfo='text+label',  # Mostrar porcentaje primero, luego label
            textfont=dict(size=13, color='#1a1a1a', family='Arial Black'),  # Aumentar tamaño, color oscuro, fuente pesada
            insidetextfont=dict(color=colores_texto, size=12, family='Arial Black'),  # Aumentar tamaño interno a 12
            textposition="middle center",
            customdata=list(zip(labels_hover, textos_porcentaje)),
            hovertemplate='<b>%{customdata[0]}</b><br><br>Cumplimiento: %{customdata[1]}<extra></extra>',
            hoverlabel=dict(
                bgcolor='white',
                font_size=13,
                font_color='black',
                namelength=-1,  # Mostrar nombre completo sin truncar
                bordercolor='#333'  # Borde oscuro para mejor contraste
            ),
            branchvalues="total",
            pathbar=dict(
                visible=True,
                thickness=35,  # Aumentar grosor de pathbar
                textfont=dict(size=13, family='Arial Black')  # Fuente más pesada
            )
        ))

        fig.update_layout(
            title=dict(
                text=f"<b style='font-size: 18px'>{titulo}</b>",
                font=dict(size=18, color=COLORS['primary'], family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.98,
                yanchor='top'
            ),
            height=700,  # Aumentar altura
            width=1000,  # Ancho optimizado
            margin=dict(t=80, b=20, l=20, r=20),
            uniformtext=dict(minsize=8, mode='show'),  # Usar 'show' para mostrar etiquetas sin restricciones de tamaño
            paper_bgcolor='rgba(245, 245, 245, 0.9)',  # Fondo muy claro para mejor contraste
            plot_bgcolor='rgba(245, 245, 245, 0.9)',
            font=dict(family='Arial, sans-serif', size=12, color='#1a1a1a')
        )

        return fig
    except Exception as e:
        st.error(f"Error al crear gráfico Treemap: {str(e)}")
        return go.Figure()


def crear_grafico_barras_objetivos(df_cascada, linea_seleccionada=None, titulo="Cumplimiento por Objetivo"):
    """
    Crea un gráfico de barras horizontales agrupadas por objetivo.
    Alternativa más amigable al treemap.

    Args:
        df_cascada: DataFrame con estructura jerárquica
        linea_seleccionada: Filtrar por línea específica (opcional)
        titulo: Título del gráfico

    Returns:
        Figura de Plotly
    """
    if df_cascada is None or df_cascada.empty:
        return go.Figure()

    try:
        df = df_cascada.copy()

        # Filtrar por línea si se especifica
        if linea_seleccionada:
            df = df[df['Linea'] == linea_seleccionada]

        # Filtrar solo nivel 2 (objetivos)
        df_objetivos = df[df['Nivel'] == 2].copy()

        if df_objetivos.empty:
            return go.Figure()

        # Ordenar por cumplimiento
        df_objetivos = df_objetivos.sort_values('Cumplimiento', ascending=True)

        # Truncar nombres largos
        df_objetivos['Objetivo_corto'] = df_objetivos['Objetivo'].apply(
            lambda x: str(x)[:60] + '...' if len(str(x)) > 60 else str(x)
        )

        # Asignar colores según semáforo
        colores = []
        for cumpl in df_objetivos['Cumplimiento']:
            if cumpl >= 100:
                colores.append(COLORS['success'])
            elif cumpl >= 80:
                colores.append(COLORS['warning'])
            else:
                colores.append(COLORS['danger'])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=df_objetivos['Objetivo_corto'],
            x=df_objetivos['Cumplimiento'],
            orientation='h',
            marker_color=colores,
            text=[f"{c:.1f}%" for c in df_objetivos['Cumplimiento']],
            textposition='outside',
            textfont=dict(size=11, weight='bold'),
            customdata=df_objetivos['Objetivo'],
            hovertemplate='<b>%{customdata}</b><br>Cumplimiento: %{x:.1f}%<br>Indicadores: %{meta}<extra></extra>',
            meta=df_objetivos['Total_Indicadores']
        ))

        # Líneas de referencia
        fig.add_vline(x=100, line_dash="dash", line_color=COLORS['success'], opacity=0.6)
        fig.add_vline(x=80, line_dash="dash", line_color=COLORS['warning'], opacity=0.6)

        altura = max(350, len(df_objetivos) * 40)

        fig.update_layout(
            title=dict(
                text=f"<b>{titulo}</b>",
                font=dict(size=14, color=COLORS['primary']),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="% Cumplimiento",
                range=[0, max(df_objetivos['Cumplimiento'].max() * 1.15, 120)],
                ticksuffix='%'
            ),
            yaxis=dict(title="", tickfont=dict(size=10)),
            height=altura,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=250, r=80, t=50, b=40),
            showlegend=False
        )

        return fig

    except Exception as e:
        st.error(f"Error al crear grafico de barras: {str(e)}")
        return go.Figure()


def crear_tabla_cascada_html(df_cascada):
    """
    Crea una tabla HTML expandible con la estructura de cascada.

    Args:
        df_cascada: DataFrame con estructura jerárquica

    Returns:
        str: HTML de la tabla
    """
    if df_cascada is None or df_cascada.empty:
        return "<p>No hay datos disponibles</p>"

    html = """
    <style>
        .cascada-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }
        .cascada-nivel-1 {
            background: #f8f9fa;
            font-weight: bold;
            font-size: 16px;
            padding: 12px;
            border-bottom: 2px solid #dee2e6;
        }
        .cascada-nivel-2 {
            background: white;
            padding: 10px 10px 10px 30px;
            border-bottom: 1px solid #e9ecef;
            font-size: 14px;
        }
        .cascada-nivel-3 {
            background: #fafafa;
            padding: 8px 8px 8px 50px;
            border-bottom: 1px solid #e9ecef;
            font-size: 13px;
            font-style: italic;
        }
        .cascada-nivel-4 {
            background: white;
            padding: 6px 6px 6px 70px;
            border-bottom: 1px dotted #e9ecef;
            font-size: 12px;
            color: #666;
        }
        .cumpl-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 12px;
            min-width: 60px;
            text-align: center;
        }
    </style>
    <table class="cascada-table">
    """

    for _, row in df_cascada.iterrows():
        nivel = int(row['Nivel'])
        cumplimiento = row['Cumplimiento']
        color = obtener_color_semaforo(cumplimiento)

        # Badge de cumplimiento
        badge_color = 'white' if color != COLORS['warning'] else '#333'
        badge_html = f'<span class="cumpl-badge" style="background: {color}; color: {badge_color};">{cumplimiento:.1f}%</span>'

        # Contenido según nivel
        if nivel == 1:
            contenido = f"📊 {row['Linea']}"
            clase = "cascada-nivel-1"
        elif nivel == 2:
            contenido = f"🎯 {row['Objetivo']}"
            clase = "cascada-nivel-2"
        elif nivel == 3:
            contenido = f"🎖️ Meta PDI: {row['Meta_PDI']}"
            clase = "cascada-nivel-3"
        else:  # nivel 4
            contenido = f"📌 {row['Indicador']}"
            clase = "cascada-nivel-4"

        html += f"""
        <tr>
            <td class="{clase}">{contenido}</td>
            <td class="{clase}" style="text-align: right; width: 100px;">{badge_html}</td>
            <td class="{clase}" style="text-align: center; width: 80px;"><small>{row['Total_Indicadores']} ind.</small></td>
        </tr>
        """

    html += "</table>"
    return html
