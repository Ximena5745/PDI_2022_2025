"""
Página 2: Análisis por Línea Estratégica
Detalle del desempeño de cada línea del PDI
Versión optimizada con Tabs para reducir scroll
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    COLORS, COLORES_LINEAS, obtener_color_semaforo,
    filtrar_por_linea, obtener_lista_objetivos,
    obtener_cumplimiento_cascada, calcular_estado_proyectos
)
from utils.visualizations import (
    crear_objetivo_card_html, crear_tabla_cascada_html,
    crear_grafico_cascada_icicle, crear_grafico_proyectos
)
from utils.ai_analysis import (
    generar_analisis_linea, preparar_objetivos_para_analisis
)


def mostrar_pagina():
    """
    Renderiza la página de Análisis por Línea Estratégica con estructura de Tabs.
    """
    # Header compacto
    st.markdown("""
    <div style="background: linear-gradient(135deg, #003d82 0%, #0056b3 100%);
                padding: 15px; border-radius: 10px; color: white; margin-bottom: 15px; text-align: center;">
        <div style="font-size: 24px; font-weight: bold;">📈 Análisis por Línea Estratégica</div>
    </div>
    """, unsafe_allow_html=True)

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

    # Selector de línea estratégica (siempre visible)
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

    # Filtrar datos por línea
    df_linea = filtrar_por_linea(df_unificado, linea_seleccionada)

    if 'Año' in df_linea.columns:
        df_linea_año = df_linea[df_linea['Año'] == año_actual]
    else:
        df_linea_año = df_linea

    # Solo considerar años 2022-2026 (omitir 2021 línea base)
    if 'Año' in df_linea_año.columns:
        df_linea_año = df_linea_año[df_linea_año['Año'].isin([2022, 2023, 2024, 2025, 2026])]

    # Filtrar solo registros con Fuente = 'Avance'
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

    # Obtener datos de cascada
    df_cascada_completa = obtener_cumplimiento_cascada(df_unificado, df_base, año_actual, max_niveles=3)
    df_cascada_linea = df_cascada_completa[df_cascada_completa['Linea'] == linea_seleccionada] if not df_cascada_completa.empty else pd.DataFrame()

    # Calcular estado de proyectos para la línea seleccionada
    df_proyectos_linea = df_unificado[df_unificado['Linea'] == linea_seleccionada] if 'Linea' in df_unificado.columns else df_unificado
    estado_proyectos_linea = calcular_estado_proyectos(df_proyectos_linea, año_actual)

    # Color de la línea
    color_linea = COLORES_LINEAS.get(linea_seleccionada, COLORS['primary'])
    color_cumpl = obtener_color_semaforo(cumplimiento_linea)

    # ============================================================
    # TABS PRINCIPALES
    # ============================================================
    tab_resumen, tab_analisis, tab_indicadores = st.tabs([
        "📊 Resumen",
        "📈 Análisis Detallado",
        "📋 Indicadores"
    ])

    # ============================================================
    # TAB 1: RESUMEN
    # ============================================================
    with tab_resumen:
        # KPIs usando st.metric nativo (mejor compatibilidad con columnas)
        st.markdown(f"#### 🎯 Métricas: {linea_seleccionada}")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="📊 Cumplimiento",
                value=f"{cumplimiento_linea:.1f}%",
                help="Promedio de cumplimiento de la línea"
            )

        with col2:
            st.metric(
                label="✅ Cumplidos",
                value=indicadores_cumplidos,
                help="Indicadores con ≥100%"
            )

        with col3:
            st.metric(
                label="⚠️ En Progreso",
                value=en_progreso,
                help="Indicadores entre 80-99%"
            )

        with col4:
            st.metric(
                label="❌ No Cumplidos",
                value=no_cumplidos,
                help="Indicadores <80%"
            )

        with col5:
            st.metric(
                label="🎯 Objetivos",
                value=total_objetivos,
                help="Total de objetivos en la línea"
            )

        st.markdown("---")

        # Dos columnas: Gráfico por objetivo + Lista de objetivos
        col_graf, col_obj = st.columns([1, 1])

        with col_graf:
            st.markdown("#### 📊 Cumplimiento por Objetivo")

            if 'Objetivo' in df_linea_año.columns and 'Cumplimiento' in df_linea_año.columns:
                df_objetivos = df_linea_año.groupby('Objetivo').agg({
                    'Cumplimiento': 'mean',
                    'Indicador': 'nunique'
                }).reset_index()
                df_objetivos.columns = ['Objetivo', 'Cumplimiento', 'Indicadores']
                df_objetivos['Cumplimiento'] = df_objetivos['Cumplimiento'].round(1)
                df_objetivos = df_objetivos.sort_values('Cumplimiento', ascending=True)

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=df_objetivos['Objetivo'],
                    x=df_objetivos['Cumplimiento'],
                    orientation='h',
                    marker_color=color_linea,
                    text=[f"{c:.1f}%" for c in df_objetivos['Cumplimiento']],
                    textposition='outside',
                    textfont=dict(size=11, color='#E91E63', weight='bold'),
                    hovertemplate='<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<extra></extra>'
                ))

                fig.update_layout(
                    xaxis=dict(title="% Cumplimiento", range=[0, 120]),
                    yaxis=dict(title=""),
                    height=max(250, len(df_objetivos) * 45),
                    margin=dict(l=20, r=50, t=10, b=40),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                fig.add_vline(x=100, line_dash="dash", line_color=COLORS['success'], opacity=0.5)
                fig.add_vline(x=80, line_dash="dash", line_color=COLORS['warning'], opacity=0.5)

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No hay datos de cumplimiento por objetivo.")

        with col_obj:
            st.markdown("#### 🎯 Lista de Objetivos")

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

        # Gráfico de proyectos para la línea
        if estado_proyectos_linea['total_proyectos'] > 0:
            st.markdown("---")
            st.markdown(f"#### 📋 Proyectos de: {linea_seleccionada}")
            col_proy1, col_proy2, col_proy3 = st.columns([1, 2, 1])
            with col_proy2:
                fig_proyectos = crear_grafico_proyectos(
                    estado_proyectos_linea['finalizados'],
                    estado_proyectos_linea['en_ejecucion'],
                    estado_proyectos_linea['stand_by']
                )
                st.plotly_chart(fig_proyectos, use_container_width=True, config={'displayModeBar': False})
                st.info(f"📋 **{estado_proyectos_linea['total_proyectos']}** Proyectos | **{estado_proyectos_linea['finalizados']}** Finalizados | **{estado_proyectos_linea['en_ejecucion']}** En Ejecución | **{estado_proyectos_linea['stand_by']}** Stand by")

    # ============================================================
    # TAB 2: ANÁLISIS DETALLADO
    # ============================================================
    with tab_analisis:
        # Sub-tabs para organizar
        subtab_historia, subtab_cascada, subtab_ia = st.tabs([
            "📈 Evolución Histórica",
            "🌊 Cascada Jerárquica",
            "🤖 Análisis IA"
        ])

        with subtab_historia:
            st.markdown(f"#### Tendencia de Cumplimiento: {linea_seleccionada}")

            if 'Año' in df_linea.columns and 'Cumplimiento' in df_linea.columns:
                df_linea_hist = df_linea[df_linea['Año'].isin([2022, 2023, 2024, 2025])]
                df_historico = df_linea_hist.groupby('Año').agg({
                    'Cumplimiento': 'mean',
                    'Indicador': 'nunique'
                }).reset_index()
                df_historico = df_historico.sort_values('Año')

                etiquetas = [str(int(año)) for año in df_historico['Año']]

                fig_hist = go.Figure()
                fig_hist.add_hrect(y0=100, y1=120, fillcolor=COLORS['success'], opacity=0.1, line_width=0)
                fig_hist.add_hrect(y0=80, y1=100, fillcolor=COLORS['warning'], opacity=0.1, line_width=0)
                fig_hist.add_hrect(y0=0, y1=80, fillcolor=COLORS['danger'], opacity=0.1, line_width=0)

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
                    xaxis=dict(title="Año", type='category', categoryorder='array', categoryarray=['2022', '2023', '2024', '2025']),
                    yaxis=dict(title="% Cumplimiento", range=[0, 130]),
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )

                st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("No hay datos históricos disponibles.")

        with subtab_cascada:
            st.markdown(f"#### Desglose Jerárquico: {linea_seleccionada}")

            if not df_cascada_linea.empty:
                col_graf, col_tabla = st.columns([1, 1])

                with col_graf:
                    fig_cascada = crear_grafico_cascada_icicle(df_cascada_linea, titulo=f"Cascada: {linea_seleccionada}")
                    st.plotly_chart(fig_cascada, use_container_width=True, config={'displayModeBar': True})

                with col_tabla:
                    tabla_cascada = crear_tabla_cascada_html(df_cascada_linea)
                    import streamlit.components.v1 as components
                    components.html(tabla_cascada, height=450, scrolling=True)

                # Resumen estadístico
                st.markdown("---")
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Objetivos", len(df_cascada_linea[df_cascada_linea['Nivel'] == 2]))
                with col_s2:
                    st.metric("Metas PDI", len(df_cascada_linea[(df_cascada_linea['Nivel'] == 3) & (df_cascada_linea['Meta_PDI'] != 'N/D')]))
                with col_s3:
                    st.metric("Indicadores", total_indicadores)
            else:
                st.info("No hay datos de cascada disponibles para esta línea.")

        with subtab_ia:
            st.markdown(f"#### Análisis Inteligente: {linea_seleccionada}")

            with st.spinner("Generando análisis..."):
                objetivos_data = preparar_objetivos_para_analisis(df_linea, año_actual)
                analisis = generar_analisis_linea(
                    nombre_linea=linea_seleccionada,
                    total_indicadores=total_indicadores,
                    cumplimiento_promedio=cumplimiento_linea,
                    objetivos_data=objetivos_data
                )

                analisis_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', analisis)
                analisis_html = analisis_html.replace('\n', '<br>')

                st.markdown(f"""
                <div class="ai-analysis">
                    {analisis_html}
                </div>
                """, unsafe_allow_html=True)

    # ============================================================
    # TAB 3: INDICADORES
    # ============================================================
    with tab_indicadores:
        st.markdown(f"#### 📋 Indicadores de: {linea_seleccionada}")

        # Filtros en fila
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            objetivos_lista = ['Todos'] + obtener_lista_objetivos(df_unificado, linea_seleccionada)
            objetivo_filtro = st.selectbox("Filtrar por Objetivo:", objetivos_lista, key="filtro_obj")

        with col_f2:
            estado_filtro = st.selectbox(
                "Filtrar por Estado:",
                ['Todos', '✅ Cumplido', '⚠️ Alerta', '❌ Peligro'],
                key="filtro_estado"
            )

        # Aplicar filtros
        df_mostrar = df_linea_año.copy()

        # Filtrar solo indicadores (excluir proyectos)
        if 'Proyectos' in df_mostrar.columns:
            df_mostrar = df_mostrar[df_mostrar['Proyectos'] == 0]

        if objetivo_filtro != 'Todos' and 'Objetivo' in df_mostrar.columns:
            df_mostrar = df_mostrar[df_mostrar['Objetivo'] == objetivo_filtro]

        if estado_filtro != 'Todos' and 'Cumplimiento' in df_mostrar.columns:
            if estado_filtro == '✅ Cumplido':
                df_mostrar = df_mostrar[df_mostrar['Cumplimiento'] >= 100]
            elif estado_filtro == '⚠️ Alerta':
                df_mostrar = df_mostrar[(df_mostrar['Cumplimiento'] >= 80) & (df_mostrar['Cumplimiento'] < 100)]
            else:
                df_mostrar = df_mostrar[df_mostrar['Cumplimiento'] < 80]

        # Preparar tabla con Meta y Alerta visibles
        columnas_base = ['Indicador', 'Objetivo', 'Meta', 'Ejecución', 'Cumplimiento']
        columnas_disponibles = [c for c in columnas_base if c in df_mostrar.columns]

        if columnas_disponibles:
            df_tabla = df_mostrar[columnas_disponibles].drop_duplicates().copy()

            # Agregar Meta_PDI desde df_base
            if df_base is not None and 'Indicador' in df_base.columns and 'Meta_PDI' in df_base.columns:
                meta_pdi_dict = df_base.set_index('Indicador')['Meta_PDI'].to_dict()
                df_tabla['Meta PDI'] = df_tabla['Indicador'].map(meta_pdi_dict)

            # Agregar columna de Alerta con más detalle
            if 'Cumplimiento' in df_tabla.columns:
                def calcular_alerta(cumpl):
                    if pd.isna(cumpl):
                        return '❓ Sin datos'
                    elif cumpl >= 100:
                        return '✅ Cumplido'
                    elif cumpl >= 80:
                        return '⚠️ Alerta'
                    else:
                        return '❌ Crítico'

                # Guardar cumplimiento numérico para ordenar
                cumpl_numerico = df_tabla['Cumplimiento'].copy()
                df_tabla['Alerta'] = cumpl_numerico.apply(calcular_alerta)
                df_tabla['Cumplimiento'] = cumpl_numerico.apply(
                    lambda x: f"{x:.1f}%" if pd.notna(x) else "N/D"
                )

            # Reordenar columnas: Indicador, Objetivo, Meta PDI, Meta, Ejecución, Cumplimiento, Estado
            columnas_orden = ['Indicador', 'Objetivo', 'Meta PDI', 'Meta', 'Ejecución', 'Cumplimiento', 'Alerta']
            columnas_finales = [c for c in columnas_orden if c in df_tabla.columns]
            df_tabla = df_tabla[columnas_finales]

            # Mostrar tabla con configuración de columnas
            st.dataframe(
                df_tabla,
                use_container_width=True,
                hide_index=True,
                height=450,
                column_config={
                    "Indicador": st.column_config.TextColumn("Indicador", width="large"),
                    "Objetivo": st.column_config.TextColumn("Objetivo", width="medium"),
                    "Meta PDI": st.column_config.TextColumn("Meta PDI", width="small"),
                    "Meta": st.column_config.NumberColumn("Meta", format="%.2f"),
                    "Ejecución": st.column_config.NumberColumn("Ejecución", format="%.2f"),
                    "Cumplimiento": st.column_config.TextColumn("Cumplimiento", width="small"),
                    "Alerta": st.column_config.TextColumn("Estado", width="small")
                }
            )

            st.caption(f"Mostrando {len(df_tabla)} indicadores")
        else:
            st.info("No hay datos disponibles para mostrar.")

    # Footer compacto
    st.markdown(f"""
    <div style="text-align: center; color: {COLORS['gray']}; font-size: 11px; padding: 10px; margin-top: 20px;">
        <strong>Semáforo:</strong> 🟢 ≥100% | 🟡 80-99% | 🔴 <80% |
        <strong>Línea:</strong> {linea_seleccionada} |
        <strong>Corte:</strong> Diciembre {año_actual}
    </div>
    """, unsafe_allow_html=True)
