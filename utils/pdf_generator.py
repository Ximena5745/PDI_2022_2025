# -*- coding: utf-8 -*-
"""
pdf_generator.py — Punto de entrada principal: funciones de exportación PDF PDI.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Any

import pandas as pd

from utils.pdf_colors import *  # noqa: F401, F403
from utils.pdf_primitives import *  # noqa: F401, F403
from utils.pdf_pages import PDFReportePOLI


# ============================================================
# FUNCIÓN PRINCIPAL DE EXPORTACIÓN
# ============================================================

def exportar_informe_pdf_reportlab(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    año: int = 2025,
    df_cascada: Optional[pd.DataFrame] = None,
    analisis_lineas: Optional[Dict[str, str]] = None,
    df_unificado: Optional[pd.DataFrame] = None,
) -> bytes:
    """
    Genera el informe PDF ejecutivo completo con ReportLab.

    Args:
        metricas: Diccionario con métricas generales del PDI.
        df_lineas: DataFrame con líneas estratégicas y su cumplimiento.
        df_indicadores: DataFrame con todos los indicadores del año.
        analisis_texto: Texto de análisis ejecutivo general (IA).
        año: Año del informe.
        df_cascada: DataFrame cascada con jerarquía (Nivel, Linea, Objetivo, Meta_PDI, ...).
        analisis_lineas: Dict {nombre_linea: texto_analisis_IA}.
        df_unificado: DataFrame completo del PDI (para extraer proyectos por línea).

    Returns:
        bytes del PDF generado.
    """
    pdf = PDFReportePOLI(año)

    # 1. Portada
    portada_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Portada.png'
    )
    pdf.portada(portada_path if os.path.exists(portada_path) else None)

    # 2. Resumen ejecutivo con gráficas
    pdf.resumen_ejecutivo(metricas, analisis_texto=analisis_texto,
                          df_lineas=df_lineas)

    # 3. Resumen circular por línea (tarjetas con mini donut)
    pdf.pagina_cumplimiento_lineas(df_lineas)

    # 4. Página detallada por línea estratégica — en ORDEN_LINEAS
    if df_lineas is not None and not df_lineas.empty:
        nc = 'Nivel' if (df_cascada is not None and 'Nivel' in df_cascada.columns) else None
        lc = 'Linea' if (df_cascada is not None and 'Linea' in df_cascada.columns) else None

        # Sort df_lineas by ORDEN_LINEAS
        def _sort_key(row):
            n = _norm(str(row.get('Linea', row.get('Línea', ''))))
            for i, ol in enumerate(ORDEN_LINEAS):
                if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                    return i
            return 99

        df_lineas_sorted = df_lineas.copy()
        df_lineas_sorted['_sort'] = [
            _sort_key(r) for _, r in df_lineas_sorted.iterrows()
        ]
        df_lineas_sorted = df_lineas_sorted.sort_values('_sort').drop(columns=['_sort'])

        for _, lr in df_lineas_sorted.iterrows():
            nom   = str(lr.get('Linea', lr.get('Línea', '')))
            cumpl = float(lr.get('Cumplimiento', 0) or 0)
            n_ind = int(lr.get('Total_Indicadores', 0) or 0)

            # ── Jerarquía: N2 Objetivo → N3 Meta_PDI → N4 Indicadores ──
            # Estructura: [{objetivo, cumplimiento, metas: [{meta_pdi, cumplimiento, indicadores[]}]}]
            objs = []
            _built_from_raw = False
            if df_unificado is not None and not df_unificado.empty and \
                    'Objetivo' in df_unificado.columns and 'Linea' in df_unificado.columns:
                # Filtrar por línea, año e indicadores (no proyectos)
                omask = df_unificado['Linea'] == nom
                if 'Año' in df_unificado.columns:
                    omask &= df_unificado['Año'] == año
                if 'Proyectos' in df_unificado.columns:
                    omask &= df_unificado['Proyectos'] == 0
                if 'Fuente' in df_unificado.columns:
                    omask &= df_unificado['Fuente'] == 'Avance'
                df_src = df_unificado[omask]

                _meta_col  = next((c for c in ['Meta', 'meta'] if c in df_src.columns), None)
                _ejec_col  = next((c for c in ['Ejecución', 'Ejecucion', 'ejecucion']
                                   if c in df_src.columns), None)
                _ind_col   = next((c for c in ['Indicador', 'indicador']
                                   if c in df_src.columns), None)
                _cumpl_col = 'Cumplimiento' if 'Cumplimiento' in df_src.columns else None
                _mpdi_col  = 'Meta_PDI' if 'Meta_PDI' in df_src.columns else None

                def _safe_val(v):
                    return None if (v is None or str(v) in ('nan', 'None', '')) else v

                if not df_src.empty and _ind_col:
                    for obj_name, df_obj in df_src.groupby('Objetivo', sort=True):
                        cumpl_obj = float(df_obj[_cumpl_col].mean()) if _cumpl_col else 0.0
                        metas_list = []

                        # Agrupar indicadores por Meta_PDI (Nivel 3)
                        if _mpdi_col and df_obj[_mpdi_col].notna().any():
                            for meta_val, df_meta in df_obj.groupby(_mpdi_col, sort=True):
                                cumpl_meta = float(df_meta[_cumpl_col].mean()) if _cumpl_col else 0.0
                                inds = []
                                for _, ir in df_meta.drop_duplicates(_ind_col).iterrows():
                                    inds.append({
                                        'nombre':       str(ir.get(_ind_col, '')),
                                        'meta_valor':   _safe_val(ir.get(_meta_col) if _meta_col else None),
                                        'ejecucion':    _safe_val(ir.get(_ejec_col) if _ejec_col else None),
                                        'cumplimiento': float(ir.get(_cumpl_col, 0) or 0) if _cumpl_col else 0.0,
                                    })
                                metas_list.append({
                                    'meta_pdi':     str(meta_val),
                                    'cumplimiento': cumpl_meta,
                                    'indicadores':  inds,
                                })
                        else:
                            # Sin Meta_PDI: todos los indicadores en un solo bloque
                            inds = []
                            for _, ir in df_obj.drop_duplicates(_ind_col).iterrows():
                                inds.append({
                                    'nombre':       str(ir.get(_ind_col, '')),
                                    'meta_valor':   _safe_val(ir.get(_meta_col) if _meta_col else None),
                                    'ejecucion':    _safe_val(ir.get(_ejec_col) if _ejec_col else None),
                                    'cumplimiento': float(ir.get(_cumpl_col, 0) or 0) if _cumpl_col else 0.0,
                                })
                            metas_list.append({
                                'meta_pdi':     '',
                                'cumplimiento': cumpl_obj,
                                'indicadores':  inds,
                            })

                        objs.append({
                            'objetivo':     str(obj_name),
                            'cumplimiento': cumpl_obj,
                            'metas':        metas_list,
                        })
                    _built_from_raw = True

            # Fallback: cascada cuando no hay df_unificado
            if not _built_from_raw and df_cascada is not None and \
                    not df_cascada.empty and nc and lc:
                mask2 = (df_cascada[nc] == 2) & (df_cascada[lc] == nom)
                for _, or_ in df_cascada[mask2].iterrows():
                    obj_name  = str(or_.get('Objetivo', nom))
                    cumpl_obj = float(or_.get('Cumplimiento', 0) or 0)
                    metas_fb  = []
                    if 'Meta_PDI' in df_cascada.columns:
                        mask3 = ((df_cascada[nc] == 3) & (df_cascada[lc] == nom) &
                                 (df_cascada['Objetivo'] == obj_name))
                        for _, mr in df_cascada[mask3].iterrows():
                            metas_fb.append({
                                'meta_pdi':     str(mr.get('Meta_PDI', '')),
                                'cumplimiento': float(mr.get('Cumplimiento', 0) or 0),
                                'indicadores':  [],
                            })
                    if not metas_fb:
                        metas_fb = [{'meta_pdi': '', 'cumplimiento': cumpl_obj, 'indicadores': []}]
                    objs.append({
                        'objetivo':     obj_name,
                        'cumplimiento': cumpl_obj,
                        'metas':        metas_fb,
                    })

            # ── Proyectos de esta línea (Proyectos=1 en df_unificado) ─
            proyectos = []
            if df_unificado is not None and not df_unificado.empty:
                has_proy = 'Proyectos' in df_unificado.columns
                has_lin  = 'Linea' in df_unificado.columns
                if has_proy and has_lin:
                    pmask = (df_unificado['Proyectos'] == 1) & (df_unificado['Linea'] == nom)
                    if 'Año' in df_unificado.columns:
                        pmask &= (df_unificado['Año'] == año)
                    id_col = 'Indicador' if 'Indicador' in df_unificado.columns else None
                    df_p = df_unificado[pmask]
                    if id_col:
                        df_p = df_p.drop_duplicates(id_col)
                    for _, pr in df_p.iterrows():
                        proyectos.append({
                            'nombre':       str(pr.get(id_col, '') if id_col else ''),
                            'cumplimiento': float(pr.get('Cumplimiento', 0) or 0),
                        })

            # ── Indicadores Sin Meta (Meta=NaN/0) ─────────────────────
            sin_meta = []
            if df_unificado is not None and not df_unificado.empty:
                has_lin_u  = 'Linea' in df_unificado.columns
                has_meta_u = 'Meta' in df_unificado.columns
                has_ind_u  = 'Indicador' in df_unificado.columns
                if has_lin_u and has_meta_u and has_ind_u:
                    smask = df_unificado['Linea'] == nom
                    if 'Año' in df_unificado.columns:
                        smask &= df_unificado['Año'] == año
                    if 'Proyectos' in df_unificado.columns:
                        smask &= df_unificado['Proyectos'] == 0
                    df_sm = df_unificado[smask]
                    # Filter where Meta is NaN or zero
                    meta_null = df_sm['Meta'].isna() | (df_sm['Meta'] == 0)
                    df_sm_null = df_sm[meta_null].drop_duplicates('Indicador')
                    for _, sr in df_sm_null.iterrows():
                        sin_meta.append({
                            'nombre': str(sr.get('Indicador', '')),
                        })

            # ── Análisis IA por línea ─────────────────────────────────
            analisis_txt = ''
            if analisis_lineas:
                analisis_txt = analisis_lineas.get(nom, '')
                if not analisis_txt:
                    nom_n = _norm(nom)
                    for k, v in analisis_lineas.items():
                        if _norm(k) == nom_n:
                            analisis_txt = v
                            break

            pdf.pagina_linea(
                nombre=nom,
                cumplimiento=cumpl,
                total_ind=n_ind,
                objetivos=objs,
                proyectos=proyectos,
                analisis=analisis_txt,
                sin_meta=sin_meta if sin_meta else None,
            )

    # 5. Tabla de indicadores
    if df_indicadores is not None and not df_indicadores.empty:
        pdf.tabla_indicadores(df_indicadores)

    # 6. Conclusiones y glosario
    pdf.conclusiones(metricas, df_lineas, df_indicadores=df_indicadores)

    return pdf.generar()


# ============================================================
# HELPERS FOR exportar_informe_pdf_poli
# ============================================================

def _build_objetivos(df_src, año: int) -> list:
    """Build N2→N3→N4 objectives hierarchy from a filtered DataFrame."""
    _ind_col   = next((c for c in ['Indicador', 'indicador'] if c in df_src.columns), None)
    _meta_col  = next((c for c in ['Meta', 'meta'] if c in df_src.columns), None)
    _ejec_col  = next((c for c in ['Ejecución', 'Ejecucion', 'ejecucion'] if c in df_src.columns), None)
    _cumpl_col = 'Cumplimiento' if 'Cumplimiento' in df_src.columns else None
    _mpdi_col  = 'Meta_PDI' if 'Meta_PDI' in df_src.columns else None

    def _safe_val(v):
        return None if (v is None or str(v) in ('nan', 'None', '')) else v

    objs = []
    if df_src.empty or not _ind_col:
        return objs

    for obj_name, df_obj in df_src.groupby('Objetivo', sort=True):
        cumpl_obj = float(df_obj[_cumpl_col].mean()) if _cumpl_col else 0.0
        metas_list = []
        if _mpdi_col and df_obj[_mpdi_col].notna().any():
            for meta_val, df_meta in df_obj.groupby(_mpdi_col, sort=True):
                cumpl_meta = float(df_meta[_cumpl_col].mean()) if _cumpl_col else 0.0
                inds = []
                for _, ir in df_meta.drop_duplicates(_ind_col).iterrows():
                    inds.append({
                        'nombre':       str(ir.get(_ind_col, '')),
                        'meta_valor':   _safe_val(ir.get(_meta_col) if _meta_col else None),
                        'ejecucion':    _safe_val(ir.get(_ejec_col) if _ejec_col else None),
                        'cumplimiento': float(ir.get(_cumpl_col, 0) or 0) if _cumpl_col else 0.0,
                    })
                metas_list.append({
                    'meta_pdi':     str(meta_val),
                    'cumplimiento': cumpl_meta,
                    'indicadores':  inds,
                })
        else:
            inds = []
            for _, ir in df_obj.drop_duplicates(_ind_col).iterrows():
                inds.append({
                    'nombre':       str(ir.get(_ind_col, '')),
                    'meta_valor':   _safe_val(ir.get(_meta_col) if _meta_col else None),
                    'ejecucion':    _safe_val(ir.get(_ejec_col) if _ejec_col else None),
                    'cumplimiento': float(ir.get(_cumpl_col, 0) or 0) if _cumpl_col else 0.0,
                })
            metas_list.append({
                'meta_pdi':     '',
                'cumplimiento': cumpl_obj,
                'indicadores':  inds,
            })
        objs.append({
            'objetivo':     str(obj_name),
            'cumplimiento': cumpl_obj,
            'metas':        metas_list,
        })
    return objs


def _build_proyectos(df_unificado: pd.DataFrame, nom: str, año: int) -> list:
    """Extract project list for a strategic line from df_unificado."""
    proyectos = []
    if df_unificado is None or df_unificado.empty:
        return proyectos
    if 'Proyectos' not in df_unificado.columns or 'Linea' not in df_unificado.columns:
        return proyectos
    pmask = (df_unificado['Proyectos'] == 1) & (df_unificado['Linea'] == nom)
    if 'Año' in df_unificado.columns:
        pmask &= (df_unificado['Año'] == año)
    id_col = 'Indicador' if 'Indicador' in df_unificado.columns else None
    df_p = df_unificado[pmask]
    if id_col:
        df_p = df_p.drop_duplicates(id_col)
    for _, pr in df_p.iterrows():
        proyectos.append({
            'nombre':       str(pr.get(id_col, '') if id_col else ''),
            'cumplimiento': float(pr.get('Cumplimiento', 0) or 0),
        })
    return proyectos


def _build_sin_meta(df_unificado: pd.DataFrame, nom: str, año: int) -> list:
    """Extract indicators without a defined meta for a strategic line."""
    sin_meta = []
    if df_unificado is None or df_unificado.empty:
        return sin_meta
    cols_needed = {'Linea', 'Meta', 'Indicador'}
    if not cols_needed.issubset(df_unificado.columns):
        return sin_meta
    smask = df_unificado['Linea'] == nom
    if 'Año' in df_unificado.columns:
        smask &= df_unificado['Año'] == año
    if 'Proyectos' in df_unificado.columns:
        smask &= df_unificado['Proyectos'] == 0
    df_sm = df_unificado[smask]
    meta_null = df_sm['Meta'].isna() | (df_sm['Meta'] == 0)
    for _, sr in df_sm[meta_null].drop_duplicates('Indicador').iterrows():
        sin_meta.append({'nombre': str(sr.get('Indicador', ''))})
    return sin_meta


def exportar_informe_pdf_poli(
    metricas: Dict[str, Any],
    df_lineas: pd.DataFrame,
    df_indicadores: pd.DataFrame,
    analisis_texto: str = "",
    año: int = 2025,
    df_cascada: Optional[pd.DataFrame] = None,
    analisis_lineas: Optional[Dict[str, str]] = None,
    df_unificado: Optional[pd.DataFrame] = None,
) -> bytes:
    """
    Genera el informe PDF POLI con diseño mejorado (versión 2):
    - Fondo con textura de puntos
    - Headers estándar navy con franja diagonal de acento
    - Header A para páginas de línea (trapecio con 4 stats)
    - Gauges semicirculares matplotlib en página de cumplimiento
    - Footer con línea de acento de color

    Args:
        metricas: Diccionario con métricas generales del PDI.
        df_lineas: DataFrame con líneas estratégicas y su cumplimiento.
        df_indicadores: DataFrame con todos los indicadores del año.
        analisis_texto: Texto de análisis ejecutivo general (IA).
        año: Año del informe.
        df_cascada: DataFrame cascada con jerarquía.
        analisis_lineas: Dict {nombre_linea: texto_analisis_IA}.
        df_unificado: DataFrame completo del PDI.

    Returns:
        bytes del PDF generado.
    """
    pdf = PDFReportePOLI(año)

    # 1. Portada
    portada_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Portada.png'
    )
    pdf.portada(portada_path if os.path.exists(portada_path) else None)

    # 2. Resumen ejecutivo
    pdf.resumen_ejecutivo(metricas, analisis_texto=analisis_texto,
                          df_lineas=df_lineas)

    # 3. Página de cumplimiento por línea (gauges)
    pdf.pagina_cumplimiento_lineas(df_lineas)

    # 4. Página detallada por línea estratégica
    if df_lineas is not None and not df_lineas.empty:
        def _sort_key(row):
            n = _norm(str(row.get('Linea', row.get('Línea', ''))))
            for i, ol in enumerate(ORDEN_LINEAS):
                if _norm(ol) == n or _norm(ol)[:8] == n[:8]:
                    return i
            return 99

        df_lineas_sorted = df_lineas.copy()
        df_lineas_sorted['_sort'] = [_sort_key(r) for _, r in df_lineas_sorted.iterrows()]
        df_lineas_sorted = df_lineas_sorted.sort_values('_sort').drop(columns=['_sort'])

        for _, lr in df_lineas_sorted.iterrows():
            nom   = str(lr.get('Linea', lr.get('Línea', '')))
            cumpl = float(lr.get('Cumplimiento', 0) or 0)
            n_ind = int(lr.get('Total_Indicadores', 0) or 0)

            # Build objectives hierarchy
            objs = []
            _built = False
            if df_unificado is not None and not df_unificado.empty and \
                    'Objetivo' in df_unificado.columns and 'Linea' in df_unificado.columns:
                omask = df_unificado['Linea'] == nom
                if 'Año' in df_unificado.columns:
                    omask &= df_unificado['Año'] == año
                if 'Proyectos' in df_unificado.columns:
                    omask &= df_unificado['Proyectos'] == 0
                if 'Fuente' in df_unificado.columns:
                    omask &= df_unificado['Fuente'] == 'Avance'
                df_src = df_unificado[omask]
                if not df_src.empty:
                    objs = _build_objetivos(df_src, año)
                    _built = True

            if not _built and df_cascada is not None and not df_cascada.empty:
                nc = 'Nivel' if 'Nivel' in df_cascada.columns else None
                lc = 'Linea' if 'Linea' in df_cascada.columns else None
                if nc and lc:
                    mask2 = (df_cascada[nc] == 2) & (df_cascada[lc] == nom)
                    for _, or_ in df_cascada[mask2].iterrows():
                        obj_name  = str(or_.get('Objetivo', nom))
                        cumpl_obj = float(or_.get('Cumplimiento', 0) or 0)
                        metas_fb  = []
                        if 'Meta_PDI' in df_cascada.columns:
                            mask3 = ((df_cascada[nc] == 3) & (df_cascada[lc] == nom) &
                                     (df_cascada['Objetivo'] == obj_name))
                            for _, mr in df_cascada[mask3].iterrows():
                                metas_fb.append({
                                    'meta_pdi':     str(mr.get('Meta_PDI', '')),
                                    'cumplimiento': float(mr.get('Cumplimiento', 0) or 0),
                                    'indicadores':  [],
                                })
                        if not metas_fb:
                            metas_fb = [{'meta_pdi': '', 'cumplimiento': cumpl_obj,
                                         'indicadores': []}]
                        objs.append({'objetivo': obj_name, 'cumplimiento': cumpl_obj,
                                     'metas': metas_fb})

            proyectos = _build_proyectos(df_unificado, nom, año)
            sin_meta  = _build_sin_meta(df_unificado, nom, año)

            analisis_txt = ''
            if analisis_lineas:
                analisis_txt = analisis_lineas.get(nom, '')
                if not analisis_txt:
                    nom_n = _norm(nom)
                    for k, v in analisis_lineas.items():
                        if _norm(k) == nom_n:
                            analisis_txt = v
                            break

            pdf.pagina_linea(
                nombre=nom,
                cumplimiento=cumpl,
                total_ind=n_ind,
                objetivos=objs,
                proyectos=proyectos,
                analisis=analisis_txt,
                sin_meta=sin_meta if sin_meta else None,
            )

    # 5. Tabla de indicadores
    if df_indicadores is not None and not df_indicadores.empty:
        pdf.tabla_indicadores(df_indicadores)

    # 6. Conclusiones y glosario
    pdf.conclusiones(metricas, df_lineas, df_indicadores=df_indicadores)

    return pdf.generar()
