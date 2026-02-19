"""
Página: CMI Estratégico
Vista que muestra indicadores organizados por Objetivo Estratégico
con opción de filtrar por año (2022-2025) y Avance
"""

import streamlit as st
import pandas as pd
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    COLORS, calcular_cumplimiento, obtener_color_semaforo,
    obtener_estado_semaforo, es_objetivo_standby, COLORES_LINEAS
)


def obtener_color_cumplimiento_badge(cumplimiento):
    """Retorna el color y emoji para un badge de cumplimiento."""
    if cumplimiento is None or pd.isna(cumplimiento):
        return COLORS['gray'], '⚪'
    elif cumplimiento >= 100:
        return COLORS['success'], '🟢'
    elif cumplimiento >= 80:
        return COLORS['warning'], '🟡'
    else:
        return COLORS['danger'], '🔴'


def mostrar_pagina():
    """
    Renderiza la página del CMI Estratégico.
    """
    # Header
    st.markdown(f"""
    <div class="header-container" style="padding: 15px; margin-bottom: 10px;">
        <div class="header-title" style="font-size: 28px;">🎯 CMI Estratégico</div>
        <div class="header-subtitle" style="font-size: 14px;">Cuadro de Mando Integral | Indicadores por Objetivo Estratégico</div>
    </div>
    """, unsafe_allow_html=True)

    # Obtener datos del estado de sesión
    df_unificado = st.session_state.get('df_unificado')
    
    if df_unificado is None or df_unificado.empty:
        st.error("⚠️ No se pudieron cargar los datos.")
        return
    
    # Asegurar que la columna Año es numérica
    if 'Año' in df_unificado.columns:
        df_unificado = df_unificado.copy()
        df_unificado['Año'] = pd.to_numeric(df_unificado['Año'], errors='coerce')

    # ============================================================
    # CONTROLES DE FILTRO
    # ============================================================
    st.markdown("#### 🔍 Filtros")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        # Filtro por año - solo mostrar 2022-2025 y 2026
        años_permitidos = [2022, 2023, 2024, 2025, 2026]
        if 'Año' in df_unificado.columns:
            años_disponibles = [int(a) for a in df_unificado['Año'].dropna().unique()]
            años_disponibles = sorted([a for a in años_permitidos if a in años_disponibles])
        else:
            años_disponibles = años_permitidos
        
        año_seleccionado = st.selectbox(
            "Seleccione Año:",
            años_disponibles,
            index=len(años_disponibles) - 1 if años_disponibles else 0,
            key="filtro_año_cmi"
        )
    
    with col2:
        # Filtro por tipo
        tipo_seleccionado = st.selectbox(
            "Tipo de Indicador:",
            ["Indicadores", "Proyectos", "Todos"],
            key="filtro_tipo_cmi"
        )
    
    with col3:
        # Filtro por línea estratégica
        if 'Linea' in df_unificado.columns:
            lineas = sorted(df_unificado['Linea'].dropna().unique())
        else:
            lineas = []
        
        linea_seleccionada = st.selectbox(
            "Línea Estratégica:",
            ["Todas"] + lineas,
            key="filtro_linea_cmi"
        )

    st.markdown("---")

    # ============================================================
    # FILTRAR DATOS
    # ============================================================
    
    # Filtrar por año - comparación segura
    df_filtrado = df_unificado[df_unificado['Año'] == año_seleccionado].copy()
    
    if df_filtrado.empty:
        st.warning(f"⚠️ No hay datos para el año {int(año_seleccionado)}")
        st.write(f"Años disponibles en BD: {sorted(df_unificado['Año'].dropna().unique().astype(int))}")
        return
    
    # Filtrar por tipo
    if 'Proyectos' in df_filtrado.columns:
        if tipo_seleccionado == "Indicadores":
            df_filtrado = df_filtrado[df_filtrado['Proyectos'] == 0]
        elif tipo_seleccionado == "Proyectos":
            df_filtrado = df_filtrado[df_filtrado['Proyectos'] == 1]
    
    # Filtrar por fuente (Cierre y Avance)
    if 'Fuente' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Fuente'].isin(['Cierre', 'Avance'])]
    
    # Filtrar por línea estratégica
    if 'Linea' in df_filtrado.columns and linea_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Linea'] == linea_seleccionada]
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos con los filtros seleccionados")
        return
    
    # ============================================================
    # AGRUPAR POR LÍNEA ESTRATÉGICA Y OBJETIVO
    # ============================================================
    
    # Ordenar por Línea y Objetivo
    df_filtrado = df_filtrado.sort_values(['Linea', 'Objetivo', 'Indicador'])
    
    # Obtener líneas únicas
    lineas_unicas = df_filtrado['Linea'].unique()
    
    # ============================================================
    # MOSTRAR INDICADORES POR LÍNEA Y OBJETIVO
    # ============================================================
    
    for linea in sorted(lineas_unicas):
        df_linea = df_filtrado[df_filtrado['Linea'] == linea]
        
        # Color de la línea
        color_linea = COLORES_LINEAS.get(linea, COLORS['primary'])
        
        # Header de la línea
        st.markdown(f"""
        <div style="background-color: {color_linea}; padding: 12px; border-radius: 5px; margin: 15px 0 10px 0;">
            <strong style="color: white; font-size: 16px;">📋 {linea}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Obtener objetivos únicos en esta línea
        objetivos_unicas = df_linea['Objetivo'].unique()
        
        for objetivo in sorted(objetivos_unicas):
            df_objetivo = df_linea[df_linea['Objetivo'] == objetivo]
            
            # Calcular cumplimiento promedio del objetivo
            cumplimiento_objetivo = df_objetivo['Cumplimiento'].mean() if 'Cumplimiento' in df_objetivo.columns else 0
            es_standby = es_objetivo_standby(objetivo)
            color_objetivo, emoji_estado = obtener_color_cumplimiento_badge(cumplimiento_objetivo if not es_standby else None)
            
            # Header del objetivo
            if es_standby:
                estado_texto = "Stand by"
                estado_color = COLORS['standby']
            else:
                estado_texto, _ = obtener_estado_semaforo(cumplimiento_objetivo)
                estado_color = obtener_color_semaforo(cumplimiento_objetivo)
            
            st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 12px; border-left: 4px solid {estado_color}; border-radius: 3px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 15px;">{objetivo}</strong>
                    </div>
                    <div style="text-align: right;">
                        <span style="background-color: {estado_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;">
                            {emoji_estado} {cumplimiento_objetivo:.1f}% {estado_texto}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Crear tabla de indicadores
            tabla_data = []
            for _, row in df_objetivo.iterrows():
                indicador = row.get('Indicador', 'N/D')
                meta = row.get('Meta', 0)
                ejecucion = row.get('Ejecución', 0)
                cumplimiento = row.get('Cumplimiento', 0)
                
                # Determinar emoji según cumplimiento
                if pd.isna(cumplimiento) or cumplimiento == 0:
                    emoji = '⚪'
                elif cumplimiento >= 100:
                    emoji = '🟢'
                elif cumplimiento >= 80:
                    emoji = '🟡'
                else:
                    emoji = '🔴'
                
                cumpl_texto = f"{emoji} {cumplimiento:.1f}%" if pd.notna(cumplimiento) and cumplimiento != 0 else '⚪ -'
                
                tabla_data.append({
                    'Indicador': indicador,
                    'Meta': meta if pd.notna(meta) else '-',
                    'Ejecución': ejecucion if pd.notna(ejecucion) else '-',
                    'Cumplimiento': cumpl_texto
                })
            
            if tabla_data:
                df_tabla = pd.DataFrame(tabla_data)
                
                # Mostrar tabla sin colores de fondo, más condensada
                st.dataframe(
                    df_tabla.style
                    .format({
                        'Meta': lambda x: f'{x:,.2f}' if isinstance(x, (int, float)) else x,
                        'Ejecución': lambda x: f'{x:,.2f}' if isinstance(x, (int, float)) else x,
                    }, na_rep='-')
                    .set_properties(**{'text-align': 'center', 'font-size': '13px'})
                    .set_properties(**{'text-align': 'left'}, subset=['Indicador']),
                    use_container_width=True,
                    hide_index=True,
                    height=len(tabla_data) * 25 + 50
                )
            else:
                st.info("No hay indicadores para este objetivo")
            
            st.markdown("")  # Espaciador
    
    # ============================================================
    # RESUMEN ESTADÍSTICO
    # ============================================================
    st.markdown("---")
    st.markdown("#### 📊 Resumen Estadístico")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calcular estadísticas
    total_indicadores = df_filtrado['Indicador'].nunique() if 'Indicador' in df_filtrado.columns else len(df_filtrado)
    cumplimiento_promedio = df_filtrado['Cumplimiento'].mean() if 'Cumplimiento' in df_filtrado.columns else 0
    
    cumplidos = len(df_filtrado[df_filtrado['Cumplimiento'] >= 100]) if 'Cumplimiento' in df_filtrado.columns else 0
    alerta = len(df_filtrado[(df_filtrado['Cumplimiento'] >= 80) & (df_filtrado['Cumplimiento'] < 100)]) if 'Cumplimiento' in df_filtrado.columns else 0
    peligro = len(df_filtrado[df_filtrado['Cumplimiento'] < 80]) if 'Cumplimiento' in df_filtrado.columns else 0
    
    with col1:
        st.metric("📋 Total Indicadores", total_indicadores)
    
    with col2:
        st.metric("📊 Cumplimiento Promedio", f"{cumplimiento_promedio:.1f}%")
    
    with col3:
        st.metric("🟢 Cumplidos", cumplidos)
    
    with col4:
        st.metric("🟡 Alerta", alerta)
    
    with col5:
        st.metric("🔴 Peligro", peligro)
    
    # ============================================================
    # INFORMACIÓN ADICIONAL
    # ============================================================
    st.markdown("---")
    
    with st.expander("ℹ️ Información y Leyenda"):
        st.markdown(f"""
        **Filtros Aplicados:**
        - Año: {int(año_seleccionado)}
        - Tipo: {tipo_seleccionado}
        - Línea: {linea_seleccionada}
        
        **Semáforo de Cumplimiento:**
        - 🟢 **Meta Cumplida**: Cumplimiento ≥ 100%
        - 🟡 **Alerta**: Cumplimiento entre 80% - 99.9%
        - 🔴 **Peligro**: Cumplimiento < 80%
        - ⚪ **Sin Datos**: Indicador sin información
        
        **Cálculo de Cumplimiento:**
        - Cumplimiento % = (Ejecución / Meta) × 100
        """)
