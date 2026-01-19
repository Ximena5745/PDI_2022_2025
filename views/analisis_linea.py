"""
Página 2: Análisis por Línea Estratégica
Detalle del desempeño de cada línea del PDI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    COLORS, calcular_metricas_generales, obtener_color_semaforo,
    filtrar_por_linea, obtener_lista_objetivos, LINEAS_ESTRATEGICAS
)
from utils.visualizations import (
    crear_objetivo_card_html, crear_tarjeta_kpi
)
from utils.ai_analysis import (
    generar_analisis_linea, preparar_objetivos_para_analisis
)


def mostrar_pagina():
    """
    Renderiza la página de Análisis por Línea Estratégica.
    """
    st.title("📈 Análisis por Línea Estratégica")
    st.markdown("---")

    # Obtener datos
    df_unificado = st.session_state.get('df_unificado')

    if df_unificado is None or df_unificado.empty:
        st.error("⚠️ No se pudieron cargar los datos.")
        return

    # Año de análisis
    año_actual = 2025
    if 'Año' in df_unificado.columns:
        año_actual = int(df_unificado['Año'].max())

    # Selector de línea estratégica
    lineas_disponibles = []
    if 'Linea' in df_unificado.columns:
        lineas_disponibles = sorted(df_unificado['Linea'].dropna().unique().tolist())

    if not lineas_disponibles:
        st.warning("No se encontraron líneas estratégicas en los datos.")
        return

    linea_seleccionada = st.selectbox(
        "🎯 Seleccione una Línea Estratégica:",
        lineas_disponibles,
        index=0
    )

    st.markdown("---")

    # Filtrar datos por línea
    df_linea = filtrar_por_linea(df_unificado, linea_seleccionada)

    if 'Año' in df_linea.columns:
        df_linea_año = df_linea[df_linea['Año'] == año_actual]
    else:
        df_linea_año = df_linea

    # Calcular métricas de la línea
    total_indicadores = df_linea_año['Indicador'].nunique() if 'Indicador' in df_linea_año.columns else len(df_linea_año)
    total_objetivos = df_linea_año['Objetivo'].nunique() if 'Objetivo' in df_linea_año.columns else 0

    cumplimiento_linea = 0
    metas_cumplidas = 0
    en_progreso = 0
    requieren_atencion = 0

    if 'Cumplimiento' in df_linea_año.columns:
        cumplimiento_linea = df_linea_año['Cumplimiento'].mean()
        cumplimiento_linea = cumplimiento_linea if pd.notna(cumplimiento_linea) else 0
        metas_cumplidas = len(df_linea_año[df_linea_año['Cumplimiento'] >= 90])
        en_progreso = len(df_linea_año[(df_linea_año['Cumplimiento'] >= 70) & (df_linea_año['Cumplimiento'] < 90)])
        requieren_atencion = len(df_linea_año[df_linea_año['Cumplimiento'] < 70])

    # KPIs de la línea
    st.markdown(f"### 📊 Métricas de: {linea_seleccionada}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        color_cumpl = obtener_color_semaforo(cumplimiento_linea)
        st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid {color_cumpl};
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 12px; color: {COLORS['gray']}; text-transform: uppercase;">Cumplimiento</div>
            <div style="font-size: 36px; font-weight: bold; color: {color_cumpl};">{cumplimiento_linea:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric(
            label="Total Objetivos",
            value=total_objetivos
        )

    with col3:
        st.metric(
            label="Total Indicadores",
            value=total_indicadores
        )

    with col4:
        st.metric(
            label="Metas Cumplidas",
            value=metas_cumplidas,
            delta=f"{(metas_cumplidas/total_indicadores*100):.0f}%" if total_indicadores > 0 else "0%"
        )

    st.markdown("---")

    # Análisis IA de la línea
    st.markdown("### 🤖 Análisis Inteligente")

    with st.expander(f"Ver análisis de {linea_seleccionada}", expanded=True):
        with st.spinner("Analizando línea estratégica..."):
            # Preparar datos de objetivos
            objetivos_data = preparar_objetivos_para_analisis(df_linea, año_actual)

            analisis = generar_analisis_linea(
                nombre_linea=linea_seleccionada,
                total_indicadores=total_indicadores,
                cumplimiento_promedio=cumplimiento_linea,
                objetivos_data=objetivos_data
            )

            # Convertir markdown a HTML
            analisis_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', analisis)
            analisis_html = analisis_html.replace('\n', '<br>')

            st.markdown(f"""
            <div class="ai-analysis">
                {analisis_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Dos columnas: Gráfico y Lista de objetivos
    col_graf, col_obj = st.columns([1, 1])

    with col_graf:
        st.markdown("### 📊 Cumplimiento por Objetivo")

        if 'Objetivo' in df_linea_año.columns and 'Cumplimiento' in df_linea_año.columns:
            # Agrupar por objetivo
            df_objetivos = df_linea_año.groupby('Objetivo').agg({
                'Cumplimiento': 'mean',
                'Indicador': 'nunique'
            }).reset_index()
            df_objetivos.columns = ['Objetivo', 'Cumplimiento', 'Indicadores']
            df_objetivos['Cumplimiento'] = df_objetivos['Cumplimiento'].round(1)
            df_objetivos = df_objetivos.sort_values('Cumplimiento', ascending=True)

            # Colores según semáforo
            colores = [obtener_color_semaforo(c) for c in df_objetivos['Cumplimiento']]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=df_objetivos['Objetivo'],
                x=df_objetivos['Cumplimiento'],
                orientation='h',
                marker_color=colores,
                text=[f"{c:.1f}%" for c in df_objetivos['Cumplimiento']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<extra></extra>'
            ))

            fig.update_layout(
                xaxis=dict(
                    title="% Cumplimiento",
                    range=[0, 120]
                ),
                yaxis=dict(title=""),
                height=max(300, len(df_objetivos) * 50),
                margin=dict(l=20, r=50, t=20, b=40),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            # Líneas de referencia
            fig.add_vline(x=90, line_dash="dash", line_color=COLORS['success'], opacity=0.5)
            fig.add_vline(x=70, line_dash="dash", line_color=COLORS['warning'], opacity=0.5)

            config = {'displayModeBar': True, 'responsive': True}
            st.plotly_chart(fig, use_container_width=True, config=config)
        else:
            st.info("No hay datos de cumplimiento por objetivo disponibles.")

    with col_obj:
        st.markdown("### 🎯 Lista de Objetivos")

        if 'Objetivo' in df_linea_año.columns:
            objetivos_unicos = df_linea_año.groupby('Objetivo').agg({
                'Cumplimiento': 'mean',
                'Indicador': 'nunique'
            }).reset_index()

            objetivos_unicos = objetivos_unicos.sort_values('Cumplimiento', ascending=False)

            for _, row in objetivos_unicos.iterrows():
                cumpl = row['Cumplimiento'] if pd.notna(row['Cumplimiento']) else 0
                st.markdown(
                    crear_objetivo_card_html(
                        objetivo=row['Objetivo'],
                        indicadores=row['Indicador'],
                        cumplimiento=cumpl
                    ),
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # Evolución histórica de la línea
    st.markdown("### 📈 Evolución Histórica de la Línea")

    if 'Año' in df_linea.columns and 'Cumplimiento' in df_linea.columns:
        # Agrupar por año
        df_historico = df_linea.groupby('Año').agg({
            'Cumplimiento': 'mean',
            'Indicador': 'nunique'
        }).reset_index()
        df_historico = df_historico.sort_values('Año')

        # Crear etiquetas
        etiquetas = []
        for año in df_historico['Año']:
            if año == 2021:
                etiquetas.append(f"{int(año)}\n(Línea Base)")
            else:
                etiquetas.append(str(int(año)))

        fig_hist = go.Figure()

        # Área de fondo para semáforo
        fig_hist.add_hrect(y0=90, y1=120, fillcolor=COLORS['success'], opacity=0.1, line_width=0)
        fig_hist.add_hrect(y0=70, y1=90, fillcolor=COLORS['warning'], opacity=0.1, line_width=0)
        fig_hist.add_hrect(y0=0, y1=70, fillcolor=COLORS['danger'], opacity=0.1, line_width=0)

        fig_hist.add_trace(go.Scatter(
            x=etiquetas,
            y=df_historico['Cumplimiento'],
            mode='lines+markers+text',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=12, color=COLORS['primary']),
            text=[f"{c:.1f}%" for c in df_historico['Cumplimiento']],
            textposition='top center',
            hovertemplate='<b>Año %{x}</b><br>Cumplimiento: %{y:.1f}%<extra></extra>'
        ))

        fig_hist.update_layout(
            title=f"Tendencia de Cumplimiento: {linea_seleccionada}",
            xaxis=dict(title="Año"),
            yaxis=dict(title="% Cumplimiento", range=[0, 120]),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        config = {'displayModeBar': True, 'responsive': True}
        st.plotly_chart(fig_hist, use_container_width=True, config=config)

    st.markdown("---")

    # Tabla de indicadores de la línea
    st.markdown("### 📋 Indicadores de la Línea")

    # Filtros adicionales
    col_filtro1, col_filtro2 = st.columns(2)

    with col_filtro1:
        # Filtro por objetivo
        objetivos_lista = ['Todos'] + obtener_lista_objetivos(df_unificado, linea_seleccionada)
        objetivo_filtro = st.selectbox("Filtrar por Objetivo:", objetivos_lista)

    with col_filtro2:
        # Filtro por estado
        estado_filtro = st.selectbox(
            "Filtrar por Estado:",
            ['Todos', '✅ Meta cumplida', '⚠️ En progreso', '❌ Requiere atención']
        )

    # Aplicar filtros
    df_mostrar = df_linea_año.copy()

    if objetivo_filtro != 'Todos' and 'Objetivo' in df_mostrar.columns:
        df_mostrar = df_mostrar[df_mostrar['Objetivo'] == objetivo_filtro]

    if estado_filtro != 'Todos' and 'Cumplimiento' in df_mostrar.columns:
        if estado_filtro == '✅ Meta cumplida':
            df_mostrar = df_mostrar[df_mostrar['Cumplimiento'] >= 90]
        elif estado_filtro == '⚠️ En progreso':
            df_mostrar = df_mostrar[(df_mostrar['Cumplimiento'] >= 70) & (df_mostrar['Cumplimiento'] < 90)]
        else:
            df_mostrar = df_mostrar[df_mostrar['Cumplimiento'] < 70]

    # Preparar tabla
    columnas_mostrar = ['Indicador', 'Objetivo', 'Meta', 'Ejecución', 'Cumplimiento']
    columnas_disponibles = [c for c in columnas_mostrar if c in df_mostrar.columns]

    if columnas_disponibles:
        df_tabla = df_mostrar[columnas_disponibles].drop_duplicates()

        if 'Cumplimiento' in df_tabla.columns:
            df_tabla['Estado'] = df_tabla['Cumplimiento'].apply(
                lambda x: '✅' if x >= 90 else '⚠️' if x >= 70 else '❌' if pd.notna(x) else '❓'
            )
            df_tabla['Cumplimiento'] = df_tabla['Cumplimiento'].apply(
                lambda x: f"{x:.1f}%" if pd.notna(x) else "N/D"
            )

        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        st.caption(f"Mostrando {len(df_tabla)} indicadores")
    else:
        st.info("No hay datos disponibles para mostrar.")
