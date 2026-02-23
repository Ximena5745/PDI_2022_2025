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

# Indicadores de Expansión a mostrar (orden fijo: 3 izq, 3 der)
INDICADORES_EXPANSION_IZQ = [
    "Total Población",
    "Total estudiantes nuevos",
    "Total Matriculados antiguos",
]
INDICADORES_EXPANSION_DER = [
    "Brand equity",
    "Conocimiento espontaneo",
    "Lanzamiento de nuevos programas virtual",
]


def _eu(num_str):
    """Convierte separadores US (1,234.56) → formato europeo (1.234,56)."""
    return num_str.replace(',', 'X').replace('.', ',').replace('X', '.')


def fmt_valor(v, signo, decimales):
    """
    Formatea un valor numérico según el tipo de signo (DAX logic).
    Separadores europeos: punto para miles, coma para decimales.
    ENT  → entero con separador de miles
    %    → número con decimales + '%'
    kWh  → entero + ' kWh'
    $    → '$' + entero con miles
    DEC  → número con decimales especificados
    """
    if v is None:
        return ''
    try:
        if pd.isna(v):
            return ''
        f = float(v)
        s = str(signo).strip() if signo and not (isinstance(signo, float) and pd.isna(signo)) else ''
        d = int(decimales) if decimales and not (isinstance(decimales, float) and pd.isna(decimales)) else 0

        if s == 'ENT':
            return _eu(f"{int(round(f)):,}")
        elif s == '%':
            if d > 0:
                return _eu(f"{round(f, d):,.{d}f}") + '%'
            else:
                return _eu(f"{int(round(f)):,}") + '%'
        elif s == 'kWh':
            return _eu(f"{int(round(f)):,}") + ' kWh'
        elif s == '$':
            return '$' + _eu(f"{int(round(f)):,}")
        elif s == 'DEC':
            if d > 0:
                return _eu(f"{round(f, d):,.{d}f}")
            else:
                return _eu(str(int(f))) if f == int(f) else _eu(f"{f:.1f}")
        else:
            # Sin signo o tipo no reconocido
            if d > 0:
                return _eu(f"{round(f, d):,.{d}f}")
            else:
                return _eu(str(int(f))) if f == int(f) else _eu(f"{f:.1f}")
    except Exception:
        return str(v) if str(v) not in ('nan', 'None', '') else ''


def _build_fila(k, row):
    """Construye el HTML de una fila de indicador."""
    ind_nombre = row.get('Indicador', '')

    # Valores con formato
    meta_v = fmt_valor(
        row.get('Meta', ''),
        row.get('Meta s', ''),
        row.get('Decimales_Meta', 0)
    )
    ejec_v = fmt_valor(
        row.get('Ejecución', ''),
        row.get('Ejecución s', ''),
        row.get('Decimales_Ejecucion', 0)
    )
    cumpl = row.get('Cumplimiento', None)

    bg = '#f5f5f5' if k % 2 == 0 else 'white'
    td_base = (
        f'padding:8px 10px;border:1px solid #e0e0e0;'
        f'font-size:17px;background:{bg};text-align:center;'
    )
    td_ind = td_base + 'text-align:left;'

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

    return (
        f'<tr>'
        f'<td style="{td_ind}">{ind_nombre}</td>'
        f'<td style="{td_base}">{meta_v}</td>'
        f'<td style="{td_base}">{ejec_v}</td>'
        f'<td style="{td_base}">{cumpl_cell}</td>'
        f'</tr>'
    )


