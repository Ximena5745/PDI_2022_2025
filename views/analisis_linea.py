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
    COLORS, COLORES_LINEAS, calcular_metricas_generales, obtener_color_semaforo,
    filtrar_por_linea, obtener_lista_objetivos, LINEAS_ESTRATEGICAS,
    obtener_cumplimiento_cascada
)
from utils.visualizations import (
    crear_objetivo_card_html, crear_tarjeta_kpi, crear_tabla_cascada_html,
    crear_grafico_cascada_icicle
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
    df_base = st.session_state.get('df_base')

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

    # Solo considerar años 2022-2026 (omitir 2021 línea base)
    if 'Año' in df_linea_año.columns:
        df_linea_año = df_linea_año[df_linea_año['Año'].isin([2022, 2023, 2024, 2025, 2026])]

    # Filtrar solo registros con Fuente = 'Avance' para los cálculos
    if 'Fuente' in df_linea_año.columns:
        df_linea_año = df_linea_año[df_linea_año['Fuente'] == 'Avance']

    # Omitir registros con cumplimiento vacío
    if 'Cumplimiento' in df_linea_año.columns:
        df_linea_año = df_linea_año[df_linea_año['Cumplimiento'].notna()]

    # Calcular métricas de la línea
    total_indicadores = df_linea_año['Indicador'].nunique() if 'Indicador' in df_linea_año.columns else len(df_linea_año)
    total_objetivos = df_linea_año['Objetivo'].nunique() if 'Objetivo' in df_linea_año.columns else 0

    cumplimiento_linea = 0
    indicadores_cumplidos = 0
    en_progreso = 0
    no_cumplidos = 0

    if 'Cumplimiento' in df_linea_año.columns and not df_linea_año.empty:
        cumplimiento_linea = df_linea_año['Cumplimiento'].mean()
        cumplimiento_linea = cumplimiento_linea if pd.notna(cumplimiento_linea) else 0
        indicadores_cumplidos = len(df_linea_año[df_linea_año['Cumplimiento'] >= 100])
        en_progreso = len(df_linea_año[(df_linea_año['Cumplimiento'] >= 80) & (df_linea_año['Cumplimiento'] < 100)])
        no_cumplidos = len(df_linea_año[df_linea_año['Cumplimiento'] < 80])

    # Importar COLORS para los colores de KPIs
    color_cumpl = obtener_color_semaforo(cumplimiento_linea)

    # Sticky KPIs - Siempre visibles al hacer scroll
    st.markdown(f'''
        <div class="sticky-kpis">
            <div class="kpi-mini" style="background:{color_cumpl};color:white;">
                <b>{cumplimiento_linea:.1f}%</b><br>
                <small>Cumplimiento</small>
            </div>
            <div class="kpi-mini" style="background:#28a745;color:white;">
                <b>{indicadores_cumplidos}</b><br>
                <small>Cumplidos</small>
            </div>
            <div class="kpi-mini" style="background:#ffc107;color:black;">
                <b>{en_progreso}</b><br>
                <small>En Progreso</small>
            </div>
            <div class="kpi-mini" style="background:#dc3545;color:white;">
                <b>{no_cumplidos}</b><br>
                <small>No Cumplidos</small>
            </div>
        </div>
        <div class="main-content-spacer"></div>
    ''', unsafe_allow_html=True)

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
            label="Indicadores Cumplidos",
            value=indicadores_cumplidos,
            delta=f"{(indicadores_cumplidos/total_indicadores*100):.0f}%" if total_indicadores > 0 else "0%"
        )

    st.markdown("---")

    # Análisis IA de la línea
    st.markdown("### 🤖 Análisis Inteligente")

    with st.expander(f"Ver análisis de {linea_seleccionada}", expanded=False):
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

            # Usar el color de la línea estratégica para todas las barras
            color_linea = COLORES_LINEAS.get(linea_seleccionada, COLORS['primary'])

            # Color distintivo para los labels de cumplimiento
            color_label_cumplimiento = '#E91E63'

            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=df_objetivos['Objetivo'],
                x=df_objetivos['Cumplimiento'],
                orientation='h',
                marker_color=color_linea,
                text=[f"{c:.1f}%" for c in df_objetivos['Cumplimiento']],
                textposition='outside',
                textfont=dict(size=11, color=color_label_cumplimiento, weight='bold'),
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
            fig.add_vline(x=100, line_dash="dash", line_color=COLORS['success'], opacity=0.5)
            fig.add_vline(x=80, line_dash="dash", line_color=COLORS['warning'], opacity=0.5)

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
        # Filtrar solo años 2022-2025 (periodo PDI)
        df_linea_hist = df_linea[df_linea['Año'].isin([2022, 2023, 2024, 2025])]

        # Agrupar por año
        df_historico = df_linea_hist.groupby('Año').agg({
            'Cumplimiento': 'mean',
            'Indicador': 'nunique'
        }).reset_index()
        df_historico = df_historico.sort_values('Año')

        # Crear etiquetas
        etiquetas = [str(int(año)) for año in df_historico['Año']]

        fig_hist = go.Figure()

        # Área de fondo para semáforo
        fig_hist.add_hrect(y0=100, y1=120, fillcolor=COLORS['success'], opacity=0.1, line_width=0)
        fig_hist.add_hrect(y0=80, y1=100, fillcolor=COLORS['warning'], opacity=0.1, line_width=0)
        fig_hist.add_hrect(y0=0, y1=80, fillcolor=COLORS['danger'], opacity=0.1, line_width=0)

        # Obtener color de la línea seleccionada
        color_linea = COLORES_LINEAS.get(linea_seleccionada, COLORS['primary'])

        # Convertir cumplimiento de decimal a porcentaje
        cumpl_pct = df_historico['Cumplimiento'] * 100

        fig_hist.add_trace(go.Scatter(
            x=etiquetas,
            y=cumpl_pct,
            mode='lines+markers+text',
            line=dict(color=color_linea, width=3),
            marker=dict(size=12, color=color_linea),
            text=[f"{c:.1f}%" for c in cumpl_pct],
            textposition='top center',
            hovertemplate='<b>Año %{x}</b><br>Cumplimiento: %{y:.1f}%<extra></extra>'
        ))

        fig_hist.update_layout(
            title=f"Tendencia de Cumplimiento: {linea_seleccionada}",
            xaxis=dict(
                title="Año",
                type='category',  # Forzar eje categórico
                categoryorder='array',
                categoryarray=['2022', '2023', '2024', '2025']
            ),
            yaxis=dict(title="% Cumplimiento", range=[0, 130]),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        config = {'displayModeBar': True, 'responsive': True}
        st.plotly_chart(fig_hist, use_container_width=True, config=config)

    st.markdown("---")

    # Vista de Cascada para la línea seleccionada
    st.markdown(f"### 🌊 Cumplimiento en Cascada: {linea_seleccionada}")

    # Obtener datos de cascada con 3 niveles (Línea → Objetivo → Meta PDI)
    df_cascada_completa = obtener_cumplimiento_cascada(df_unificado, df_base, año_actual, max_niveles=3)
    df_cascada_linea = df_cascada_completa[df_cascada_completa['Linea'] == linea_seleccionada] if not df_cascada_completa.empty else pd.DataFrame()

    if not df_cascada_linea.empty:
        with st.expander("📊 Ver Desglose Jerárquico Completo", expanded=False):
            st.markdown(f"""
            **Estructura de cumplimiento para {linea_seleccionada}:**

            Esta vista muestra la cascada desde objetivos hasta metas PDI.
            """)

            # Dos columnas: gráfico sunburst y tabla
            col_graf, col_tabla = st.columns([1, 1])

            with col_graf:
                # Gráfico sunburst para esta línea
                fig_cascada = crear_grafico_cascada_icicle(df_cascada_linea, titulo=f"Cascada: {linea_seleccionada}")
                config = {'displayModeBar': True, 'responsive': True}
                st.plotly_chart(fig_cascada, use_container_width=True, config=config)

            with col_tabla:
                # Tabla HTML con jerarquía
                tabla_cascada = crear_tabla_cascada_html(df_cascada_linea)
                import streamlit.components.v1 as components
                components.html(tabla_cascada, height=400, scrolling=True)

            # Resumen estadístico
            st.markdown("---")
            col_stat1, col_stat2, col_stat3 = st.columns(3)

            with col_stat1:
                total_objetivos = len(df_cascada_linea[df_cascada_linea['Nivel'] == 2])
                st.metric("Objetivos", total_objetivos)

            with col_stat2:
                total_metas_pdi = len(df_cascada_linea[(df_cascada_linea['Nivel'] == 3) & (df_cascada_linea['Meta_PDI'] != 'N/D')])
                st.metric("Metas PDI Definidas", total_metas_pdi)

            with col_stat3:
                # Contar indicadores únicos de los datos filtrados
                total_indicadores_linea = df_linea_año['Indicador'].nunique() if 'Indicador' in df_linea_año.columns else 0
                st.metric("Indicadores Totales", total_indicadores_linea)
    else:
        # Mostrar valores en 0 cuando no hay datos
        st.info("No hay datos de cascada disponibles para esta línea.")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Objetivos", 0)
        with col_stat2:
            st.metric("Metas PDI Definidas", 0)
        with col_stat3:
            st.metric("Indicadores Totales", 0)

    st.markdown("---")

    # Tabla de indicadores de la línea (oculta por defecto)
    st.markdown("### 📋 Indicadores de la Línea")

    with st.expander("Ver tabla de indicadores", expanded=False):
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
                ['Todos', '✅ Meta cumplida', '⚠️ Alerta', '❌ Peligro']
            )

        # Aplicar filtros
        df_mostrar = df_linea_año.copy()

        if objetivo_filtro != 'Todos' and 'Objetivo' in df_mostrar.columns:
            df_mostrar = df_mostrar[df_mostrar['Objetivo'] == objetivo_filtro]

        if estado_filtro != 'Todos' and 'Cumplimiento' in df_mostrar.columns:
            if estado_filtro == '✅ Meta cumplida':
                df_mostrar = df_mostrar[df_mostrar['Cumplimiento'] >= 100]
            elif estado_filtro == '⚠️ Alerta':
                df_mostrar = df_mostrar[(df_mostrar['Cumplimiento'] >= 80) & (df_mostrar['Cumplimiento'] < 100)]
            else:
                df_mostrar = df_mostrar[df_mostrar['Cumplimiento'] < 80]

        # Preparar tabla
        columnas_mostrar = ['Indicador', 'Objetivo', 'Meta', 'Ejecución', 'Cumplimiento']
        columnas_disponibles = [c for c in columnas_mostrar if c in df_mostrar.columns]

        if columnas_disponibles:
            df_tabla = df_mostrar[columnas_disponibles].drop_duplicates()

            # Agregar Meta_PDI desde df_base
            if df_base is not None and 'Indicador' in df_base.columns and 'Meta_PDI' in df_base.columns:
                meta_pdi_dict = df_base.set_index('Indicador')['Meta_PDI'].to_dict()
                df_tabla['Meta PDI'] = df_tabla['Indicador'].map(meta_pdi_dict)

            if 'Cumplimiento' in df_tabla.columns:
                df_tabla['Estado'] = df_tabla['Cumplimiento'].apply(
                    lambda x: '✅' if x >= 100 else '⚠️' if x >= 80 else '❌' if pd.notna(x) else '❓'
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
