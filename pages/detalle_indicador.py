"""
Página 3: Detalle de Indicadores
Análisis individual de cada indicador con histórico y IA
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    COLORS, calcular_cumplimiento, obtener_color_semaforo,
    filtrar_por_linea, filtrar_por_objetivo, obtener_lista_objetivos,
    obtener_lista_indicadores, obtener_historico_indicador
)
from utils.visualizations import (
    crear_grafico_historico, crear_grafico_tendencia,
    crear_indicador_semaforo_html
)
from utils.ai_analysis import (
    generar_analisis_indicador, preparar_historico_para_analisis
)


def mostrar_pagina():
    """
    Renderiza la página de Detalle de Indicadores.
    """
    st.title("🔍 Detalle de Indicadores")
    st.markdown("---")

    # Obtener datos
    df_unificado = st.session_state.get('df_unificado')
    df_base = st.session_state.get('df_base')

    if df_unificado is None or df_unificado.empty:
        st.error("⚠️ No se pudieron cargar los datos.")
        return

    # Filtros jerárquicos
    st.markdown("### 🔎 Selección de Indicador")

    col1, col2 = st.columns(2)

    with col1:
        # Selector de Línea Estratégica
        lineas_disponibles = []
        if 'Linea' in df_unificado.columns:
            lineas_disponibles = sorted(df_unificado['Linea'].dropna().unique().tolist())

        if not lineas_disponibles:
            st.warning("No se encontraron líneas estratégicas.")
            return

        linea_seleccionada = st.selectbox(
            "Linea Estrategica:",
            lineas_disponibles,
            key="linea_detalle"
        )

    with col2:
        # Selector de Objetivo (dependiente de la línea)
        objetivos_disponibles = obtener_lista_objetivos(df_unificado, linea_seleccionada)

        if not objetivos_disponibles:
            st.warning("No se encontraron objetivos para esta línea.")
            return

        objetivo_seleccionado = st.selectbox(
            "🎯 Objetivo:",
            objetivos_disponibles,
            key="objetivo_detalle"
        )

    # Selector de Indicador
    indicadores_disponibles = obtener_lista_indicadores(
        df_unificado,
        linea_seleccionada,
        objetivo_seleccionado
    )

    if not indicadores_disponibles:
        st.warning("No se encontraron indicadores para esta selección.")
        return

    # Búsqueda de indicadores
    col_busqueda, col_selector = st.columns([1, 2])

    with col_busqueda:
        busqueda = st.text_input("🔍 Buscar indicador:", placeholder="Escriba para filtrar...")

    indicadores_filtrados = indicadores_disponibles
    if busqueda:
        indicadores_filtrados = [i for i in indicadores_disponibles if busqueda.lower() in i.lower()]

    with col_selector:
        if indicadores_filtrados:
            indicador_seleccionado = st.selectbox(
                "📊 Indicador:",
                indicadores_filtrados,
                key="indicador_detalle"
            )
        else:
            st.warning("No se encontraron indicadores con ese término de búsqueda.")
            return

    st.markdown("---")

    # Obtener datos del indicador
    df_indicador = df_unificado[df_unificado['Indicador'] == indicador_seleccionado].copy()

    if df_indicador.empty:
        st.warning("No se encontraron datos para este indicador.")
        return

    # Información del indicador
    col_info, col_estado = st.columns([3, 1])

    with col_info:
        st.markdown(f"## {indicador_seleccionado}")

        # Obtener descripción y metadatos del indicador
        descripcion = ""
        periodicidad = ""
        sentido = "Creciente"
        meta_pdi = ""

        if df_base is not None and 'Indicador' in df_base.columns:
            indicador_base = df_base[df_base['Indicador'] == indicador_seleccionado]
            if not indicador_base.empty:
                fila = indicador_base.iloc[0]
                if 'Periodicidad' in fila:
                    periodicidad = fila.get('Periodicidad', '')
                if 'Sentido' in fila:
                    sentido = fila.get('Sentido', 'Creciente')
                if 'Meta_PDI' in fila:
                    meta_pdi = fila.get('Meta_PDI', '')

        # Información en badges
        info_cols = st.columns(4)

        with info_cols[0]:
            st.markdown(f"""
            <div style="background: {COLORS['light']}; padding: 10px; border-radius: 5px; text-align: center;">
                <small style="color: {COLORS['gray']};">Línea</small><br>
                <strong>{linea_seleccionada}</strong>
            </div>
            """, unsafe_allow_html=True)

        with info_cols[1]:
            st.markdown(f"""
            <div style="background: {COLORS['light']}; padding: 10px; border-radius: 5px; text-align: center;">
                <small style="color: {COLORS['gray']};">Periodicidad</small><br>
                <strong>{periodicidad if periodicidad else 'N/D'}</strong>
            </div>
            """, unsafe_allow_html=True)

        with info_cols[2]:
            st.markdown(f"""
            <div style="background: {COLORS['light']}; padding: 10px; border-radius: 5px; text-align: center;">
                <small style="color: {COLORS['gray']};">Sentido</small><br>
                <strong>{'📈' if sentido == 'Creciente' else '📉'} {sentido}</strong>
            </div>
            """, unsafe_allow_html=True)

        with info_cols[3]:
            st.markdown(f"""
            <div style="background: {COLORS['light']}; padding: 10px; border-radius: 5px; text-align: center;">
                <small style="color: {COLORS['gray']};">Meta PDI</small><br>
                <strong>{meta_pdi if meta_pdi else 'N/D'}</strong>
            </div>
            """, unsafe_allow_html=True)

    with col_estado:
        # Estado actual (último año)
        año_actual = df_indicador['Año'].max() if 'Año' in df_indicador.columns else 2025
        df_actual = df_indicador[df_indicador['Año'] == año_actual] if 'Año' in df_indicador.columns else df_indicador

        cumplimiento_actual = 0
        if 'Cumplimiento' in df_actual.columns and not df_actual.empty:
            cumplimiento_actual = df_actual['Cumplimiento'].mean()
            cumplimiento_actual = cumplimiento_actual if pd.notna(cumplimiento_actual) else 0

        color = obtener_color_semaforo(cumplimiento_actual)

        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 25px;
            background: {color};
            color: {'#333' if color == COLORS['warning'] else 'white'};
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        ">
            <div style="font-size: 12px; opacity: 0.9; text-transform: uppercase;">
                Cumplimiento {int(año_actual)}
            </div>
            <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">
                {cumplimiento_actual:.1f}%
            </div>
            <div style="font-size: 14px;">
                {'✅ Meta cumplida' if cumplimiento_actual >= 90 else '⚠️ En progreso' if cumplimiento_actual >= 70 else '❌ Requiere atención'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Gráfico histórico
    st.markdown("### 📊 Evolución Histórica 2021-2025")

    if 'Año' in df_indicador.columns:
        # Preparar datos para el gráfico
        df_historico = df_indicador.groupby('Año').agg({
            'Meta': 'mean',
            'Ejecución': 'mean'
        }).reset_index()
        df_historico = df_historico.sort_values('Año')

        # Calcular cumplimiento
        df_historico['Cumplimiento'] = df_historico.apply(
            lambda x: calcular_cumplimiento(x['Meta'], x['Ejecución']),
            axis=1
        )

        # Crear gráfico
        fig = crear_grafico_historico(df_historico, indicador_seleccionado)
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de tendencia adicional
        with st.expander("📈 Ver gráfico de tendencia de cumplimiento"):
            fig_tendencia = crear_grafico_tendencia(df_historico, indicador_seleccionado)
            st.plotly_chart(fig_tendencia, use_container_width=True)
    else:
        st.warning("No hay datos históricos disponibles para este indicador.")

    st.markdown("---")

    # Análisis con IA
    st.markdown("### 🤖 Análisis Inteligente del Indicador")

    with st.expander("Ver análisis generado por IA", expanded=True):
        with st.spinner("Analizando indicador..."):
            # Preparar datos históricos
            historico_data = preparar_historico_para_analisis(df_historico if 'df_historico' in dir() else df_indicador)

            analisis = generar_analisis_indicador(
                nombre_indicador=indicador_seleccionado,
                linea=linea_seleccionada,
                descripcion=descripcion,
                historico_data=historico_data,
                sentido=sentido
            )

            st.markdown(f"""
            <div class="ai-analysis">
                {analisis}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabla de datos históricos detallados
    st.markdown("### 📋 Datos Históricos Detallados")

    # Preparar tabla
    if 'Año' in df_indicador.columns:
        df_tabla = df_indicador.groupby('Año').agg({
            'Meta': 'mean',
            'Ejecución': 'mean'
        }).reset_index()
        df_tabla = df_tabla.sort_values('Año')

        # Calcular cumplimiento
        df_tabla['Cumplimiento'] = df_tabla.apply(
            lambda x: calcular_cumplimiento(x['Meta'], x['Ejecución']),
            axis=1
        )

        # Agregar estado y nota para línea base
        df_tabla['Estado'] = df_tabla['Cumplimiento'].apply(
            lambda x: '✅ Meta cumplida' if pd.notna(x) and x >= 90 else '⚠️ En progreso' if pd.notna(x) and x >= 70 else '❌ Requiere atención' if pd.notna(x) else 'N/D'
        )

        df_tabla['Nota'] = df_tabla['Año'].apply(
            lambda x: '📍 Línea Base' if x == 2021 else ''
        )

        # Formatear columnas
        df_tabla['Meta'] = df_tabla['Meta'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/D")
        df_tabla['Ejecución'] = df_tabla['Ejecución'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/D")
        df_tabla['Cumplimiento'] = df_tabla['Cumplimiento'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/D")
        df_tabla['Año'] = df_tabla['Año'].astype(int)

        # Reordenar columnas
        df_tabla = df_tabla[['Año', 'Meta', 'Ejecución', 'Cumplimiento', 'Estado', 'Nota']]

        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True
        )
    else:
        # Mostrar datos disponibles
        columnas_mostrar = ['Meta', 'Ejecución', 'Cumplimiento']
        columnas_disponibles = [c for c in columnas_mostrar if c in df_indicador.columns]

        if columnas_disponibles:
            st.dataframe(
                df_indicador[columnas_disponibles],
                use_container_width=True,
                hide_index=True
            )

    st.markdown("---")

    # Sección de comparación y exportación
    col_comp, col_export = st.columns(2)

    with col_comp:
        st.markdown("### 🔄 Comparar con otro indicador")

        # Selector para comparación
        otros_indicadores = [i for i in indicadores_disponibles if i != indicador_seleccionado]

        if otros_indicadores:
            indicador_comparar = st.selectbox(
                "Seleccione indicador para comparar:",
                ["Ninguno"] + otros_indicadores
            )

            if indicador_comparar != "Ninguno":
                df_comparar = df_unificado[df_unificado['Indicador'] == indicador_comparar].copy()

                if not df_comparar.empty and 'Año' in df_comparar.columns:
                    df_comp = df_comparar.groupby('Año').agg({
                        'Cumplimiento': 'mean'
                    }).reset_index()
                    df_comp = df_comp.sort_values('Año')

                    # Gráfico de comparación
                    fig_comp = go.Figure()

                    # Indicador principal
                    if 'df_historico' in dir():
                        fig_comp.add_trace(go.Scatter(
                            x=df_historico['Año'],
                            y=df_historico['Cumplimiento'],
                            name=indicador_seleccionado[:30] + "...",
                            line=dict(color=COLORS['primary'], width=3),
                            marker=dict(size=10)
                        ))

                    # Indicador de comparación
                    fig_comp.add_trace(go.Scatter(
                        x=df_comp['Año'],
                        y=df_comp['Cumplimiento'],
                        name=indicador_comparar[:30] + "...",
                        line=dict(color=COLORS['accent'], width=3, dash='dash'),
                        marker=dict(size=10)
                    ))

                    fig_comp.update_layout(
                        title="Comparación de Cumplimiento",
                        xaxis_title="Año",
                        yaxis_title="% Cumplimiento",
                        yaxis=dict(range=[0, 120]),
                        height=350,
                        plot_bgcolor='white',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.3,
                            xanchor="center",
                            x=0.5
                        )
                    )

                    st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No hay otros indicadores disponibles para comparar.")

    with col_export:
        st.markdown("### 📥 Exportar Datos")

        if st.button("📊 Preparar Excel del Indicador", use_container_width=True):
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    # Datos del indicador
                    df_indicador.to_excel(writer, sheet_name='Datos_Indicador', index=False)

                    # Resumen histórico
                    if 'df_historico' in dir() and not df_historico.empty:
                        df_historico.to_excel(writer, sheet_name='Resumen_Historico', index=False)

                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=buffer.getvalue(),
                    file_name=f"indicador_{indicador_seleccionado[:20]}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error al generar Excel: {str(e)}")

        if st.button("🔄 Regenerar Análisis IA", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Información adicional
    st.markdown("---")
    st.markdown(f"""
    <div class="info-box">
        <strong>📌 Información del análisis:</strong>
        <ul>
            <li><strong>Indicador:</strong> {indicador_seleccionado}</li>
            <li><strong>Línea Estratégica:</strong> {linea_seleccionada}</li>
            <li><strong>Objetivo:</strong> {objetivo_seleccionado}</li>
            <li><strong>Año 2021:</strong> Considerado como Línea Base del PDI</li>
            <li><strong>Sentido:</strong> {sentido} - {'valores mayores indican mejor desempeño' if sentido == 'Creciente' else 'valores menores indican mejor desempeño'}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
