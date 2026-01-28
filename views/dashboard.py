"""
Página 1: Dashboard General
Informe Estratégico POLI 2025 - Resumen Ejecutivo
Versión optimizada con Tabs para reducir scroll
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
    obtener_color_semaforo, exportar_a_excel, obtener_cumplimiento_cascada,
    calcular_estado_proyectos
)
from utils.visualizations import (
    crear_grafico_lineas, crear_grafico_semaforo, crear_tarjeta_kpi,
    crear_grafico_cascada, crear_tabla_cascada_html, crear_grafico_proyectos
)
from utils.ai_analysis import (
    generar_analisis_general, preparar_lineas_para_analisis
)
from utils.pdf_generator import exportar_informe_pdf, previsualizar_html


def mostrar_pagina():
    """
    Renderiza la página del Dashboard General con estructura de Tabs.
    """
    # Header compacto
    st.markdown(f"""
    <div class="header-container" style="padding: 15px; margin-bottom: 10px;">
        <div class="header-title" style="font-size: 28px;">📊 Informe Estratégico POLI 2025</div>
        <div class="header-subtitle" style="font-size: 14px;">Plan de Desarrollo Institucional | Seguimiento y Monitoreo</div>
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
    metricas_anterior = calcular_metricas_generales(df_unificado, año_actual - 1)
    delta_cumplimiento = metricas['cumplimiento_promedio'] - metricas_anterior.get('cumplimiento_promedio', 0)

    # Obtener datos necesarios
    df_cascada = obtener_cumplimiento_cascada(df_unificado, df_base, año_actual, max_niveles=2)
    df_lineas = obtener_cumplimiento_por_linea(df_unificado, año_actual)
    estado_proyectos = calcular_estado_proyectos(df_unificado, año_actual)

    # ============================================================
    # TABS PRINCIPALES - Estructura optimizada
    # ============================================================
    tab_resumen, tab_analisis, tab_datos = st.tabs([
        "📊 Resumen Ejecutivo",
        "📈 Análisis Detallado",
        "📥 Datos y Exportación"
    ])

    # ============================================================
    # TAB 1: RESUMEN EJECUTIVO
    # ============================================================
    with tab_resumen:
    # KPIs usando st.metric nativo (mejor compatibilidad con columnas)
        st.markdown("#### 🎯 Indicadores Clave")
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            delta_str = f"{delta_cumplimiento:+.1f}%" if delta_cumplimiento != 0 else None
            st.metric(
                label="📊 Cumplimiento",
                value=f"{metricas['cumplimiento_promedio']:.1f}%",
                delta=delta_str
            )

        with col2:
            st.metric(
                label="✅ Cumplidos",
                value=metricas['indicadores_cumplidos'],
                help="Indicadores con ≥100% de cumplimiento"
            )

        with col3:
            st.metric(
                label="⚠️ En Progreso",
                value=metricas['en_progreso'],
                help="Indicadores entre 80-99%"
            )

        with col4:
            st.metric(
                label="❌ No Cumplidos",
                value=metricas['no_cumplidos'],
                help="Indicadores <80%"
            )

        with col5:
            st.metric(
                label="⏸️ Stand by",
                value=metricas['stand_by'],
                help="Indicadores en pausa o sin iniciarse"
            )

        with col6:
            st.metric(
                label="📋 Total",
                value=metricas['total_indicadores'],
                help="Total de indicadores evaluados"
            )

        st.markdown("---")

        # Layout de 2 columnas: Cascada (60%) + Semáforo (40%)
        col_cascada, col_semaforo = st.columns([3, 2])

        with col_cascada:
            st.markdown("#### 🌊 Cumplimiento en Cascada")
            if not df_cascada.empty:
                fig_cascada = crear_grafico_cascada(df_cascada)
                config = {'displayModeBar': False, 'responsive': True}
                st.plotly_chart(fig_cascada, use_container_width=True, config=config)
            else:
                st.info("No hay datos de cascada disponibles.")

        with col_semaforo:
            st.markdown("#### 🚦 Estado de Indicadores")
            fig_semaforo = crear_grafico_semaforo(
                metricas['indicadores_cumplidos'],
                metricas['en_progreso'],
                metricas['no_cumplidos'],
                metricas.get('stand_by', 0)
            )
            config = {'displayModeBar': False, 'responsive': True}
            st.plotly_chart(fig_semaforo, use_container_width=True, config=config)

            # Info compacta
            st.info(f"📌 **{metricas['total_lineas']}** Líneas Estratégicas | Corte: **Diciembre {año_actual}**")

        # Gráfico de proyectos en fila separada
        if estado_proyectos['total_proyectos'] > 0:
            st.markdown("---")
            col_proy1, col_proy2, col_proy3 = st.columns([1, 2, 1])
            with col_proy2:
                st.markdown("#### 📋 Estado de Proyectos")
                fig_proyectos = crear_grafico_proyectos(
                    estado_proyectos['finalizados'],
                    estado_proyectos['en_ejecucion'],
                    estado_proyectos['stand_by']
                )
                config = {'displayModeBar': False, 'responsive': True}
                st.plotly_chart(fig_proyectos, use_container_width=True, config=config)
                st.info(f"📋 **{estado_proyectos['total_proyectos']}** Proyectos | **{estado_proyectos['finalizados']}** Finalizados | **{estado_proyectos['en_ejecucion']}** En Ejecución | **{estado_proyectos['stand_by']}** Stand by")

        # Interpretación compacta
        with st.expander("📌 ¿Cómo interpretar este gráfico?", expanded=False):
            st.markdown("""
            - **Centro del Sunburst**: Líneas estratégicas con su color distintivo
            - **Anillo exterior**: Objetivos dentro de cada línea
            - **Colores**: Verde (≥100%), Amarillo (80-99%), Rojo (<80%)

            Haz clic en cualquier segmento para ver más detalles.
            """)

    # ============================================================
    # TAB 2: ANÁLISIS DETALLADO
    # ============================================================
    with tab_analisis:
        # Sub-tabs para organizar el análisis
        subtab_lineas, subtab_ia, subtab_tabla = st.tabs([
            "📊 Por Línea Estratégica",
            "🤖 Análisis IA",
            "📋 Tabla Cascada"
        ])

        with subtab_lineas:
            st.markdown("#### Cumplimiento por Línea Estratégica")
            if not df_lineas.empty:
                fig_lineas = crear_grafico_lineas(df_lineas)
                config = {'displayModeBar': True, 'responsive': True}
                st.plotly_chart(fig_lineas, use_container_width=True, config=config)

                # Tabla compacta debajo
                st.markdown("**Resumen numérico:**")
                df_tabla = df_lineas.copy()
                df_tabla['Estado'] = df_tabla['Cumplimiento'].apply(
                    lambda x: '✅' if x >= 100 else '⚠️' if x >= 80 else '❌'
                )
                df_tabla['Cumplimiento'] = df_tabla['Cumplimiento'].apply(lambda x: f"{x:.1f}%")
                df_tabla = df_tabla[['Linea', 'Total_Indicadores', 'Cumplimiento', 'Estado']]
                df_tabla.columns = ['Línea', 'Indicadores', 'Cumplimiento', 'Estado']
                st.dataframe(df_tabla, use_container_width=True, hide_index=True, height=250)
            else:
                st.info("No hay datos disponibles.")

        with subtab_ia:
            st.markdown("#### Análisis Inteligente - Resumen Ejecutivo")
            with st.spinner("Generando análisis..."):
                lineas_data = preparar_lineas_para_analisis(df_unificado, año_actual)
                analisis = generar_analisis_general(metricas, lineas_data)

                analisis_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', analisis)
                analisis_html = analisis_html.replace('\n', '<br>')

                st.markdown(f"""
                <div class="ai-analysis">
                    {analisis_html}
                </div>
                """, unsafe_allow_html=True)

        with subtab_tabla:
            st.markdown("#### Vista Completa de Cascada Jerárquica")
            if not df_cascada.empty:
                # Tabla HTML con jerarquía
                tabla_html = crear_tabla_cascada_html(df_cascada)
                import streamlit.components.v1 as components
                components.html(tabla_html, height=min(len(df_cascada) * 35 + 100, 600), scrolling=True)
            else:
                st.info("No hay datos de cascada disponibles.")

            # Metas PDI (si existen)
            if df_base is not None and 'Meta_PDI' in df_base.columns:
                with st.expander("🎯 Ver Metas PDI por Línea", expanded=False):
                    df_año_metas = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado
                    if 'Fuente' in df_año_metas.columns:
                        df_año_metas = df_año_metas[df_año_metas['Fuente'] == 'Avance']

                    meta_pdi_dict = df_base.set_index('Indicador')['Meta_PDI'].to_dict()
                    df_año_metas = df_año_metas.copy()
                    df_año_metas['Meta_PDI'] = df_año_metas['Indicador'].map(meta_pdi_dict)

                    for linea in sorted(df_año_metas['Linea'].dropna().unique()):
                        df_linea_data = df_año_metas[df_año_metas['Linea'] == linea]
                        st.markdown(f"**{linea}**")
                        for objetivo in sorted(df_linea_data['Objetivo'].dropna().unique()):
                            df_obj_data = df_linea_data[df_linea_data['Objetivo'] == objetivo]
                            metas_obj = df_obj_data[['Meta_PDI']].dropna().drop_duplicates()
                            if not metas_obj.empty:
                                st.markdown(f"- {objetivo}")
                                for _, row in metas_obj.iterrows():
                                    st.markdown(f"  - `{row['Meta_PDI']}`")

    # ============================================================
    # TAB 3: DATOS Y EXPORTACIÓN
    # ============================================================
    with tab_datos:
        st.markdown("#### 📥 Exportar Datos del Dashboard")

        # Sección de exportación PDF destacada
        st.markdown("""
        <div style="background: linear-gradient(90deg, #003d82 0%, #0056b3 100%);
                    padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;">
            <span style="color: white; font-size: 16px; font-weight: bold;">
                📄 Informe PDF Corporativo
            </span>
            <span style="color: rgba(255,255,255,0.8); font-size: 12px; margin-left: 10px;">
                Genera un informe profesional con diseño institucional
            </span>
        </div>
        """, unsafe_allow_html=True)

        col_pdf1, col_pdf2 = st.columns([2, 1])

        with col_pdf1:
            # Preparar datos para el PDF
            df_año_pdf = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado
            if 'Fuente' in df_año_pdf.columns:
                df_año_pdf = df_año_pdf[df_año_pdf['Fuente'] == 'Avance']

            # Obtener análisis para incluir en PDF
            try:
                lineas_data = preparar_lineas_para_analisis(df_unificado, año_actual)
                analisis_pdf = generar_analisis_general(metricas, lineas_data)
            except Exception:
                analisis_pdf = ""

            try:
                pdf_bytes = exportar_informe_pdf(
                    metricas=metricas,
                    df_lineas=df_lineas,
                    df_indicadores=df_año_pdf,
                    analisis_texto=analisis_pdf,
                    figuras=None,  # Sin gráficos por ahora (requiere kaleido)
                    año=año_actual
                )

                st.download_button(
                    label="📄 Descargar Informe PDF Corporativo",
                    data=pdf_bytes,
                    file_name=f"Informe_Estrategico_POLI_{año_actual}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except ImportError as e:
                st.warning(f"⚠️ Para generar PDFs, instale: `pip install fpdf2`")
            except Exception as e:
                st.error(f"Error al generar PDF: {str(e)}")

        with col_pdf2:
            st.markdown("""
            <div style="background: #E3F2FD; padding: 15px; border-radius: 8px; font-size: 12px;">
                <strong>📋 Contenido del PDF:</strong><br>
                • Portada corporativa<br>
                • KPIs principales<br>
                • Análisis por línea<br>
                • Detalle de indicadores<br>
                • Análisis ejecutivo IA
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📊 Exportar a Excel")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Exportar Informe Completo**")
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_resumen = pd.DataFrame([metricas])
                    df_resumen.to_excel(writer, sheet_name='Resumen_General', index=False)

                    if not df_lineas.empty:
                        df_lineas.to_excel(writer, sheet_name='Por_Linea', index=False)

                    if not df_cascada.empty:
                        df_cascada.to_excel(writer, sheet_name='Cascada', index=False)

                    df_año = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado
                    df_año.to_excel(writer, sheet_name='Datos_Completos', index=False)

                st.download_button(
                    label="📊 Descargar Excel Completo",
                    data=buffer.getvalue(),
                    file_name=f"informe_poli_{año_actual}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

        with col2:
            st.markdown("**Exportar Solo Cascada**")
            if not df_cascada.empty:
                buffer_cascada = io.BytesIO()
                with pd.ExcelWriter(buffer_cascada, engine='openpyxl') as writer:
                    df_cascada.to_excel(writer, sheet_name='Cascada_Cumplimiento', index=False)

                st.download_button(
                    label="🌊 Descargar Cascada",
                    data=buffer_cascada.getvalue(),
                    file_name=f"cascada_{año_actual}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.info("No hay datos de cascada.")

        st.markdown("---")

        # Datos completos en tabla interactiva
        st.markdown("#### 📋 Vista de Datos Completos")
        df_año = df_unificado[df_unificado['Año'] == año_actual] if 'Año' in df_unificado.columns else df_unificado

        # Filtros rápidos
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            lineas_filtro = ['Todas'] + sorted(df_año['Linea'].dropna().unique().tolist())
            linea_sel = st.selectbox("Filtrar por Línea:", lineas_filtro, key="filtro_linea_datos")
        with col_f2:
            estado_filtro = st.selectbox("Filtrar por Estado:", ['Todos', '✅ Cumplido', '⚠️ Alerta', '❌ Peligro'], key="filtro_estado_datos")

        df_filtrado = df_año.copy()

        # Filtrar solo indicadores (excluir proyectos)
        if 'Proyectos' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Proyectos'] == 0]

        if linea_sel != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Linea'] == linea_sel]
        if estado_filtro != 'Todos':
            if estado_filtro == '✅ Cumplido':
                df_filtrado = df_filtrado[df_filtrado['Cumplimiento'] >= 100]
            elif estado_filtro == '⚠️ Alerta':
                df_filtrado = df_filtrado[(df_filtrado['Cumplimiento'] >= 80) & (df_filtrado['Cumplimiento'] < 100)]
            else:
                df_filtrado = df_filtrado[df_filtrado['Cumplimiento'] < 80]

        columnas_base = ['Indicador', 'Linea', 'Objetivo', 'Meta', 'Ejecución', 'Cumplimiento']
        columnas_disponibles = [c for c in columnas_base if c in df_filtrado.columns]

        if columnas_disponibles:
            df_tabla = df_filtrado[columnas_disponibles].drop_duplicates().copy()

            # Agregar Meta_PDI desde df_base
            if df_base is not None and 'Indicador' in df_base.columns and 'Meta_PDI' in df_base.columns:
                meta_pdi_dict = df_base.set_index('Indicador')['Meta_PDI'].to_dict()
                df_tabla['Meta PDI'] = df_tabla['Indicador'].map(meta_pdi_dict)

            # Agregar columna de Alerta
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

                cumpl_numerico = df_tabla['Cumplimiento'].copy()
                df_tabla['Alerta'] = cumpl_numerico.apply(calcular_alerta)
                df_tabla['Cumplimiento'] = cumpl_numerico.apply(
                    lambda x: f"{x:.1f}%" if pd.notna(x) else "N/D"
                )

            # Reordenar columnas: Indicador, Linea, Objetivo, Meta PDI, Meta, Ejecución, Cumplimiento, Estado
            columnas_orden = ['Indicador', 'Linea', 'Objetivo', 'Meta PDI', 'Meta', 'Ejecución', 'Cumplimiento', 'Alerta']
            columnas_finales = [c for c in columnas_orden if c in df_tabla.columns]
            df_tabla = df_tabla[columnas_finales]

            st.dataframe(
                df_tabla,
                use_container_width=True,
                hide_index=True,
                height=400,
                column_config={
                    "Indicador": st.column_config.TextColumn("Indicador", width="large"),
                    "Linea": st.column_config.TextColumn("Línea", width="medium"),
                    "Objetivo": st.column_config.TextColumn("Objetivo", width="medium"),
                    "Meta PDI": st.column_config.TextColumn("Meta PDI", width="small"),
                    "Meta": st.column_config.NumberColumn("Meta", format="%.2f"),
                    "Ejecución": st.column_config.NumberColumn("Ejecución", format="%.2f"),
                    "Cumplimiento": st.column_config.TextColumn("Cumplimiento", width="small"),
                    "Alerta": st.column_config.TextColumn("Estado", width="small")
                }
            )
            st.caption(f"Mostrando {len(df_tabla)} registros")

        st.markdown("---")

        # Acciones adicionales
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🔄 Actualizar Datos", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with col_act2:
            st.button("📄 Exportar PDF", use_container_width=True, disabled=True,
                      help="Próximamente disponible")

    # Footer compacto
    st.markdown(f"""
    <div style="text-align: center; color: {COLORS['gray']}; font-size: 11px; padding: 10px; margin-top: 20px;">
        <strong>Semáforo:</strong> 🟢 ≥100% | 🟡 80-99% | 🔴 <80% |
        <strong>Línea Base:</strong> 2021 |
        <strong>Corte:</strong> Diciembre {año_actual}
    </div>
    """, unsafe_allow_html=True)
