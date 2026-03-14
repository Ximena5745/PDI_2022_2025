"""
utils/data_loader.py — Shim de compatibilidad.

Toda la lógica real ha migrado a:
  - core/config.py        → COLORS, COLORES_LINEAS, LINEAS_ESTRATEGICAS
  - core/calculations.py  → calcular_cumplimiento, obtener_color_semaforo, …
  - core/filters.py       → filtrar_por_linea, obtener_lista_indicadores, …
  - core/repository.py    → DataRepository
  - services/analytics_service.py → calcular_metricas_generales, cascada, …

Este archivo re-exporta todo para que los imports legacy de las views
sigan funcionando sin cambios durante la transición.
"""

import streamlit as st
import pandas as pd

# ── Re-exports desde core ──────────────────────────────────────────────────
from core.config import (
    COLORS,
    COLORES_LINEAS,
    LINEAS_ESTRATEGICAS,
    OBJETIVO_STANDBY,
)
from core.calculations import (
    calcular_cumplimiento,
    obtener_color_semaforo,
    obtener_estado_semaforo,
    es_objetivo_standby,
)
from core.filters import (
    filtrar_por_linea,
    filtrar_por_objetivo,
    obtener_lista_indicadores,
    obtener_lista_objetivos,
)
from core.repository import DataRepository, DataLoadError
from core.processor import normalizar_columnas
from services.analytics_service import AnalyticsService
from utils.helpers import exportar_a_excel

# ── Instancias singleton (reutilizadas por las funciones de compatibilidad) ─
_repo = DataRepository()
_svc = AnalyticsService()


# ── Carga de datos (con caché de Streamlit) ────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos():
    """
    Carga Base_Indicadores y Unificado desde el Excel.
    Retorna (df_base, df_unificado, df_base) para mantener la firma original.
    """
    try:
        df_base, df_unificado = _repo.cargar()
        return df_base, df_unificado, df_base
    except DataLoadError as e:
        st.error(str(e))
        return None, None, None
    except Exception as e:
        st.error(f"Error inesperado al cargar datos: {e}")
        return None, None, None


# ── Métricas y análisis (wrappers sobre AnalyticsService) ─────────────────
def calcular_metricas_generales(df_unificado: pd.DataFrame, año=None) -> dict:
    metricas = _svc.calcular_metricas_generales(df_unificado, año)
    return metricas.as_dict()


def calcular_estado_proyectos(df_unificado: pd.DataFrame, año=None) -> dict:
    estado = _svc.calcular_estado_proyectos(df_unificado, año)
    return estado.as_dict()


def obtener_cumplimiento_por_linea(df_unificado: pd.DataFrame, año=None) -> pd.DataFrame:
    lineas = _svc.cumplimiento_por_linea(df_unificado, año)
    if not lineas:
        return pd.DataFrame()
    rows = []
    for l in lineas:
        rows.append({
            "Linea": l.linea,
            "Cumplimiento": l.cumplimiento,
            "Total_Indicadores": l.total_indicadores,
            "Color": l.color,
        })
    return pd.DataFrame(rows)


def obtener_historico_indicador_completo(
    df_unificado: pd.DataFrame,
    df_base: pd.DataFrame,
    indicador_nombre: str,
):
    df_hist, meta = _svc.historico_indicador(df_unificado, df_base, indicador_nombre)
    return df_hist, meta.periodicidad, meta.sentido, meta.unidad_meta, meta.unidad_ejecucion


def obtener_historico_indicador(df_unificado: pd.DataFrame, indicador_id):
    if df_unificado is None or df_unificado.empty:
        return pd.DataFrame()
    if "Id" in df_unificado.columns:
        df = df_unificado[df_unificado["Id"] == indicador_id].copy()
    elif "Indicador" in df_unificado.columns:
        df = df_unificado[df_unificado["Indicador"] == indicador_id].copy()
    else:
        return pd.DataFrame()
    if not df.empty and "Año" in df.columns:
        df = df.sort_values("Año")
    return df


def obtener_cumplimiento_cascada(
    df_unificado: pd.DataFrame,
    df_base: pd.DataFrame,
    año=None,
    max_niveles: int = 4,
    filtro_tipo: str = "indicadores",
) -> pd.DataFrame:
    return _svc.calcular_cascada(df_unificado, df_base, año, max_niveles, filtro_tipo)


# ── Re-export para imports directos ────────────────────────────────────────
__all__ = [
    "COLORS", "COLORES_LINEAS", "LINEAS_ESTRATEGICAS", "OBJETIVO_STANDBY",
    "cargar_datos",
    "calcular_cumplimiento", "obtener_color_semaforo", "obtener_estado_semaforo",
    "es_objetivo_standby", "normalizar_columnas",
    "calcular_metricas_generales", "calcular_estado_proyectos",
    "obtener_cumplimiento_por_linea", "obtener_historico_indicador",
    "obtener_historico_indicador_completo", "obtener_cumplimiento_cascada",
    "filtrar_por_linea", "filtrar_por_objetivo",
    "obtener_lista_indicadores", "obtener_lista_objetivos",
    "exportar_a_excel",
]
