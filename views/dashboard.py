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
    generar_analisis_general, preparar_lineas_para_analisis, generar_analisis_linea
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

    # Mostrar cortes en los títulos como 'Diciembre 2025' (fijo)
    display_corte = 2025

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
        col1, col2, col3, col4, col5 = st.columns(5)

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
                label="📋 Total",
                value=metricas['total_indicadores'],
                help="Total de indicadores evaluados"
            )

        st.markdown("---")

        # Layout de 2 columnas: Cascada (60%) + Semáforo (40%)
        col_cascada, col_semaforo = st.columns([3, 2])

        with col_cascada:
            st.markdown("#### 🌊 Cumplimiento en Cascada")

            # Selector para filtrar indicadores/proyectos/todos
            filtro_cascada = st.radio(
                "Filtrar por:",
                ["Indicadores", "Proyectos", "Todos"],
                horizontal=True,
                key="filtro_cascada_dashboard",
                help="Indicadores: métricas de gestión | Proyectos: iniciativas específicas"
            )

            # Mapear selección a parámetro
            filtro_map = {"Indicadores": "indicadores", "Proyectos": "proyectos", "Todos": "todos"}
            df_cascada_filtrado = obtener_cumplimiento_cascada(
                df_unificado, df_base, año_actual,
                max_niveles=2,
                filtro_tipo=filtro_map[filtro_cascada]
            )

            if not df_cascada_filtrado.empty:
                fig_cascada = crear_grafico_cascada(df_cascada_filtrado)
                config = {'displayModeBar': False, 'responsive': True}
                st.plotly_chart(fig_cascada, use_container_width=True, config=config)
            else:
                st.info(f"No hay datos de {filtro_cascada.lower()} disponibles.")

        with col_semaforo:
            st.markdown("#### Estado de Indicadores")
            fig_semaforo = crear_grafico_semaforo(
                metricas['indicadores_cumplidos'],
                metricas['en_progreso'],
                metricas['no_cumplidos'],
                metricas.get('stand_by', 0)
            )
            config = {'displayModeBar': False, 'responsive': True}
            st.plotly_chart(fig_semaforo, use_container_width=True, config=config)

            # Info compacta
            st.info(f"📌 **{metricas['total_lineas']}** Líneas Estratégicas | Corte: **Diciembre {display_corte}**")

        # Gráfico de proyectos en fila separada
        if estado_proyectos['total_proyectos'] > 0:
            st.markdown("---")
            col_proy1, col_proy2, col_proy3 = st.columns([1, 2, 1])
            with col_proy2:
                st.markdown("#### 📋 Estado de Proyectos")
                fig_proyectos = crear_grafico_proyectos(
                    estado_proyectos['finalizados'],
                    estado_proyectos['en_ejecucion'],
                    estado_proyectos['stand_by'],
                    estado_proyectos.get('sin_clasificar', 0)
                )
                config = {'displayModeBar': False, 'responsive': True}
                st.plotly_chart(fig_proyectos, use_container_width=True, config=config)

                # Construir texto de resumen
                resumen_proy = f"📋 **{estado_proyectos['total_proyectos']}** Proyectos | **{estado_proyectos['finalizados']}** Finalizados | **{estado_proyectos['en_ejecucion']}** En Ejecución | **{estado_proyectos['stand_by']}** Stand by"
                if estado_proyectos.get('sin_clasificar', 0) > 0:
                    resumen_proy += f" | **{estado_proyectos['sin_clasificar']}** Sin clasificar"
                st.info(resumen_proy)

        # Interpretación compacta
        with st.expander("📌 ¿Cómo interpretar este gráfico?", expanded=False):
            st.markdown("""
            - **Centro del Sunburst**: Líneas estratégicas con su color distintivo
            - **Anillo exterior**: Objetivos dentro de cada línea
            - **Colores**: Verde (≥100%), Amarillo (80-99%), Rojo (<80%)

            Haz clic en cualquier segmento para ver más detalles.
            """)

    # ============================================================
    # TAB 2: ANÁLISIS DETALLADO (Simplificado)
    # ============================================================
    with tab_analisis:
        # Gráfico de líneas - ancho completo arriba
        st.markdown("#### Cumplimiento por Linea Estrategica")
        if not df_lineas.empty:
            fig_lineas = crear_grafico_lineas(df_lineas)
            config = {'displayModeBar': True, 'responsive': True}
            st.plotly_chart(fig_lineas, use_container_width=True, config=config)
        else:
            st.info("No hay datos disponibles.")

        # Tabla de cumplimiento - ancho completo
        if not df_lineas.empty:
            st.markdown("##### 📋 Tabla de Cumplimiento")
            df_tabla = df_lineas.copy()

            def get_estado_badge(cumpl):
                if cumpl >= 100:
                    return '✅ Cumple'
                elif cumpl >= 80:
                    return '⚠️ Alerta'
                else:
                    return '❌ Crítico'

            df_tabla['Estado'] = df_tabla['Cumplimiento'].apply(get_estado_badge)
            df_tabla['Cumplimiento_Display'] = df_tabla['Cumplimiento'].apply(lambda x: f"{x:.1f}%")

            df_tabla = df_tabla[['Linea', 'Total_Indicadores', 'Cumplimiento_Display', 'Estado']]
            df_tabla.columns = ['Línea Estratégica', 'Indicadores', '% Cumplimiento', 'Estado']

            # Construir tabla con estilos inline (evita problemas de indentación en markdown)
            hdr_style = f'background-color:{COLORS["primary"]};color:white;padding:12px;text-align:left;font-weight:bold;border:1px solid #dee2e6;font-size:14px;'
            cel_style = 'padding:10px;border:1px solid #dee2e6;background-color:white;font-size:14px;font-family:Arial,sans-serif;'
            cols = df_tabla.columns.tolist()

            header_row = '<tr>' + ''.join(f'<th style="{hdr_style}">{c}</th>' for c in cols) + '</tr>'
            data_rows = ''.join(
                '<tr>' + ''.join(f'<td style="{cel_style}">{row[c]}</td>' for c in cols) + '</tr>'
                for _, row in df_tabla.iterrows()
            )

            tabla_html = f'<table style="width:100%;border-collapse:collapse;font-family:Arial,sans-serif;box-shadow:0 2px 4px rgba(0,0,0,0.1);">{header_row}{data_rows}</table>'
            st.markdown(tabla_html, unsafe_allow_html=True)

        # Análisis IA - ancho completo con max-width para legibilidad
        st.markdown("#### Analisis Inteligente - Resumen Ejecutivo")
        with st.spinner("Generando analisis..."):
            lineas_data = preparar_lineas_para_analisis(df_unificado, año_actual)
            analisis = generar_analisis_general(metricas, lineas_data)

            analisis_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', analisis)
            analisis_html = analisis_html.replace('\n', '<br>')

            st.markdown(f"""
            <div class="ai-analysis" style="max-width: 750px;">
                {analisis_html}
            </div>
            """, unsafe_allow_html=True)

        # Vista de cascada en expander (opcional)
        with st.expander("Ver desglose jerarquico completo", expanded=False):
            if not df_cascada.empty:
                tabla_html = crear_tabla_cascada_html(df_cascada)
                import streamlit.components.v1 as components
                components.html(tabla_html, height=min(len(df_cascada) * 35 + 100, 500), scrolling=True)
            else:
                st.info("No hay datos de cascada disponibles.")

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
                # Generar cascada completa para el PDF (todos los niveles)
                df_cascada_pdf = obtener_cumplimiento_cascada(df_unificado, df_base, año_actual, max_niveles=4)

                # Generar análisis IA por línea estratégica
                analisis_lineas_pdf = {}
                try:
                    with st.spinner('Generando análisis IA por línea...'):
                        for _, lr in df_lineas.iterrows():
                            nom = str(lr.get('Linea', lr.get('Línea', '')))
                            cumpl_l = float(lr.get('Cumplimiento', 0) or 0)
                            n_ind_l = int(lr.get('Total_Indicadores', 0) or 0)
                            # Objetivos de esta línea desde la cascada (Nivel 2)
                            objs_l = []
                            if df_cascada_pdf is not None and not df_cascada_pdf.empty:
                                mask = (df_cascada_pdf['Nivel'] == 2) & (df_cascada_pdf['Linea'] == nom)
                                for _, or_ in df_cascada_pdf[mask].iterrows():
                                    objs_l.append({
                                        'objetivo': str(or_.get('Objetivo', '')),
                                        'cumplimiento': float(or_.get('Cumplimiento', 0) or 0),
                                        'indicadores': int(or_.get('Total_Indicadores', 0) or 0),
                                    })
                            texto_l = generar_analisis_linea(nom, n_ind_l, cumpl_l, objs_l)
                            analisis_lineas_pdf[nom] = texto_l
                except Exception:
                    analisis_lineas_pdf = {}

                pdf_bytes = exportar_informe_pdf(
                    metricas=metricas,
                    df_lineas=df_lineas,
                    df_indicadores=df_año_pdf,
                    analisis_texto=analisis_pdf,
                    figuras=None,  # Sin gráficos por ahora (requiere kaleido)
                    año=año_actual,
                    df_cascada=df_cascada_pdf,
                    analisis_lineas=analisis_lineas_pdf
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
        <strong>Corte:</strong> Diciembre {display_corte}
    </div>
    """, unsafe_allow_html=True)
