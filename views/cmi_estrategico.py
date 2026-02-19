"""
Página: CMI Estratégico
Cuadro de Mando Integral con vista compacta 2 columnas por objetivo.
Línea estratégica obligatoria. Sin barras de desplazamiento.
"""

import streamlit as st
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    COLORS, obtener_color_semaforo, COLORES_LINEAS
)


def fmt_num(v):
    """Formatea valor numérico de forma compacta: entero si es entero, 1 decimal si no."""
    if v is None:
        return ''
    try:
        if pd.isna(v):
            return ''
        f = float(v)
        return str(int(f)) if f == int(f) else f"{f:.1f}"
    except Exception:
        return str(v) if str(v) not in ('nan', 'None', '') else ''


def mostrar_pagina():
    """Renderiza la página del CMI Estratégico."""

    # Header
    st.markdown(
        '<div class="header-container" style="padding:15px;margin-bottom:10px;">'
        '<div class="header-title" style="font-size:26px;">🎯 CMI Estratégico</div>'
        '<div class="header-subtitle" style="font-size:13px;">'
        'Cuadro de Mando Integral | Indicadores por Objetivo Estratégico</div>'
        '</div>',
        unsafe_allow_html=True
    )

    df_unificado = st.session_state.get('df_unificado')

    if df_unificado is None or df_unificado.empty:
        st.error("⚠️ No se pudieron cargar los datos.")
        return

    # Normalizar columna Año
    if 'Año' in df_unificado.columns:
        df_unificado = df_unificado.copy()
        df_unificado['Año'] = pd.to_numeric(df_unificado['Año'], errors='coerce')

    # ============================================================
    # FILTROS
    # ============================================================
    st.markdown("#### 🔍 Filtros")
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])

    with col_f1:
        años_permitidos = [2022, 2023, 2024, 2025]
        if 'Año' in df_unificado.columns:
            años_disp = sorted([
                int(a) for a in df_unificado['Año'].dropna().unique()
                if int(a) in años_permitidos
            ])
        else:
            años_disp = años_permitidos

        año_sel = st.selectbox(
            "Seleccione Año:",
            años_disp,
            index=len(años_disp) - 1 if años_disp else 0,
            key="filtro_año_cmi"
        )

    with col_f2:
        tipo_sel = st.selectbox(
            "Tipo de Indicador:",
            ["Indicadores", "Proyectos", "Todos"],
            key="filtro_tipo_cmi"
        )

    with col_f3:
        if 'Linea' in df_unificado.columns:
            lineas_disp = sorted(df_unificado['Linea'].dropna().unique().tolist())
        else:
            lineas_disp = []

        if not lineas_disp:
            st.error("No hay líneas disponibles en los datos.")
            return

        # Línea OBLIGATORIA — sin opción "Todas"
        linea_sel = st.selectbox(
            "Línea Estratégica: ✳️",
            lineas_disp,
            index=0,
            key="filtro_linea_cmi",
            help="Seleccione una línea estratégica para visualizar su CMI"
        )

    st.markdown("---")

    # ============================================================
    # FILTRAR DATOS
    # ============================================================
    df = df_unificado[df_unificado['Año'] == año_sel].copy()

    if df.empty:
        st.warning(f"No hay datos para el año {int(año_sel)}.")
        return

    # Tipo de indicador (fix NaN)
    if 'Proyectos' in df.columns:
        if tipo_sel == "Indicadores":
            df = df[df['Proyectos'].fillna(0) == 0]
        elif tipo_sel == "Proyectos":
            df = df[df['Proyectos'].fillna(0) == 1]

    # Solo avance/cierre
    if 'Fuente' in df.columns:
        df = df[df['Fuente'].isin(['Cierre', 'Avance'])]

    # Línea obligatoria
    if 'Linea' in df.columns:
        df = df[df['Linea'] == linea_sel]

    if df.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        return

    # ============================================================
    # COLOR DE LÍNEA
    # ============================================================
    color_linea = COLORES_LINEAS.get(linea_sel, COLORS['primary'])

    # Header de línea — ancho completo
    st.markdown(
        f'<div style="background:{color_linea};color:white;padding:12px 20px;'
        f'border-radius:6px;font-size:16px;font-weight:bold;margin-bottom:14px;">'
        f'📋 {linea_sel}</div>',
        unsafe_allow_html=True
    )

    # ============================================================
    # CUADRÍCULA 2 COLUMNAS POR OBJETIVO
    # ============================================================
    df = df.sort_values(['Objetivo', 'Indicador'])
    objetivos = []
    if 'Objetivo' in df.columns:
        objetivos = sorted(df['Objetivo'].dropna().unique().tolist())

    # Estilos de encabezados de tabla (reutilizables)
    th_ind = (
        f'background:{color_linea};color:white;padding:7px 10px;font-size:11px;'
        f'font-weight:bold;border:1px solid rgba(255,255,255,0.3);'
        f'text-align:left;white-space:nowrap;'
    )
    th_col = (
        f'background:{color_linea};color:white;padding:7px 10px;font-size:11px;'
        f'font-weight:bold;border:1px solid rgba(255,255,255,0.3);'
        f'text-align:center;white-space:nowrap;'
    )

    for i in range(0, len(objetivos), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j >= len(objetivos):
                break

            objetivo = objetivos[i + j]
            df_obj = df[df['Objetivo'] == objetivo]
            if 'Indicador' in df_obj.columns:
                df_obj = df_obj.drop_duplicates(subset=['Indicador'])

            # Construir filas de indicadores
            filas = ''
            for k, (_, row) in enumerate(df_obj.iterrows()):
                ind_nombre = row.get('Indicador', '')
                meta_v = fmt_num(row.get('Meta', ''))
                ejec_v = fmt_num(row.get('Ejecución', ''))
                cumpl = row.get('Cumplimiento', None)

                bg = '#f5f5f5' if k % 2 == 0 else 'white'
                td_base = (
                    f'padding:6px 10px;border:1px solid #e0e0e0;'
                    f'font-size:12px;background:{bg};text-align:center;'
                )
                td_ind = td_base + 'text-align:left;'

                # Celda de cumplimiento con círculo de color
                if cumpl is not None and pd.notna(cumpl):
                    cf = float(cumpl)
                    ccolor = (
                        COLORS['success'] if cf >= 100
                        else COLORS['warning'] if cf >= 80
                        else COLORS['danger']
                    )
                    dot = (
                        f'<span style="display:inline-block;width:11px;height:11px;'
                        f'border-radius:50%;background:{ccolor};vertical-align:middle;'
                        f'margin-left:5px;"></span>'
                    )
                    cumpl_cell = (
                        f'<span style="color:{ccolor};font-weight:bold;">'
                        f'{cf:.1f}%</span>{dot}'
                    )
                else:
                    cumpl_cell = '<span style="color:#aaa;">N/D</span>'

                filas += (
                    f'<tr>'
                    f'<td style="{td_ind}">{ind_nombre}</td>'
                    f'<td style="{td_base}">{meta_v}</td>'
                    f'<td style="{td_base}">{ejec_v}</td>'
                    f'<td style="{td_base}">{cumpl_cell}</td>'
                    f'</tr>'
                )

            # Card completa del objetivo
            card = (
                f'<div style="border:2px solid {color_linea};border-radius:8px;'
                f'overflow:hidden;margin-bottom:14px;">'
                # Encabezado del objetivo — mismo color que la línea
                f'<div style="background:{color_linea};color:white;padding:10px 14px;'
                f'font-weight:bold;font-size:11px;text-transform:uppercase;'
                f'text-align:center;line-height:1.4;">{objetivo}</div>'
                # Tabla de indicadores
                f'<table style="width:100%;border-collapse:collapse;">'
                f'<tr>'
                f'<th style="{th_ind}">Indicador</th>'
                f'<th style="{th_col}">Meta</th>'
                f'<th style="{th_col}">Ejecución</th>'
                f'<th style="{th_col}">Cumplimiento</th>'
                f'</tr>'
                f'{filas}'
                f'</table>'
                f'</div>'
            )

            with cols[j]:
                st.markdown(card, unsafe_allow_html=True)

    # ============================================================
    # RESUMEN ESTADÍSTICO
    # ============================================================
    st.markdown("---")
    col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

    total_ind = df['Indicador'].nunique() if 'Indicador' in df.columns else len(df)
    cumpl_prom = df['Cumplimiento'].mean() if 'Cumplimiento' in df.columns else 0
    if pd.isna(cumpl_prom):
        cumpl_prom = 0
    cumplidos = len(df[df['Cumplimiento'] >= 100]) if 'Cumplimiento' in df.columns else 0
    alerta = len(df[(df['Cumplimiento'] >= 80) & (df['Cumplimiento'] < 100)]) if 'Cumplimiento' in df.columns else 0
    peligro = len(df[df['Cumplimiento'] < 80]) if 'Cumplimiento' in df.columns else 0

    with col_s1:
        st.metric("📋 Indicadores", total_ind)
    with col_s2:
        st.metric("📊 Cumpl. Promedio", f"{cumpl_prom:.1f}%")
    with col_s3:
        st.metric("🟢 Cumplidos", cumplidos)
    with col_s4:
        st.metric("🟡 Alerta", alerta)
    with col_s5:
        st.metric("🔴 Peligro", peligro)
