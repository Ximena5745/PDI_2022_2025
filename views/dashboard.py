"""
Página 1: Dashboard General
Informe Estratégico POLI 2025 - Resumen Ejecutivo
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    COLORS, calcular_metricas_generales, obtener_cumplimiento_por_linea,
    obtener_color_semaforo, exportar_a_excel, obtener_cumplimiento_cascada
)
from utils.visualizations import (
    crear_grafico_lineas, crear_grafico_semaforo, crear_tarjeta_kpi,
    crear_grafico_cascada, crear_tabla_cascada_html
)
from utils.ai_analysis import (
    generar_analisis_general, preparar_lineas_para_analisis
)


def mostrar_pagina():
    """
    Renderiza la página del Dashboard General.
    """
    # Header
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">📊 Informe Estratégico POLI 2025</div>
        <div class="header-subtitle">Plan de Desarrollo Institucional | Seguimiento y Monitoreo</div>
    </div>
    """, unsafe_allow_html=True)

    # Obtener datos del estado de sesión
    df_unificado = st.session_state.get('df_unificado')
    df_base = st.session_state.get('df_base')

    if df_unificado is None or df_unificado.empty:
        st.error("⚠️ No se pudieron cargar los datos. Verifique que el archivo Excel existe y no está abierto en otro programa.")
        return

    # Calcular métricas generales
    año_actual = 2025
    if 'Año' in df_unificado.columns:
        año_actual = int(df_unificado['Año'].max())

    metricas = calcular_metricas_generales(df_unificado, año_actual)

    # Calcular métricas del año anterior para deltas
    metricas_anterior = calcular_metricas_generales(df_unificado, año_actual - 1)
    delta_cumplimiento = metricas['cumplimiento_promedio'] - metricas_anterior.get('cumplimiento_promedio', 0)

    # KPIs principales en tarjetas
    st.markdown("### 🎯 Indicadores Clave de Desempeño")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(crear_tarjeta_kpi(
            valor=f"{metricas['cumplimiento_promedio']:.1f}%",
            etiqueta="Cumplimiento Promedio",
            icono="📈",
            delta=delta_cumplimiento if metricas_anterior.get('cumplimiento_promedio', 0) > 0 else None
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(crear_tarjeta_kpi(
            valor=f"{metricas['indicadores_cumplidos']}",
            etiqueta=f"Indicadores Cumplidos (≥100%)",
            icono="✅",
            color_fondo=f"linear-gradient(135deg, {COLORS['success']} 0%, #1e7e34 100%)"
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(crear_tarjeta_kpi(
            valor=f"{metricas['en_progreso']}",
            etiqueta="En Progreso (80-99%)",
            icono="⚡",
            color_fondo=f"linear-gradient(135deg, {COLORS['warning']} 0%, #d39e00 100%)"
        ), unsafe_allow_html=True)

    with col4:
        st.markdown(crear_tarjeta_kpi(
            valor=f"{metricas['no_cumplidos']}",
            etiqueta="No Cumplidos (<80%)",
            icono="⚠️",
            color_fondo=f"linear-gradient(135deg, {COLORS['danger']} 0%, #a71d2a 100%)"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Fila adicional con más KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Indicadores",
            value=metricas['total_indicadores'],
            delta=None
        )

    with col2:
        st.metric(
            label="Líneas Estratégicas",
            value=metricas['total_lineas']
        )

    with col3:
        st.metric(
            label="Año de Reporte",
            value=año_actual
        )

    st.markdown("---")

    # Sección de Cumplimiento en Cascada
    st.markdown("### 🌊 Cumplimiento en Cascada Jerárquica")

    # Obtener datos de cascada (2 niveles: Línea y Objetivo)
    df_cascada = obtener_cumplimiento_cascada(df_unificado, df_base, año_actual, max_niveles=2)

    if not df_cascada.empty:
        # Tabs para diferentes vistas
        tab1, tab2 = st.tabs(["📊 Vista Gráfica", "📋 Vista Tabla Detallada"])

        with tab1:
            col_graf, col_info = st.columns([2, 1])

            with col_graf:
                # Gráfico sunburst
                fig_cascada = crear_grafico_cascada(df_cascada)
                config = {'displayModeBar': True, 'responsive': True}
                st.plotly_chart(fig_cascada, use_container_width=True, config=config)

            with col_info:
                st.markdown("""
                **📌 Interpretación:**

                Este gráfico muestra la estructura jerárquica del cumplimiento en 2 niveles:

                - **Centro**: Líneas estratégicas con su color distintivo
                - **Anillo exterior**: Objetivos dentro de cada línea
                - **Color**: Tonos graduales del color de la línea

                Haz clic en un segmento para explorar en detalle.

                Para ver el desglose completo por Meta PDI e Indicador,
                visite la página **Análisis por Línea**.
                """)

                # Resumen de niveles
                st.markdown("**Niveles de la cascada:**")
                st.markdown("""
                1. 📊 **Línea Estratégica**
                2. 🎯 **Objetivo**
                """)

        with tab2:
            st.markdown("**Vista completa de la jerarquía de cumplimiento**")

            # Tabla HTML con jerarquía
            tabla_html = crear_tabla_cascada_html(df_cascada)
            # Usar components.html para renderizar HTML complejo
            import streamlit.components.v1 as components
            components.html(tabla_html, height=min(len(df_cascada) * 35 + 100, 800), scrolling=True)

            # Botón de exportación de la cascada
            st.markdown("")
            if st.button("📥 Exportar Cascada a Excel"):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_cascada.to_excel(writer, sheet_name='Cascada_Cumplimiento', index=False)

                st.download_button(
                    label="⬇️ Descargar Excel de Cascada",
                    data=buffer.getvalue(),
                    file_name=f"cascada_cumplimiento_{año_actual}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("No hay datos de Avance disponibles para generar la vista de cascada.")
        # Mostrar métricas en 0
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Líneas Estratégicas", 0)
        with col2:
            st.metric("Objetivos", 0)

    st.markdown("---")

    # Análisis IA - Resumen Ejecutivo
    st.markdown("### 🤖 Análisis Inteligente - Resumen Ejecutivo")

    with st.expander("Ver análisis generado por IA", expanded=True):
        with st.spinner("Generando análisis inteligente..."):
            # Preparar datos para el análisis
            lineas_data = preparar_lineas_para_analisis(df_unificado, año_actual)

            analisis = generar_analisis_general(metricas, lineas_data)

            # Convertir markdown a HTML
            analisis_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', analisis)
            analisis_html = analisis_html.replace('\n', '<br>')

            st.markdown(f"""
            <div class="ai-analysis">
                {analisis_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Gráficos principales
    col_graf1, col_graf2 = st.columns([3, 2])

    with col_graf1:
        st.markdown("### 📊 Cumplimiento por Línea Estratégica")

        # Obtener cumplimiento por línea
        df_lineas = obtener_cumplimiento_por_linea(df_unificado, año_actual)

        if not df_lineas.empty:
            fig_lineas = crear_grafico_lineas(df_lineas)
            # Configuración explícita para renderizado web
            config = {'displayModeBar': True, 'responsive': True}
            st.plotly_chart(fig_lineas, use_container_width=True, config=config)
        else:
            st.info("No hay datos de cumplimiento por línea disponibles.")

    with col_graf2:
        st.markdown("### 🚦 Distribución por Estado")

        fig_semaforo = crear_grafico_semaforo(
            metricas['indicadores_cumplidos'],
            metricas['en_progreso'],
            metricas['no_cumplidos']
        )
        config = {'displayModeBar': True, 'responsive': True}
        st.plotly_chart(fig_semaforo, use_container_width=True, config=config)

    st.markdown("---")

    # Tabla resumen por línea estratégica
    st.markdown("### 📋 Resumen por Línea Estratégica")

    if not df_lineas.empty:
        # Formatear tabla
        df_tabla = df_lineas.copy()
        df_tabla['Estado'] = df_tabla['Cumplimiento'].apply(
            lambda x: '✅ Meta cumplida' if x >= 100 else '⚠️ Alerta' if x >= 80 else '❌ Peligro'
        )
        df_tabla['Cumplimiento'] = df_tabla['Cumplimiento'].apply(lambda x: f"{x:.1f}%")

        # Renombrar columnas
        df_tabla = df_tabla[['Linea', 'Total_Indicadores', 'Cumplimiento', 'Estado']]
        df_tabla.columns = ['Línea Estratégica', 'Indicadores', 'Cumplimiento', 'Estado']

        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True
        )

        # Mostrar información de Meta PDI con jerarquía Línea → Objetivo → Meta
        if df_base is not None and 'Meta_PDI' in df_base.columns:
            st.markdown("")
            with st.expander("🎯 Ver Metas PDI por Línea Estratégica"):
                # Filtrar datos del año actual con Fuente='Avance'
                df_año_metas = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado
                if 'Fuente' in df_año_metas.columns:
                    df_año_metas = df_año_metas[df_año_metas['Fuente'] == 'Avance']

                # Agregar Meta_PDI a los datos
                meta_pdi_dict = df_base.set_index('Indicador')['Meta_PDI'].to_dict()
                df_año_metas = df_año_metas.copy()
                df_año_metas['Meta_PDI'] = df_año_metas['Indicador'].map(meta_pdi_dict)

                # Agrupar por Línea → Objetivo → Meta PDI
                for linea in sorted(df_año_metas['Linea'].dropna().unique()):
                    df_linea_data = df_año_metas[df_año_metas['Linea'] == linea]
                    st.markdown(f"**{linea}**")

                    for objetivo in sorted(df_linea_data['Objetivo'].dropna().unique()):
                        df_obj_data = df_linea_data[df_linea_data['Objetivo'] == objetivo]
                        # Obtener metas PDI únicas para este objetivo
                        metas_obj = df_obj_data[['Meta_PDI']].dropna().drop_duplicates()

                        if not metas_obj.empty:
                            st.markdown(f"- **{objetivo}**:")
                            for _, row in metas_obj.iterrows():
                                st.markdown(f"  - `{row['Meta_PDI']}`")

                    st.markdown("")

    st.markdown("---")

    # Sección de exportación
    st.markdown("### 📥 Exportar Datos")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Exportar a Excel
        if st.button("📊 Preparar Excel", use_container_width=True):
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    # Hoja de resumen
                    df_resumen = pd.DataFrame([metricas])
                    df_resumen.to_excel(writer, sheet_name='Resumen_General', index=False)

                    # Hoja de líneas
                    if not df_lineas.empty:
                        df_lineas.to_excel(writer, sheet_name='Por_Linea', index=False)

                    # Hoja de datos completos del año
                    df_año = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado
                    df_año.to_excel(writer, sheet_name='Datos_Completos', index=False)

                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=buffer.getvalue(),
                    file_name=f"informe_poli_{año_actual}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error al generar Excel: {str(e)}")

    with col2:
        st.button("📄 Exportar PDF", use_container_width=True, disabled=True,
                  help="Funcionalidad próximamente disponible")

    with col3:
        if st.button("🔄 Regenerar Análisis IA", use_container_width=True):
            # Limpiar caché de análisis
            st.cache_data.clear()
            st.rerun()

    # Notas al pie
    st.markdown(f"""
    <div class="info-box">
        <strong>📌 Notas:</strong>
        <ul>
            <li><strong>Línea Base:</strong> Los datos de 2021 sirven como punto de referencia inicial del PDI.</li>
            <li><strong>Semáforo:</strong> Verde (≥100%), Amarillo (80-99%), Rojo (&lt;80%)</li>
            <li><strong>Análisis IA:</strong> Generado automáticamente usando inteligencia artificial.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