def _build_card(objetivo, df_obj, color_linea):
    """Construye el HTML de una card completa de objetivo."""
    # Encabezados: fondo claro, texto del color de la línea, centrados
    th_style = (
        f'background:#f0f0f0;color:{color_linea};padding:9px 10px;font-size:16px;'
        f'font-weight:bold;border:1px solid {color_linea};'
        f'text-align:center;white-space:nowrap;'
    )
    th_ind = th_style
    th_col = th_style

    filas = ''
    for k, (_, row) in enumerate(df_obj.iterrows()):
        filas += _build_fila(k, row)

    return (
        f'<div style="border:2px solid {color_linea};border-radius:8px;'
        f'overflow:hidden;margin-bottom:14px;">'
        f'<div style="background:{color_linea};color:white;padding:10px 14px;'
        f'font-weight:bold;font-size:15px;text-transform:uppercase;'
        f'text-align:center;line-height:1.4;">{objetivo}</div>'
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


def mostrar_pagina():
    """Renderiza la página del CMI Estratégico."""

    # Header
    st.markdown(
        '<div class="header-container" style="padding:15px;margin-bottom:10px;">'
        '<div class="header-title" style="font-size:26px;">CMI Estratégico</div>'
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

    # Mapa año numérico → etiqueta visible (2026 = "Avance")
    YEAR_MAP = {2022: "2022", 2023: "2023", 2024: "2024", 2025: "2025", 2026: "Avance"}
    YEAR_MAP_INV = {"2022": 2022, "2023": 2023, "2024": 2024, "2025": 2025, "Avance": 2026}

    with col_f1:
        anios_permitidos = [2022, 2023, 2024, 2025, 2026]
        if 'Año' in df_unificado.columns:
            anios_disp_num = sorted([
                int(a) for a in df_unificado['Año'].dropna().unique()
                if int(a) in anios_permitidos
            ])
        else:
            anios_disp_num = anios_permitidos

        anios_labels = [YEAR_MAP.get(a, str(a)) for a in anios_disp_num]

        label_sel = st.selectbox(
            "Seleccione Año:",
            anios_labels,
            index=len(anios_labels) - 1 if anios_labels else 0,
            key="filtro_anio_cmi"
        )
        anio_sel = YEAR_MAP_INV.get(label_sel, 2025)

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

    # ============================================================
    # MULTISELECT DE INDICADORES/PROYECTOS
    # Filtro preliminar para obtener las opciones disponibles
    # ============================================================
    df_prev = df_unificado.copy()
    if 'Año' in df_prev.columns:
        df_prev['Año'] = pd.to_numeric(df_prev['Año'], errors='coerce')
    df_prev = df_prev[df_prev['Año'] == anio_sel]
    if 'Proyectos' in df_prev.columns:
        if tipo_sel == "Indicadores":
            df_prev = df_prev[df_prev['Proyectos'].fillna(0) == 0]
        elif tipo_sel == "Proyectos":
            df_prev = df_prev[df_prev['Proyectos'].fillna(0) == 1]
    if 'Fuente' in df_prev.columns:
        df_prev = df_prev[df_prev['Fuente'].isin(['Cierre', 'Avance'])]
    if 'Linea' in df_prev.columns:
        df_prev = df_prev[df_prev['Linea'] == linea_sel]

    indicadores_disp = (
        sorted(df_prev['Indicador'].dropna().unique().tolist())
        if 'Indicador' in df_prev.columns else []
    )

    # La key incluye los 3 filtros principales: al cambiar línea/año/tipo se resetea la selección
    ms_key = f"filtro_ind_cmi_{linea_sel}_{label_sel}_{tipo_sel}"

    indicadores_sel = st.multiselect(
        "Indicadores / Proyectos a mostrar:",
        options=indicadores_disp,
        default=indicadores_disp,
        key=ms_key,
        placeholder="Seleccione uno o más indicadores…"
    )

    st.markdown("---")

    # ============================================================
    # FILTRAR DATOS
    # ============================================================
    df = df_unificado[df_unificado['Año'] == anio_sel].copy()

    if df.empty:
        st.warning(f"No hay datos para {label_sel}.")
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

    # Filtro de indicadores seleccionados en el multiselect
    if indicadores_sel and 'Indicador' in df.columns:
        df = df[df['Indicador'].isin(indicadores_sel)]

    if df.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        return

    # ============================================================
    # COLOR Y TÍTULO DE LÍNEA
    # ============================================================
    color_linea = COLORES_LINEAS.get(linea_sel, COLORS['primary'])
    titulo_linea = linea_sel.replace('_', ' ')

    def _render_titulo(container=None):
        """Renderiza el header de línea en el contenedor dado (o en la página si None)."""
        html = (
            f'<div style="background:{color_linea};color:white;padding:12px 20px;'
            f'border-radius:6px;font-size:18px;font-weight:bold;margin-bottom:14px;'
            f'text-align:center;">'
            f'{titulo_linea}</div>'
        )
        if container:
            container.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(html, unsafe_allow_html=True)

    # ============================================================
    # LAYOUT ESPECIAL PARA EXPANSIÓN
    # ============================================================
    if linea_sel == 'Expansión':
        _render_titulo()
        _mostrar_expansion(df, color_linea)

    # ============================================================
    # CUADRÍCULA 2 COLUMNAS POR OBJETIVO (otras líneas)
    # ============================================================
    else:
        df = df.sort_values(['Objetivo', 'Indicador'])
        objetivos = []
        if 'Objetivo' in df.columns:
            objetivos = sorted(df['Objetivo'].dropna().unique().tolist())

        # Título a ancho completo solo cuando hay más de un objetivo
        if len(objetivos) != 1:
            _render_titulo()

        for i in range(0, len(objetivos), 2):
            restantes = len(objetivos) - i

            if restantes == 1:
                # Objetivo impar: título + card centrados en columna central
                objetivo = objetivos[i]
                df_obj = df[df['Objetivo'] == objetivo]
                if 'Indicador' in df_obj.columns:
                    df_obj = df_obj.drop_duplicates(subset=['Indicador'])
                _, col_center, _ = st.columns([1, 2, 1])
                with col_center:
                    # Título dentro de la columna solo si es el único objetivo de la línea
                    if len(objetivos) == 1:
                        _render_titulo(col_center)
                    st.markdown(
                        _build_card(objetivo, df_obj, color_linea),
                        unsafe_allow_html=True
                    )
            else:
                # Par de objetivos: 2 columnas iguales
                cols = st.columns(2)
                for j in range(2):
                    if i + j >= len(objetivos):
                        break

                    objetivo = objetivos[i + j]
                    df_obj = df[df['Objetivo'] == objetivo]
                    if 'Indicador' in df_obj.columns:
                        df_obj = df_obj.drop_duplicates(subset=['Indicador'])

                    with cols[j]:
                        st.markdown(
                            _build_card(objetivo, df_obj, color_linea),
                            unsafe_allow_html=True
                        )

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


def _mostrar_expansion(df, color_linea):
    """
    Layout especial para Expansión: dos paneles planos con indicadores fijos.
    Izquierda: poblacional | Derecha: posicionamiento.
    """
    # Encabezados: fondo claro, texto del color de la línea, centrados
    th_style = (
        f'background:#f0f0f0;color:{color_linea};padding:9px 10px;font-size:16px;'
        f'font-weight:bold;border:1px solid {color_linea};'
        f'text-align:center;white-space:nowrap;'
    )
    th_ind = th_style
    th_col = th_style

    def get_objetivo(indicadores_lista):
        """Obtiene el nombre del objetivo del primer indicador encontrado."""
        for nombre in indicadores_lista:
            df_ind = df[df['Indicador'] == nombre]
            if not df_ind.empty and 'Objetivo' in df_ind.columns:
                val = df_ind.iloc[0].get('Objetivo', '')
                if val and str(val) not in ('', 'nan', 'None'):
                    return str(val)
        return ''

    def build_panel(indicadores_lista):
        """Construye una tabla plana para una lista de indicadores (sin header de objetivo)."""
        filas = ''
        for k, nombre in enumerate(indicadores_lista):
            df_ind = df[df['Indicador'] == nombre]
            if df_ind.empty:
                continue
            row = df_ind.drop_duplicates(subset=['Indicador']).iloc[0]
            filas += _build_fila(k, row)

        if not filas:
            return ''

        return (
            f'<div style="border:2px solid {color_linea};border-radius:8px;'
            f'overflow:hidden;margin-bottom:14px;">'
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

    # Header de objetivo — ancho completo, una sola vez
    objetivo_nombre = get_objetivo(INDICADORES_EXPANSION_IZQ) or get_objetivo(INDICADORES_EXPANSION_DER)
    if objetivo_nombre:
        st.markdown(
            f'<div style="background:{color_linea};color:white;padding:10px 14px;'
            f'font-weight:bold;font-size:15px;text-transform:uppercase;'
            f'text-align:center;line-height:1.4;border-radius:6px;margin-bottom:10px;">'
            f'{objetivo_nombre}</div>',
            unsafe_allow_html=True
        )

    col_izq, col_der = st.columns(2)
    html_izq = build_panel(INDICADORES_EXPANSION_IZQ)
    html_der = build_panel(INDICADORES_EXPANSION_DER)

    with col_izq:
        if html_izq:
            st.markdown(html_izq, unsafe_allow_html=True)
        else:
            st.info("Sin datos para el panel izquierdo.")

    with col_der:
        if html_der:
            st.markdown(html_der, unsafe_allow_html=True)
        else:
            st.info("Sin datos para el panel derecho.")
