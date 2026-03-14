"""
Funciones de filtrado y consulta sobre DataFrames del PDI.
Sin dependencias de Streamlit.
"""

from __future__ import annotations

import pandas as pd
from typing import Optional


# ---------------------------------------------------------------------------
# Filtros básicos
# ---------------------------------------------------------------------------
def filtrar_por_linea(df: pd.DataFrame, linea: str) -> pd.DataFrame:
    if df is None or "Linea" not in df.columns:
        return df
    return df[df["Linea"] == linea]


def filtrar_por_objetivo(df: pd.DataFrame, objetivo: str) -> pd.DataFrame:
    if df is None or "Objetivo" not in df.columns:
        return df
    return df[df["Objetivo"] == objetivo]


def filtrar_por_año(df: pd.DataFrame, año: int) -> pd.DataFrame:
    if df is None or "Año" not in df.columns:
        return df
    return df[df["Año"] == año]


def filtrar_por_fuente(df: pd.DataFrame, fuente: str) -> pd.DataFrame:
    if df is None or "Fuente" not in df.columns:
        return df
    return df[df["Fuente"] == fuente]


def filtrar_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """Excluye proyectos (Proyectos == 0)."""
    if df is None or "Proyectos" not in df.columns:
        return df
    return df[df["Proyectos"] == 0]


def filtrar_proyectos(df: pd.DataFrame) -> pd.DataFrame:
    """Solo proyectos (Proyectos == 1)."""
    if df is None or "Proyectos" not in df.columns:
        return df
    return df[df["Proyectos"] == 1]


def excluir_standby(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas marcadas como Stand by en 'Ejecución s'."""
    if df is None or "Ejecución s" not in df.columns:
        return df
    mask = df["Ejecución s"].astype(str).str.strip().str.lower() == "stand by"
    return df[~mask]


def filtrar_años_validos(df: pd.DataFrame, años: list[int]) -> pd.DataFrame:
    """Conserva solo los años del PDI (excluye línea base 2021)."""
    if df is None or "Año" not in df.columns:
        return df
    return df[df["Año"].isin(años)]


# ---------------------------------------------------------------------------
# Consultas de catálogo
# ---------------------------------------------------------------------------
def obtener_lista_indicadores(
    df: pd.DataFrame,
    linea: Optional[str] = None,
    objetivo: Optional[str] = None,
) -> list[str]:
    if df is None:
        return []
    temp = df.copy()
    if linea and "Linea" in temp.columns:
        temp = temp[temp["Linea"] == linea]
    if objetivo and "Objetivo" in temp.columns:
        temp = temp[temp["Objetivo"] == objetivo]
    if "Indicador" not in temp.columns:
        return []
    return sorted(temp["Indicador"].dropna().unique().tolist())


def obtener_lista_objetivos(
    df: pd.DataFrame,
    linea: Optional[str] = None,
) -> list[str]:
    if df is None:
        return []
    temp = df.copy()
    if linea and "Linea" in temp.columns:
        temp = temp[temp["Linea"] == linea]
    if "Objetivo" not in temp.columns:
        return []
    return sorted(temp["Objetivo"].dropna().unique().tolist())


def obtener_año_mas_reciente(df: pd.DataFrame) -> int:
    """Retorna el año máximo disponible en el DataFrame, default 2025."""
    if df is None or "Año" not in df.columns:
        return 2025
    año = df["Año"].max()
    return int(año) if pd.notna(año) else 2025


def contar_standby(df: pd.DataFrame) -> int:
    """Cuenta indicadores únicos en estado Stand by."""
    if df is None or "Ejecución s" not in df.columns:
        return 0
    mask = df["Ejecución s"].astype(str).str.strip().str.lower() == "stand by"
    df_sb = df[mask]
    if "Indicador" in df_sb.columns:
        return int(df_sb["Indicador"].nunique())
    return len(df_sb)
